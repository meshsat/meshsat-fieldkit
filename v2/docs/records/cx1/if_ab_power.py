#!/usr/bin/env python3
"""IF-AB-POWER desk arithmetic, standard library only; stdout is the sole output.

Prototype, no physical measurements. Source keys are expanded in ANALYSIS.md.
No number inferred here becomes a verified typical current or a measured peak.
Run from the repository root as specified in the job.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# Job inputs and IF-AB-POWER, pcb_interfaces.yaml, define these paths and order.
A_PATH = Path("v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json")
B_PATH = Path("v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json")
# Literal pins for the two runtime inputs at this correction's supplied base.
# Do not refresh these automatically: changed declarations need a new review.
INPUT_SHA256 = {
    A_PATH: "3422910a15c4d1450141aa9a5fd725ba75bca9fcb42ae8c87e4cf3385d7d4498",
    B_PATH: "96ee391b3e3f638d7436cad51fcabf77999b530d8734c1feb93f7766a4877d8a",
}
RAILS = ("+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+54V_POE")
# ASSEMBLY.md section 4: 150 mm each way, AWG16 except the AWG18 PoE pair.
LENGTH_M = 0.150
GAUGES = dict(zip(RAILS, (16, 16, 16, 16, 18)))
CONDUCTORS = 2  # IF-AB-POWER pins 1 rail and 2 GND; no return sharing credited.
# JST VH catalogue p.2 range endpoints, not a finished-cable area guarantee.
AREA_MM2 = {16: 1.25, 18: 0.83}
# Tree's dc_drop.py:23, read only; no verdict-writing module is imported.
RHO20_OHM_M = 1.72e-8
ALPHA_PER_C = 0.00393  # Explicit ideal-copper assumption, not stated by held sources.
T_REF_C = 20.0  # Requested copper reference temperature.
T_HOT_C = 60.0  # Requested hot conductor temperature, not inferred ambient.
# TI LM5176 SNVSAI1D p.7 VSNS; p.17 section 7.3.6, equation 4.
VSNS_V = (0.043, 0.050, 0.057)
# gen_sch_a.py lm5176 S2/SD/POE calls, R35/R43/R71; helper r(risns) says 1%.
SHUNTS_OHM = {"+5V_S2": 0.006, "+5V_DEV": 0.006, "+54V_POE": 0.020}
SHUNT_TOL = 0.01
# Diodes AP64500 DS41979 Rev.5-2 p.1, continuous output rating.
AP64500_A = 5.0
# JST VH held catalogue, revision not printed, p.1. 10 A applies AWG16 STANDARD.
VH16_A = 10.0
# p.1 gives 7 A for AWG18 SHROUDED, not the fitted standard B2P-VH. Comparator only.
VH18_SHROUDED_A = 7.0
# JST p.1 contact resistance maxima: initial 10 mOhm; after test 20 mOhm.
CONTACT_R_OHM = (0.010, 0.020)
MATED_CONTACTS = 4  # Two conductors and a mated connection at each board.
# CM5 release 3, printed pp.15,27 Table 9 and p.35 B.3 respectively.
CM5_TYP_A = 0.9
CM5_DESIGN_A = 2.5
# gen_sch_b.py _SLOT_LOADS: 1.6 A is a project stress allowance, not a maker peak.
CM5_INTENT_A = 1.6
# AsiaRF AW7915-AED_V1 held sheet p.4: average 7 W, maximum 9.1 W.
WIFI_W = (7.0, 9.1)
# IF-AB-POWER quotes this rounded conditional coincidence figure; not a measured peak.
CONTRACT_S2_PEAK_A = 5.63
# Microchip DS00002330D Table 6-1 p.169, 25 C, full 1000 Mb/s operation.
# POWER-THERMAL.md:145,962 (PWR-F03): VERIFIED maker typical, no maximum.
KSZ_CORE_MAKER_A = 0.460 + 0.750
# POWER-THERMAL.md:706-711,1037-1038: inferred PS-ALLTX model, not measurement.
REGISTRY_S1_PLAN_A = 4.65
REGISTRY_DEV_PLAN_A = 5.89
REGISTRY_DEV_HIGH_A = 7.8

SLOT_BASES = (
    ("CM5", "estimate, neither sourced typical nor peak", "CM5 Table 9: 0.9 A typical; B.3: 2.5 A design allowance; 1.6 A is generator headroom"),
    ("card buck input", "capacity-derived estimate, not typical", "generator applies 2.2 A to every slot; S2 is now 3.456 V; Q11 minimum supply 3/4 A; W1 applies to S1/S3"),
    ("NVMe and PCIe 3.3 V buck", "typical allocation, unverified", "generator; child +3V3_SxB declares 0.9/1.8 A; selected SSD/workload and efficiency not established"),
    ("PCIe 1.0 V buck", "typical allocation, unverified", "generator; child +1V0_Sx declares 0.8/1.2 A; efficiency is an assumption"),
    ("cooler fan", "estimate, typical/peak unspecified", "generator; IF-CM5-FAN current is TBD with exact fan part"),
    ("card enable gate", "design allowance, not typical/peak", "generator 1 mA; TI SCLS739F p.6 ICC maximum 10 uA, switching current extra"),
)
DEV_BASES = {
    "U23": ("LimeSDR eFuse", "typical estimate, unverified", "generator 1.2 A; held Mini 2.0 pages say 4.5 W / 5 V 900 mA; exact 2.4 configuration not established"),
    "U25": ("shared 3.3 V buck", "typical allocation, assumed efficiency", "0.9 A matches child 1.2 A at 3.3 V with 0.88 efficiency; generator's 1.4 A comment is stale"),
    "U21": ("LoRa switch", "transmit estimate, not maker peak", "E22 v1.20 p.2 (PDF p.3) gives 0.650 A typical instantaneous TX, not 0.600 A"),
    "F1": ("panel feed", "typical allocation, unverified", "generator cites board C declaration; not a maker load or loaded-panel measurement"),
    "U24": ("RockBLOCK eFuse", "burst estimate, not proven peak", "held Ground Control input documentation: default charge limit about 0.460 A, input maximum 0.500 A; configurable 0.800 A"),
    "F3": ("QMX USB VBUS", "allocation, typical/peak unspecified", "generator only; HF main DC supply is separate; USB sink draw not established"),
    "U28": ("camera switch", "typical estimate, unverified", "child intent 0.250 A typical / 0.500 A port allocation; exact camera absent"),
    "F2": ("HDMI VBUS", "allocation, neither child typical nor peak", "generator comment wrongly names display switches; child +5V_HDMI declares 0.100/0.500 A at J_HDMI"),
    "U26": ("KSZ 1.2 V buck", "declaration below VERIFIED maker typical; input inferred", "PWR-F03; DS00002330D Table 6-1 p.169: 0.460+0.750=1.210 A typical at 1.2 V, 25 C, full 1000 Mb/s; 0.341647 A input at assumed 0.85 efficiency and 5.0 V; no maker maximum"),
}
# These designators and numerical allocations are read from the input; grouping is from gen_sch_b.py.
for ref in ("U106", "U206", "U306"):
    DEV_BASES[ref] = ("hub 1.1 V buck", "typical allocation, unverified", "child 0.400 A typical / 0.700 A peak; 0.85 efficiency assumption")
for ref in ("U40", "U50", "U60"):
    DEV_BASES[ref] = ("supervisor private LDO", "typical allocation, inconsistent", "child +3V3_IOCx declares 0.120/0.250 A; LDO input current approximately output plus bias, not 0.050 A")
for ref in ("U15", "U16", "U17", "U18"):
    DEV_BASES[ref] = ("CP2102N bridge", "design allocation, not maker typical/peak", "Silicon Labs rev.1.5 p.10: 9.5/13.7 mA typical at 115200 baud/3 Mbaud; no max; generator allocates 20 mA")


def table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        print("| " + " | ".join(str(x) for x in row) + " |")
    print()


def resistance(gauge, temp):
    # SI conversion of mm2 to m2; Ohm's law and linear copper temperature model.
    return RHO20_OHM_M * CONDUCTORS * LENGTH_M / (AREA_MM2[gauge] * 1e-6) * (1 + ALPHA_PER_C * (temp - T_REF_C))


def limit(rail):
    if rail not in SHUNTS_OHM:
        return AP64500_A
    return VSNS_V[0] / (SHUNTS_OHM[rail] * (1 + SHUNT_TOL))


def margin(cap, current):
    return f"{cap-current:+.6f} ({(cap-current)/cap*100:+.2f}%)"


def case_table(rail, volts, budget, cases):
    cap = limit(rail)
    rating = VH16_A if GAUGES[rail] == 16 else None
    rows = []
    for name, lead_i, conv_i in cases:
        drop20 = lead_i * resistance(GAUGES[rail], T_REF_C)
        drop60 = lead_i * resistance(GAUGES[rail], T_HOT_C)
        contact = margin(rating, lead_i) if rating is not None else "INCONCLUSIVE (7 A is other header)"
        rows.append((name, f"{lead_i:.6f}", f"{conv_i:.6f}", margin(cap, conv_i), contact,
                     f"{drop20:.6f}", f"{drop60:.6f}", f"{volts*budget-drop20:+.6f} / {volts*budget-drop60:+.6f}"))
    table(("Case (conditional unless declaration)", "Lead A", "Converter A", "Converter margin A (%)", "Contact margin A (%)", "Pair drop 20 C V", "Pair drop 60 C V", "Unused WHOLE 2% budget 20/60 C V"), rows)
    rows = []
    for name, current, _ in cases:
        initial20 = current * (resistance(GAUGES[rail], T_REF_C) + MATED_CONTACTS * CONTACT_R_OHM[0])
        initial60 = current * (resistance(GAUGES[rail], T_HOT_C) + MATED_CONTACTS * CONTACT_R_OHM[0])
        after20 = current * (resistance(GAUGES[rail], T_REF_C) + MATED_CONTACTS * CONTACT_R_OHM[1])
        after60 = current * (resistance(GAUGES[rail], T_HOT_C) + MATED_CONTACTS * CONTACT_R_OHM[1])
        rows.append((name, f"{initial20:.6f} / {initial60:.6f}", f"{after20:.6f} / {after60:.6f}",
                     f"{volts*budget-initial60:+.6f} / {volts*budget-after60:+.6f}"))
    table(("Case", "Wire + initial contact MAX bound, 20/60 C V", "Wire + after-test contact MAX bound, 20/60 C V", "Whole-budget margin at 60 C, initial/after V"), rows)


def input_current(rails, name, field, parent_v):
    r = rails[name]
    return r[field] * r["volts"] / (r["efficiency"] * parent_v)


def pinned_inputs():
    """Verify all runtime inputs before parsing; return the exact checked bytes."""
    checked = {}
    for path, expected in INPUT_SHA256.items():
        try:
            data = (ROOT / path).read_bytes()
        except OSError as error:
            raise SystemExit(f"Refused: input {path}: {error}") from error
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise SystemExit(f"Refused: input {path}: sha256 mismatch; expected {expected}, got {actual}")
        checked[path] = data
    return checked


def main():
    checked = pinned_inputs()
    a = json.loads(checked[A_PATH])["rails"]
    b = json.loads(checked[B_PATH])["rails"]
    print("# IF-AB-POWER calculation: prototype, AI review arithmetic")
    print("Mode: PS-ALLTX, REQ-018 / CONOPS section 5, case S3 over S2. Condition: three CM5s loaded; standby WiFi in slot 3, PoE, USB-C outlet and heater off.\n")
    print("No sourced typical or guaranteed coincident peak is established. Generic declarations and conditional stresses follow; they are not alternate operating modes.\n")
    for path in (A_PATH, B_PATH):
        print(f"Input {path}: sha256 {INPUT_SHA256[path]} (pin verified)")
    print()
    print("Copper model: dc_drop.py:23 rho20=1.72e-8 ohm m; JST VH catalogue p.2 areas AWG16=1.25 mm2, AWG18=0.83 mm2. Alpha=0.00393/C remains an explicit ideal-copper assumption; actual cable is INCONCLUSIVE.\n")
    table(("Rail", "AWG", "Pair length m", "Pair R20 ohm", "Pair R60 ohm", "Contact rating"),
          [(r, GAUGES[r], f"{CONDUCTORS*LENGTH_M:.3f}", f"{resistance(GAUGES[r],T_REF_C):.9f}", f"{resistance(GAUGES[r],T_HOT_C):.9f}", "10 A, standard/AWG16" if GAUGES[r] == 16 else "INCONCLUSIVE: 7 A quoted only for shrouded/AWG18") for r in RAILS])
    for rail in RAILS:
        ar, br = a[rail], b[rail]
        total = math.fsum(br["loads"].values())
        print(f"## {rail}\n")
        table(("End", "V", "Typical A", "Peak A", "Source", "Raw load sum A", "Loads"),
              [(board, r["volts"], r["amps_typ"], r["amps_peak"], r["source"], f"{math.fsum(r['loads'].values()):.6f}", json.dumps(r["loads"], sort_keys=True)) for board,r in (("A converter",ar),("B lead",br))])
        print("A note: " + ar["note"] + "\n")
        print("B note: " + br["note"] + "\n")
        print(f"B raw sum minus B typical = {total-br['amps_typ']:+.6f} A; raw sum minus B peak = {total-br['amps_peak']:+.6f} A. Mixed allocations, not a sourced operating total.\n")
        load_rows=[]
        for ref,current in br["loads"].items():
            if rail.startswith("+5V_S"):
                # Function mapping from gen_sch_b.py _SLOT_LOADS, independent of JSON key order.
                keys = (f"U3{int(rail[-1])-1}A", f"U{rail[-1]}03", f"U{rail[-1]}04",
                        f"U{rail[-1]}05", f"J_FAN{rail[-1]}", f"U{rail[-1]}16")
                desc,kind,basis = SLOT_BASES[keys.index(ref)]
            elif rail == "+5V_DEV":
                desc,kind,basis = DEV_BASES[ref]
            elif ref == "R13":
                desc,kind,basis = ("PoE port", "peak residual allocation, not maker figure", "generator: 0.600 A total minus 0.007 A controller; disabled in named mode")
            else:
                desc,kind,basis = ("TPS23861 VPWR", "maximum at stated test condition", "TI SLUSBX9I p.7: 0.007 A max at 57 V; not a typical at 54 V; mode supply disabled")
            load_rows.append((ref,desc,f"{current:.6f}",kind,basis))
        table(("B load", "Function", "Declared A", "Typical or peak?", "Basis and uncertainty"),load_rows)
        if rail in SHUNTS_OHM:
            sh=SHUNTS_OHM[rail]
            print(f"Converter {ar['switch']} LM5176: shunt {ar['source']} = {sh:.6f} ohm +/-1%; nominal-R VSNS limits = " + "/".join(f"{v/sh:.6f}" for v in VSNS_V) + " A (min/typ/max).")
            print(f"Including initial shunt tolerance: {limit(rail):.6f} to {VSNS_V[2]/(sh*(1-SHUNT_TOL)):.6f} A. This is average-loop onset, not a guaranteed stage rating or instantaneous clamp.\n")
        else:
            print(f"Converter {ar['switch']} AP64500: rated continuous output {AP64500_A:.6f} A (D1 p.1), not its switch-current threshold.\n")
        if rail == "+5V_DEV":
            local = math.fsum(v for k,v in ar["loads"].items() if k != "J_5V_DEV")
            local_typ = a["+5V_D8"]["amps_typ"] + a["VBUS_WALL"]["amps_typ"]
            local_peak = a["+5V_D8"]["amps_peak"] + a["VBUS_WALL"]["amps_peak"]
            interim_typ = br["amps_typ"] + a["+5V_D8"]["amps_typ"] + ar["loads"]["U32"]
            d_typ_peak = br["amps_peak"] + a["+5V_D8"]["amps_typ"] + a["VBUS_WALL"]["amps_peak"]
            ksz = b["+1V2_KSZ"]
            ksz_input = KSZ_CORE_MAKER_A * ksz["volts"] / (ksz["efficiency"] * br["volts"])
            print(f"U26 inferred input from VERIFIED maker typical: {KSZ_CORE_MAKER_A:.3f} * {ksz['volts']} / ({ksz['efficiency']} * {br['volts']}) = {ksz_input:.9f} A. Replacing only U26's {br['loads']['U26']:.3f} A moves the mixed B sum to {total-br['loads']['U26']+ksz_input:.9f} A; not a mode total.\n")
            cases=[("A J_5V_DEV allocation, local allocations",ar["loads"]["J_5V_DEV"],ar["amps_typ"]),
                   ("B declared typical + A local allocations",br["amps_typ"],br["amps_typ"]+local),
                   ("INTERIM B typical + D8 typical + parent wall",br["amps_typ"],interim_typ),
                   ("B raw loads + A local allocations",total,total+local),
                   ("B declared typical + A child typical",br["amps_typ"],br["amps_typ"]+local_typ),
                   ("B peak + D8 typical + wall peak coincidence",br["amps_peak"],d_typ_peak),
                   ("B declared peak + A child peak BOUND",br["amps_peak"],br["amps_peak"]+local_peak)]
            print(f"A converter declared peak alone = {ar['amps_peak']:.6f} A; onset margin {margin(limit(rail),ar['amps_peak'])}; no per-lead peak apportioned by A.\n")
            print(f"Held A peak {ar['amps_peak']:.3f} = B peak {br['amps_peak']:.3f} + wall peak {a['VBUS_WALL']['amps_peak']:.3f} + D8 ZERO. D8 and wall are not outlets dropped by D-11.\n")
            print(f"POWER-THERMAL.md:706-711,1037-1038 PS-ALLTX PLAN/HIGH = {REGISTRY_DEV_PLAN_A:.2f}/{REGISTRY_DEV_HIGH_A:.1f} A at converter. HIGH onset margin {margin(limit(rail),REGISTRY_DEV_HIGH_A)}; HIGH is inside the loop band, not below it. PWR-F01 to PWR-F03 at lines 960-962 also flag understated child declarations.\n")
            print(f"Recommend SESSION decision: converter peak {br['amps_peak']+local_peak:.3f} A coincident BOUND; {d_typ_peak:.3f} A with D8 typical. Limiter: LM5176 average-loop fold-back (SNVSAI1D p.17), reducing output voltage if sustained demand reaches its threshold. Device brown-out/shared-fabric loss is possible; REQ-018 regulation remains unproven. Draft applies only interim typical alignment, not this pending peak decision.\n")
        else:
            cases=[("A declared typical",ar["amps_typ"],ar["amps_typ"]),("A declared peak",ar["amps_peak"],ar["amps_peak"]),
                   ("B declared typical",br["amps_typ"],br["amps_typ"]),("B declared peak",br["amps_peak"],br["amps_peak"]),("B mixed raw load sum",total,total)]
        if rail.startswith("+5V_S"):
            slot=int(rail[-1])
            typ_other=sum(input_current(b,n,"amps_typ",br["volts"]) for n in (f"+3V3_S{slot}B",f"+1V0_S{slot}"))
            pk_other=sum(input_current(b,n,"amps_peak",br["volts"]) for n in (f"+3V3_S{slot}B",f"+1V0_S{slot}"))
            fan=br["loads"][f"J_FAN{slot}"]; gate=br["loads"][f"U{slot}16"]
            card=f"+3V3_S{slot}A"
            if slot == 3:
                card_typ=card_pk=0.0  # REQ-018 explicitly requires standby WiFi off; leakage unknown.
            elif slot == 1:
                card_typ,card_pk=(w/(b[card]["efficiency"]*br["volts"]) for w in WIFI_W)
            else:
                card_typ=input_current(b,card,"amps_typ",br["volts"])
                card_pk=input_current(b,card,"amps_peak",br["volts"])
            reconstructed=CM5_TYP_A+card_typ+typ_other+fan+gate
            loaded=CM5_DESIGN_A+card_pk+pk_other+fan+gate
            cases += [("Sourced/intent planning mix, NOT typical",reconstructed,reconstructed),
                      ("CM5 design + child peaks conditional BOUND",loaded,loaded)]
            if slot == 1:
                registry_mix = CM5_INTENT_A + card_pk + typ_other + fan + gate
                print(f"PS-ALLTX registry comparison: CM5 project 1.6 A + AsiaRF 9.1 W + other children typical + fan/gate = {registry_mix:.9f} A, difference from POWER-THERMAL.md:707 PLAN {REGISTRY_S1_PLAN_A:.2f} A = {registry_mix-REGISTRY_S1_PLAN_A:+.9f} A. PWR-F01/F02 (:960-961); HIGH is 4.66 A. Original planning mix uses 0.9 A CM5 and 7 W WiFi instead.\n")
                cases += [("Registry PLAN comparison input mix",registry_mix,registry_mix)]
            if slot == 2:
                old_coincident=CM5_INTENT_A+card_pk+typ_other+fan  # B comment omits later 1 mA gate.
                loaded_typ_other=CM5_DESIGN_A+card_pk+typ_other+fan+gate
                print(f"Reproduce old S2 coincidence: 1.6 + {card_pk:.9f} + {typ_other:.9f} + {fan:.6f} = {old_coincident:.9f} A; with gate {old_coincident+gate:.9f} A.\n")
                print(f"INTERIM draft alignment: A/B S2 typical {br['amps_typ']:.1f} A, peak/J_5V_S2 {CONTRACT_S2_PEAK_A:.2f} A; Q28 nominal-input allocation {CONTRACT_S2_PEAK_A*br['volts']/(ar['efficiency']*a['VBAT']['volts']):.9f} A rounds to 2.22 A. All-peak conditional bound {loaded:.6f} A remains above loop minimum; mode INCONCLUSIVE.\n")
                cases += [("Contract quoted 5.63 A conditional",CONTRACT_S2_PEAK_A,CONTRACT_S2_PEAK_A),
                          ("CM5 design + 5G peak + other typical",loaded_typ_other,loaded_typ_other)]
            print("Reconstruction uses child intent V, I and efficiency. Efficiency is an unverified assumption; the resulting stress is a CONDITIONAL BOUND, not a guaranteed upper bound.\n")
        if rail == "+54V_POE":
            cases += [("Named mode commanded OFF, ideal settled",0.0,0.0)]  # D-11/REQ-018, not measured leakage.
        case_table(rail,br["volts"],br["budget"],cases)
        print("Contact bounds apply the catalogue maximum to four mated contacts, without a further temperature correction not stated by JST. Crimp/wire tolerances and board drops are additional or uncharacterised. These are conditional resistance bounds, not measured drops.\n")
        if rail == "+54V_POE":
            print("Verdict: INCONCLUSIVE for a sourced mode current/contact margin. Generic A/B declarations AGREE; mode demands outlet OFF, actual leakage/discharge needs evidence.\n")
        elif rail in ("+5V_S2","+5V_DEV"):
            print("Verdict: INCONCLUSIVE mode current. Held A/B declarations DISAGREE; unexecuted draft supplies INTERIM alignment. Conditional peaks do not become verified operating figures.\n")
        else:
            print("Verdict: INCONCLUSIVE mode current. A/B scalar declarations AGREE, but neither the raw allocations nor conditional stress validate those scalars.\n")
    print("All current margins are limit minus current; positive is arithmetic headroom only. Negative conditional margins flag unresolved regulation risk. The 2% voltage column is the entire existing budget, NOT a new allowance for the cable; A/B shares already sum to 2%. No requirement, protection or declaration was changed.")


if __name__ == "__main__":
    main()
