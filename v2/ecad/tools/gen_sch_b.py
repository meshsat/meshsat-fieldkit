#!/usr/bin/env python3
"""PCB-B COMPUTE, phase B16 (MESHSAT-830, appendix 32.52 fabric, 32.58 floor plan): generate the KiCad 9 schematic (netlist style: every pin gets a
stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box). Usage: gen_sch_b.py <out.kicad_sch> <project>

Three identical slot columns S1, S2, S3, each a Compute Module 5 on two Amphenol 10164227 receptacles (U30A/B, U31A/B, U32A/B) with, per slot:
a Diodes PI7C9X2G404SL one-to-three PCIe switch (upstream the module's Gen 2 lane; port 1 an NVMe M.2 M-key 2242 socket, port 2 the slot's card
socket: S1 the WiFi link card on an M.2 E-key 2230, S2 the 5G module on an M.2 B-key 3052 with two nano-SIM holders, S3 a spare M-key 2242), a TI
TUSB8041I four-port USB 3 hub on the module's USB3-0 port, the module's Ethernet pairs into the shared KSZ9897R switch through coupling capacitors,
the module's HDMI0 into the shared two-stage TS3DV642 display switch, the slot's 5 V lead from A22 (J_5V_Sx), two AP64500 3.3 V bucks (A: the card
socket rail on PCIE_PWR_EN; B: switch, hub and NVMe, following the module's 3.3 V), TPS62933 bucks for the switch core (1.0 V) and the hub core
(1.1 V), the flashing USB-C, fan header, LEDs, bench headers and 2N7002 level stages on every line that crosses into the module domain.
Shared: KSZ9897R (ports 1-3 the modules, port 4 the wall RJ45 through Pulse H5007NL magnetics with the TPS23861 PoE injector on the 54 V lead), the
HDMI type A receptacle for the monitor, the LG290P GNSS, the E22-900M30S 1 W LoRa module on S3's SPI, two E72 CC2652P radios, four CP2102N bridges,
the LimeSDR USB 3 receptacle and the RockBLOCK 9704 header behind TPS259631 eFuses, the QMX, camera and spare USB headers, two PCA9555, the
ATECC608B secure element, DS3231MZ holdover clock, TMP117, the hardware EMCON gates (74LVC08), the panel ribbon J_PANEL (2x13) and the A22 ribbon
J_AB1 (2x13, underside). Every radio is a USB device of one hub; the kit I2C bus (SDA/SCL from the panel controller) reaches A22 over J_AB1.
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-b-compute"
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(":
                sub, i = rd(i + 1); out.append(sub)
            elif t == ")":
                return out, i + 1
            else:
                out.append(t); i += 1
        return out, i
    return rd(0)[0]
def ser(n, ind=0):
    if not isinstance(n, list): return n
    if all(not isinstance(x, list) for x in n): return "(" + " ".join(n) + ")"
    head = []
    i = 0
    while i < len(n) and not isinstance(n[i], list): head.append(n[i]); i += 1
    s = "(" + " ".join(head)
    for x in n[i:]:
        s += "\n" + "\t" * (ind + 1) + ser(x, ind + 1) if isinstance(x, list) else " " + x
    return s + "\n" + "\t" * ind + ")"
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def uq(s): return s[1:-1] if s.startswith('"') else s
LIBCACHE = {}
def lib_tree(lib):
    if lib not in LIBCACHE: LIBCACHE[lib] = parse(open(SYMDIR + lib + ".kicad_sym").read())[0]
    return LIBCACHE[lib]
def find_sym(lib, name):
    for e in lib_tree(lib)[1:]:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]) == name: return e
    raise SystemExit("symbol not found: %s:%s" % (lib, name))
def flatten(lib, name):
    sym = find_sym(lib, name)
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext:
        parent = flatten_raw(lib, uq(ext[0][1]))
        child_props = {uq(e[1]): e for e in sym if isinstance(e, list) and e and e[0] == "property"}
        out = ["symbol", q(lib + ":" + name)]
        for e in parent[2:]:
            if isinstance(e, list) and e and e[0] == "property": e = child_props.get(uq(e[1]), e)
            out.append(e)
        for k, e in child_props.items():
            if not any(isinstance(x, list) and x and x[0] == "property" and uq(x[1]) == k for x in out): out.append(e)
        return rename_units(out, uq(ext[0][1]), name)
    return rename_units(flatten_raw(lib, name), name, name)
def flatten_raw(lib, name):
    import copy
    sym = copy.deepcopy(find_sym(lib, name))
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext: return flatten(lib, name)
    sym[1] = q(lib + ":" + name); return sym
def rename_units(sym, oldname, newname):
    for e in sym:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]).startswith(oldname + "_"): e[1] = q(newname + uq(e[1])[len(oldname):])
    return [e for e in sym if not (isinstance(e, list) and e and e[0] == "extends")]
def pins_of(sym):
    pins = []
    def walk(n):
        for e in n:
            if isinstance(e, list) and e:
                if e[0] == "symbol": walk(e)
                elif e[0] == "pin":
                    at = [x for x in e if isinstance(x, list) and x and x[0] == "at"][0]
                    num = uq([x for x in e if isinstance(x, list) and x and x[0] == "number"][0][1])
                    nm = uq([x for x in e if isinstance(x, list) and x and x[0] == "name"][0][1])
                    pins.append((num, nm, float(at[1]), float(at[2]), int(float(at[3]))))
    walk(sym); return pins

# ----------------------------------------------------------------- synthetic box symbols (parts with more pins than any library symbol): odd pins left, even pins right
CM5_PINS = {1:"GND",2:"GND",3:"Ethernet_Pair3_P",4:"Ethernet_Pair1_P",5:"Ethernet_Pair3_N",6:"Ethernet_Pair1_N",7:"GND",8:"GND",9:"Ethernet_Pair2_N",10:"Ethernet_Pair0_N",11:"Ethernet_Pair2_P",12:"Ethernet_Pair0_P",13:"GND",14:"GND",15:"Ethernet_nLED3",16:"Fan_Tacho",17:"Ethernet_nLED2",18:"Ethernet_SYNC_OUT",19:"Fan_PWM",20:"EEPROM_nWP",21:"LED_nACT",22:"GND",23:"GND",24:"GPIO26",25:"GPIO21",26:"GPIO19",27:"GPIO20",28:"GPIO13",29:"GPIO16",30:"GPIO6",31:"GPIO12",32:"GND",33:"GND",34:"GPIO5",35:"ID_SC",36:"ID_SD",37:"GPIO7",38:"GPIO11",39:"GPIO8",40:"GPIO9",41:"GPIO25",42:"GND",43:"GND",44:"GPIO10",45:"GPIO24",46:"GPIO22",47:"GPIO23",48:"GPIO27",49:"GPIO18",50:"GPIO17",51:"GPIO15",52:"GND",53:"GND",54:"GPIO4",55:"GPIO14",56:"GPIO3",57:"SD_CLK",58:"GPIO2",59:"GND",60:"GND",61:"SD_DAT3",62:"SD_CMD",63:"SD_DAT0",64:"SD_DAT5",65:"GND",66:"GND",67:"SD_DAT1",68:"SD_DAT4",69:"SD_DAT2",70:"SD_DAT7",71:"GND",72:"SD_DAT6",73:"SD_VDD_OVERRIDE",74:"GND",75:"SD_PWR_ON",76:"VBAT",77:"5V",78:"GPIO_VREF",79:"5V",80:"SCL0",81:"5V",82:"SDA0",83:"5V",84:"CM5_3.3V",85:"5V",86:"CM5_3.3V",87:"5V",88:"CM5_1.8V",89:"WL_nDisable",90:"CM5_1.8V",91:"BT_nDisable",92:"PWR_Button",93:"nRPIBOOT",94:"CC1",95:"LED_nPWR",96:"CC2",97:"CAM_GPIO0",98:"GND",99:"PMIC_Enable",100:"CAM_GPIO1",101:"USB_OTG_ID",102:"PCIe_CLK_nREQ",103:"USB_N",104:"PCIE_nWAKE",105:"USB_P",106:"PCIE_PWR_EN",107:"GND",108:"GND",109:"PCIe_nRST",110:"PCIe_CLK_P",111:"VBUS_EN",112:"PCIe_CLK_N",113:"GND",114:"GND",115:"MIPI0_D0_N",116:"PCIe_RX_P",117:"MIPI0_D0_P",118:"PCIe_RX_N",119:"GND",120:"GND",121:"MIPI0_D1_N",122:"PCIe_TX_P",123:"MIPI0_D1_P",124:"PCIe_TX_N",125:"GND",126:"GND",127:"MIPI0_C_N",128:"USB3-0-RX_N",129:"MIPI0_C_P",130:"USB3-0-RX_P",131:"GND",132:"GND",133:"MIPI0_D2_N",134:"USB3-0-DP",135:"MIPI0_D2_P",136:"USB3-0-DM",137:"GND",138:"GND",139:"MIPI0_D3_N",140:"USB3-0-TX_N",141:"MIPI0_D3_P",142:"USB3-0-TX_P",143:"HDMI1_HOTPLUG",144:"GND",145:"HDMI1_SDA",146:"HDMI1_TX2_P",147:"HDMI1_SCL",148:"HDMI1_TX2_N",149:"HDMI1_CEC",150:"GND",151:"HDMI0_CEC",152:"HDMI1_TX1_P",153:"HDMI0_HOTPLUG",154:"HDMI1_TX1_N",155:"GND",156:"GND",157:"USB3-1-RX_N",158:"HDMI1_TX0_P",159:"USB3-1-RX_P",160:"HDMI1_TX0_N",161:"GND",162:"GND",163:"USB3-1-DP",164:"HDMI1_CLK_P",165:"USB3-1-DM",166:"HDMI1_CLK_N",167:"GND",168:"GND",169:"USB3-1-TX_N",170:"HDMI0_TX2_P",171:"USB3-1-TX_P",172:"HDMI0_TX2_N",173:"GND",174:"GND",175:"MIPI1_D0_N",176:"HDMI0_TX1_P",177:"MIPI1_D0_P",178:"HDMI0_TX1_N",179:"GND",180:"GND",181:"MIPI1_D1_N",182:"HDMI0_TX0_P",183:"MIPI1_D1_P",184:"HDMI0_TX0_N",185:"GND",186:"GND",187:"MIPI1_C_N",188:"HDMI0_CLK_P",189:"MIPI1_C_P",190:"HDMI0_CLK_N",191:"GND",192:"GND",193:"MIPI1_D2_N",194:"MIPI1_D3_N",195:"MIPI1_D2_P",196:"MIPI1_D3_P",197:"GND",198:"GND",199:"HDMI0_SDA",200:"HDMI0_SCL"}
# Diodes PI7C9X2G404SL, 128-LQFP, DS40068 rev 5-2 section 4.1 (pin 129 = exposed pad)
PI7C = {1:'VDDR',2:'VSS',3:'VDDC',4:'VSS',5:'DWNRST_L1',6:'DWNRST_L2',7:'DWNRST_L3',8:'VDDR',9:'TEST1',10:'PERST_L',11:'VSS',12:'VSS',13:'VDDCAUX',14:'VDDCAUX',15:'VAUX',16:'TEST2',17:'TEST3',18:'VC1_EN',19:'PRSNT1',20:'PRSNT2',21:'PRSNT3',22:'TEST4',23:'VDDC',24:'RXPOLINV_DIS',25:'TEST5',26:'SMBCLK',27:'SMBDATA',28:'PWR_SAV',29:'VDDC',30:'VSS',31:'VDDC',32:'VSS',33:'SLOTCLK',34:'VSS',35:'GPIO1',36:'GPIO0',37:'GPIO2',38:'GPIO3',39:'GPIO4',40:'VDDC',41:'VSS',42:'GPIO5',43:'GPIO6',44:'GPIO7',45:'SLOT_IMP1',46:'SLOT_IMP2',47:'SLOT_IMP3',48:'NC',49:'VDDR',50:'VSS',51:'TEST6',52:'NC',53:'PL_512B',54:'NC',55:'VDDC',56:'VSS',57:'NC',58:'NC',59:'NC',60:'CLKBUF_PD',61:'VSS',62:'VDDC',63:'VSS',64:'VDDR',65:'VDDC',66:'VSS',67:'PORTSTATUS0',68:'PORTSTATUS1',69:'PORTSTATUS2',70:'EECLK',71:'EEPD',72:'SCAN_EN',73:'REFCLKI_N',74:'REFCLKI_P',75:'REFCLKO_N3',76:'REFCLKO_P3',77:'REFCLKO_N2',78:'REFCLKO_P2',79:'CVDDR',80:'REFCLKO_N1',81:'REFCLKO_P1',82:'CVDDR',83:'REFCLKO_N0',84:'CVDDR',85:'REFCLKO_P0',86:'IREF',87:'VSS',88:'TDO',89:'TCK',90:'VSS',91:'VDDC',92:'TMS',93:'TDI',94:'TRST_L',95:'VSS',96:'VDDR',97:'PERP1',98:'PERN1',99:'AVDD',100:'PETP1',101:'PETN1',102:'PERP2',103:'PERN2',104:'VSS',105:'AVDD',106:'PETP2',107:'PETN2',108:'AVDD',109:'CGND',110:'REFCLKP',111:'REFCLKN',112:'CGND',113:'AVDDH',114:'NC',115:'REXT_GND',116:'REXT',117:'PETN3',118:'PETP3',119:'AVDD',120:'VSS',121:'PERN3',122:'PERP3',123:'PETN0',124:'PETP0',125:'AVDD',126:'VSS',127:'PERN0',128:'PERP0',129:'E_PAD'}
# TI TUSB8041I, 64-QFN (RGC), SLLSEE4E pin functions (pin 65 = thermal pad)
TUSB = {1:"USB_DP_DN1",2:"USB_DM_DN1",3:"USB_SSTXP_DN1",4:"USB_SSTXM_DN1",5:"VDD",6:"USB_SSRXP_DN1",7:"USB_SSRXM_DN1",8:"VDD",9:"USB_DP_DN2",10:"USB_DM_DN2",11:"USB_SSTXP_DN2",12:"USB_SSTXM_DN2",13:"VDD",14:"USB_SSRXP_DN2",15:"USB_SSRXM_DN2",16:"VDD33",17:"USB_DP_DN3",18:"USB_DM_DN3",19:"USB_SSTXP_DN3",20:"USB_SSTXM_DN3",21:"VDD",22:"USB_SSRXP_DN3",23:"USB_SSRXM_DN3",24:"USB_DP_DN4",25:"USB_DM_DN4",26:"USB_SSTXP_DN4",27:"USB_SSTXM_DN4",28:"VDD",29:"USB_SSRXP_DN4",30:"USB_SSRXM_DN4",31:"VDD",32:"PWRCTL4",33:"PWRCTL3",34:"VDD33",35:"PWRCTL2",36:"PWRCTL1",37:"SDA",38:"SCL",39:"SMBUSz",40:"FULLPWRMGMTz",41:"PWRCTL_POL",42:"GANGED",43:"OVERCUR4z",44:"OVERCUR3z",45:"AUTOENz",46:"OVERCUR1z",47:"OVERCUR2z",48:"USB_VBUS",49:"TEST",50:"GRSTz",51:"VDD",52:"VDD33",53:"USB_DP_UP",54:"USB_DM_UP",55:"USB_SSTXP_UP",56:"USB_SSTXM_UP",57:"VDD",58:"USB_SSRXP_UP",59:"USB_SSRXM_UP",60:"NC",61:"XO",62:"XI",63:"VDD33",64:"USB_R1",65:"GND"}
# TI TS3DV642, 42-WQFN (pin 43 = pad); Microchip KSZ9897R 128-TQFP-EP (129 = pad)
TS3 = {1:"VCC",2:"EN",3:"SCL",4:"SDA",5:"D0P",6:"D0N",7:"D1P",8:"D1N",9:"NC",10:"D2P",11:"D2N",12:"D3P",13:"D3N",14:"HPD",15:"CEC",16:"SEL1",17:"SEL2",18:"CEC_A",19:"HPD_A",20:"CEC_B",21:"HPD_B",22:"D3N_B",23:"D3P_B",24:"D2N_B",25:"D2P_B",26:"D1N_B",27:"D1P_B",28:"D0N_B",29:"D0P_B",30:"NC",31:"D3N_A",32:"D3P_A",33:"D2N_A",34:"D2P_A",35:"D1N_A",36:"D1P_A",37:"D0N_A",38:"D0P_A",39:"SDA_B",40:"SCL_B",41:"SDA_A",42:"SCL_A",43:"GND"}
KSZ = {1:'TXRX1P_A',2:'TXRX1M_A',3:'AVDDL',4:'TXRX1P_B',5:'TXRX1M_B',6:'TXRX1P_C',7:'TXRX1M_C',8:'TXRX1P_D',9:'TXRX1M_D',10:'AVDDH',11:'DVDDL',12:'TXRX2P_A',13:'TXRX2M_A',14:'AVDDL',15:'TXRX2P_B',16:'TXRX2M_B',17:'TXRX2P_C',18:'TXRX2M_C',19:'AVDDL',20:'TXRX2P_D',21:'TXRX2M_D',22:'AVDDH',23:'DVDDL',24:'TXRX3P_A',25:'TXRX3M_A',26:'TXRX3P_B',27:'TXRX3M_B',28:'TXRX3P_C',29:'TXRX3M_C',30:'AVDDL',31:'TXRX3P_D',32:'TXRX3M_D',33:'AVDDH',34:'TXRX4P_A',35:'TXRX4M_A',36:'AVDDL',37:'TXRX4P_B',38:'TXRX4M_B',39:'TXRX4P_C',40:'TXRX4M_C',41:'AVDDL',42:'TXRX4P_D',43:'TXRX4M_D',44:'AVDDH',45:'DVDDL',46:'GND',47:'GND',48:'TX_CLK6',49:'TX_EN6',50:'TX_ER6',51:'COL6',52:'TXD6_3',53:'TXD6_2',54:'TXD6_1',55:'TXD6_0',56:'DVDDL',57:'RX_CLK6',58:'RX_DV6',59:'RX_ER6',60:'CRS6',61:'VDDIO',62:'RXD6_3',63:'RXD6_2',64:'RXD6_1',65:'RXD6_0',66:'TX_CLK7',67:'TX_EN7',68:'TX_ER7',69:'COL7',70:'TXD7_3',71:'TXD7_2',72:'TXD7_1',73:'TXD7_0',74:'DVDDL',75:'RX_CLK7',76:'RX_DV7',77:'VDDIO',78:'RX_ER7',79:'CRS7',80:'RXD7_3',81:'RXD7_2',82:'RXD7_1',83:'RXD7_0',84:'GND',85:'LED4_0',86:'LED4_1',87:'DVDDL',88:'LED3_0',89:'LED3_1',90:'NC',91:'LED2_0',92:'LED2_1',93:'PME_N',94:'INTRP_N',95:'CLKO_25_125',96:'RESET_N',97:'SDO',98:'SDI_SDA',99:'VDDIO',100:'SCS_N',101:'SCL_MDC',102:'LED5_0',103:'LED5_1',104:'DVDDL',105:'LED1_0',106:'LED1_1',107:'GND',108:'NC',109:'GND',110:'DVDDL',111:'AVDDH',112:'TXRX5P_A',113:'TXRX5M_A',114:'AVDDL',115:'TXRX5P_B',116:'TXRX5M_B',117:'TXRX5P_C',118:'TXRX5M_C',119:'AVDDL',120:'TXRX5P_D',121:'TXRX5M_D',122:'AVDDH',123:'GND',124:'AVDDL',125:'XO',126:'XI',127:'ISET',128:'AVDDH',129:'E_PAD'}
# Quectel LG290P (hardware design Table 6; 25-79 the ground matrix), Ebyte E22-900M30S (manual 3.3), Pulse H5007NL (HC500), TI TPS23861 TSSOP-28, Silicon Labs CP2102N QFN28
LG = {1:"RESERVED",2:"RESERVED",3:"1PPS",4:"EVENT",5:"RESERVED",6:"TXD2",7:"RXD2",8:"RESET_N",9:"VDD_RF",10:"GND",11:"RF_IN",12:"GND",13:"GND",14:"RTK_STAT_ANT_ON",15:"RXD3",16:"TXD3",17:"RESERVED",18:"I2C_SDA",19:"I2C_SCL",20:"TXD1",21:"RXD1",22:"V_BCKP",23:"VCC",24:"GND"}
LG.update({n: "GND" for n in range(25, 80)})
E22P = {1:"GND",2:"GND",3:"GND",4:"GND",5:"GND",6:"RXEN",7:"TXEN",8:"DIO2",9:"VCC",10:"VCC",11:"GND",12:"GND",13:"DIO1",14:"BUSY",15:"NRST",16:"MISO",17:"MOSI",18:"SCK",19:"NSS",20:"GND",21:"ANT",22:"GND"}
H5007 = {1:"TCT1",2:"TD1P",3:"TD1N",4:"TCT2",5:"TD2P",6:"TD2N",7:"TCT3",8:"TD3P",9:"TD3N",10:"TCT4",11:"TD4P",12:"TD4N",13:"MX4N",14:"MX4P",15:"MCT4",16:"MX3N",17:"MX3P",18:"MCT3",19:"MX2N",20:"MX2P",21:"MCT2",22:"MX1N",23:"MX1P",24:"MCT1"}
TPS23861 = {1:"VDD",2:"RESET",3:"SCL",4:"SDAI",5:"SDAO",6:"INT",7:"DGND",8:"SEN3",9:"DRAIN3",10:"GATE3",11:"KSENSB",12:"SEN4",13:"DRAIN4",14:"GATE4",15:"SEN1",16:"DRAIN1",17:"GATE1",18:"KSENSA",19:"SEN2",20:"DRAIN2",21:"GATE2",22:"AGND",23:"A3",24:"SHTDWN",25:"AIN",26:"AOUT",27:"NC",28:"VPWR"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
SYNTH = {"CM5A": {k: v for k, v in CM5_PINS.items() if k <= 100}, "CM5B": {k: v for k, v in CM5_PINS.items() if k > 100},
         "PI7C9X2G404SL": PI7C, "TUSB8041": TUSB, "TS3DV642": TS3, "KSZ9897R": KSZ, "LG290P": LG, "E22_900M30S": E22P, "H5007NL": H5007, "TPS23861": TPS23861, "CP2102N": CP2102}
def synth_symbol(lib, name):
    pins = SYNTH[name]; n = len(pins); rows = (n + 1) // 2; first = min(pins)
    W = 30.48; H = rows * 2.54 + 2.54
    fx = lambda: ["effects", ["font", ["size", "1.27", "1.27"]]]
    sym = ["symbol", q(lib + ":" + name), ["pin_names", ["offset", "1.016"]], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
           ["property", q("Reference"), q("U"), ["at", "0", "%.2f" % (H / 2 + 1.27), "0"], fx()],
           ["property", q("Value"), q(name), ["at", "0", "%.2f" % (-H / 2 - 1.27), "0"], fx()],
           ["property", q("Footprint"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
           ["property", q("Datasheet"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]]]
    body = ["symbol", q(name + "_0_1"), ["rectangle", ["start", "%.2f" % (-W / 2), "%.2f" % (H / 2)], ["end", "%.2f" % (W / 2), "%.2f" % (-H / 2)],
            ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]]
    unit = ["symbol", q(name + "_1_1")]
    for num in sorted(pins):
        row = (num - first) // 2; y = H / 2 - 2.54 * (row + 1)
        if (num - first) % 2 == 0: at = ["at", "%.2f" % (-W / 2 - 2.54), "%.2f" % y, "0"]
        else: at = ["at", "%.2f" % (W / 2 + 2.54), "%.2f" % y, "180"]
        unit.append(["pin", "passive", "line", at, ["length", "2.54"], ["name", q(pins[num]), fx()], ["number", q(str(num)), fx()]])
    sym.append(body); sym.append(unit); return sym

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "R2512": "Resistor_SMD:R_2512_6332Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "C1812": "Capacitor_SMD:C_1812_4532Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "F1812": "Fuse:Fuse_1812_4532Metric",
 "QFN64": "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm", "WQFN42": "Package_DFN_QFN:WQFN-42-1EP_3.5x9mm_P0.5mm_EP2.05x7.55mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm",
 "LQFP128EP": "meshsat:LQFP-128_14x14mm_P0.4mm_EP6.0", "TQFP128EP": "meshsat:TQFP-128_14x14mm_P0.4mm_EP10.0",
 "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "TSSOP28": "Package_SO:TSSOP-28_4.4x9.7mm_P0.65mm", "SOIC8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
 "DDA8": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "SO8EP": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT23": "Package_TO_SOT_SMD:SOT-23", "TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT583": "Package_TO_SOT_SMD:SOT-583-8",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "L0402": "Inductor_SMD:L_0402_1005Metric",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "VH4": "Connector_JST:JST_VH_B4P-VH_1x04_P3.96mm_Vertical",
 "SH4": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
 "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical", "IDC26": "Connector_IDC:IDC-Header_2x13_P2.54mm_Vertical",
 "PH1x2": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "PH1x3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PH1x4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
 "PH1x5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", "PH2x5": "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
 "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USB3A": "Connector_USB:USB3_A_Receptacle_Wuerth_692122030100", "HDMI": "Connector_Video:HDMI_A_Molex_208658-1001_Horizontal",
 "RJ45": "Connector_RJ:RJ45_Amphenol_RJHSE5380", "TP": "TestPoint:TestPoint_Pad_D1.5mm", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", "CR2032": "Battery:BatteryHolder_Keystone_3034_1x20mm",
 "NANOSIM": "Connector_Card:nanoSIM_GCT_SIM8060-6-0-14-00",
 # B16 sites (gen_footprints_b16.py and the B13/B14 files in meshsat.pretty)
 "CM5A": "meshsat:CM5_Conn_A_10164227", "CM5B": "meshsat:CM5_Conn_B_10164227", "M2E": "meshsat:M2_E-Key_Socket_2230", "M2M": "meshsat:M2_M-Key_Socket_2242", "M2B": "meshsat:M2_B-Key_Socket_3052",
 "LG290P": "meshsat:Quectel_LG290P", "E22": "meshsat:Ebyte_E22-900M30S", "E72": "meshsat:Ebyte_E72-2G4M20S1E", "H5007": "meshsat:Pulse_H5007NL",
}
P = []
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    if any(p["ref"] == ref for p in P): raise SystemExit("duplicate reference " + ref)
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets={str(k): v for k, v in nets.items()}, lcsc=lcsc))
def synth(ref, name, value, fp, nets, lcsc=""):
    full = {str(k): nets.get(k, nets.get(str(k), "NC")) for k in SYNTH[name]}
    part(ref, "Connector_Generic", name, value, fp, full, lcsc)
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc=""): part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
def led(ref, colour, anode, cathode): part(ref, "Device", "LED", colour, "LED", {"2": anode, "1": cathode})
def nfet(ref, gate, source, drain, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")   # 1 G 2 S 3 D (SOT-23 order, appendix 32.36)
def level(ref, rn, far, near, near_rail, far_rail=None, rf=None):
    """Bidirectional 2N7002 stage between a module-domain line (near, pulled up to the module's rail) and the always-on side (far); the module off = gate low, nothing flows."""
    nfet(ref, near_rail, near, far); r(rn, "10k", near, near_rail)
    if far_rail: r(rf, "10k", far, far_rail)
def usb_c_recept(ref, dp, dm, vbus, cc1, cc2):
    part(ref, "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C 2.0 receptacle", "USBC",
         {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": vbus, "A9": vbus, "B4": vbus, "B9": vbus, "A5": cc1, "B5": cc2, "A6": dp, "B6": dp, "A7": dm, "B7": dm, "A8": "NC", "B8": "NC", "S1": "GND"}, "C165948")
def esd(ref, dp, dm, vbus): part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6", "SOT236", {"1": dp, "6": dp, "3": dm, "4": dm, "5": vbus, "2": "GND"}, "C7519")
def tps2065(ref, rail, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ic(ref, npins, value, fp, nets, lcsc=""): part(ref, "Connector_Generic", "Conn_01x%02d" % npins, value, fp, {str(k): nets.get(str(k), "NC") for k in range(1, npins + 1)}, lcsc)
def efuse(uref, vin, vout, en, flt, refs, ilim):
    cd, rilm, rflt, rov1, rov2, cin = refs
    ic(uref, 9, "TPS259631DDAR eFuse %s -> %s (%s)" % (vin, vout, ilim), "DDA8", {"1": "GND", "2": uref + "_DVDT", "3": en, "4": vin, "5": vout, "6": flt, "7": uref + "_ILM", "8": uref + "_OVLO", "9": "GND"}, "C2155778")
    c(cd, "10n", uref + "_DVDT", "GND"); r(rilm, ilim, uref + "_ILM", "GND"); r(rflt, "10k", flt, "+3V3_DEV"); r(rov1, "100k 1%", vin, uref + "_OVLO"); r(rov2, "10k 1% (OVLO)", uref + "_OVLO", "GND"); c(cin, "100n", vin, "GND")
def buck33(uref, tag, vin, en, out, refs):
    """AP64500SP-13 5 A buck (A22 buck5 recipe) set to 3.32 V: 31.6k/10k on the 0.8 V reference, 3.3 uH XAL6060, 500 kHz."""
    L, cb, ci1, ci2, co1, co2, co3, rt, rb, rrt, rco, cco = refs
    ic(uref, 9, "AP64500SP-13 5 A buck, 3.3 V rail %s" % out, "SO8EP", {"1": tag + "_BOOT", "2": vin, "3": en, "4": tag + "_RT", "5": tag + "_FB", "6": tag + "_COMP", "7": "GND", "8": tag + "_SW", "9": "GND"}, "C2070920")
    part(L, "Device", "L", "3.3uH XAL6060-332ME", "L6060", {"1": tag + "_SW", "2": out}); c(cb, "100n", tag + "_BOOT", tag + "_SW")
    c(ci1, "22u 10V X7R 1210", vin, "GND", "C1210"); c(ci2, "22u 10V X7R 1210", vin, "GND", "C1210")
    for cr in (co1, co2, co3): c(cr, "22u 10V X7R 1210", out, "GND", "C1210")
    r(rt, "31.6k 1%", out, tag + "_FB"); r(rb, "10k 1%", tag + "_FB", "GND"); r(rrt, "68k (RT: 500 kHz)", tag + "_RT", "GND"); r(rco, "22k", tag + "_COMP", tag + "_COMPC"); c(cco, "3.3n", tag + "_COMPC", "GND")
def buck_small(uref, tag, vin, en, out, refs, rb_val, note):
    """TPS62933 3 A buck (SOT-583: 1 RT 2 EN 3 VIN 4 GND 5 SW 6 BST 7 SS/PG 8 FB; 0.8 V reference, RT floating = 500 kHz): 10k top, rb_val bottom."""
    L, ci, co1, co2, cb, css, rt, rb = refs
    ic(uref, 8, "TPS62933DRLR buck %s" % note, "SOT583", {"1": "NC", "2": en, "3": vin, "4": "GND", "5": tag + "_SW", "6": tag + "_BST", "7": tag + "_SS", "8": tag + "_FB"})
    part(L, "Device", "L", "2.2uH XAL4020-222ME", "L4020", {"1": tag + "_SW", "2": out}); c(ci, "10u", vin, "GND", "C10u"); c(co1, "22u 6.3V", out, "GND", "C10u"); c(co2, "22u 6.3V", out, "GND", "C10u")
    c(cb, "100n", tag + "_BST", tag + "_SW"); c(css, "10n", tag + "_SS", "GND"); r(rt, "10k 1%", out, tag + "_FB"); r(rb, rb_val, tag + "_FB", "GND")
def cp2102(uref, tag, vusb, dp, dm, txd, rxd, rts="NC", dtr="NC", refs=()):
    """CP2102N-A02-GQFN28 bridge: bus sense and regulator input from the slot rail whose hub carries it, its own 3.3 V out (VDD) bypassed, RSTb pulled to VDD."""
    synth(uref, "CP2102N", "CP2102N-A02-GQFN28 USB-UART bridge (%s)" % tag, "QFN28", {3: "GND", 29: "GND", 4: dp, 5: dm, 6: tag + "_3V3", 7: vusb, 8: vusb, 9: tag + "_RST", 25: rxd, 26: txd, 24: rts, 28: dtr}, "C964632")
    rr, c1, c2 = refs
    r(rr, "1k", tag + "_RST", tag + "_3V3"); c(c1, "4.7u", tag + "_3V3", "GND", "C10u"); c(c2, "100n", tag + "_3V3", "GND")

# ================================================================= the three slot columns
GPIO_FIXED = {6: "PI_SHDN_REQ_CM%d", 7: "SPI%d_CE1", 8: "SPI%d_CE0", 9: "SPI%d_MISO", 10: "SPI%d_MOSI", 11: "SPI%d_SCLK", 14: "UART0_TX%d", 15: "UART0_RX%d", 16: "HB_CM%d", 17: "PI_KILL_CM%d",
              22: "GNSS_PPS_CM%d", 23: "SPI%d_IO23", 24: "SPI%d_IO24", 26: "SPI%d_IO26", 2: "SDA_CM%d", 3: "SCL_CM%d"}
HUB_PORT = {1: (1, 2, 3, 4, 6, 7), 2: (9, 10, 11, 12, 14, 15), 3: (17, 18, 19, 20, 22, 23), 4: (24, 25, 26, 27, 29, 30)}   # DP DM SSTXP SSTXM SSRXP SSRXM
def slot(s):
    n5 = "+5V_S%d" % s; cm33 = "+3V3_CM%d" % s; cm18 = "+1V8_CM%d" % s; a33 = "+3V3_S%dA" % s; b33 = "+3V3_S%dB" % s; v10 = "+1V0_S%d" % s; v11 = "+1V1_S%d" % s
    R = lambda k: "R%d" % (100 * s + k); C = lambda k: "C%d" % (100 * s + k); U = lambda k: "U%d" % (100 * s + k); Q = lambda k: "Q%d" % (100 * s + k); L = lambda k: "L%d" % (100 * s + k)
    # --- the module
    CM5 = {}
    for n, nm in CM5_PINS.items():
        if nm == "GND": CM5[n] = "GND"
        elif nm == "5V": CM5[n] = n5
        elif nm == "CM5_3.3V": CM5[n] = cm33
        elif nm == "CM5_1.8V": CM5[n] = cm18
        elif nm.startswith("GPIO") and nm[4:].isdigit():
            g = int(nm[4:]); CM5[n] = GPIO_FIXED[g] % s if g in GPIO_FIXED else "NC"
        else: CM5[n] = "NC"
    if s < 3:
        for g in (7, 8, 9, 10, 11, 23, 24, 26): CM5[{7: 37, 8: 39, 9: 40, 10: 44, 11: 38, 23: 47, 24: 45, 26: 24}[g]] = "NC"   # the SPI0 breakout exists on S3 only (the E22)
    CM5.update({54: "LORA_TXEN" if s == 3 else "NC", 34: "LORA_RXEN" if s == 3 else "NC",   # GPIO4, GPIO5: the E22's T/R switch lines on S3
                16: "FAN_TACHO%d" % s, 19: "FAN_PWM%d" % s, 20: "NC", 21: "LED_nACT%d" % s, 76: "VBAT", 78: cm33, 89: "WL_nDIS%d" % s, 91: "BT_nDIS%d" % s, 92: "NC",
                93: "nRPIBOOT%d" % s, 95: "LED_nPWR%d" % s, 99: "NC", 103: "USB_OTG_N%d" % s, 105: "USB_OTG_P%d" % s,
                3: "ETH%d_P3_P" % s, 5: "ETH%d_P3_N" % s, 4: "ETH%d_P1_P" % s, 6: "ETH%d_P1_N" % s, 9: "ETH%d_P2_N" % s, 11: "ETH%d_P2_P" % s, 10: "ETH%d_P0_N" % s, 12: "ETH%d_P0_P" % s,
                102: "PCIE%d_CLKREQ_n" % s, 104: "PCIE%d_nWAKE" % s, 106: "PCIE_PWR_EN%d" % s, 109: "PCIE%d_nRST" % s, 110: "PCIE%d_CLK_P" % s, 112: "PCIE%d_CLK_N" % s,
                116: "PCIE%d_RX_P" % s, 118: "PCIE%d_RX_N" % s, 122: "PCIE%d_TX_P" % s, 124: "PCIE%d_TX_N" % s,
                128: "USB3%d_RX_N" % s, 130: "USB3%d_RX_P" % s, 134: "USB%d_UP_P" % s, 136: "USB%d_UP_N" % s, 140: "USB3%d_TX_N" % s, 142: "USB3%d_TX_P" % s,
                163: "USB%d_CARD_P" % s if s < 3 else "NC", 165: "USB%d_CARD_N" % s if s < 3 else "NC",
                170: "HDMI%d_D2_P" % s, 172: "HDMI%d_D2_N" % s, 176: "HDMI%d_D1_P" % s, 178: "HDMI%d_D1_N" % s, 182: "HDMI%d_D0_P" % s, 184: "HDMI%d_D0_N" % s, 188: "HDMI%d_CK_P" % s, 190: "HDMI%d_CK_N" % s,
                151: "HDMI%d_CEC" % s, 153: "HDMI%d_HPD" % s, 199: "HDMI%d_SDA" % s, 200: "HDMI%d_SCL" % s})
    ra, rb = "U3%dA" % (s - 1), "U3%dB" % (s - 1)
    part(ra, "Connector_Generic", "CM5A", "Amphenol 10164227-1004A1RLF receptacle A, slot S%d (CM5 pins 1-100, GPIO side); module CM5108064 bench-fitted" % s, "CM5A", {str(k): v for k, v in CM5.items() if k <= 100}, "C7435219")
    part(rb, "Connector_Generic", "CM5B", "Amphenol 10164227-1004A1RLF receptacle B, slot S%d (CM5 pins 101-200, high-speed side)" % s, "CM5B", {str(k): v for k, v in CM5.items() if k > 100}, "C7435219")
    # --- the slot rail: J_5V_Sx from A22 (AP64500 5.1 V, 32.55), bulk at the lead and at the module's 5 V pins
    part("J_5V_S%d" % s, "Connector_Generic", "Conn_01x02", "5 V slot rail S%d from A22 J_5V_S%d (JST-VH, 16 AWG): + -" % (s, s), "VH2", {"1": n5, "2": "GND"})
    part("D%d" % (100 * s + 1), "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": n5, "2": "GND"})
    for k in (1, 2, 3, 4): c(C(k), "100u 10V", n5, "GND", "C100u")
    for k in (5, 6, 7, 8): c(C(k), "10u", n5, "GND", "C10u")
    c(C(9), "10u", cm33, "GND", "C10u"); c(C(10), "100n", cm33, "GND")
    r(R(1), "1k", n5, "LED_5V_A%d" % s); led("LED%d1" % s, "green 5 V S%d" % s, "LED_5V_A%d" % s, "GND")
    # --- 3.3 V bucks: A the card socket (PCIE_PWR_EN, as the B14 WiFi rail), B the switch, hub and NVMe (follows the module's 3.3 V); the two cores from TPS62933 on the 5 V rail
    buck33(U(3), "S%dA" % s, n5, "PCIE_PWR_EN%d" % s, a33, [L(1), C(11), C(12), C(13), C(14), C(15), C(16), R(2), R(3), R(4), R(5), C(17)]); r(R(6), "100k", "PCIE_PWR_EN%d" % s, "GND")
    buck33(U(4), "S%dB" % s, n5, "EN33_S%d" % s, b33, [L(2), C(18), C(19), C(20), C(21), C(22), C(23), R(7), R(8), R(9), R(10), C(24)])
    r(R(11), "100k", cm33, "EN33_S%d" % s); r(R(12), "100k", "EN33_S%d" % s, "GND")   # 1.65 V when the module's 3.3 V is up
    buck_small(U(5), "S%dC" % s, n5, "EN33_S%d" % s, v10, [L(3), C(25), C(26), C(27), C(28), C(29), R(13), R(14)], "40.2k 1%", "1.0 V PCIe switch core S%d" % s)
    buck_small(U(6), "S%dD" % s, n5, "EN33_S%d" % s, v11, [L(4), C(30), C(31), C(32), C(33), C(34), R(15), R(16)], "26.7k 1%", "1.1 V hub core S%d" % s)
    # --- PCIe switch PI7C9X2G404SL: upstream port 0 to the module, port 1 the NVMe socket, port 2 the card socket, port 3 unused; the integrated clock buffer fans the module's 100 MHz to the switch core and both sockets
    m = {}
    for n, nm in PI7C.items():
        if nm in ("VDDR", "CVDDR", "VAUX", "AVDDH"): m[n] = b33
        elif nm in ("VDDC", "VDDCAUX", "AVDD"): m[n] = v10
        elif nm in ("VSS", "CGND", "E_PAD", "REXT_GND"): m[n] = "GND"
        else: m[n] = "NC"
    m.update({5: "PCIE%d_RST1_n" % s, 6: "PCIE%d_RST2_n" % s, 10: "PCIE%d_nRST" % s, 123: "PCIE%d_RX_N" % s, 124: "PCIE%d_RX_P" % s, 127: "PCIE%d_TX_N" % s, 128: "PCIE%d_TX_P" % s,
              100: "NVME%d_RX_P" % s, 101: "NVME%d_RX_N" % s, 97: "NVME%d_TX_P" % s, 98: "NVME%d_TX_N" % s, 106: "CARD%d_RX_P" % s, 107: "CARD%d_RX_N" % s, 102: "CARD%d_TX_P" % s, 103: "CARD%d_TX_N" % s,
              73: "PCIE%d_CLK_N" % s, 74: "PCIE%d_CLK_P" % s, 83: "PCIE%d_RCLK0_N" % s, 85: "PCIE%d_RCLK0_P" % s, 110: "PCIE%d_RCLK0_P" % s, 111: "PCIE%d_RCLK0_N" % s,
              80: "NVME%d_CLK_N" % s, 81: "NVME%d_CLK_P" % s, 77: "CARD%d_CLK_N" % s, 78: "CARD%d_CLK_P" % s,
              86: "S%d_IREF" % s, 116: "S%d_REXT" % s, 33: "S%d_SLOTCLK" % s, 45: "S%d_SLOTIMP" % s, 46: "S%d_SLOTIMP" % s, 19: "GND", 20: "GND", 21: "S%d_PRSNT3" % s, 28: "S%d_PWRSAV" % s,
              9: "S%d_TEST1" % s, 16: "S%d_TESTL" % s, 17: "S%d_TESTL" % s, 22: "S%d_TESTL" % s, 25: "S%d_TESTL" % s, 51: "S%d_TESTL" % s, 18: "S%d_TESTL" % s, 26: "S%d_SMBCLK" % s, 27: "S%d_SMBDAT" % s,
              71: "S%d_EEPD" % s, 89: "S%d_JTAGL" % s, 92: "S%d_JTAGL" % s, 93: "S%d_JTAGL" % s, 94: "S%d_JTAGL" % s, 67: "S%d_PST0" % s, 68: "S%d_PST1" % s})
    synth(U(1), "PI7C9X2G404SL", "Diodes PI7C9X2G404SL PCIe 2.0 switch, slot S%d: up = CM5 lane, port 1 NVMe, port 2 card socket" % s, "LQFP128EP", m, "C2827826")
    r(R(17), "475 1% (IREF)", "S%d_IREF" % s, "GND"); r(R(18), "1.43k 1% (REXT)", "S%d_REXT" % s, "GND"); r(R(19), "5.1k", "S%d_SLOTCLK" % s, b33); r(R(20), "5.1k", "S%d_SLOTIMP" % s, b33)
    r(R(21), "5.1k", "S%d_PRSNT3" % s, b33); r(R(22), "330", "S%d_PWRSAV" % s, "GND"); r(R(23), "5.1k", "S%d_TEST1" % s, b33); r(R(24), "330", "S%d_TESTL" % s, "GND"); r(R(25), "5.1k", "S%d_SMBCLK" % s, b33)
    r(R(26), "5.1k", "S%d_SMBDAT" % s, b33); r(R(27), "4.7k", "S%d_EEPD" % s, "GND"); r(R(28), "330", "S%d_JTAGL" % s, "GND"); r(R(29), "1k", "PCIE%d_CLKREQ_n" % s, "GND")   # the switch cannot forward CLKREQ: the module's clock is always requested
    r(R(30), "1k", b33, "LED_PST0_A%d" % s); led("LED%d2" % s, "green NVMe link (PORTSTATUS0)", "LED_PST0_A%d" % s, "S%d_PST0" % s)
    r(R(31), "1k", b33, "LED_PST1_A%d" % s); led("LED%d3" % s, "green card link (PORTSTATUS1)", "LED_PST1_A%d" % s, "S%d_PST1" % s)
    r(R(32), "10k", "PCIE%d_nWAKE" % s, b33); r(R(33), "10k", "NVME%d_CLKREQ_n" % s, b33); r(R(34), "10k", "CARD%d_CLKREQ_n" % s, a33)
    for k in range(35, 41): c(C(k), "100n", b33, "GND")
    for k in range(41, 47): c(C(k), "100n", v10, "GND")
    c(C(47), "10u", b33, "GND", "C10u"); c(C(48), "10u", v10, "GND", "C10u")
    # --- NVMe socket (M.2 M-key 2242, Amphenol MDT420M02001) on switch port 1; the card sockets below on port 2
    M = {n: "NC" for n in range(1, 76) if not 59 <= n <= 66}
    M.update({n: b33 for n in (2, 4, 12, 14, 16, 18, 70, 72, 74)}); M.update({n: "GND" for n in (1, 3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 71, 73, 75)})
    M.update({41: "NVME%d_RX_N" % s, 43: "NVME%d_RX_P" % s, 47: "NVME%d_TX_N" % s, 49: "NVME%d_TX_P" % s, 53: "NVME%d_CLK_N" % s, 55: "NVME%d_CLK_P" % s, 50: "PCIE%d_RST1_n" % s, 52: "NVME%d_CLKREQ_n" % s,
              54: "PCIE%d_nWAKE" % s, 38: "NVME%d_DEVSLP" % s, 10: "NVME%d_nLED" % s})
    part("J_M2N%d" % s, "Connector", "Bus_M.2_Socket_M", "M.2 M-key 2242 socket, Amphenol MDT420M02001, M2.5 standoff: NVMe drive of slot S%d (k3s replicated storage)" % s, "M2M", M, "C2803771")
    r(R(35), "10k", "NVME%d_DEVSLP" % s, "GND"); r(R(36), "1k", b33, "LED_NV_A%d" % s); led("LED%d4" % s, "amber NVMe activity", "LED_NV_A%d" % s, "NVME%d_nLED" % s)
    c(C(49), "22u 6.3V", b33, "GND", "C10u"); c(C(50), "100n", b33, "GND")
    if s == 1:   # WiFi link card AW7915-AED on an E-key 2230 (B14 wiring); W_DISABLE1# from the hardware EMCON line through a level stage on the card rail
        E = {n: "NC" for n in list(range(1, 24)) + list(range(32, 76))}
        E.update({n: "GND" for n in (1, 7, 18, 33, 39, 45, 51, 57, 63, 69, 75)}); E.update({n: a33 for n in (2, 4, 72, 74)})
        E.update({3: "USB1_CARD_P", 5: "USB1_CARD_N", 35: "CARD1_TX_P", 37: "CARD1_TX_N", 41: "CARD1_RX_P", 43: "CARD1_RX_N", 47: "CARD1_CLK_P", 49: "CARD1_CLK_N", 52: "PCIE1_RST2_n", 53: "CARD1_CLKREQ_n",
                  55: "PCIE1_nWAKE", 56: "WIFI_W_DIS_n", 54: "WIFI_W_DIS2_n", 6: "WIFI_nLED"})
        part("J_M2C1", "Connector", "Bus_M.2_Socket_E", "M.2 E-key 2230 socket, TE 2199230-4, M2.5 standoff: AsiaRF AW7915-AED WiFi 6 link card (two MHF4 leads to A22's P2P jacks)", "M2E", E, "C2803764")
        r(R(37), "10k", "WIFI_W_DIS_n", a33); r(R(38), "10k", "WIFI_W_DIS2_n", a33); nfet(Q(6), a33, "WIFI_W_DIS_n", "EMCON_HW", "2N7002 EMCON -> W_DISABLE1#")
        r(R(39), "1k", a33, "LED_WIFI_A"); led("LED15", "blue WiFi link", "LED_WIFI_A", "WIFI_nLED")
    elif s == 2:   # 5G module RM520N-GL on a B-key 3052 (M.2 WWAN socket 2 pinout; TE 1-2199119-5); SIM 1 on the UIM pins, SIM 2 on GPIO_0..3 per the RM5xx series (to confirm from the RM520N-GL hardware design)
        B = {n: "NC" for n in range(1, 76) if not 12 <= n <= 19}
        B.update({n: "GND" for n in (3, 5, 11, 27, 33, 39, 45, 51, 57, 71, 73)}); B.update({n: a33 for n in (2, 4, 70, 72, 74)})
        B.update({7: "USB2_CARD_P", 9: "USB2_CARD_N", 41: "CARD2_RX_N", 43: "CARD2_RX_P", 47: "CARD2_TX_N", 49: "CARD2_TX_P", 53: "CARD2_CLK_N", 55: "CARD2_CLK_P", 50: "PCIE2_RST2_n", 52: "CARD2_CLKREQ_n",
                  54: "PCIE2_nWAKE", 6: "5G_PWROFF_n", 8: "5G_W_DIS_n", 67: "5G_RST_n", 30: "SIM1_RST", 32: "SIM1_CLK", 34: "SIM1_IO", 36: "SIM1_VCC", 40: "SIM2_CLK", 42: "SIM2_IO", 44: "SIM2_RST", 46: "SIM2_VCC", 10: "5G_nLED"})
        part("J_M2C2", "Connector", "Bus_M.2_Socket_B", "M.2 B-key 3052 socket, TE 1-2199119-5, M2.5 standoff: Quectel RM520N-GL 5G module (PCIe or USB 2.0; two antenna leads to A22's 5G jacks)", "M2B", B, "C2803770")
        r(R(37), "10k", "5G_W_DIS_n", a33); nfet(Q(6), a33, "5G_W_DIS_n", "EMCON_HW", "2N7002 EMCON -> W_DISABLE1#")
        r(R(38), "10k", "5G_PWROFF_n", a33); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", "2N7002 expander -> FULL_CARD_POWER_OFF#")
        r(R(40), "10k", "5G_RST_n", a33); nfet(Q(8), "5G_RESET", "GND", "5G_RST_n", "2N7002 expander -> RESET#")
        r(R(39), "1k", a33, "LED_5G_A"); led("LED25", "amber 5G network", "LED_5G_A", "5G_nLED")
        for k, (vcc, rst, clk, io) in ((1, ("SIM1_VCC", "SIM1_RST", "SIM1_CLK", "SIM1_IO")), (2, ("SIM2_VCC", "SIM2_RST", "SIM2_CLK", "SIM2_IO"))):
            part("J_SIM%d" % k, "Connector", "SIM_Card_Shielded", "nano-SIM push-push GCT SIM8060 (SIM %d)" % k, "NANOSIM", {"1": vcc, "2": rst, "3": clk, "5": "GND", "6": "NC", "7": io, "SH": "GND"})
            c(C(83 + 3 * k), "100n", vcc, "GND"); c(C(84 + 3 * k), "33p", io, "GND", "C0402"); c(C(85 + 3 * k), "33p", clk, "GND", "C0402")
    else:   # spare M-key 2242 on port 2 (the 2280 of 32.52 gave way to space, 32.58)
        M3 = {n: "NC" for n in range(1, 76) if not 59 <= n <= 66}
        M3.update({n: a33 for n in (2, 4, 12, 14, 16, 18, 70, 72, 74)}); M3.update({n: "GND" for n in (1, 3, 9, 15, 21, 27, 33, 39, 45, 51, 57, 71, 73, 75)})
        M3.update({41: "CARD3_RX_N", 43: "CARD3_RX_P", 47: "CARD3_TX_N", 49: "CARD3_TX_P", 53: "CARD3_CLK_N", 55: "CARD3_CLK_P", 50: "PCIE3_RST2_n", 52: "CARD3_CLKREQ_n", 54: "PCIE3_nWAKE", 38: "CARD3_DEVSLP", 10: "CARD3_nLED"})
        part("J_M2C3", "Connector", "Bus_M.2_Socket_M", "M.2 M-key 2242 socket, Amphenol MDT420M02001, M2.5 standoff: spare drive slot of S3", "M2M", M3, "C2803771")
        r(R(37), "10k", "CARD3_DEVSLP", "GND"); r(R(39), "1k", a33, "LED_C3_A"); led("LED35", "amber spare drive activity", "LED_C3_A", "CARD3_nLED")
    c(C(57), "22u 6.3V", a33, "GND", "C10u"); c(C(58), "100n", a33, "GND")
    # --- USB 3 hub TUSB8041I on the module's USB3-0 port; downstream ports per the fabric of 32.58
    h = {}
    for n, nm in TUSB.items():
        if nm == "VDD": h[n] = v11
        elif nm == "VDD33": h[n] = b33
        elif nm == "GND": h[n] = "GND"
        else: h[n] = "NC"
    h.update({53: "USB%d_UP_P" % s, 54: "USB%d_UP_N" % s, 55: "HUB%d_SSTX_P" % s, 56: "HUB%d_SSTX_N" % s, 58: "USB3%d_TX_P" % s, 59: "USB3%d_TX_N" % s, 50: "HUB%d_RST_n" % s, 64: "HUB%d_R1" % s,
              48: "HUB%d_VBUS" % s, 61: "HUB%d_XO" % s, 62: "HUB%d_XI" % s, 49: "GND", 39: "HUB%d_SMBUS_n" % s, 41: "HUB%d_PWRPOL" % s})
    PORTS = {1: {1: ("LIME_DP", "LIME_DM", "HUB1_D1TX_P", "HUB1_D1TX_N", "LIME_SSTX_P", "LIME_SSTX_N"), 2: ("USB_PNL_P", "USB_PNL_N"), 3: ("CAM_DP", "CAM_DM"), 4: ("RB_DP", "RB_DM")},
             2: {1: ("GNSS_DP", "GNSS_DM"), 2: ("ZBA_DP", "ZBA_DM"), 3: ("ZBB_DP", "ZBB_DM"), 4: ("QMX_DP", "QMX_DM")},
             3: {1: ("USB_D8_P", "USB_D8_N"), 2: ("USB_E6_P", "USB_E6_N"), 3: ("USB_WALL_P", "USB_WALL_N"), 4: ("USBX_DP", "USBX_DM")}}[s]
    for port, nets in PORTS.items():
        dp, dm, txp, txm, rxp, rxm = HUB_PORT[port]
        h[dp] = nets[0]; h[dm] = nets[1]
        if len(nets) == 6: h[txp], h[txm], h[rxp], h[rxm] = nets[2], nets[3], nets[4], nets[5]
    if s == 1: h[36] = "LIME_HW_EN"; h[46] = "LIME_FLT"
    synth(U(2), "TUSB8041", "TI TUSB8041IRGCR four-port USB 3.0 hub, slot S%d (upstream the CM5 USB3-0 port)" % s, "QFN64", h, "C2841998")
    c(C(59), "100n", "HUB%d_SSTX_P" % s, "USB3%d_RX_P" % s, "C0402"); c(C(60), "100n", "HUB%d_SSTX_N" % s, "USB3%d_RX_N" % s, "C0402")   # AC coupling on the hub's transmit pairs
    if s == 1: c(C(61), "100n", "HUB1_D1TX_P", "LIME_SSRX_P", "C0402"); c(C(62), "100n", "HUB1_D1TX_N", "LIME_SSRX_N", "C0402")
    r(R(41), "10k", "HUB%d_RST_n" % s, b33); c(C(63), "1u", "HUB%d_RST_n" % s, "GND"); r(R(42), "9.53k 1%", "HUB%d_R1" % s, "GND"); r(R(43), "90.9k 1%", n5, "HUB%d_VBUS" % s); r(R(44), "10k 1%", "HUB%d_VBUS" % s, "GND")
    r(R(45), "10k", "HUB%d_SMBUS_n" % s, b33); r(R(46), "10k", "HUB%d_PWRPOL" % s, b33)
    part("Y%d" % (100 * s + 1), "Device", "Crystal_GND24", "24 MHz 3225", "XTAL", {"1": "HUB%d_XI" % s, "3": "HUB%d_XO" % s, "2": "GND", "4": "GND"})
    c(C(64), "18p", "HUB%d_XI" % s, "GND", "C0402"); c(C(65), "18p", "HUB%d_XO" % s, "GND", "C0402"); r(R(47), "1M", "HUB%d_XI" % s, "HUB%d_XO" % s)
    for k in range(66, 70): c(C(k), "100n", v11, "GND")
    for k in range(70, 74): c(C(k), "100n", b33, "GND")
    c(C(74), "10u", v11, "GND", "C10u")
    # --- module support: LEDs, fan, flashing port, bench headers, the SPI breakout, the domain-boundary stages
    r(R(48), "1k", cm33, "LED_ACT_A%d" % s); led("LED%d6" % s, "green ACT (LED_nACT sinks)", "LED_ACT_A%d" % s, "LED_nACT%d" % s)
    part(Q(1), "Transistor_BJT", "BC857", "BC857: LED_nPWR must be buffered (datasheet Table 4)", "SOT23", {"1": "Q%dB" % s, "2": cm33, "3": "Q%dC" % s})
    r(R(49), "10k", "LED_nPWR%d" % s, "Q%dB" % s); r(R(50), "1k", "Q%dC" % s, "LED_PWR_A%d" % s); led("LED%d7" % s, "red PWR", "LED_PWR_A%d" % s, "GND")
    part("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d (JST-SH 1.0): 5V GND TACHO PWM" % s, "SH4", {"1": n5, "2": "GND", "3": "FAN_TACHO%d" % s, "4": "FAN_PWM%d" % s}); r(R(51), "10k", "FAN_PWM%d" % s, cm33)
    usb_c_recept("J_FLASH%d" % s, "USB_OTG_P%d" % s, "USB_OTG_N%d" % s, "VBUS_FLASH%d" % s, "CC1_F%d" % s, "CC2_F%d" % s); r(R(52), "5.1k", "CC1_F%d" % s, "GND"); r(R(53), "5.1k", "CC2_F%d" % s, "GND")
    esd(U(7), "USB_OTG_P%d" % s, "USB_OTG_N%d" % s, "VBUS_FLASH%d" % s)
    part("J_RPIBOOT%d" % s, "Connector_Generic", "Conn_01x02", "nRPIBOOT jumper S%d: fit to flash the eMMC over J_FLASH%d" % (s, s), "PH1x2", {"1": "nRPIBOOT%d" % s, "2": "GND"})
    # B16: the EEPROM_nWP, PMIC_Enable and PWR_Button bench jumpers of B15 are gone (the module pins stay unconnected; the panel controller owns power control over SLOT_ENx)
    part("J_DBG%d" % s, "Connector_Generic", "Conn_01x05", "console UART0 and the module I2C of S%d (3.3 V, bench): GND TX RX SDA SCL" % s, "PH1x5", {"1": "GND", "2": "UART0_TX%d" % s, "3": "UART0_RX%d" % s, "4": "SDA_CM%d" % s, "5": "SCL_CM%d" % s})
    if s == 3: part("J_SPI3", "Connector_Generic", "Conn_02x05_Odd_Even", "SPI0 breakout of S3 (2x5): 3V3 GND MISO MOSI SCLK CE0 CE1 IO23 IO24 IO26; the E22 LoRa module hangs on these nets", "PH2x5",
                    {"1": b33, "2": "GND", "3": "SPI3_MISO", "4": "SPI3_MOSI", "5": "SPI3_SCLK", "6": "SPI3_CE0", "7": "SPI3_CE1", "8": "SPI3_IO23", "9": "SPI3_IO24", "10": "SPI3_IO26"})
    level(Q(2), R(54), "PI_SHDN_REQ", "PI_SHDN_REQ_CM%d" % s, cm33)
    level(Q(3), R(55), "PI_KILL", "PI_KILL_CM%d" % s, cm33)
    level(Q(4), R(56), "GNSS_PPS", "GNSS_PPS_CM%d" % s, cm33)
    level(Q(5), R(57), "HB%d" % s, "HB_CM%d" % s, cm33, "+3V3_DEV", R(58))
    # --- Ethernet: the module's four pairs into switch port s through 100 nF (PHY to PHY, no magnetics)
    for k, x in ((0, "A"), (1, "B"), (2, "C"), (3, "D")):
        c(C(75 + 2 * k), "100n", "ETH%d_P%d_P" % (s, k), "SWP%d_%s_P" % (s, x), "C0402"); c(C(76 + 2 * k), "100n", "ETH%d_P%d_N" % (s, k), "SWP%d_%s_N" % (s, x), "C0402")
for s in (1, 2, 3): slot(s)

# ================================================================= shared: power
part("J_5V_DEV", "Connector_Generic", "Conn_01x02", "USB device rail from A22 J_5V_DEV (JST-VH): + -", "VH2", {"1": "+5V_DEV", "2": "GND"})
part("D1", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_DEV", "2": "GND"}); c("C1", "100u 10V", "+5V_DEV", "GND", "C100u"); c("C2", "100u 10V", "+5V_DEV", "GND", "C100u")
ic("U25", 6, "AP63203WU-7 3.3 V 2 A buck: the shared logic (+3V3_DEV)", "TSOT6", {"1": "+3V3_DEV", "2": "+5V_DEV", "3": "+5V_DEV", "4": "GND", "5": "DEV_SW", "6": "DEV_BST"})
part("L1", "Device", "L", "4.7uH XAL4020-472ME", "L4020", {"1": "DEV_SW", "2": "+3V3_DEV"}); c("C3", "100n", "DEV_BST", "DEV_SW"); c("C4", "10u", "+5V_DEV", "GND", "C10u"); c("C5", "22u 6.3V", "+3V3_DEV", "GND", "C10u"); c("C6", "22u 6.3V", "+3V3_DEV", "GND", "C10u")
buck_small("U26", "KSZC", "+5V_DEV", "+5V_DEV", "+1V2_KSZ", ["L2", "C7", "C8", "C9", "C10", "C11", "R1", "R2"], "20.0k 1%", "1.2 V Ethernet switch core")
ic("U27", 5, "AP2112K-2.5 LDO: the switch's 2.5 V analog rail", "SOT235", {"1": "+3V3_DEV", "2": "GND", "3": "+3V3_DEV", "4": "NC", "5": "+2V5_KSZ"}); c("C12", "1u", "+2V5_KSZ", "GND"); c("C13", "1u", "+3V3_DEV", "GND")
part("BT1", "Device", "Battery_Cell", "CR2032 holder Keystone 3034: VBAT for the three modules' RTCs, the LG290P backup and the DS3231", "CR2032", {"1": "VBAT", "2": "GND"})
# ================================================================= Ethernet switch KSZ9897R: ports 1-3 the modules, port 4 the wall RJ45 through the magnetics with the PoE injector
k = {}
for n, nm in KSZ.items():
    if nm == "VDDIO": k[n] = "+3V3_DEV"
    elif nm == "AVDDH": k[n] = "+2V5_KSZ"
    elif nm in ("AVDDL", "DVDDL"): k[n] = "+1V2_KSZ"
    elif nm in ("GND", "E_PAD"): k[n] = "GND"
    elif nm.startswith("TXRX") and nm[4] in "123":
        s_ = nm[4]; pol = "P" if nm[5] == "P" else "N"; k[n] = "SWP%s_%s_%s" % (s_, nm[-1], pol)
    elif nm.startswith("TXRX4"):
        k[n] = "SWP4_%s_%s" % (nm[-1], "P" if nm[5] == "P" else "N")
    else: k[n] = "NC"
k.update({125: "KSZ_XO", 126: "KSZ_XI", 127: "KSZ_ISET", 96: "KSZ_RST_n", 94: "EXP_INT", 98: "SDA", 101: "SCL", 105: "KSZ_LED1", 91: "KSZ_LED2", 88: "KSZ_LED3", 85: "KSZ_LED4", 86: "KSZ_STRAP_I2C"})
synth("U1", "KSZ9897R", "Microchip KSZ9897RTXI seven-port Gigabit switch: ports 1-3 the CM5 slots (PHY to PHY), port 4 the wall RJ45; I2C management on the kit bus", "TQFP128EP", k, "C2830106")
part("Y1", "Device", "Crystal_GND24", "25 MHz 3225", "XTAL", {"1": "KSZ_XI", "3": "KSZ_XO", "2": "GND", "4": "GND"}); c("C14", "18p", "KSZ_XI", "GND", "C0402"); c("C15", "18p", "KSZ_XO", "GND", "C0402")
r("R57", "1k (strap [LED4_1, LED3_1] = 01: I2C management, Table 3-3)", "KSZ_STRAP_I2C", "GND"); r("R3", "6.04k 1% (ISET)", "KSZ_ISET", "GND"); r("R4", "10k", "KSZ_RST_n", "+3V3_DEV"); c("C16", "10u", "KSZ_RST_n", "GND", "C10u"); nfet("Q2", "KSZ_RST", "GND", "KSZ_RST_n", "2N7002 expander -> switch reset")
for i, nm in enumerate(("KSZ_LED1", "KSZ_LED2", "KSZ_LED3", "KSZ_LED4"), 1):
    r("R%d" % (4 + i), "1k", "+3V3_DEV", "LED_KSZ_A%d" % i); led("LED%d" % i, "green Ethernet port %d link" % i, "LED_KSZ_A%d" % i, nm)
for i in range(17, 27): c("C%d" % i, "100n", ("+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ")[(i - 17) % 3], "GND")
c("C27", "10u", "+1V2_KSZ", "GND", "C10u"); c("C28", "10u", "+2V5_KSZ", "GND", "C10u")
# magnetics: chip side centre taps to ground through separate 100 nF (voltage-mode PHY, KSZ9897 section 7); MDI side to the RJ45, PoE on the pair 1-2 and 3-6 centre taps
t = {1: "TCT1", 4: "TCT2", 7: "TCT3", 10: "TCT4", 2: "SWP4_A_P", 3: "SWP4_A_N", 5: "SWP4_B_P", 6: "SWP4_B_N", 8: "SWP4_C_P", 9: "SWP4_C_N", 11: "SWP4_D_P", 12: "SWP4_D_N",
     23: "MDI_A_P", 22: "MDI_A_N", 20: "MDI_B_P", 19: "MDI_B_N", 17: "MDI_C_P", 16: "MDI_C_N", 14: "MDI_D_P", 13: "MDI_D_N", 24: "POE_P", 21: "POE_DRAIN", 18: "MCT3", 15: "MCT4"}
synth("T1", "H5007NL", "Pulse H5007NL 1000BASE-T magnetics (switch port 4 to the wall RJ45)", "H5007", t, "C2891392")
for i, nm in enumerate(("TCT1", "TCT2", "TCT3", "TCT4"), 29): c("C%d" % i, "100n", nm, "GND")
r("R9", "75", "MCT3", "BOB"); r("R10", "75", "MCT4", "BOB"); c("C33", "1n 2kV", "BOB", "GND", "C1812")
part("J_ETH", "Connector", "RJ45_Shielded", "RJ45 jack (Amphenol RJHSE5380): patch lead to the sealed wall RJ45; PoE out on 1-2 (+) and 3-6", "RJ45",
     {"1": "MDI_A_P", "2": "MDI_A_N", "3": "MDI_B_P", "4": "MDI_C_P", "5": "MDI_C_N", "6": "MDI_B_N", "7": "MDI_D_P", "8": "MDI_D_N", "SH": "GND"})
# PoE injector TPS23861 (one port used; unused ports per section 8.2.2: SEN grounded, GATE floating, DRAIN open); 54 V from A22's LM5176 boost over J_54V
part("J_54V", "Connector_Generic", "Conn_01x02", "54 V PoE feed from A22 J_54V (JST-VH): + -", "VH2", {"1": "+54V_POE", "2": "GND"})
part("D2", "Device", "D_TVS", "SMBJ58A", "TVS", {"1": "+54V_POE", "2": "GND"}); c("C34", "100n 100V", "+54V_POE", "GND", "C10u"); c("C35", "10u 100V", "+54V_POE", "GND", "C1812")
synth("U5", "TPS23861", "TI TPS23861PWR PoE PSE controller, port 1 to the wall RJ45 (802.3at), I2C on the kit bus", "TSSOP28",
      {1: "+3V3_DEV", 2: "POE_RST_n", 3: "SCL", 4: "SDA", 5: "SDA", 6: "EXP_INT", 7: "GND", 22: "GND", 28: "+54V_POE", 15: "POE_SEN", 16: "POE_DRAIN", 17: "POE_GATE", 18: "GND", 11: "GND", 8: "GND", 12: "GND", 19: "GND"}, "C2927919")
r("R11", "10k", "POE_RST_n", "+3V3_DEV"); c("C36", "100n", "+3V3_DEV", "GND")
part("Q1", "Connector_Generic", "Conn_01x05", "FDMC3612 100 V N-FET, PoE port switch (PowerPAK SO-8: 1-3 source, 4 gate, 5 drain tab)", "PPAK", {"1": "POE_SEN", "2": "POE_SEN", "3": "POE_SEN", "4": "POE_GATE", "5": "POE_DRAIN"}, "C2827865")
r("R12", "0.255R 1% 2512", "POE_SEN", "GND", "R2512"); r("R13", "24.9 (POE_P tie)", "+54V_POE", "POE_P")   # the positive pair tap sits on the 54 V bus through a low-value link for the fit of the PSE detection
# ================================================================= display switch: two TS3DV642 in cascade to the HDMI receptacle; SEL2 chooses the slot (SEL1 high = all channels), selects from the panel controller
def ts3(ref, a, b, cmn, sel):
    d = {1: "+3V3_DEV", 2: "HDMI_SW_EN", 16: "HDMI_SW_EN", 17: sel, 9: "NC", 30: "NC", 43: "GND",
         5: cmn + "_D0_P", 6: cmn + "_D0_N", 7: cmn + "_D1_P", 8: cmn + "_D1_N", 10: cmn + "_D2_P", 11: cmn + "_D2_N", 12: cmn + "_CK_P", 13: cmn + "_CK_N", 3: cmn + "_SCL", 4: cmn + "_SDA", 14: cmn + "_HPD", 15: cmn + "_CEC",
         38: a + "_D0_P", 37: a + "_D0_N", 36: a + "_D1_P", 35: a + "_D1_N", 34: a + "_D2_P", 33: a + "_D2_N", 32: a + "_CK_P", 31: a + "_CK_N", 42: a + "_SCL", 41: a + "_SDA", 19: a + "_HPD", 18: a + "_CEC",
         29: b + "_D0_P", 28: b + "_D0_N", 27: b + "_D1_P", 26: b + "_D1_N", 25: b + "_D2_P", 24: b + "_D2_N", 23: b + "_CK_P", 22: b + "_CK_N", 40: b + "_SCL", 39: b + "_SDA", 21: b + "_HPD", 20: b + "_CEC"}
    synth(ref, "TS3DV642", "TI TS3DV642A0RUAR HDMI 2:1 switch (%s / %s -> %s)" % (a, b, cmn), "WQFN42", d, "C2846591")
ts3("U3", "HDMI1", "HDMI2", "HDMIM", "HDMI_SEL1"); ts3("U4", "HDMIM", "HDMI3", "HDMIO", "HDMI_SEL2")
r("R14", "10k", "HDMI_SW_EN", "+3V3_DEV"); r("R15", "100k", "HDMI_SEL1", "GND"); r("R16", "100k", "HDMI_SEL2", "GND"); c("C37", "100n", "+3V3_DEV", "GND"); c("C38", "100n", "+3V3_DEV", "GND")
part("J_HDMI", "Connector", "HDMI_A", "HDMI type A receptacle (Molex 208658-1001): cable to the Xenarc 709GNK pass-through on the face plate", "HDMI",
     {"1": "HDMIO_D2_P", "3": "HDMIO_D2_N", "4": "HDMIO_D1_P", "6": "HDMIO_D1_N", "7": "HDMIO_D0_P", "9": "HDMIO_D0_N", "10": "HDMIO_CK_P", "12": "HDMIO_CK_N", "2": "GND", "5": "GND", "8": "GND", "11": "GND",
      "13": "HDMIO_CEC", "14": "NC", "15": "HDMIO_SCL", "16": "HDMIO_SDA", "17": "GND", "18": "+5V_HDMI", "19": "HDMIO_HPD_IN", "SH": "GND"})
part("F2", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_DEV", "2": "+5V_HDMI"}); c("C39", "10u", "+5V_HDMI", "GND", "C10u")
r("R17", "2.2k", "HDMIO_SCL", "+5V_HDMI"); r("R18", "2.2k", "HDMIO_SDA", "+5V_HDMI")   # source-side DDC pull-ups as the CM5IO board (2.2k)
r("R19", "15k", "HDMIO_HPD_IN", "HDMIO_HPD"); r("R20", "22k", "HDMIO_HPD", "GND")   # the monitor's 5 V hot-plug level down to 3 V for the module pins
# ================================================================= GNSS LG290P on a CP2102N bridge (S2 hub port 1); 1PPS to the three slots through level stages; active antenna bias from VDD_RF
g = {n: "GND" for n, nm in LG.items() if nm == "GND"}
g.update({23: "+3V3_DEV", 22: "VBAT", 20: "GNSS_TXD", 21: "GNSS_RXD", 3: "GNSS_PPS", 8: "GNSS_RST_n", 9: "GNSS_VDD_RF", 11: "GNSS_RF_IN", 6: "GNSS_TXD2", 7: "GNSS_RXD2"})
synth("U11", "LG290P", "Quectel LG290P03AAMD GNSS RTK module: UART1 to the bridge, 1PPS to every slot, active antenna on the west-wall GNSS jack", "LG290P", g, "C22453086")
r("R21", "10k", "GNSS_RST_n", "+3V3_DEV"); c("C40", "100n", "+3V3_DEV", "GND"); c("C41", "10u", "+3V3_DEV", "GND", "C10u"); r("R22", "10k", "GNSS_PPS", "GND")
r("R23", "10R", "GNSS_VDD_RF", "GNSS_BIAS"); part("L3", "Device", "L", "27nH 0402 (antenna bias tee)", "L0402", {"1": "GNSS_BIAS", "2": "GNSS_ANT"}); c("C42", "47p", "GNSS_ANT", "GNSS_RF_IN", "C0402")
part("J_GNSS1", "Connector", "Conn_Coaxial", "U.FL: pigtail to A22's GNSS jack J_RF4", "UFL", {"1": "GNSS_ANT", "2": "GND"})
part("J_GNSS2", "Connector_Generic", "Conn_01x03", "LG290P UART2 (bench): GND TX RX", "PH1x3", {"1": "GND", "2": "GNSS_TXD2", "3": "GNSS_RXD2"})
cp2102("U15", "GNSS", "+5V_S2", "GNSS_DP", "GNSS_DM", "GNSS_RXD", "GNSS_TXD", refs=("R24", "C43", "C44"))
# ================================================================= LoRa E22-900M30S on S3's SPI0, 5 V through a TPS22810 gated by EMCON; antenna pad to a U.FL for A22's LoRa jack
e22 = {n: "GND" for n, nm in E22P.items() if nm == "GND"}
e22.update({9: "+5V_LORA", 10: "+5V_LORA", 6: "LORA_RXEN", 7: "LORA_TXEN", 8: "NC", 13: "SPI3_IO24", 14: "SPI3_IO23", 15: "SPI3_IO26", 16: "SPI3_MISO", 17: "SPI3_MOSI", 18: "SPI3_SCLK", 19: "SPI3_CE1", 21: "LORA_ANT"})
synth("U12", "E22_900M30S", "Ebyte E22-900M30S 1 W LoRa (SX1262) on S3 SPI0 CE1: TXEN GPIO4, RXEN GPIO5, DIO1 GPIO24, BUSY GPIO23, NRST GPIO26; EU power cap in meshtasticd", "E22", e22, "C2913441")
tps22810("U21", "+5V_DEV", "E22_EN", "+5V_LORA", "E22_CT"); c("C45", "1n", "E22_CT", "GND"); c("C46", "10u", "+5V_LORA", "GND", "C10u"); c("C47", "100n", "+5V_LORA", "GND"); r("R25", "10k", "SPI3_CE1", "+3V3_S3B")
part("J_LORA1", "Connector", "Conn_Coaxial", "U.FL: pigtail to A22's LoRa jack J_RF11", "UFL", {"1": "LORA_ANT", "2": "GND"})
# ================================================================= two E72 CC2652P radios (Zigbee coordinator, Thread RCP) on CP2102N bridges (S2 hub ports 2 and 3), 3.3 V through one TPS22810 gated by EMCON
for i, (tag, uref, ub, refs) in enumerate((("ZBA", "U13", "U16", ("R26", "C48", "C49")), ("ZBB", "U14", "U17", ("R27", "C50", "C51"))), 1):
    E72 = {n: "GND" for n in (1, 11, 12, 19, 23, 34)}
    E72.update({2: tag + "_LED_R", 3: tag + "_LED_G", 7: tag + "_RXD", 8: tag + "_TXD", 10: tag + "_BSL", 13: tag + "_TMSC", 14: tag + "_TCKC", 20: "+3V3_ZB", 24: tag + "_RST_n"})
    part(uref, "Connector_Generic", "Conn_01x34", "Ebyte E72-2G4M20S1E CC2652P (%s): 7 DIO_12 RX, 8 DIO_13 TX, 10 DIO_15 BSL, 24 RESET_N; PCB antenna to the north edge" % ("Zigbee coordinator" if i == 1 else "OpenThread RCP for Matter"), "E72", {str(n): E72.get(n, "NC") for n in range(1, 35)})
    r("R%d" % (27 + i), "10k", tag + "_RST_n", "+3V3_ZB"); r("R%d" % (29 + i), "10k", tag + "_BSL", "+3V3_ZB")
    r("R%d" % (31 + i), "1k", tag + "_LED_R", "LED_%sR_A" % tag); led("LED%d" % (5 + 2 * i - 1), "red %s (DIO_7)" % tag, "LED_%sR_A" % tag, "GND")
    r("R%d" % (33 + i), "1k", tag + "_LED_G", "LED_%sG_A" % tag); led("LED%d" % (5 + 2 * i), "green %s (DIO_8)" % tag, "LED_%sG_A" % tag, "GND")
    part("J_ZBDBG%d" % i, "Connector_Generic", "Conn_01x05", "CC2652P cJTAG %s (bench): 3V3 GND TMSC TCKC RESET" % tag, "PH1x5", {"1": "+3V3_ZB", "2": "GND", "3": tag + "_TMSC", "4": tag + "_TCKC", "5": tag + "_RST_n"})
    cp2102(ub, tag, "+5V_S2", tag + "_DP", tag + "_DM", tag + "_RXD", tag + "_TXD", rts=tag + "_RST_n", dtr=tag + "_BSL", refs=refs)
tps22810("U22", "+3V3_DEV", "E72_EN", "+3V3_ZB", "E72_CT"); c("C52", "1n", "E72_CT", "GND"); c("C53", "10u", "+3V3_ZB", "GND", "C10u"); c("C54", "100n", "+3V3_ZB", "GND"); c("C55", "100n", "+3V3_ZB", "GND")
# ================================================================= LimeSDR Mini receptacle (S1 hub port 1, USB 3) and the RockBLOCK 9704 header (S1 hub port 4 through a CP2102N), both behind TPS259631 eFuses
part("J_LIME", "Connector", "USB3_A", "USB 3.0 type A receptacle (Wuerth 692122030100 land): the LimeSDR Mini 2.4 in its bay", "USB3A",
     {"1": "+5V_LIME", "2": "LIME_DM", "3": "LIME_DP", "4": "GND", "5": "LIME_SSRX_N", "6": "LIME_SSRX_P", "7": "GND", "8": "LIME_SSTX_N", "9": "LIME_SSTX_P", "10": "GND"}, "C2802372")
esd("U33", "LIME_DP", "LIME_DM", "+5V_LIME")
efuse("U23", "+5V_DEV", "+5V_LIME", "LIME_EN", "LIME_FLT", ["C56", "R36", "R37", "R38", "R39", "C57"], "3.0 A (ILM)"); c("C58", "22u 6.3V", "+5V_LIME", "GND", "C10u")
part("J_RB9704", "Connector_Generic", "Conn_02x08_Odd_Even", "RockBLOCK 9704 16-pin (IDC 2x8) on the Ground Control bracket", "IDC16", {
 "1": "GND", "2": "NC", "3": "RB_IEN", "4": "GND", "5": "NC", "6": "RB_CTRL", "7": "RB_STATUS", "8": "RB_XMTG", "9": "NC", "10": "GND", "11": "NC", "12": "NC", "13": "RB_TXD", "14": "RB_RXD", "15": "+5V_RB", "16": "GND"})
cp2102("U18", "RB", "+5V_S1", "RB_DP", "RB_DM", "RB_RXD", "RB_TXD", refs=("R40", "C59", "C60"))
r("R41", "10k", "RB_STATUS", "+3V3_DEV"); r("R42", "10k", "RB_XMTG", "+3V3_DEV")
efuse("U24", "+5V_DEV", "+5V_RB", "RB_EN", "RB_FLT", ["C61", "R43", "R44", "R45", "R46", "C62"], "3.0 A (ILM)"); c("C63", "22u 6.3V", "+5V_RB", "GND", "C10u")
# ================================================================= camera, QMX and spare USB headers, the wall USB pair (S3 hub port 3) with its ESD
tps2065("U28", "+5V_DEV", "CAM_EN", "+5V_CAM", "CAM_FLT"); r("R47", "10k", "CAM_FLT", "+3V3_DEV"); r("R48", "100k", "CAM_EN", "GND"); c("C64", "10u", "+5V_CAM", "GND", "C10u")
part("J_CAM", "Connector_Generic", "Conn_01x04", "camera lead (USB 2.0, S1 hub port 3): 5V D- D+ GND", "PH1x4", {"1": "+5V_CAM", "2": "CAM_DM", "3": "CAM_DP", "4": "GND"}); esd("U34", "CAM_DP", "CAM_DM", "+5V_CAM")
part("F3", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_DEV", "2": "VBUS_QMX"})
part("J_QMX", "Connector_Generic", "Conn_01x04", "QMX USB lead (S2 hub port 4): VBUS D- D+ GND; pigtail to the unit's USB-C", "PH1x4", {"1": "VBUS_QMX", "2": "QMX_DM", "3": "QMX_DP", "4": "GND"}); esd("U35", "QMX_DP", "QMX_DM", "VBUS_QMX")
# the QMX 12 V lead runs from A22's J_HF straight to the unit's DC jack (no B16 part)
part("F4", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_DEV", "2": "+5V_USBX"})
part("J_USBX", "Connector_Generic", "Conn_01x04", "spare USB 2.0 header (S3 hub port 4): 5V D- D+ GND", "PH1x4", {"1": "+5V_USBX", "2": "USBX_DM", "3": "USBX_DP", "4": "GND"}); esd("U36", "USBX_DP", "USBX_DM", "+5V_USBX")
esd("U29", "USB_WALL_P", "USB_WALL_N", "+3V3_DEV")
# ================================================================= hardware EMCON gates (74LVC08APW: 1 1A 2 1B 3 1Y 4 2A 5 2B 6 2Y 7 GND 8 3Y 9 3A 10 3B 11 4Y 12 4A 13 4B 14 VCC); EMCON_HW low silences every transmitter on this board
part("U19", "Connector_Generic", "Conn_01x14", "74LVC08APW quad AND: LimeSDR (hub port power AND EMCON AND software), RockBLOCK (EMCON AND software), LoRa (EMCON AND software)", "TSSOP14",
     {"1": "EMCON_HW", "2": "LIME_HW_EN", "3": "LIME_EN_A", "4": "LIME_EN_A", "5": "LIME_SW_EN", "6": "LIME_EN", "7": "GND", "8": "RB_EN", "9": "EMCON_HW", "10": "RB_SW_EN", "11": "E22_EN", "12": "EMCON_HW", "13": "LORA_ON", "14": "+3V3_DEV"}, "C6009")
part("U20", "Connector_Generic", "Conn_01x14", "74LVC08APW quad AND: E72 radios (EMCON AND software); spare gates grounded", "TSSOP14",
     {"1": "EMCON_HW", "2": "ZB_ON", "3": "E72_EN", "4": "GND", "5": "GND", "6": "NC", "7": "GND", "8": "NC", "9": "GND", "10": "GND", "11": "NC", "12": "GND", "13": "GND", "14": "+3V3_DEV"}, "C6009")
c("C65", "100n", "+3V3_DEV", "GND"); c("C66", "100n", "+3V3_DEV", "GND"); r("R49", "100k", "LIME_HW_EN", "GND"); r("R50", "100k", "LIME_SW_EN", "GND"); r("R51", "100k", "RB_SW_EN", "GND"); r("R52", "100k", "LORA_ON", "GND"); r("R53", "100k", "ZB_ON", "GND")
# ================================================================= expanders, secure element, holdover clock, temperature (kit I2C bus, mastered by the panel controller over J_PANEL)
part("U6", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x20: outputs (switch reset, rail enables, module radio disables, 5G control)", "EXP", {
 "24": "+3V3_DEV", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "GND", "3": "GND",
 "4": "KSZ_RST", "5": "LIME_SW_EN", "6": "RB_SW_EN", "7": "LORA_ON", "8": "ZB_ON", "9": "CAM_EN", "10": "5G_OFF", "11": "5G_RESET",
 "13": "WL_nDIS1", "14": "WL_nDIS2", "15": "WL_nDIS3", "16": "BT_nDIS1", "17": "BT_nDIS2", "18": "BT_nDIS3", "19": "RB_IEN", "20": "RB_CTRL"}, "C5626")
part("U7", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x25: inputs (faults, RockBLOCK status) and spares", "EXP", {
 "24": "+3V3_DEV", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "+3V3_DEV", "3": "+3V3_DEV",
 "4": "LIME_FLT", "5": "RB_FLT", "6": "CAM_FLT", "7": "RB_STATUS", "8": "RB_XMTG", "9": "EXP_SPARE1", "10": "EXP_SPARE2", "11": "EXP_SPARE3",
 "13": "EXP_SPARE4", "14": "EXP_SPARE5", "15": "EXP_SPARE6", "16": "EXP_SPARE7", "17": "EXP_SPARE8", "18": "EXP_SPARE9", "19": "EXP_SPARE10", "20": "EXP_SPARE11"}, "C5626")
c("C67", "100n", "+3V3_DEV", "GND"); c("C68", "100n", "+3V3_DEV", "GND"); r("R54", "2.2k", "SDA", "+3V3_DEV"); r("R55", "2.2k", "SCL", "+3V3_DEV"); r("R56", "10k", "EXP_INT", "+3V3_DEV")
for i in range(1, 12): part("TP%d" % (40 + i), "Connector", "TestPoint", "EXP_SPARE%d" % i, "TP", {"1": "EXP_SPARE%d" % i})
ic("U8", 8, "ATECC608B-SSHDA-T secure element (I2C 0x60): keys behind ZEROIZE", "SOIC8", {"4": "GND", "5": "SDA", "6": "SCL", "8": "+3V3_DEV"}, "C2836813"); c("C69", "100n", "+3V3_DEV", "GND")
ic("U9", 8, "DS3231MZ+ holdover clock (I2C 0x68), CR2032 backed", "SOIC8", {"2": "+3V3_DEV", "3": "EXP_INT", "5": "GND", "6": "VBAT", "7": "SDA", "8": "SCL"}, "C9866"); c("C70", "100n", "+3V3_DEV", "GND")
part("U10", "Sensor_Temperature", "TMP117xxDRV", "TMP117AIDRVR board temperature under the coolers (I2C 0x49)", "WSON6", {"1": "SCL", "2": "GND", "3": "EXP_INT", "4": "+3V3_DEV", "5": "+3V3_DEV", "6": "SDA", "7": "GND"}, "C2842210"); c("C71", "100n", "+3V3_DEV", "GND")
# ================================================================= the panel ribbon J_PANEL (2x13) to C7's controller and the A22 ribbon J_AB1 (2x13, underside)
part("F1", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V_DEV", "2": "PANEL_5V"})
part("J_PANEL", "Connector_Generic", "Conn_02x13_Odd_Even", "panel ribbon to PCB-C C7 (IDC 2x13): the RP2040 panel controller's USB, the kit I2C, EMCON/ZEROIZE/TX_INHIBIT, HDMI selects, heartbeats, slot enables, power control lines", "IDC26", {
 "1": "PANEL_5V", "2": "PANEL_5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EMCON_HW", "9": "GND", "10": "ZEROIZE_HW", "11": "TX_INHIBIT_n", "12": "HDMI_SEL1", "13": "HDMI_SEL2",
 "14": "GND", "15": "USB_PNL_P", "16": "USB_PNL_N", "17": "GND", "18": "HB1", "19": "HB2", "20": "HB3", "21": "SLOT_EN1", "22": "SLOT_EN2", "23": "SLOT_EN3", "24": "PI_SHDN_REQ", "25": "PI_KILL", "26": "SHORE_INHIBIT"})
esd("U37", "USB_PNL_P", "USB_PNL_N", "+3V3_DEV")
part("J_AB1", "Connector_Generic", "Conn_02x13_Odd_Even", "A-B interconnect (IDC 2x13, underside, mates A22's J_AB1 at the same case XY)", "IDC26", {
 "1": "PI_SHDN_REQ", "2": "PI_KILL", "3": "GND", "4": "USB_D8_P", "5": "USB_D8_N", "6": "GND", "7": "USB_E6_P", "8": "USB_E6_N", "9": "GND", "10": "USB_WALL_P", "11": "USB_WALL_N", "12": "GND",
 "13": "SDA", "14": "SCL", "15": "EXP_INT", "16": "TR_APRS", "17": "EMCON_HW", "18": "TX_INHIBIT_n", "19": "SLOT_EN1", "20": "SLOT_EN2", "21": "SLOT_EN3", "22": "ZEROIZE_HW", "23": "GND", "24": "SHORE_INHIBIT", "25": "AB_SPARE", "26": "GND"})
part("TP1", "Connector", "TestPoint", "AB_SPARE", "TP", {"1": "AB_SPARE"})
for i, net in enumerate(("+5V_DEV", "+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ", "VBAT", "EMCON_HW", "ZEROIZE_HW", "GNSS_PPS", "SDA", "SCL", "+54V_POE", "POE_DRAIN", "+5V_LIME", "+5V_RB", "+5V_LORA", "+3V3_ZB", "HDMI_SEL1", "HDMI_SEL2",
                        "+3V3_S1A", "+3V3_S1B", "+1V0_S1", "+1V1_S1", "+3V3_S2A", "+3V3_S2B", "+1V0_S2", "+1V1_S2", "+3V3_S3A", "+3V3_S3B", "+1V0_S3", "+1V1_S3"), 2):
    part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
RAILS = ["+5V_DEV", "+3V3_DEV", "+1V2_KSZ", "+2V5_KSZ", "VBAT", "+54V_POE", "+5V_LIME", "+5V_RB", "+5V_LORA", "+3V3_ZB", "+5V_HDMI", "+5V_CAM", "VBUS_QMX", "+5V_USBX", "PANEL_5V", "GND", "POE_P", "POE_DRAIN", "GNSS_3V3", "ZBA_3V3", "ZBB_3V3", "RB_3V3"]
for s in (1, 2, 3): RAILS += ["+5V_S%d" % s, "+3V3_S%dA" % s, "+3V3_S%dB" % s, "+1V0_S%d" % s, "+1V1_S%d" % s, "+3V3_CM%d" % s, "+1V8_CM%d" % s, "VBUS_FLASH%d" % s]
for i, net in enumerate(RAILS, 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = {}; out = []; ROOT = str(uuid.uuid4())
def U(): return str(uuid.uuid4())
def ensure(lib, name):
    key = lib + ":" + name
    if key not in libsyms: libsyms[key] = synth_symbol(lib, name) if name in SYNTH else flatten(lib, name)
    return libsyms[key]
def extents(sym):
    pins = pins_of(sym); xs = [p[2] for p in pins] or [0]; ys = [p[3] for p in pins] or [0]
    return min(xs), max(xs), min(ys), max(ys)
def place_symbol(lib, name, ref, value, fp, x, y, lcsc="", hide_props=False):
    sym = ensure(lib, name); pins = pins_of(sym); x0, x1, y0, y1 = extents(sym)
    s = '(symbol (lib_id %s) (at %.2f %.2f 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (fields_autoplaced yes) (uuid "%s")\n' % (
        q(lib + ":" + name), x, y, "no" if lib == "power" or name in ("TestPoint",) else "yes", "no" if lib == "power" else "yes", U())
    def prop(k, v, px, py, hide): return '\t(property %s %s (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left)%s))\n' % (q(k), q(v), px, py, " (hide yes)" if hide else "")
    s += prop("Reference", ref, x + x1 + 1.27, y - y1 - 1.27, hide_props); s += prop("Value", value, x + x1 + 1.27, y - y1 + 1.27, hide_props)
    s += prop("Footprint", fp, x, y, True); s += prop("Datasheet", "", x, y, True); s += prop("Description", "", x, y, True)
    if lcsc: s += prop("LCSC", lcsc, x, y, True)
    for num, nm, px, py, rot in pins: s += '\t(pin %s (uuid "%s"))\n' % (q(num), U())
    s += '\t(instances (project %s (path "/%s" (reference %s) (unit 1))))\n)\n' % (q(PROJECT), ROOT, q(ref))
    out.append(s); return pins
def wire(x1, y1, x2, y2): out.append('(wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (x1, y1, x2, y2, U()))
def label(net, x, y, rot):
    just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
    out.append('(label %s (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (q(net), x, y, rot, just, U()))
def noconn(x, y): out.append('(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (x, y, U()))
def text(t, x, y, size=2.0): out.append('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f) bold) (justify left bottom)) (uuid "%s"))\n' % (q(t), x, y, size, size, U()))
STUB = 5.08
pf_n = [0]
def emit_part(p, x, y):
    pins = place_symbol(p["lib"], p["sym"], p["ref"], p["value"], p["fp"], x, y, p["lcsc"]); seen = set()
    for num, nm, px, py, rot in pins:
        sx, sy = x + px, y - py; key = (round(sx, 2), round(sy, 2)); net = p["nets"].get(num)
        if net is None: raise SystemExit("%s pin %s (%s) has no net assignment" % (p["ref"], num, nm))
        if key in seen: continue
        seen.add(key)
        if net == "NC": noconn(sx, sy); continue
        dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[rot]; ex, ey = sx + dx * STUB, sy + dy * STUB; wire(sx, sy, ex, ey)
        if net in POWER:
            lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", ex, ey); pf_n[0] += 1
        else: label(net, ex, ey, {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)])
def emit_pwr_flag(p, x, y):
    place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x, y); net = p["nets"]["1"]; wire(x, y, x, y + STUB)
    if net in POWER:
        lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", x, y + STUB); pf_n[0] += 1
    else: label(net, x, y + STUB, 270)
byref = {p["ref"]: p for p in P}
def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("SHARED POWER: DEVICE RAIL, +3V3_DEV, KSZ CORE RAILS, CR2032", ["J_5V_DEV", "D1", "C1", "C2", "U25", "L1", "C3", "C4", "C5", "C6", "U26", "L2", "C7", "C8", "C9", "C10", "C11", "R1", "R2", "U27", "C12", "C13", "BT1"] + ["TP%d" % k for k in range(1, 32)] + ["TP%d" % k for k in range(41, 52)] + ["#FLG%02d" % k for k in range(1, len(RAILS) + 1)])]
for s in (1, 2, 3):
    mine = lambda ref, s=s: (ref[0] in "RCLQDUY" and ref[1:].isdigit() and 100 * s <= int(ref[1:]) < 100 * (s + 1)) or ref in ("U3%dA" % (s - 1), "U3%dB" % (s - 1)) or ref.startswith("LED%d" % s) and len(ref) == 5 or ref.endswith("%d" % s) and ref.startswith(("J_5V_S", "J_FAN", "J_FLASH", "J_RPIBOOT", "J_DBG", "J_SPI", "J_M2N", "J_M2C")) or (s == 2 and ref in ("J_SIM1", "J_SIM2"))
    SECTIONS.append(("SLOT S%d: COMPUTE MODULE 5, PCIe SWITCH, USB 3 HUB, M.2 SOCKETS, RAILS, SUPPORT" % s, refs_matching(mine)))
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("SHARED: ETHERNET SWITCH, MAGNETICS, RJ45, PoE; HDMI SWITCH; GNSS; LoRa; E72 x2; BRIDGES; LimeSDR; ROCKBLOCK; HEADERS; EMCON; EXPANDERS; RIBBONS", [p["ref"] for p in P if p["ref"] not in placed_refs]))
def layout(page_h):
    global out, pf_n
    out = []; pf_n = [0]; placed = set(); COLW = 92.0; x = 20.0; y = 30.0
    for title, refs in SECTIONS:
        hs = []
        for ref in refs:
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
        if y + 20 > page_h and y > 30.0: x += COLW; y = 30.0
        text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27); y += 4.0
        for ref, h in zip(refs, hs):
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
            if y + h > page_h: x += COLW; y = 34.0
            cy = y + (y1 + STUB) + 4.0; gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27
            if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
            else: emit_part(p, gx, gy)
            placed.add(ref); y += h
        y += 8.0
    missing = [p["ref"] for p in P if p["ref"] not in placed]
    if missing: raise SystemExit("unplaced parts: %s" % missing)
    return x + COLW
max_x = layout(800.0); PAPER = "A0"
print("layout width %.0f mm -> paper %s (A0 landscape is 1189 wide; the schematic PDF is a netlist record, not a drawing)" % (max_x, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper "%s")\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-B COMPUTE") (date "2026-09-07") (rev "A") (company "MeshSat") (comment 1 "Phase B16 schematic (three CM5 slots on a PCIe/USB/Ethernet/HDMI fabric, appendix 32.52 and 32.58), generated by tools/gen_sch_b.py. Netlist style: every pin carries a stub and a label; GND pins carry power symbols."))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
open(OUT, "w").write(hdr + body + '\t(sheet_instances (path "/" (page "1")))\n)\n')
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)
