// Keymapper: turns keyboard/mouse state into up to 5 simultaneous touches.
// Slot 0: virtual joystick (WASD), slot 1: camera/look drag (mouse motion),
// slots 2..4: tap buttons (keys and mouse buttons), first-come first-served.
#include <string.h>
#include "pico/stdlib.h"
#include "pico/sync.h"
#include "tusb.h"
#include "kmtouch.h"
#include "keymap_gen.h"

typedef struct { uint8_t key; uint16_t x, y; } keytap_t;
static const keytap_t keytaps[] = KM_KEYS_INIT;
#define NKEYTAPS (sizeof(keytaps) / sizeof(keytaps[0]))

// pseudo key codes for mouse buttons (unused HID usages)
#define MB_L 0xF0
#define MB_R 0xF1
#define MB_M 0xF2

static spin_lock_t *lock;
static uint8_t keys[16];                 // currently pressed usages (incl. modifiers)
static uint8_t mbuttons;
static int32_t acc_dx, acc_dy, acc_wheel;

static uint32_t lk(void) {
  if (!lock) lock = spin_lock_instance(spin_lock_claim_unused(true));
  return spin_lock_blocking(lock);
}

void input_keyboard(const uint8_t *r) {
  uint32_t s = lk();
  memset(keys, 0, sizeof keys);
  int n = 0;
  for (int b = 0; b < 8; b++) if (r[0] & (1 << b)) keys[n++] = 0xE0 + b;
  for (int i = 2; i < 8 && n < 16; i++) if (r[i] > 3) keys[n++] = r[i];
  spin_unlock(lock, s);
}
void input_reset_keyboard(void) { uint32_t s = lk(); memset(keys, 0, sizeof keys); spin_unlock(lock, s); }
void input_mouse(uint8_t b, int8_t dx, int8_t dy, int8_t w) {
  uint32_t s = lk();
  mbuttons = b; acc_dx += dx; acc_dy += dy; acc_wheel += w;
  spin_unlock(lock, s);
}

static bool down(const uint8_t *k, uint8_t code) {
  if (!code) return false;
  for (int i = 0; i < 16; i++) if (k[i] == code) return true;
  return false;
}

static int32_t clampi(int32_t v, int32_t lo, int32_t hi) { return v < lo ? lo : v > hi ? hi : v; }

// --- state ---
static bool game_mode = true;
static bool toggle_prev;
static struct { bool active; int32_t x, y; uint8_t id; } look;
static bool look_lift_frame;
static uint8_t next_id = 8;
typedef struct { uint8_t code; bool used; uint8_t id; uint16_t x, y; } tapslot_t;
static tapslot_t taps[3];
static uint8_t joy_id = 0, look_id = 1;
static bool joy_was;
static bool lifted;   // touches released after entering cursor mode

static uint8_t new_id(void) { next_id = (uint8_t)(next_id + 1); if (next_id > KMT_MAX_CONTACTS - 1 + 8) next_id = 2; return next_id; }

static bool code_pos(uint8_t code, uint16_t *x, uint16_t *y) {
  if (code == MB_L) { *x = KM_MB_L_X; *y = KM_MB_L_Y; return true; }
  if (code == MB_R) { *x = KM_MB_R_X; *y = KM_MB_R_Y; return true; }
  if (code == MB_M) { *x = KM_MB_M_X; *y = KM_MB_M_Y; return true; }
  for (unsigned i = 0; i < NKEYTAPS; i++) if (keytaps[i].key == code) { *x = keytaps[i].x; *y = keytaps[i].y; return true; }
  return false;
}

