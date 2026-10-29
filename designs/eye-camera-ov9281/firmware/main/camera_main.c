// R11 board-specific capture implementation. See ../board-contract.json.
// Public API basis:
// [@espressifOv9281Driver; @espIdfCameraController; @espTinyusbSerialExample].
// Build validation is not evidence of a functioning physical camera.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_cam_ctlr.h"
#include "esp_cam_ctlr_csi.h"
#include "esp_cam_sensor.h"
#include "esp_sccb_i2c.h"
#include "esp_ldo_regulator.h"
#include "esp_timer.h"
#include "esp_cache.h"
#include "esp_log.h"
#include "ov9281.h"
#include "tinyusb.h"
#include "tusb_cdc_acm.h"
#include "tusb.h"
#ifndef CONFIG_SKELLY_SYNTHETIC
#define CONFIG_SKELLY_SYNTHETIC 0
#endif

enum { WIDTH = 640, HEIGHT = 400, FRAME_BYTES = WIDTH * HEIGHT,
       LED_GPIO = 5, RESET_ASSERT_GPIO = 6, SCL_GPIO = 7, SDA_GPIO = 8 };
static QueueHandle_t requests, completed;
static esp_cam_ctlr_handle_t controller;
static uint8_t *pixels;
static uint32_t sequence;
static const char *TAG = "skelly_camera";
typedef struct { uint8_t *buffer; size_t size; int64_t timestamp_us; } completion_t;
typedef struct { char opcode; uint32_t value; } command_t;
static esp_cam_sensor_device_t *sensor;

