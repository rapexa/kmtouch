// kmtouch: USB mouse + keyboard -> USB HID multi-touch for Android
// core0: TinyUSB device on native USB-C (to phone) + mapper
// core1: TinyUSB host on Pico-PIO-USB (through a hub to 2x USB-A)
// Architecture inspired by jfedor2/hid-remapper and Pico-PIO-USB examples.
#include "pico/stdlib.h"
#include "pico/multicore.h"
#include "hardware/clocks.h"
#include "pio_usb.h"
#include "tusb.h"
#include "kmtouch.h"

#ifndef KMT_PIO_DP_PIN
#define KMT_PIO_DP_PIN 2
#endif
#ifndef KMT_VBUS_EN_PIN
#define KMT_VBUS_EN_PIN 18   // drives load-switch EN for USB-A VBUS (custom board); harmless on Pico
#endif

static void core1_main(void) {
  sleep_ms(10);
  pio_usb_configuration_t cfg = PIO_USB_DEFAULT_CONFIG;
  cfg.pin_dp = KMT_PIO_DP_PIN;
  tuh_configure(1, TUH_CFGID_RPI_PIO_USB_CONFIGURATION, &cfg);
  tuh_init(1);
  while (true) tuh_task();
}

int main(void) {
  set_sys_clock_khz(120000, true);   // PIO-USB needs a multiple of 12 MHz
  gpio_init(KMT_VBUS_EN_PIN); gpio_set_dir(KMT_VBUS_EN_PIN, GPIO_OUT); gpio_put(KMT_VBUS_EN_PIN, 1);
  sleep_ms(10);
  multicore_reset_core1();
  multicore_launch_core1(core1_main);
  tud_init(0);
  while (true) {
    tud_task();
    mapper_task();
  }
}

//--------------------------------------------------------------------+
// Host HID callbacks (core1)
//--------------------------------------------------------------------+
void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance, uint8_t const *desc, uint16_t len) {
  (void)desc; (void)len;
  // TinyUSB sets BOOT protocol by default for boot keyboards/mice -> fixed report format
  tuh_hid_receive_report(dev_addr, instance);
}
void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance) {
  if (tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD) input_reset_keyboard();
}
void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t instance, uint8_t const *r, uint16_t len) {
  switch (tuh_hid_interface_protocol(dev_addr, instance)) {
    case HID_ITF_PROTOCOL_KEYBOARD: if (len >= 8) input_keyboard(r); break;
    case HID_ITF_PROTOCOL_MOUSE:
      if (len >= 3) input_mouse(r[0], (int8_t)r[1], (int8_t)r[2], len >= 4 ? (int8_t)r[3] : 0);
      break;
    default: break;
  }
  tuh_hid_receive_report(dev_addr, instance);
}
