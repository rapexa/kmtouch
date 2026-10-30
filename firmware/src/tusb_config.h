#pragma once
// Native USB (rhport 0) = device to the phone; PIO-USB (rhport 1) = host for mouse/keyboard
#define CFG_TUSB_MCU OPT_MCU_RP2040
#define CFG_TUSB_OS OPT_OS_PICO
#define CFG_TUSB_RHPORT0_MODE OPT_MODE_DEVICE
#define CFG_TUD_ENABLED 1
#define CFG_TUH_ENABLED 1
#define CFG_TUH_RPI_PIO_USB 1
#define BOARD_TUH_RHPORT 1
#define CFG_TUD_ENDPOINT0_SIZE 64
#define CFG_TUD_HID 1
#define CFG_TUD_HID_EP_BUFSIZE 64
#define CFG_TUD_CDC 0
#define CFG_TUD_MSC 0
#define CFG_TUD_MIDI 0
#define CFG_TUD_VENDOR 0
// Host: external hub so two USB-A ports work on one PIO-USB root port
#define CFG_TUH_ENUMERATION_BUFSIZE 256
#define CFG_TUH_HUB 1
#define CFG_TUH_DEVICE_MAX (CFG_TUH_HUB ? 4 : 1)
#define CFG_TUH_HID (3 * CFG_TUH_DEVICE_MAX)
#define CFG_TUH_HID_EPIN_BUFSIZE 64
#define CFG_TUH_HID_EPOUT_BUFSIZE 8
