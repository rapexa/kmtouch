import sys,uuid,copy; sys.path.insert(0,"/workspace/kmtouch/hardware/kicad/gen")
from sexp import *
import circuit
NS=uuid.UUID("6b6d746f-7563-6800-0000-000000000000")
def U(s): return str(uuid.uuid5(NS,s))
ROOT=U("root")
parts=list(circuit.P)
flags=["VBUS","GND","+5V"]
for i,n in enumerate(flags): parts.append(dict(ref=f"#FLG0{i+1}",sym="power:PWR_FLAG",fp="",val="PWR_FLAG",lcsc="",pins={"1":n}))
libsyms={}
for p in parts:
    if p["sym"] not in libsyms:
        lib,name=p["sym"].split(":"); s=copy.deepcopy(load_symbol(lib,name)); s[1]=p["sym"]; libsyms[p["sym"]]=s
def font(h=None): 
    e=[Sym("effects"),[Sym("font"),[Sym("size"),1.27,1.27]]]
    if h: e.append([Sym("justify"),Sym(h)])
    return e
def hide_eff(): return [Sym("effects"),[Sym("font"),[Sym("size"),1.27,1.27]],[Sym("hide"),Sym("yes")]]
items=[]
G=2.54
def snap(v): return round(v/1.27)*1.27
x,y,rowh=20*G/G*25.4/10,20.32,0
X=25.4; Y=25.4; W=560
for p in parts:
    s=libsyms[p["sym"]]; ps=pins(s)
    xs=[q["x"] for q in ps]+[0]; ys=[-q["y"] for q in ps]+[0]
    lw=max([len(n) for n in p["pins"].values()]+[3])*1.1+5
    minx,maxx,miny,maxy=min(xs)-lw,max(xs)+lw,min(ys)-5,max(ys)+5
    if max(xs)-min(xs)<2: minx-=4; maxx+=4
    w=maxx-minx; h=maxy-miny
    if X+w>W: X=25.4; Y+=rowh+5; rowh=0
    sx=snap(X-minx); sy=snap(Y-miny); X+=w+5; rowh=max(rowh,h)
    if p["sym"].startswith("power:"): rf=p["ref"]
    else: rf=p["ref"]
    inst=[Sym("symbol"),[Sym("lib_id"),p["sym"]],[Sym("at"),sx,sy,0],[Sym("unit"),1],[Sym("exclude_from_sim"),Sym("no")],
          [Sym("in_bom"),Sym("no" if rf.startswith("#") or rf.startswith("H") or rf.startswith("TP") else "yes")],[Sym("on_board"),Sym("no" if rf.startswith("#") else "yes")],[Sym("dnp"),Sym("no")],
          [Sym("uuid"),U(rf)]]
    by=min(ys); ty=max(ys)
    inst.append([Sym("property"),"Reference",rf,[Sym("at"),sx,sy+by-2.54 if by<0 else sy-3.81,0],font()] + ([] ))
    inst.append([Sym("property"),"Value",p["val"],[Sym("at"),sx,sy+ty+2.54,0],font()])
    inst.append([Sym("property"),"Footprint",p["fp"],[Sym("at"),sx,sy,0],hide_eff()])
    inst.append([Sym("property"),"Datasheet","",[Sym("at"),sx,sy,0],hide_eff()])
    if p["lcsc"]: inst.append([Sym("property"),"LCSC",p["lcsc"],[Sym("at"),sx,sy,0],hide_eff()])
    for q in ps: inst.append([Sym("pin"),q["num"],[Sym("uuid"),U(rf+"/"+q["num"])]])
    inst.append([Sym("instances"),[Sym("project"),"kmtouch",[Sym("path"),"/"+ROOT,[Sym("reference"),rf],[Sym("unit"),1]]]])
    items.append(inst)
    seen=set()
    for q in ps:
        px=round(sx+q["x"],2); py=round(sy-q["y"],2)
        if (px,py) in seen: continue
        n=p["pins"].get(q["num"])
        if n is None:
            if q["type"]=="no_connect" or "hide" in str(q): continue
            items.append([Sym("no_connect"),[Sym("at"),px,py],[Sym("uuid"),U(rf+"nc"+q["num"])]]); seen.add((px,py)); continue
        seen.add((px,py))
        ang={0:180,180:0,90:270,270:90}[int(q["rot"])%360]
        just="right" if ang in (180,270) else "left"
        items.append([Sym("global_label"),n,[Sym("shape"),Sym("passive")],[Sym("at"),px,py,ang],[Sym("fields_autoplaced"),Sym("yes")],font(just),[Sym("uuid"),U(rf+"lb"+q["num"])],[Sym("property"),"Intersheetrefs","${INTERSHEET_REFS}",[Sym("at"),px,py,0],hide_eff()]])
sch=[Sym("kicad_sch"),[Sym("version"),20250114],[Sym("generator"),"eeschema"],[Sym("generator_version"),"9.0"],[Sym("uuid"),ROOT],[Sym("paper"),"A2"],
     [Sym("title_block"),[Sym("title"),"kmtouch - USB keyboard/mouse to HID touchscreen for Android"],[Sym("rev"),"1"],[Sym("company"),"kmtouch"]],
     [Sym("lib_symbols")]+list(libsyms.values())]+items+[[Sym("sheet_instances"),[Sym("path"),"/",[Sym("page"),"1"]]],[Sym("embedded_fonts"),Sym("no")]]
open("/workspace/kmtouch/hardware/kicad/kmtouch.kicad_sch","w").write(dump(sch)+"\n")
print("ok",len(items))
