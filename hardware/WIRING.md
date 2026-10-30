# سیم‌کشی با برد آماده

## گزینه ۱: Adafruit Feather RP2040 USB Host (پیشنهادی)
- USB-C برد ← کابل C به C (یا C به OTG) ← گوشی.
- USB-A برد (PIO-USB روی GPIO16=D+، GPIO17=D−؛ برق 5V با GPIO18 روشن می‌شه) ← یه هاب USB کوچیک بدون برق ← موس و کیبورد.
  یا یه دانگل بی‌سیم «موس+کیبورد» با یه گیرنده (بدون هاب).
- فریم‌ور: `firmware_bin/kmtouch_feather_usbhost_dp16.uf2`

## گزینه ۲: Waveshare RP2040-Zero یا Raspberry Pi Pico
| سیگنال | پین برد | مادگی USB-A (یا ورودی upstream ماژول هاب) |
|---|---|---|
| 5V | پین 5V (RP2040-Zero) / VBUS (Pico، پین 40) | پین 1 VBUS (ترجیحاً از طریق فیوز PTC 0.5A) |
| D+ | GPIO2 ← مقاومت 22Ω | پین 3 D+ |
| D− | GPIO3 ← مقاومت 22Ω | پین 2 D− |
| GND | GND | پین 4 GND |
- دو پورت: یه ماژول هاب کوچیک (مثلاً برد FE1.1s/SL2.1A) رو به همین چهار سیم وصل کن و موس و کیبورد رو به خروجی‌هاش بزن.
- USB-C خود برد ← گوشی.
- فریم‌ور: `firmware_bin/kmtouch_pico_custom_dp2.uf2`
- نکته: D− باید دقیقاً پین بعد از D+ باشه (محدودیت PIO-USB). اگه پین دیگه‌ای خواستی: `cmake -DKMT_PIO_DP_PIN=<n>`.
