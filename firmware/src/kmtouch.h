#pragma once
#include <stdint.h>
#include <stdbool.h>
#define KMT_MAX_CONTACTS 5
#define KMT_RID_TOUCH 1
#define KMT_RID_MOUSE 2
#define KMT_RID_MAXCOUNT 3

typedef struct __attribute__((packed)) {
  uint8_t tip;        // bit0 tip switch, bits1-7 padding
  uint8_t id;         // contact identifier
  uint16_t x, y;      // 0..32767
} kmt_contact_t;

typedef struct __attribute__((packed)) {
  kmt_contact_t c[KMT_MAX_CONTACTS];
  uint8_t count;      // contact count (valid contacts in this report)
} kmt_touch_report_t;

typedef struct __attribute__((packed)) {
  uint8_t buttons; int8_t x, y, wheel;
} kmt_mouse_report_t;

// Input state, written by host side (core1), read by mapper (core0)
void input_keyboard(const uint8_t *boot_report);
void input_mouse(uint8_t buttons, int8_t dx, int8_t dy, int8_t wheel);
void input_reset_keyboard(void);
// Mapper, called every frame on core0
void mapper_task(void);
