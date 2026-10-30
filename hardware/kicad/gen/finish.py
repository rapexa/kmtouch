import pcbnew
from pcbnew import FromMM as M, ToMM as T, VECTOR2I
P="/workspace/kmtouch/hardware/kicad/kmtouch.kicad_pcb"
b=pcbnew.LoadBoard(P)
X0,Y0,X1,Y1=100.3,100.3,159.7,135.7
def bx(bb,e=0): return (T(bb.GetLeft())-e,T(bb.GetTop())-e,T(bb.GetRight())+e,T(bb.GetBottom())+e)
def ov(a,c): return not(a[2]<=c[0] or c[2]<=a[0] or a[3]<=c[1] or c[3]<=a[1])
pads=[bx(p.GetBoundingBox(),0.12) for p in b.GetPads()]
holes=[bx(f.GetBoundingBox(False)) for f in b.GetFootprints() if f.GetReference().startswith("H")]
rm=[]
for f in b.GetFootprints():
    for g in list(f.GraphicalItems()):
        if g.GetLayer()==pcbnew.F_SilkS and g.GetClass()!="PCB_FIELD":
            a=bx(g.GetBoundingBox())
            if a[0]<X0 or a[2]>X1 or a[1]<Y0 or a[3]>Y1 or any(ov(a,p) for p in pads): rm.append((f,g))
for f,g in rm: f.Remove(g)
silk=[]
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_SilkS and g.GetClass()!="PCB_FIELD": silk.append(bx(g.GetBoundingBox(),0.1))
for f in b.GetFootprints():
    r=f.GetReference(); ref=f.Reference()
    show=(r[0] in "UJYDF" or r.startswith(("SW","TP")))
    ref.SetVisible(show)
    if not show: continue
    ref.SetTextSize(VECTOR2I(M(0.8),M(0.8))); ref.SetTextThickness(M(0.15)); ref.SetTextAngleDegrees(0)
    c=bx(f.GetBoundingBox(False,False)); cx=(c[0]+c[2])/2; cy=(c[1]+c[3])/2
    cands=[(cx,c[1]-0.6),(cx,c[3]+0.6),(c[0]-1.2,cy),(c[2]+1.2,cy),(cx,cy)]
    cands+=[(cx+dx,cy+dy) for dx in (-3,-1.5,0,1.5,3) for dy in (-3,-1.5,0,1.5,3)]
    if r.startswith("J"): cands=[(cx,cy)]+cands
    done=False
    for x,y in cands:
        ref.SetPosition(VECTOR2I(M(x),M(y))); a=bx(ref.GetBoundingBox(),0.05)
        if a[0]<X0 or a[2]>X1 or a[1]<Y0 or a[3]>Y1: continue
        if any(ov(a,p) for p in pads+silk+holes): continue
        done=True; break
    if not done: ref.SetVisible(False); print("hid ref",r)
    else: silk.append(bx(ref.GetBoundingBox(),0.1))
t=pcbnew.PCB_TEXT(b); t.SetText("kmtouch v1"); t.SetLayer(pcbnew.F_SilkS)
t.SetTextSize(VECTOR2I(M(1),M(1))); t.SetTextThickness(M(0.15))
for x,y in [(146,134.3),(128,134.3),(150,101.5),(135,101.5)]:
    t.SetPosition(VECTOR2I(M(x),M(y))); a=bx(t.GetBoundingBox(),0.05)
    if not any(ov(a,p) for p in pads+silk+holes) and a[3]<Y1: break
b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(P)
