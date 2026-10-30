// kmtouch case - parametric, two-part (base + lid), M2 screws, plus lid snap lip.
// part = "base" | "lid" | "both" | "preview"
part = "preview";
pcb_w = 60;   pcb_d = 36;  pcb_t = 1.6;   // PCB size (X along ports axis)
clear = 0.6;  wall = 2.0;  floor_t = 1.6;
inner_h = 16;                              // inside height (USB-A ~7mm tall + standoff)
standoff_h = 3;
lid_t = 1.6;  lip_h = 2.0;
screw_d = 2.2; post_d = 5.5; insert_d = 1.8; // M2 self-tapping into post
// USB-A openings (on -X wall), centers along Y
usba_w = 13.8; usba_h = 7.4; usba_y = [-8.7, 8.7];   // matches KiCad J2/J3 (17.4 mm pitch)
// USB-C opening (on +X wall)
usbc_w = 9.6; usbc_h = 3.8; usbc_r = 1.6;
port_z = floor_t + standoff_h + pcb_t;     // bottom of connectors (top of PCB)
corner_r = 3;
$fn = 40;

ow = pcb_w + 2*clear + 2*wall;
boss_zone = 6;                             // strip on each long side for lid-screw bosses (clear of PCB)
od = pcb_d + 2*clear + 2*wall + 2*boss_zone;
boss_pos = [for (sx=[-1,1], sy=[-1,1]) [sx*(pcb_w/2-10), sy*(pcb_d/2+clear+boss_zone/2)]];
oh = floor_t + inner_h;
// PCB M2 holes, from KiCad H1..H4 (case x = x_kicad-130, y = 118-y_kicad)
holes = [[-11.8, 14.5], [26.5, 14.5], [-11.8, -14.5], [26.5, -14.5]];
btn_pos = [[18, -10], [8, -10]];             // SW1 BOOTSEL, SW2 RESET (press with a pin)

module rbox(w, d, h, r) {
  linear_extrude(h) offset(r) square([w-2*r, d-2*r], center=true);
}

module base() {
  difference() {
    rbox(ow, od, oh, corner_r);
    translate([0,0,floor_t]) rbox(ow-2*wall, od-2*wall, oh, corner_r-1);
    for (y = usba_y) translate([-ow/2-1, y-usba_w/2, port_z-0.4]) cube([wall+2, usba_w, usba_h+0.8]);
    translate([ow/2-wall-1, 0, port_z+usbc_h/2-0.2]) rotate([0,90,0])
      linear_extrude(wall+2) offset(usbc_r) square([usbc_h-2*usbc_r+0.4, usbc_w-2*usbc_r], center=true);
    // LED/boot-button window on top edge not needed; label recess on floor
    translate([0,0,-0.01]) linear_extrude(0.6) mirror([1,0,0])
      text("kmtouch", size=6, halign="center", valign="center");
  }
  // PCB standoffs (and lid screw path through them)
  for (h = holes) translate([h[0], h[1], 0]) difference() {
    cylinder(d=post_d, h=floor_t+standoff_h);
    translate([0,0,floor_t*0.5]) cylinder(d=insert_d, h=20);
  }
  // corner bosses for lid screws
  for (b = boss_pos) translate([b[0], b[1], 0]) difference() {
    cylinder(d=post_d, h=oh-lip_h-0.2);
    translate([0,0,floor_t]) cylinder(d=insert_d, h=oh);
  }
}

module lid() {
  difference() {
    union() {
      rbox(ow, od, lid_t, corner_r);
      // inner lip: snaps into base for alignment / light friction fit
      translate([0,0,lid_t]) difference() {
        rbox(ow-2*wall-0.4, od-2*wall-0.4, lip_h, corner_r-1);
        translate([0,0,-1]) rbox(ow-2*wall-2.8, od-2*wall-2.8, lip_h+2, corner_r-2);
      }
    }
    for (b = boss_pos) translate([b[0], b[1], -1]) {
      cylinder(d=screw_d, h=10);
      cylinder(d1=4.4, d2=screw_d, h=1+1.2);   // countersink
    }
    // corner cut for screw posts inside lip
        // vent slots + BOOTSEL / RESET pin holes
    for (i=[-3:3]) translate([i*5, 6, -1]) rbox(2, 10, lid_t+2, 0.9);
    for (b = btn_pos) translate([b[0], b[1], -1]) cylinder(d=3, h=10);
  }
}

if (part == "base") base();
else if (part == "lid") lid();
else if (part == "both") { base(); translate([0, od+8, 0]) lid(); }
else { color("SteelBlue") base(); color("LightSteelBlue", 0.85) translate([0,0,oh+lid_t+10]) mirror([0,0,1]) lid(); }
