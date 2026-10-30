# Single source of truth for kmtouch circuit: parts, footprints, LCSC, nets.
R0402="Resistor_SMD:R_0402_1005Metric"; C0402="Capacitor_SMD:C_0402_1005Metric"
C0603="Capacitor_SMD:C_0603_1608Metric"; C0805="Capacitor_SMD:C_0805_2012Metric"
LCSC_R={"5.1k":"C25905","27R":"C25100","22R":"C25092","1k":"C11702","10k":"C25744","2.7k":"C284470","470R":"C25117"}
LCSC_C={"100nF":"C1525","1uF":"C52923","15pF":"C1548","10uF":"C15850","22uF":"C45783"}
P=[]
def part(ref,sym,fp,val,lcsc,pins,anchor=None,place=None):
    P.append(dict(ref=ref,sym=sym,fp=fp,val=val,lcsc=lcsc,pins=pins,anchor=anchor,place=place))
def R(ref,val,a,b,anchor=None): part(ref,"Device:R",R0402,val,LCSC_R[val],{"1":a,"2":b},anchor)
def C(ref,val,a,b="GND",anchor=None):
    fp=C0805 if val in("10uF","22uF") else C0402
    part(ref,"Device:C",fp,val,LCSC_C[val],{"1":a,"2":b},anchor)

# --- USB-C upstream (to phone) ---
part("J1","Connector:USB_C_Receptacle_USB2.0_16P","Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal","USB4105-GF-A","C3020560",
 {"A1":"GND","A12":"GND","B1":"GND","B12":"GND","A4":"VBUS","A9":"VBUS","B4":"VBUS","B9":"VBUS",
  "A5":"CC1","B5":"CC2","A6":"CDP","B6":"CDP","A7":"CDM","B7":"CDM","S1":"GND"})
R("R1","5.1k","CC1","GND",("J1","A5")); R("R2","5.1k","CC2","GND",("J1","B5"))
part("U4","Power_Protection:USBLC6-2SC6","Package_TO_SOT_SMD:SOT-23-6","USBLC6-2SC6","C7519",
 {"1":"CDP","6":"CDP","3":"CDM","4":"CDM","2":"GND","5":"VBUS"})
R("R3","27R","CDP","USB_DP",("U1","47")); R("R4","27R","CDM","USB_DM",("U1","46"))
part("F1","Device:Polyfuse","Fuse:Fuse_1206_3216Metric","0.5A PTC","C70076",{"1":"VBUS","2":"+5V"})
C("C1","10uF","+5V",anchor=("F1","2")); C("C2","100nF","+5V",anchor=("U2","1"))
# --- 3.3 V LDO ---
part("U2","Regulator_Linear:AP2112K-3.3","Package_TO_SOT_SMD:SOT-23-5","AP2112K-3.3","C51118",{"1":"+5V","3":"+5V","2":"GND","5":"+3V3"})
C("C3","10uF","+3V3",anchor=("U2","5"))
# --- RP2040 ---
U1={"1":"+3V3","10":"+3V3","22":"+3V3","33":"+3V3","42":"+3V3","49":"+3V3","43":"+3V3","48":"+3V3","44":"+3V3",
    "45":"+1V1","23":"+1V1","50":"+1V1","57":"GND","19":"GND","20":"XIN","21":"XOUT",
    "24":"SWCLK","25":"SWDIO","26":"RUN","46":"USB_DM","47":"USB_DP",
    "56":"QSPI_SS","51":"QSPI_SD3","52":"QSPI_SCLK","53":"QSPI_SD0","54":"QSPI_SD2","55":"QSPI_SD1",
    "4":"GP2","5":"GP3","29":"VBUS_EN","30":"FLT","37":"GP25"}
part("U1","MCU_RaspberryPi:RP2040","Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm","RP2040","C2040",U1)
for i,pin in enumerate(["1","10","22","33","42","49"]): C(f"C{4+i}","100nF","+3V3",anchor=("U1",pin))
C("C10","100nF","+3V3",anchor=("U1","44")); C("C11","1uF","+1V1",anchor=("U1","45"))
C("C12","100nF","+1V1",anchor=("U1","23")); C("C13","100nF","+1V1",anchor=("U1","50"))
part("Y1","Device:Crystal_GND24","Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm","12MHz","C9002",{"1":"XIN","3":"XO1","2":"GND","4":"GND"},("U1","20"))
R("R10","1k","XOUT","XO1",("U1","21"))
C("C14","15pF","XIN",anchor=("Y1","1")); C("C15","15pF","XO1",anchor=("Y1","3"))
part("U3","Memory_Flash:W25Q128JVS","Package_SO:SOIC-8_5.3x5.3mm_P1.27mm","W25Q128JVSIQ","C97521",
 {"1":"QSPI_SS","2":"QSPI_SD1","3":"QSPI_SD2","4":"GND","5":"QSPI_SD0","6":"QSPI_SCLK","7":"QSPI_SD3","8":"+3V3"})