void mapper_task(void) {
  static uint32_t last_us;
  uint32_t now = time_us_32();
  if (now - last_us < 4000) return;      // 250 Hz
  if (!tud_hid_ready()) return;
  last_us = now;

  uint8_t k[16]; uint8_t mb; int32_t dx, dy, wh;
  uint32_t s = lk();
  memcpy(k, keys, sizeof k); mb = mbuttons; dx = acc_dx; dy = acc_dy; wh = acc_wheel;
  acc_dx = acc_dy = acc_wheel = 0;
  spin_unlock(lock, s);

  bool t = down(k, KM_TOGGLE_KEY);
  if (t && !toggle_prev) { game_mode = !game_mode; look.active = false; lifted = false; }
  toggle_prev = t;

  if (!game_mode) {
    // cursor mode: lift all touches once, then behave as a normal mouse
    if (!lifted) { kmt_touch_report_t r = {0}; tud_hid_report(KMT_RID_TOUCH, &r, sizeof r); lifted = true;
      memset(taps, 0, sizeof taps); joy_was = false; return; }
    kmt_mouse_report_t m = { mb, (int8_t)clampi(dx, -127, 127), (int8_t)clampi(dy, -127, 127), (int8_t)clampi(wh, -127, 127) };
    tud_hid_report(KMT_RID_MOUSE, &m, sizeof m);
    return;
  }

  kmt_touch_report_t r; memset(&r, 0, sizeof r);
  int n = 0;

  // joystick
  int jx = (down(k, KM_JOY_RIGHT) ? 1 : 0) - (down(k, KM_JOY_LEFT) ? 1 : 0);
  int jy = (down(k, KM_JOY_DOWN) ? 1 : 0) - (down(k, KM_JOY_UP) ? 1 : 0);
  if (jx || jy) {
    if (!joy_was) joy_id = new_id();
    int32_t rr = KM_JOY_R; if (jx && jy) rr = rr * 707 / 1000;
    r.c[n].tip = 1; r.c[n].id = joy_id;
    r.c[n].x = clampi(KM_JOY_X + jx * rr, 0, 32767); r.c[n].y = clampi(KM_JOY_Y + jy * rr * 16 / 9, 0, 32767);
    n++; joy_was = true;
  } else joy_was = false;

  // look / camera drag
  bool look_enabled = KM_LOOK_HOLD_KEY ? down(k, KM_LOOK_HOLD_KEY) : true;
  if (look_lift_frame) { look_lift_frame = false; look.active = false; }
  else if (look_enabled && (dx || dy || look.active)) {
    if (!look.active) { look.active = true; look.x = KM_LOOK_X; look.y = KM_LOOK_Y; look.id = new_id(); }
    look.x += dx * KM_LOOK_SX; look.y += dy * KM_LOOK_SY * 16 / 9;
    bool out = look.x < KM_LOOK_X - KM_LOOK_HW || look.x > KM_LOOK_X + KM_LOOK_HW ||
               look.y < KM_LOOK_Y - KM_LOOK_HH || look.y > KM_LOOK_Y + KM_LOOK_HH;
    r.c[n].tip = 1; r.c[n].id = look.id;
    r.c[n].x = clampi(look.x, 0, 32767); r.c[n].y = clampi(look.y, 0, 32767); n++;
    if (out) look_lift_frame = true;     // finger leaves edge -> next frame lift, then re-center
  } else look.active = false;
  (void)look_id;

  // taps: release slots whose code is no longer down
  uint8_t codes[20]; int nc = 0;
  for (int i = 0; i < 16; i++) if (k[i] && k[i] != KM_TOGGLE_KEY) codes[nc++] = k[i];
  if (mb & 1) codes[nc++] = MB_L;
  if (mb & 2) codes[nc++] = MB_R;
  if (mb & 4) codes[nc++] = MB_M;
  for (int i = 0; i < 3; i++) if (taps[i].used) {
    bool still = false; for (int j = 0; j < nc; j++) if (codes[j] == taps[i].code) still = true;
    if (!still) taps[i].used = false;
  }
  for (int j = 0; j < nc; j++) {
    uint16_t x, y; bool have = false;
    for (int i = 0; i < 3; i++) if (taps[i].used && taps[i].code == codes[j]) have = true;
    if (have || !code_pos(codes[j], &x, &y)) continue;
    for (int i = 0; i < 3; i++) if (!taps[i].used) { taps[i] = (tapslot_t){codes[j], true, new_id(), x, y}; break; }
  }
  for (int i = 0; i < 3 && n < KMT_MAX_CONTACTS; i++) if (taps[i].used) {
    r.c[n].tip = 1; r.c[n].id = taps[i].id; r.c[n].x = taps[i].x; r.c[n].y = taps[i].y; n++;
  }

  // Report only when something changed (plus keep-alive while touching)
  static kmt_touch_report_t prev; static uint32_t prev_t;
  r.count = n;
  if (memcmp(&r, &prev, sizeof r) == 0 && (n == 0 || now - prev_t < 50000)) return;
  tud_hid_report(KMT_RID_TOUCH, &r, sizeof r);
  prev = r; prev_t = now;
}
