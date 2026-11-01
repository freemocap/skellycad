cmake_minimum_required(VERSION 3.16)
get_filename_component(SKELLY_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)
set(EXTRA_COMPONENT_DIRS "${SKELLY_ROOT}/.cad-tools/esp-video-components/esp_cam_sensor"
                         "${SKELLY_ROOT}/.cad-tools/esp-video-components/esp_sccb_intf")
set(COMPONENTS main)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(skelly_eye_camera)
