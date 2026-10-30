#!/usr/bin/env python3
"""Convert keymap.json into src/keymap_gen.h (normalized 0..32767 coords)."""
import json, sys
K = {"NONE":0,"SPACE":0x2C,"ENTER":0x28,"ESC":0x29,"BACKSPACE":0x2A,"TAB":0x2B,"GRAVE":0x35,
     "SHIFT":0xE1,"CTRL":0xE0,"ALT":0xE2,"RSHIFT":0xE5,"RCTRL":0xE4,"RALT":0xE6,
     "UP":0x52,"DOWN":0x51,"LEFT":0x50,"RIGHT":0x4F,"MINUS":0x2D,"EQUAL":0x2E,
     "LBRACKET":0x2F,"RBRACKET":0x30,"SEMICOLON":0x33,"QUOTE":0x34,"COMMA":0x36,"DOT":0x37,"SLASH":0x38}
for i,c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"): K[c]=0x04+i
for i,c in enumerate("1234567890"): K[c]=0x1E+i
for i in range(1,13): K["F%d"%i]=0x3A+i-1
def kc(n):
    n=str(n).upper()
    if n not in K: sys.exit("unknown key name: "+n)
    return K[n]
def c(v): return max(0,min(32767,int(round(float(v)*32767))))
src,dst=sys.argv[1],sys.argv[2]
j=json.load(open(src))
js,lk=j["joystick"],j["look"]
o=["// AUTO-GENERATED from keymap.json by tools/json2keymap.py - do not edit","#pragma once",
 "#define KM_TOGGLE_KEY 0x%02X"%kc(j.get("toggle_mode_key","GRAVE")),
 "#define KM_LOOK_HOLD_KEY 0x%02X"%kc(j.get("look_hold_key","NONE")),
 "#define KM_JOY_X %d"%c(js["x"]),"#define KM_JOY_Y %d"%c(js["y"]),"#define KM_JOY_R %d"%c(js["radius"]),
 "#define KM_JOY_UP 0x%02X"%kc(js["up"]),"#define KM_JOY_DOWN 0x%02X"%kc(js["down"]),
 "#define KM_JOY_LEFT 0x%02X"%kc(js["left"]),"#define KM_JOY_RIGHT 0x%02X"%kc(js["right"]),
 "#define KM_LOOK_X %d"%c(lk["x"]),"#define KM_LOOK_Y %d"%c(lk["y"]),
 "#define KM_LOOK_HW %d"%c(lk["half_w"]),"#define KM_LOOK_HH %d"%c(lk["half_h"]),
 "#define KM_LOOK_SX %d"%int(lk["sens_x"]),"#define KM_LOOK_SY %d"%int(lk["sens_y"])]
for b,n in (("mouse_left","L"),("mouse_right","R"),("mouse_middle","M")):
    p=j[b]; o+=["#define KM_MB_%s_X %d"%(n,c(p["x"])),"#define KM_MB_%s_Y %d"%(n,c(p["y"]))]
o.append("#define KM_KEYS_INIT { \\")
for k in j["keys"]: o.append("  {0x%02X, %d, %d}, \\"%(kc(k["key"]),c(k["x"]),c(k["y"])))
o.append("}")
open(dst,"w").write("\n".join(o)+"\n")
print("wrote",dst)
