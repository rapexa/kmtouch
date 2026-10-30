import pcbnew,sys
FP="/usr/share/kicad/footprints/"
for a in sys.argv[1:]:
    lib,n=a.split(":")
    f=pcbnew.FootprintLoad(FP+lib+".pretty",n)
    bb=f.GetBoundingBox(False)
    print("==",n,"bbox mm",pcbnew.ToMM(bb.GetX()),pcbnew.ToMM(bb.GetY()),pcbnew.ToMM(bb.GetWidth()),pcbnew.ToMM(bb.GetHeight()))
    print(sorted(set((p.GetNumber(),round(pcbnew.ToMM(p.GetPosition().x),2),round(pcbnew.ToMM(p.GetPosition().y),2),"TH" if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH else "") for p in f.Pads())))
