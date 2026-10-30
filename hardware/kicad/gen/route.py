import pcbnew,sys
from pcbnew import FromMM as M, VECTOR2I
P="/workspace/kmtouch/hardware/kicad/kmtouch.kicad_pcb"
b=pcbnew.LoadBoard(P)
step=sys.argv[1]
def zones(layers=(pcbnew.F_Cu,pcbnew.B_Cu)):
    gnd=b.FindNet("GND")
    for L in layers:
        z=pcbnew.ZONE(b); z.SetLayer(L); z.SetNet(gnd)
        o=z.Outline(); o.NewOutline()
        for x,y in [(100.2,100.2),(159.8,100.2),(159.8,135.8),(100.2,135.8)]: o.Append(M(x),M(y))
        z.SetLocalClearance(M(0.25)); z.SetMinThickness(M(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetThermalReliefGap(M(0.25)); z.SetThermalReliefSpokeWidth(M(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
if step=="dsn":
    b.Save(P)
    print(pcbnew.ExportSpecctraDSN(b,"/workspace/kmtouch/hardware/kicad/gen/kmtouch.dsn"))
elif step=="ses":
    print(pcbnew.ImportSpecctraSES(b,"/workspace/kmtouch/hardware/kicad/gen/kmtouch.ses"))
    zones(); b.Save(P)
