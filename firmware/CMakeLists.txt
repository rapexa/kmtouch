cmake_minimum_required(VERSION 3.13)
# Paths: set PICO_SDK_PATH and PICO_PIO_USB_PATH (env or -D)
if(NOT DEFINED PICO_PIO_USB_PATH)
  set(PICO_PIO_USB_PATH ${CMAKE_CURRENT_LIST_DIR}/../deps/Pico-PIO-USB)
endif()
set(PICO_BOARD pico CACHE STRING "board")
include(pico_sdk_import.cmake)
project(kmtouch C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_subdirectory(${PICO_PIO_USB_PATH} pico_pio_usb)

# Optional: regenerate keymap.h from keymap.json
find_package(Python3 COMPONENTS Interpreter)
if(Python3_FOUND)
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_LIST_DIR}/src/keymap_gen.h
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/tools/json2keymap.py
            ${CMAKE_CURRENT_LIST_DIR}/keymap.json ${CMAKE_CURRENT_LIST_DIR}/src/keymap_gen.h
    DEPENDS ${CMAKE_CURRENT_LIST_DIR}/keymap.json ${CMAKE_CURRENT_LIST_DIR}/tools/json2keymap.py)
endif()

add_executable(kmtouch
  src/main.c src/mapper.c src/usb_descriptors.c src/keymap_gen.h
  ${PICO_TINYUSB_PATH}/src/portable/raspberrypi/pio_usb/hcd_pio_usb.c)
target_include_directories(kmtouch PRIVATE src)
# GPIO of PIO-USB D+ (D- = D+ + 1). Override: -DKMT_PIO_DP_PIN=12
if(NOT DEFINED KMT_PIO_DP_PIN)
  set(KMT_PIO_DP_PIN 2)
endif()
target_compile_definitions(kmtouch PRIVATE PIO_USB_USE_TINYUSB KMT_PIO_DP_PIN=${KMT_PIO_DP_PIN})
target_compile_options(kmtouch PRIVATE -Wall)
target_link_libraries(kmtouch PRIVATE pico_stdlib pico_multicore pico_pio_usb
  tinyusb_device tinyusb_host hardware_clocks pico_unique_id)
pico_add_extra_outputs(kmtouch)
