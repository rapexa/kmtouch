import pcbnew,uuid,sys,subprocess
sys.path.insert(0,"/workspace/kmtouch/hardware/kicad/gen"); from sexp import parse,find,find1
NS=uuid.UUID("6b6d746f-7563-6800-0000-000000000000")
K="/workspace/kmtouch/hardware/kicad/"
subprocess.run(["kicad-cli","sch","export","netlist","-o","/tmp/kmt.net",K+"kmtouch.kicad_sch"],check=True,capture_output=True)
nl=parse(open("/tmp/kmt.net").read())[0]
pin2net={}
for n in find(find1(nl,"nets"),"net"):
    name=find1(n,"name")[1]
    for nd in find(n,"node"): pin2net[(find1(nd,"ref")[1],find1(nd,"pin")[1])]=name
b=pcbnew.LoadBoard(K+"kmtouch.kicad_pcb")
bad=0
for f in b.GetFootprints():
    r=f.GetReference()
    f.SetPath(pcbnew.KIID_PATH("/"+str(uuid.uuid5(NS,r)))); f.SetSheetname("Root"); f.SetSheetfile("kmtouch.kicad_sch")
    for p in f.Pads():
        want=pin2net.get((r,p.GetNumber()))
        if not want: continue
        if p.GetNetname()!=want:
            if p.GetNetCode()>0: print("MISMATCH",r,p.GetNumber(),p.GetNetname(),want); bad+=1; continue
            ni=b.FindNet(want)
            if ni is None: ni=pcbnew.NETINFO_ITEM(b,want); b.Add(ni)
            p.SetNet(ni)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(K+"kmtouch.kicad_pcb"); print("mismatches",bad)
import circuit
b=pcbnew.LoadBoard(K+"kmtouch.kicad_pcb")
L={p["ref"]:p for p in circuit.P}
for f in b.GetFootprints():
    p=L[f.GetReference()]
    if p["lcsc"]:
        f.SetField("LCSC",p["lcsc"]); fl=f.GetFieldByName("LCSC"); fl.SetVisible(False); fl.SetLayer(pcbnew.F_Fab)
    f.SetValue(p["val"])
b.Save(K+"kmtouch.kicad_pcb")
