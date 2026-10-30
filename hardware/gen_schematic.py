#!/usr/bin/env python3
"""Generates schematic.svg (block-level schematic with pin-level nets)."""
from xml.sax.saxutils import escape
E = lambda t: escape(t.replace('&lt;', '<'))
W,H=1500,980
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="monospace" font-size="13">',
   f'<rect width="{W}" height="{H}" fill="white"/>',
   '<text x="20" y="30" font-size="20" font-weight="bold">kmtouch - USB mouse+keyboard to HID multitouch (RP2040) - schematic v1.0</text>']
def box(x,y,w,h,title,pins_l=(),pins_r=(),color="#eef4ff"):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="black" stroke-width="2" rx="6"/>')
    o.append(f'<text x="{x+w/2}" y="{y+20}" text-anchor="middle" font-weight="bold">{E(title)}</text>')
    for i,p in enumerate(pins_l): o.append(f'<text x="{x+6}" y="{y+42+i*18}">{E(p)}</text>')
    for i,p in enumerate(pins_r): o.append(f'<text x="{x+w-6}" y="{y+42+i*18}" text-anchor="end">{E(p)}</text>')
def wire(pts,label=None,color="black"):
    d=" ".join(f"{x},{y}" for x,y in pts)
    o.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="2"/>')
    if label: x,y=pts[0]; o.append(f'<text x="{x+4}" y="{y-5}" fill="{color}" font-size="12">{E(label)}</text>')
R="#c00000"; G="#006000"; B="#0040c0"
# J1 USB-C
box(30,80,230,230,"J1 USB-C receptacle (UFP)",["VBUS (A4/A9/B4/B9)","CC1 (A5) -R1 5.1k- GND","CC2 (B5) -R2 5.1k- GND","D+ (A6/B6)","D- (A7/B7)","GND","SHIELD -1M||4.7nF- GND"])
box(30,340,230,110,"U4 USBLC6-2SC6 (ESD)",["I/O1 = D+ , I/O2 = D-","VBUS pin = VBUS_IN","GND"],color="#fff4e0")
box(30,480,230,120,"F1 PTC 0.5A (MF-MSMF050-2)",["VBUS_IN -> F1 -> 5V_SYS","C: 10uF + 100nF on 5V_SYS"],color="#fff4e0")
box(30,630,230,150,"U2 AP2112K-3.3 (LDO)",["VIN, EN  &lt;- 5V_SYS","VOUT -> 3V3 (600mA)","CIN 1uF, COUT 1uF","GND"],color="#fff4e0")
# RP2040
box(420,80,420,560,"U1 RP2040 (QFN-56)",
 ["USB_DP (47) -R3 27R- J1.D+","USB_DM (46) -R4 27R- J1.D-","","XIN (20) / XOUT (21)","  Y1 12MHz ABM8-272-T3","  2x 15pF, 1k on XOUT","QSPI_SS/SD0-3/SCLK","  -> U3 W25Q16JVUXIQ","  SS: 10k pull-up, BOOTSEL","","IOVDD/USB_VDD/ADC_VDD &lt;- 3V3","VREG_VIN &lt;- 3V3, VREG_VOUT->DVDD","  (1.1V, 1uF)","DVDD x2 100nF; 3V3 x8 100nF","RUN: 10k pull-up + RESET btn","TESTEN, GND pad -> GND"],
 ["GPIO2 -R5 22R- PIO_DP","GPIO3 -R6 22R- PIO_DM","","GPIO18 -> U5.EN (VBUS_A_EN)","GPIO19 &lt;- U5.FLG (opt.)","GPIO25 -> LED (330R)","","SWDIO/SWCLK -> TP1/TP2","","","BOOTSEL btn:","QSPI_SS-1k-GND"])
# flash
box(420,670,420,110,"U3 W25Q16JVUXIQ 2MB QSPI flash",["/CS=QSPI_SS  CLK=QSPI_SCLK","IO0..IO3 = QSPI_SD0..SD3","VCC=3V3 (100nF)"],color="#eef4ff")
# Hub
box(960,80,300,330,"U6 FE1.1s USB2.0 hub (SSOP-28)",["USBDP0/DM0 &lt;- PIO_DP/DM","  (upstream, full-speed)","XIN/XOUT: Y2 12MHz +","  2x 20pF (per datasheet)","VDD5 &lt;- 5V_A, VD33 1uF","VD18 1uF","RESET: 10k/10uF RC","DP1/DM1 -> J2","DP2/DM2 -> J3","DP3,DP4 unused","PWRJ/OVCJ: tie per DS"],[],color="#eefff0")
# load switch
box(960,440,300,150,"U5 TPS2051C / AP2553 (load sw)",["IN &lt;- 5V_SYS","EN &lt;- GPIO18","OUT -> 5V_A (500mA lim.)","FLG -> GPIO19 (10k PU)","COUT 47uF on 5V_A"],[],color="#fff4e0")
# USB-A
box(1300,80,180,150,"J2 USB-A (mouse)",["1 VBUS &lt;- 5V_A","2 D- &lt;- U6.DM1","3 D+ &lt;- U6.DP1","4 GND"],color="#f4eeff")
box(1300,260,180,150,"J3 USB-A (keyb.)",["1 VBUS &lt;- 5V_A","2 D- &lt;- U6.DM2","3 D+ &lt;- U6.DP2","4 GND"],color="#f4eeff")
box(1300,440,180,150,"U7,U8 USBLC6",["one per USB-A","on D+/D-","and 5V_A"],color="#fff4e0")
# wires
wire([(260,190),(420,190)],"D+/D- (via R3/R4 27R)",B)
wire([(260,520),(330,520),(330,600)],"5V_SYS",R)
wire([(260,140),(300,140),(300,520)],"VBUS_IN",R)
wire([(260,700),(420,700)],"3V3",R)
wire([(840,120),(960,120)],"PIO_DP/PIO_DM",B)
wire([(840,390),(900,390),(900,480),(960,480)],"VBUS_A_EN",G)
wire([(1260,520),(1280,520),(1280,120),(1300,120)],"5V_A",R)
wire([(1260,250),(1300,250)],"DP1/DM1, DP2/DM2",B)
o.append('<text x="20" y="830" font-size="14">Notes: Phone is USB host and powers everything via J1 VBUS (5V). CC1/CC2 5.1k to GND = UFP (sink), so phone turns on VBUS.</text>')
o.append('<text x="20" y="852" font-size="14">PIO-USB host runs on GPIO2/3 (D-=D+ +1, required). One PIO-USB root port -> FE1.1s hub -> 2x USB-A, so TinyUSB can enumerate both devices.</text>')
o.append('<text x="20" y="874" font-size="14">Alt (no hub): 2nd PIO-USB root port on GPIO4/5 via pio_usb_host_add_port() - needs custom host code (not TinyUSB), see README.</text>')
o.append('<text x="20" y="896" font-size="14">Budget: RP2040+hub ~50mA, mouse+kbd ~100-200mA. Many phones limit OTG to 500mA. LED/RGB keyboards may exceed it.</text>')
o.append('<text x="20" y="918" font-size="14">Reference: RP2040 "Hardware design with RP2040" minimal design; Adafruit Feather RP2040 USB Host; jfedor2/hid-remapper.</text>')
o.append('</svg>')
open("schematic.svg","w").write("\n".join(o))
