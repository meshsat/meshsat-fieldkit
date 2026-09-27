#!/usr/bin/env python3
"""EQ-16 / R8E-N01: the dock's VIN_RAW contacts, and the return beside them (board E stream w3de, MESHSAT-1357,
27 September 2026). Desk arithmetic only: nothing here is a measurement, nothing has been built.

Inputs, each from a document this tree holds or from a declaration in a generator:
  I_VIN     14.10 A   board E's VIN_RAW, typical and peak (gen_sch_e.py, R4A-N12: board A's front end at its ISNS
                      limit drawing from a 9.0 V bus; 14.4 A at a 9.0 V vehicle measured at the connector)
  I_PACK    10.0 / 18.0 A the pack's continuous and 60 s peak (gen_sch_e.py CELL_F, gen_sch_a.py CELL+)
  813       "OPERATING CURRENT Max. 3.5 A", "CONTACT RESISTANCE 10 mOhm (static measurement, halfway position)"
            (Preci-Dip pages 31-34, p.34); "-55 ... +125 C (-55 ... +85 C with music wire spring)" (p.31); the 813's
            spring is "Music wire DIN 17223, gold plated" (p.34), so 85 C; no current-temperature curve, no rise figure
  MILL-MAX  "Rated Current (Free air): Continuous 9 amps @ 10 C temperature rise", "Contact Resistance: 20 mOhm max",
            "Operating temperature range: -55/+125 C" (Mill-Max page 28, v2/vendor/connectors/)
  AIR       51 C: the inside-air bar part_temps.py resolves from pcb_envelope.yaml (max(+35 C + 16 K three modules,
            +40 C + 10 K one module)); 65 C: the +55 C qualification margin (owner ruling D-02a) in the reduced mode
            (one module, +10 K)
  ECSS      ECSS-Q-ST-30-11C Rev.2 Table 6-10 (connectors): current 50 percent, maximum operating temperature 30 C
            below the maximum rated. A SPACE screen, reported as the fuse screen is (energy_chain.py), not a limit
            this project claims the standard sets for a terrestrial kit.
  WIRES     24 AWG 60 mm per 813 contact (ASSEMBLY.md, block signal wires): 84.2 mOhm/m, 5.1 mOhm; the E5 track to
            each land 0.3 to 0.4 mm on 2 oz over about 10 mm, about 6 mOhm and a via; 12 AWG from E5 to the strip:
            5.2 mOhm/m, 0.3 mOhm at 60 mm. Copper resistivity 1.72e-8 ohm m.
ASSUMPTIONS (stated, each a session choice): the 813's rise at its 3.5 A rating is at most 60 K (the rating read at a
25 C reference cannot put the contact above its own 85 C limit), and it scales as I^2; the Mill-Max rise scales as I^2
from the maker's 10 K at 9 A; paralleled contacts of one kind may differ 2:1 in resistance (the makers state a static
value or a maximum only)."""
import itertools

I_VIN = 14.10
I_PACK_T, I_PACK_P = 10.0, 18.0
PD_MAX, PD_R, PD_TMAX, PD_RISE_AT_MAX = 3.5, 10.0, 85.0, 60.0
MM_RATED, MM_RISE, MM_RMAX, MM_TMAX = 9.0, 10.0, 20.0, 125.0
AIR = {"envelope 51 C": 51.0, "margin 65 C": 65.0}
R_813_PATH = 10.0 + 5.1 + 6.1 + 0.5          # mOhm: contact, 24 AWG 60 mm, E5 track, via
R_12AWG = 0.31; R_POUR = 0.3


def rise_813(i): return PD_RISE_AT_MAX * (i / PD_MAX) ** 2
def rise_mm(i): return MM_RISE * (i / MM_RATED) ** 2


def worst_share(n, spread=2.0, open_=0):
    """The largest fraction one of n parallel contacts takes when it is the lowest resistance and the others are
    `spread` times it, with `open_` of the others open."""
    others = n - 1 - open_
    return 1.0 / (1.0 + others / spread)