C("C16","100nF","+3V3",anchor=("U3","8"))
R("R8","10k","QSPI_SS","+3V3",("U3","1")); R("R9","1k","QSPI_SS","BOOT",("U3","1"))
part("SW1","Switch:SW_Push","Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A","BOOTSEL","C318884",{"1":"BOOT","2":"GND"},place=(148,128,0))
R("R7","10k","RUN","+3V3",("U1","26"))
part("SW2","Switch:SW_Push","Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A","RESET","C318884",{"1":"RUN","2":"GND"},place=(138,128,0))
R("R11","470R","GP25","LED_A",("U1","37"))
part("D1","Device:LED","LED_SMD:LED_0603_1608Metric","green","C72043",{"1":"GND","2":"LED_A"},("R11","2"))
part("TP1","Connector:TestPoint","TestPoint:TestPoint_Pad_D1.0mm","SWCLK","",{"1":"SWCLK"},("U1","24"))
part("TP2","Connector:TestPoint","TestPoint:TestPoint_Pad_D1.0mm","SWDIO","",{"1":"SWDIO"},("U1","25"))
part("TP3","Connector:TestPoint","TestPoint:TestPoint_Pad_D1.0mm","GND","",{"1":"GND"},("TP2","1"))
# --- PIO-USB host -> FE1.1s hub ---
R("R5","22R","GP2","HUB_DP",("U1","4")); R("R6","22R","GP3","HUB_DM",("U1","5"))
part("U6","Interface_USB:FE1.1s","Package_SO:SSOP-28_3.9x9.9mm_P0.635mm","FE1.1s","C9359",
 {"1":"GND","2":"HXO","3":"HXI","10":"A1DM","11":"A1DP","8":"A2DM","9":"A2DP","14":"REXT","15":"HUB_DM","16":"HUB_DP",
  "17":"HRST","18":"+5V","19":"VD33H","20":"+5V","21":"VD33H","13":"VD33H","26":"FLT"},place=(122.5,118,0))
part("Y2","Device:Crystal_GND24","Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm","12MHz","C9002",{"1":"HXI","3":"HXO","2":"GND","4":"GND"},("U6","2"))
R("R13","2.7k","REXT","GND",("U6","14")); R("R14","10k","HRST","VD33H",("U6","17"))
C("C17","10uF","VD33H",anchor=("U6","21")); C("C18","100nF","VD33H",anchor=("U6","13"))
C("C19","100nF","+5V",anchor=("U6","20"))
# --- downstream VBUS switch ---
part("U5","Power_Management:TPS2051CDBV","Package_TO_SOT_SMD:SOT-23-5","TPS2051CDBVR","C129581",{"1":"5V_A","2":"GND","3":"FLT","4":"VBUS_EN","5":"+5V"},place=(124.5,106,0))
R("R12","10k","FLT","+3V3",("U5","3")); R("R15","10k","VBUS_EN","GND",("U5","4"))
C("C20","22uF","5V_A",anchor=("U5","1")); C("C21","1uF","+5V",anchor=("U5","5"))
for j,(dm,dp,u,y) in {"J2":("A1DM","A1DP","U7",109.3),"J3":("A2DM","A2DP","U8",126.7)}.items():
    part(j,"Connector:USB_A","Connector_USB:USB_A_Molex_67643_Horizontal","USB-A","C19170946",{"1":"5V_A","2":dm,"3":dp,"4":"GND","5":"GND"},place=(100,y,"W"))
    part(u,"Power_Protection:USBLC6-2SC6","Package_TO_SOT_SMD:SOT-23-6","USBLC6-2SC6","C7519",{"1":dp,"6":dp,"3":dm,"4":dm,"2":"GND","5":"5V_A"},(j,"3"))
part("H1","Mechanical:MountingHole","MountingHole:MountingHole_2.2mm_M2","M2","",{},place=(118.2,103.5,0))
part("H2","Mechanical:MountingHole","MountingHole:MountingHole_2.2mm_M2","M2","",{},place=(156.5,103.5,0))
part("H3","Mechanical:MountingHole","MountingHole:MountingHole_2.2mm_M2","M2","",{},place=(118.2,132.5,0))
part("H4","Mechanical:MountingHole","MountingHole:MountingHole_2.2mm_M2","M2","",{},place=(156.5,132.5,0))
# fixed positions for main parts
FIXED={"J1":(160,118,"E"),"U1":(138,115,0),"U3":(130,126,90),"U2":(150,108,0),"F1":(147.5,113,0),"U4":(148,122.5,0)}
for p in P:
    if p["ref"] in FIXED: p["place"]=FIXED[p["ref"]]
NETS=sorted({n for p in P for n in p["pins"].values()})