static uint32_t frame_crc(const uint8_t *data, size_t len) {
    uint32_t crc = UINT32_MAX;
    while (len--) {
        crc ^= *data++;
        for (int bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
static void put_le(uint8_t *dst, uint64_t n, unsigned bytes) {
    for (unsigned i = 0; i < bytes; ++i) dst[i] = (uint8_t)(n >> (8 * i));
}
static bool write_usb(const uint8_t *data, size_t len) {
    int64_t deadline = esp_timer_get_time() + 5000000;
    while (len && tud_cdc_connected() && esp_timer_get_time() < deadline) {
        size_t wanted = len > 4096 ? 4096 : len;
        size_t written = tinyusb_cdcacm_write_queue(TINYUSB_CDC_ACM_0, data, wanted);
        data += written; len -= written;
        esp_err_t err = tinyusb_cdcacm_write_flush(TINYUSB_CDC_ACM_0, pdMS_TO_TICKS(20));
        if (err != ESP_OK && err != ESP_ERR_TIMEOUT) return false;
        if (!written) vTaskDelay(pdMS_TO_TICKS(1));
    }
    return len == 0;
}
static void receive_command(int itf, cdcacm_event_t *event) {
    (void)event;
    uint8_t commands[64]; size_t count = 0;
    if (tinyusb_cdcacm_read(itf, commands, sizeof(commands), &count) != ESP_OK) return;
    // One client, request/response. F remains the legacy single-byte snapshot.
    // Settings are E<decimal lines>\n and G<decimal gain-table index>\n.
    // No sensor calls or USB writes occur in this receive callback.
    static char opcode;
    static uint32_t value;
    static unsigned digits;
    static bool invalid;
    for (size_t i = 0; i < count; ++i) {
        char ch = commands[i];
        if (ch == '\n') {
            if (opcode && digits && !invalid) {
                command_t command = {opcode, value};
                xQueueSend(requests, &command, 0);
            }
            opcode = 0; value = 0; digits = 0; invalid = false;
        } else if (!opcode && !invalid && ch == 'F') {
            command_t command = {'F', 0}; xQueueSend(requests, &command, 0);
        } else if (!opcode && !invalid && (ch == 'E' || ch == 'G')) {
            opcode = ch;
        } else if (opcode && ch >= '0' && ch <= '9' && digits < 9 && !invalid) {
            value = value * 10 + (ch - '0'); ++digits;
        } else invalid = true;
    }
    // Queue overflow or malformed input yields no response; host times out.
}
static void set_control(command_t command) {
    uint32_t id = command.opcode == 'E' ? ESP_CAM_SENSOR_EXPOSURE_VAL : ESP_CAM_SENSOR_GAIN;
    esp_cam_sensor_param_desc_t desc = {.id = id};
    esp_err_t err = sensor ? esp_cam_sensor_query_para_desc(sensor, &desc) : ESP_ERR_NOT_SUPPORTED;
    if (err == ESP_OK) {
        bool valid = command.opcode == 'E'
            ? (command.value >= desc.number.minimum && command.value <= desc.number.maximum)
            : command.value < desc.enumeration.count;
        err = valid ? esp_cam_sensor_set_para_value(sensor, id, &command.value, sizeof(command.value)) : ESP_ERR_INVALID_ARG;
    }
    char response[64];
    int length = snprintf(response, sizeof(response), "!%c %s %lu\n", command.opcode,
                          err == ESP_OK ? "OK" : "ERR", (unsigned long)(err == ESP_OK ? command.value : err));
    write_usb((const uint8_t *)response, (size_t)length);
}
static bool capture_finished(esp_cam_ctlr_handle_t handle, esp_cam_ctlr_trans_t *trans, void *ctx) {
    (void)handle; (void)ctx;
    completion_t done = {trans->buffer, trans->received_size, esp_timer_get_time()};
    BaseType_t wake = pdFALSE;
    xQueueSendFromISR(completed, &done, &wake);
    return wake == pdTRUE;
}
static void init_camera(void) {
    esp_ldo_channel_handle_t mipi_supply;
    esp_ldo_channel_config_t ldo = {.chan_id = 3, .voltage_mv = 2500};
    ESP_ERROR_CHECK(esp_ldo_acquire_channel(&ldo, &mipi_supply));
    // Q103 inverts GPIO6. Do not pass GPIO6 as the driver's active-low reset.
    gpio_set_level(RESET_ASSERT_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(20));
    gpio_set_level(RESET_ASSERT_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(20));
    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_0, .sda_io_num = SDA_GPIO, .scl_io_num = SCL_GPIO,
        .clk_source = I2C_CLK_SRC_DEFAULT, .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = false,
    };
    i2c_master_bus_handle_t bus;
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &bus));
    // Assembly variant: R7 DNP, R8 populated; SID low, 7-bit address 0x60.
    _Static_assert(OV9281_SCCB_ADDR == 0x60, "SID-low assembly mismatch");
    sccb_i2c_config_t sccb_config = {.device_address = OV9281_SCCB_ADDR,
        .dev_addr_length = I2C_ADDR_BIT_LEN_7, .scl_speed_hz = 100000};
    esp_sccb_io_handle_t sccb;
    ESP_ERROR_CHECK(sccb_new_i2c_io(bus, &sccb_config, &sccb));
    esp_cam_sensor_config_t sensor_config = {.sccb_handle = sccb,
        .reset_pin = -1, .pwdn_pin = -1, .xclk_pin = -1,
        .sensor_port = ESP_CAM_SENSOR_MIPI_CSI};
    sensor = ov9281_detect(&sensor_config);
    ESP_ERROR_CHECK(sensor ? ESP_OK : ESP_ERR_NOT_FOUND);
    esp_cam_sensor_format_array_t modes;
    ESP_ERROR_CHECK(esp_cam_sensor_query_format(sensor, &modes));
    const esp_cam_sensor_format_t *mode = NULL;
    for (int i = 0; i < modes.count; ++i)
        if (strcmp(modes.format_array[i].name, "MIPI_2lane_24Minput_RAW8_640x400_100fps") == 0)
            mode = &modes.format_array[i];
    ESP_ERROR_CHECK(mode ? ESP_OK : ESP_ERR_NOT_SUPPORTED);
    ESP_ERROR_CHECK(esp_cam_sensor_set_format(sensor, mode));
    esp_cam_ctlr_csi_config_t csi = {.ctlr_id = 0, .h_res = WIDTH, .v_res = HEIGHT,
        .data_lane_num = 2, .lane_bit_rate_mbps = CONFIG_SKELLY_CSI_LANE_MBPS, .queue_items = 1,
        .input_data_color_type = CAM_CTLR_COLOR_RAW8,
        .output_data_color_type = CAM_CTLR_COLOR_RAW8};
    ESP_ERROR_CHECK(esp_cam_new_csi_ctlr(&csi, &controller));
    pixels = esp_cam_ctlr_alloc_buffer(controller, FRAME_BYTES, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
    ESP_ERROR_CHECK(pixels ? ESP_OK : ESP_ERR_NO_MEM);
    memset(pixels, 0, FRAME_BYTES);
    ESP_ERROR_CHECK(esp_cache_msync(pixels, FRAME_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_C2M));
    esp_cam_ctlr_evt_cbs_t callbacks = {.on_trans_finished = capture_finished};
    ESP_ERROR_CHECK(esp_cam_ctlr_register_event_callbacks(controller, &callbacks, NULL));
    ESP_ERROR_CHECK(esp_cam_ctlr_enable(controller));
    ESP_ERROR_CHECK(esp_cam_ctlr_start(controller));
    int stream = 1;
    ESP_ERROR_CHECK(esp_cam_sensor_ioctl(sensor, ESP_CAM_SENSOR_IOC_S_STREAM, &stream));
    // No ISP or Bayer interpolation: retain each monochrome sensor sample.
}
void app_main(void) {
    requests = xQueueCreate(1, sizeof(command_t));
    completed = xQueueCreate(1, sizeof(completion_t));
    assert(requests && completed);
    gpio_set_level(LED_GPIO, 0);
    gpio_set_level(RESET_ASSERT_GPIO, 1);
    gpio_config_t gpio = {.pin_bit_mask = (1ULL << LED_GPIO) | (1ULL << RESET_ASSERT_GPIO),
        .mode = GPIO_MODE_OUTPUT};
    ESP_ERROR_CHECK(gpio_config(&gpio));
    if (CONFIG_SKELLY_SYNTHETIC) {
        pixels = heap_caps_malloc(FRAME_BYTES, MALLOC_CAP_SPIRAM);
        ESP_ERROR_CHECK(pixels ? ESP_OK : ESP_ERR_NO_MEM);
    } else init_camera();
    const tinyusb_config_t usb = {.external_phy = false};
    ESP_ERROR_CHECK(tinyusb_driver_install(&usb));
    tinyusb_config_cdcacm_t cdc = {.usb_dev = TINYUSB_USBDEV_0,
        .cdc_port = TINYUSB_CDC_ACM_0, .rx_unread_buf_sz = 64,
        .callback_rx = receive_command};
    ESP_ERROR_CHECK(tusb_cdc_acm_init(&cdc));
    ESP_LOGI(TAG, "R11 RAW8 snapshot service; synthetic=%d; LED remains OFF", CONFIG_SKELLY_SYNTHETIC);
    while (1) {
        command_t command;
        xQueueReceive(requests, &command, portMAX_DELAY);
        if (!tud_cdc_connected()) continue;
        if (command.opcode != 'F') { set_control(command); continue; }
        int64_t timestamp;
        if (CONFIG_SKELLY_SYNTHETIC) {
            for (size_t y = 0; y < HEIGHT; ++y)
                for (size_t x = 0; x < WIDTH; ++x) pixels[y * WIDTH + x] = (x + y + sequence) & 255;
            timestamp = esp_timer_get_time();
        } else {
            esp_cam_ctlr_trans_t transaction = {.buffer = pixels, .buflen = FRAME_BYTES};
            ESP_ERROR_CHECK(esp_cam_ctlr_receive(controller, &transaction, 1000));
            completion_t done;
            if (xQueueReceive(completed, &done, pdMS_TO_TICKS(1000)) != pdTRUE) {
                // A timed-out DMA may still own pixels. Hold reset and stop here;
                // never requeue or transmit a buffer whose ownership is unknown.
                gpio_set_level(RESET_ASSERT_GPIO, 1);
                ESP_LOGE(TAG, "Camera timeout; capture halted until reset");
                vTaskSuspend(NULL);
            }
            ESP_ERROR_CHECK(done.buffer == pixels && done.size == FRAME_BYTES ? ESP_OK : ESP_FAIL);
            // v5.5.6 CSI code invalidates using received_size before assigning it.
            // Invalidate the complete known DMA buffer explicitly before reading.
            ESP_ERROR_CHECK(esp_cache_msync(pixels, FRAME_BYTES, ESP_CACHE_MSYNC_FLAG_DIR_M2C));
            timestamp = done.timestamp_us;
        }
        uint8_t header[32] = {'S','K','Y','1'};
        put_le(header + 4, 1, 2); put_le(header + 6, CONFIG_SKELLY_SYNTHETIC ? 1 : 0, 2);
        put_le(header + 8, WIDTH, 2); put_le(header + 10, HEIGHT, 2);
        put_le(header + 12, sequence++, 4); put_le(header + 16, timestamp, 8);
        put_le(header + 24, FRAME_BYTES, 4); put_le(header + 28, frame_crc(pixels, FRAME_BYTES), 4);
        if (!write_usb(header, sizeof(header)) || !write_usb(pixels, FRAME_BYTES))
            ESP_LOGW(TAG, "USB transfer interrupted; host must resynchronize");
        // The application buffer is not queued again until USB has copied it.
        // CSI discards intervening frames into its separate backup buffer.
    }
}
