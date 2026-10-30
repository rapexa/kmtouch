import pcbnew
from pcbnew import ToMM as T
b=pcbnew.LoadBoard("/workspace/kmtouch/hardware/kicad/kmtouch.kicad_pcb")
for f in b.GetFootprints():
    xs=[];ys=[]
    for g in f.GraphicalItems():
        if g.GetLayer()==pcbnew.F_CrtYd:
            bb=g.GetBoundingBox(); xs+=[bb.GetLeft(),bb.GetRight()]; ys+=[bb.GetTop(),bb.GetBottom()]
    if xs: print(f.GetReference(),[round(T(v),2) for v in (min(xs),min(ys),max(xs),max(ys))],f.GetOrientationDegrees())
