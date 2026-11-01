idf_component_register(SRCS "camera_main.c" INCLUDE_DIRS "."
    REQUIRES esp_driver_cam esp_driver_gpio esp_driver_i2c esp_timer esp_cam_sensor esp_sccb_intf esp_tinyusb)
