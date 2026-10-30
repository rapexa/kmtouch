// USB device descriptors: one HID interface exposing
//  - Report 1: multi-touch touchscreen (Digitizer page, 5 contacts, 0..32767)
//  - Report 2: relative mouse (used in "cursor" mode)
//  - Report 3: feature "Contact Count Maximum" (required by Windows, fine on Android)
#include "tusb.h"
#include "kmtouch.h"
#include "pico/unique_id.h"

#define CONTACT \
  HID_USAGE_PAGE(HID_USAGE_PAGE_DIGITIZER), HID_USAGE(0x22), /* Finger */ \
  HID_COLLECTION(HID_COLLECTION_LOGICAL), \
    HID_USAGE(0x42), HID_LOGICAL_MIN(0), HID_LOGICAL_MAX(1), \
    HID_REPORT_SIZE(1), HID_REPORT_COUNT(1), HID_INPUT(HID_DATA|HID_VARIABLE|HID_ABSOLUTE), /* Tip Switch */ \
    HID_REPORT_COUNT(7), HID_INPUT(HID_CONSTANT), \
    HID_USAGE(0x51), HID_REPORT_SIZE(8), HID_REPORT_COUNT(1), HID_LOGICAL_MAX(KMT_MAX_CONTACTS-1+8), \
    HID_INPUT(HID_DATA|HID_VARIABLE|HID_ABSOLUTE), /* Contact ID */ \
    HID_USAGE_PAGE(HID_USAGE_PAGE_DESKTOP), \
    HID_LOGICAL_MIN(0), HID_LOGICAL_MAX_N(32767, 2), HID_REPORT_SIZE(16), HID_REPORT_COUNT(1), \
    HID_UNIT_EXPONENT(0x0E), HID_UNIT(0x11), HID_PHYSICAL_MIN(0), HID_PHYSICAL_MAX_N(1500, 2), \
    HID_USAGE(HID_USAGE_DESKTOP_X), HID_INPUT(HID_DATA|HID_VARIABLE|HID_ABSOLUTE), \
    HID_PHYSICAL_MAX_N(700, 2), \
    HID_USAGE(HID_USAGE_DESKTOP_Y), HID_INPUT(HID_DATA|HID_VARIABLE|HID_ABSOLUTE), \
    HID_PHYSICAL_MAX(0), HID_UNIT(0), HID_UNIT_EXPONENT(0), \
  HID_COLLECTION_END

uint8_t const desc_hid_report[] = {
  HID_USAGE_PAGE(HID_USAGE_PAGE_DIGITIZER), HID_USAGE(0x04), /* Touch Screen */
  HID_COLLECTION(HID_COLLECTION_APPLICATION),
    HID_REPORT_ID(KMT_RID_TOUCH)
    CONTACT, CONTACT, CONTACT, CONTACT, CONTACT,
    HID_USAGE_PAGE(HID_USAGE_PAGE_DIGITIZER),
    HID_USAGE(0x54), HID_LOGICAL_MIN(0), HID_LOGICAL_MAX(KMT_MAX_CONTACTS), /* Contact Count */
    HID_REPORT_SIZE(8), HID_REPORT_COUNT(1), HID_INPUT(HID_DATA|HID_VARIABLE|HID_ABSOLUTE),
    HID_REPORT_ID(KMT_RID_MAXCOUNT)
    HID_USAGE(0x55), HID_LOGICAL_MAX(KMT_MAX_CONTACTS), /* Contact Count Maximum */
    HID_FEATURE(HID_DATA|HID_VARIABLE|HID_ABSOLUTE),
  HID_COLLECTION_END,
  TUD_HID_REPORT_DESC_MOUSE(HID_REPORT_ID(KMT_RID_MOUSE))
};

tusb_desc_device_t const desc_device = {
  .bLength = sizeof(tusb_desc_device_t), .bDescriptorType = TUSB_DESC_DEVICE, .bcdUSB = 0x0200,
  .bDeviceClass = 0, .bDeviceSubClass = 0, .bDeviceProtocol = 0,
  .bMaxPacketSize0 = CFG_TUD_ENDPOINT0_SIZE,
  .idVendor = 0x1209, .idProduct = 0x4B54, /* pid.codes test range; get your own PID before selling */
  .bcdDevice = 0x0100, .iManufacturer = 1, .iProduct = 2, .iSerialNumber = 3, .bNumConfigurations = 1
};
uint8_t const *tud_descriptor_device_cb(void) { return (uint8_t const *)&desc_device; }
uint8_t const *tud_hid_descriptor_report_cb(uint8_t itf) { (void)itf; return desc_hid_report; }

#define CONFIG_TOTAL_LEN (TUD_CONFIG_DESC_LEN + TUD_HID_DESC_LEN)
uint8_t const desc_configuration[] = {
  // bus powered, 100 mA for the gadget itself (+ mouse/keyboard draw from phone VBUS)
  TUD_CONFIG_DESCRIPTOR(1, 1, 0, CONFIG_TOTAL_LEN, 0, 100),
  TUD_HID_DESCRIPTOR(0, 0, HID_ITF_PROTOCOL_NONE, sizeof(desc_hid_report), 0x81, CFG_TUD_HID_EP_BUFSIZE, 1)
};
uint8_t const *tud_descriptor_configuration_cb(uint8_t index) { (void)index; return desc_configuration; }

static char const *string_desc[] = { (const char[]){0x09, 0x04}, "kmtouch", "kmtouch Mouse/Keyboard Touch Adapter", NULL };
static uint16_t _desc_str[33];
uint16_t const *tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
  (void)langid; uint8_t n;
  if (index == 0) { memcpy(&_desc_str[1], string_desc[0], 2); n = 1; }
  else {
    char serial[2 * PICO_UNIQUE_BOARD_ID_SIZE_BYTES + 1];
    const char *s;
    if (index == 3) { pico_get_unique_board_id_string(serial, sizeof serial); s = serial; }
    else if (index < 3) s = string_desc[index]; else return NULL;
    n = strlen(s); if (n > 32) n = 32;
    for (uint8_t i = 0; i < n; i++) _desc_str[1 + i] = s[i];
  }
  _desc_str[0] = (TUSB_DESC_STRING << 8) | (2 * n + 2);
  return _desc_str;
}

// Feature report: Contact Count Maximum
uint16_t tud_hid_get_report_cb(uint8_t itf, uint8_t report_id, hid_report_type_t type, uint8_t *buf, uint16_t reqlen) {
  (void)itf; (void)reqlen;
  if (type == HID_REPORT_TYPE_FEATURE && report_id == KMT_RID_MAXCOUNT) { buf[0] = KMT_MAX_CONTACTS; return 1; }
  return 0;
}
void tud_hid_set_report_cb(uint8_t itf, uint8_t report_id, hid_report_type_t type, uint8_t const *buf, uint16_t size) {
  (void)itf; (void)report_id; (void)type; (void)buf; (void)size;
}
