import json
f="/workspace/kmtouch/hardware/kicad/kmtouch.kicad_pro"; pro=json.load(open(f))
ns=pro["net_settings"]; base=ns["classes"][0]
def cls(n,c,t):
    d=dict(base); d.update(name=n,clearance=c,track_width=t,via_diameter=0.6,via_drill=0.3,priority=(2147483647 if n=="Default" else 0)); return d
ns["classes"]=[cls("Default",0.15,0.18),cls("Power",0.15,0.3),cls("Supply",0.15,0.2),cls("USB",0.15,0.2)]
ns["netclass_patterns"]=[{"netclass":"Power","pattern":p} for p in ["VBUS","+5V","5V_A"]]+[{"netclass":"Supply","pattern":p} for p in ["+3V3","+1V1","VD33H"]]+[{"netclass":"USB","pattern":p} for p in ["USB_D?","CD?","HUB_D?","A?D?"]]
r=pro["board"]["design_settings"]["rules"]
r.update(min_clearance=0.15,min_track_width=0.15,min_via_diameter=0.6,min_through_hole_diameter=0.3,min_via_annular_width=0.13,min_copper_edge_clearance=0.3,min_hole_clearance=0.25,min_hole_to_hole=0.25)
json.dump(pro,open(f,"w"),indent=2); print(list(pro["board"]["design_settings"].keys()))
pro=json.load(open(f))
pro["board"]["design_settings"]["rule_severities"]["lib_footprint_mismatch"]="ignore"
pro["board"]["design_settings"]["rules"]["min_text_height"]=0.8
json.dump(pro,open(f,"w"),indent=2)