def supply_rows():
    rows = []
    for name, n, rated, rise, tmax in (("813 x4 (as drawn)", 4, PD_MAX, rise_813, PD_TMAX),
                                       ("813 x5 (spare pin 12 added)", 5, PD_MAX, rise_813, PD_TMAX),
                                       ("813 x8 (a 2x8 813, pins 1-4 and 12-15)", 8, PD_MAX, rise_813, PD_TMAX),
                                       ("Mill-Max 0858 x4 (the decision)", 4, MM_RATED, rise_mm, MM_TMAX)):
        for label, i in (("even", I_VIN / n), ("even, one open", I_VIN / (n - 1)),
                         ("2:1 spread", I_VIN * worst_share(n)), ("2:1 spread, one open", I_VIN * worst_share(n, open_=1))):
            t = {k: a + rise(i) for k, a in AIR.items()}
            rows.append((name, label, i, 100 * i / rated, rise(i), t, tmax))
    return rows


def parallel(*rs): return 1.0 / sum(1.0 / r for r in rs)


def return_rows():
    """The ground current from A to E shares every ground contact of the dock. Two groups: the Mill-Max pins (pack
    return CN, and the decision's VN) behind their pours and 12 AWG wires, and the 813 ground contacts behind their 24 AWG
    wires. The share is set by the groups' resistances, which the makers bound only from above."""
    out = []
    for design, n_mm, n_wires, n_813 in (("as drawn: 4 CN + 4 x 813 GND", 4, 1, 4),
                                         ("the decision: 4 CN + 4 VN + 8 x 813 GND", 8, 2, 8)):
        for r_mm in (5.0, MM_RMAX):
            for i_ret, what in ((I_VIN + I_PACK_T, "continuous 24.1 A"), (I_VIN + I_PACK_P, "peak 32.1 A")):
                for opened in ("none", "one 813", "one Mill-Max"):
                    nm = n_mm - (1 if opened == "one Mill-Max" else 0)
                    n8 = n_813 - (1 if opened == "one 813" else 0)
                    g_mm = r_mm / nm + R_POUR + R_12AWG / n_wires
                    g_813 = R_813_PATH / n8
                    share_813 = g_mm / (g_mm + g_813)
                    i813 = i_ret * share_813 / n8
                    imm = i_ret * (1 - share_813) / nm
                    out.append((design, r_mm, what, opened, share_813, i813, 100 * i813 / PD_MAX, imm, 100 * imm / MM_RATED,
                                {k: a + rise_813(i813) for k, a in AIR.items()}))
    return out


if __name__ == "__main__":
    print("SUPPLY SIDE, VIN_RAW %.2f A" % I_VIN)
    print("%-40s %-22s %6s %6s %7s %s" % ("contacts", "case", "A each", "% rtg", "rise K", "contact C at 51 / 65 C air (limit)"))
    for name, label, i, pct, rs, t, tmax in supply_rows():
        print("%-40s %-22s %6.2f %6.0f %7.1f %5.1f / %5.1f (%.0f)%s" % (name, label, i, pct, rs, t["envelope 51 C"], t["margin 65 C"], tmax,
              "  OVER" if pct > 100 or t["envelope 51 C"] > tmax else ""))
    print()
    print("ECSS-Q-ST-30-11C Rev.2 Table 6-10 screen: 813 at 50 %% is %.2f A and 30 C under 85 C is 55 C (the 51 C inside air "
          "leaves 4 K); Mill-Max at 50 %% is %.1f A and 95 C" % (PD_MAX / 2, MM_RATED / 2))
    print()
    print("RETURN SIDE (ground current A to E: VIN_RAW's %.2f A plus the pack's, both flowing toward board A at once, the "
          "conservative coincidence)" % I_VIN)
    print("%-42s %5s %-18s %-13s %6s %6s %5s %6s %5s %s" % ("design", "MM mO", "return", "open", "813 sh", "813 A", "%", "MM A", "%", "813 at 51/65 C"))
    for d, r, w, o, sh, i8, p8, imm, pmm, t in return_rows():
        print("%-42s %5.0f %-18s %-13s %5.0f%% %6.2f %4.0f%% %6.2f %4.0f%% %5.1f / %5.1f%s" % (d, r, w, o, 100 * sh, i8, p8, imm, pmm,
              t["envelope 51 C"], t["margin 65 C"], "  OVER" if p8 > 100 or pmm > 100 or t["envelope 51 C"] > PD_TMAX else ""))
