import sys,math; sys.path.insert(0,"/workspace/kmtouch/hardware/kicad/gen")
import pcbnew
from pcbnew import VECTOR2I, FromMM as M, ToMM as T
import circuit
OUT="/workspace/kmtouch/hardware/kicad/kmtouch.kicad_pcb"
FPL="/usr/share/kicad/footprints/"
X0,Y0,W,H=100,100,60,36
b=pcbnew.BOARD(); b.SetCopperLayerCount(2)
ds=b.GetDesignSettings()
ds.m_TrackMinWidth=M(0.15); ds.m_MinClearance=M(0.15); ds.m_ViasMinSize=M(0.6); ds.m_MinThroughDrill=M(0.3)
ds.m_ViasMinAnnularWidth=M(0.13); ds.m_CopperEdgeClearance=M(0.3); ds.m_HoleClearance=M(0.25); ds.m_HoleToHoleMin=M(0.25)
ds.m_SolderMaskExpansion=M(0.05) if False else ds.m_SolderMaskExpansion
# outline with 1mm corner radius
def seg(a,bb):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(VECTOR2I(M(a[0]),M(a[1]))); s.SetEnd(VECTOR2I(M(bb[0]),M(bb[1]))); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(M(0.1)); b.Add(s)
r=1.0
seg((X0+r,Y0),(X0+W-r,Y0)); seg((X0+W,Y0+r),(X0+W,Y0+H-r)); seg((X0+W-r,Y0+H),(X0+r,Y0+H)); seg((X0,Y0+H-r),(X0,Y0+r))
for cx,cy,sa in [(X0+r,Y0+r,180),(X0+W-r,Y0+r,270),(X0+W-r,Y0+H-r,0),(X0+r,Y0+H-r,90)]:
    a=pcbnew.PCB_SHAPE(b); a.SetShape(pcbnew.SHAPE_T_ARC); a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(M(0.1))
    a.SetCenter(VECTOR2I(M(cx),M(cy))); st=(cx+r*math.cos(math.radians(sa)),cy+r*math.sin(math.radians(sa)))
    a.SetStart(VECTOR2I(M(st[0]),M(st[1]))); a.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90,pcbnew.DEGREES_T)); b.Add(a)
nets={}
for n in circuit.NETS:
    ni=pcbnew.NETINFO_ITEM(b,n); b.Add(ni); nets[n]=ni
def layerbox(fp,layer):
    xs=[];ys=[]
    for g in fp.GraphicalItems():
        if g.GetLayer()==layer:
            bb=g.GetBoundingBox(); xs+=[bb.GetLeft(),bb.GetRight()]; ys+=[bb.GetTop(),bb.GetBottom()]
    if not xs: return None
    return T(min(xs)),T(min(ys)),T(max(xs)),T(max(ys))
def crt(fp):
    c=layerbox(fp,pcbnew.F_CrtYd)
    if c: return c
    bb=fp.GetBoundingBox(False); return T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom())
fps={}; placed=[]
def mk(p):
    lib,name=p["fp"].split(":")
    f=pcbnew.FootprintLoad(FPL+lib+".pretty",name)
    f.SetReference(p["ref"]); f.SetValue(p["val"])
    f.SetFPIDAsString(p["fp"])
    for pad in f.Pads():
        n=p["pins"].get(pad.GetNumber())
        if n: pad.SetNet(nets[n])
    if p["lcsc"]:
        f.SetField("LCSC",p["lcsc"]); fld=f.GetFieldByName("LCSC"); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
    b.Add(f); fps[p["ref"]]=f; return f
def padpos(ref,num):
    for pad in fps[ref].Pads():
        if pad.GetNumber()==num: return T(pad.GetPosition().x),T(pad.GetPosition().y)
def setpos(f,x,y,rot):
    f.SetOrientationDegrees(rot); f.SetPosition(VECTOR2I(M(x),M(y)))
for p in circuit.P:
    if not p["place"]: continue
    f=mk(p); x,y,rot=p["place"]
    if rot in("W","E"):
        for rr in (0,90,180,270):
            setpos(f,0,0,rr); fb=layerbox(f,pcbnew.F_Fab)
            pc=sum(T(q.GetPosition().x) for q in f.Pads())/len(list(f.Pads()))
            cx=(fb[0]+fb[2])/2
            if (rot=="W" and pc>cx+1) or (rot=="E" and pc<cx-1): break
        cy=(fb[1]+fb[3])/2
        dx = (x-0.5-fb[0]) if rot=="W" else (x+0.5-fb[2])
        setpos(f,dx,y-cy,rr)
    else: setpos(f,x,y,rot)
    placed.append(f)
def overlap(a,c,m=0.2):
    return not(a[2]+m<=c[0] or c[2]+m<=a[0] or a[3]+m<=c[1] or c[3]+m<=a[1])
pending=[p for p in circuit.P if not p["place"]]
while pending:
    for p in list(pending):
        ar,an=p["anchor"]
        if ar not in fps: continue
        ax,ay=padpos(ar,an); f=mk(p); ok=False
        for rad in [i*0.25 for i in range(0,100)]:
            steps=max(1,int(2*math.pi*rad/0.25))
            for k in range(steps):
                t=2*math.pi*k/steps; x=ax+rad*math.cos(t); y=ay+rad*math.sin(t)
                for rot in (0,90):
                    setpos(f,round(x*4)/4,round(y*4)/4,rot); c=crt(f)
                    if c[0]<X0+0.4 or c[1]<Y0+0.4 or c[2]>X0+W-0.4 or c[3]>Y0+H-0.4: continue
                    if any(overlap(c,crt(o),(1.0 if o.GetReference()=="U1" else 0.45)) for o in placed): continue
                    ok=True; break
                if ok: break
            if ok: break
        if not ok: print("FAILED place",p["ref"])
        placed.append(f); pending.remove(p)
for f in placed:
    c=crt(f)
    for o in placed:
        if o is not f and o.GetReference()<f.GetReference() and overlap(c,crt(o),0): print("overlap",f.GetReference(),o.GetReference())
    f.Reference().SetTextSize(VECTOR2I(M(0.6),M(0.6))); f.Reference().SetTextThickness(M(0.1))
    f.Value().SetVisible(False)
b.Save(OUT); print("saved")
