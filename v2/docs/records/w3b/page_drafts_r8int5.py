"""r8int5, stream w3b: drafts/w3b/page-drafts.md applied (sections 1, 2 and 4; section 3 is 'nothing'; section 5 is for
the tools owner and stays an open item), plus pcb_rules_coverage.yaml's PWR-001 sentence for board B and the SOURCES.yaml
entry of drafts/w3b/sources-entries.yaml with its document filed at v2/vendor/slkor/ and its sources.txt line. The EQ-19
text says VBAT_RTC (was VBAT), as the independent check asked, and names the open items by the ids the registry script
took (argv: the three S ids). Run from the worktree root; idempotent by marker."""
import os, shutil, sys, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
K = os.path.dirname(os.path.abspath(__file__))
SA, SB, SC = sys.argv[1:4]
DEC = 'v2/docs/feasibility/DECOUPLING.md'
EQ = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
PB3 = 'v2/ecad/tools/gen_pcb_b3.py'
COV = 'v2/ecad/tools/pcb_rules_coverage.yaml'
SRC = 'v2/vendor/SOURCES.yaml'
STX = 'v2/vendor/sources.txt'

once(DEC, " ".join("""Open: the classes. The round's author read `intent.py` as unable to carry them and filed the class of every declared
capacitor in `v2/docs/records/r8b/decoupling-classes-b.json` (274 entries, intent `5af19ea259fba27b`); boards A, C, D, E
and P now write `class` and `basis` into their intent from their own generators (T5's keys), and board B's generator
does not yet, so B's classes stay in that record until it does. The seats wait for board B's next placement""".split("\n")),
" ".join("""The classes: board B's generator writes `class` and `basis` (with `value_floor` and `esr_max` on class L, `same_side` on
class R) onto every declaration since stream w3b (27 September 2026, integrated in `fnd/r8int5`), T5's keys as boards A, C,
D, E and P write them, and an entry without a class stops it. They are the round's map
(`v2/docs/records/r8b/decoupling-classes-b.json`) with four corrections, C65, C66, C508 and C509, which serve the
SN74LVC1G08 gates U501 to U504 (class D, TI SCES217AA, where the map carried another part's clause and, for C508 and C509,
class R), and three new class D entries, C72 to C74 at the LG290P's V_BCKP (W3B-F2); 277 entries
(`v2/docs/records/w3b/evidence/`). The seats wait for board B's next placement""".split("\n")), marker="since stream w3b (27 September 2026, integrated in `fnd/r8int5`)")

once(EQ, "B (28 supplies undeclared, 26 undecided)",
     "B (28 supplies undeclared, 26 undecided; declared since stream w3b, 27 September 2026: 17 rails and 40 nodes, each from its "
     "maker's sheet, and PWR-001 read PASS of 59 in the stream's scratch on the candidate netlist, awaiting the consolidated re-take)",
     marker="declared since stream w3b, 27 September 2026: 17 rails and 40 nodes")
once(EQ, "PWR-001 on A's regenerated netlist reads PASS of 35 (34 declared rails, 0 undecided). B, D and E stay open. |",
     "PWR-001 on A's regenerated netlist reads PASS of 35 (34 declared rails, 0 undecided). **Board B (stream w3b):** every one of "
     "the 28 undeclared and 26 undecided nets declared, a rail where it carries a current (VBAT_RTC, the coin-cell net renamed from "
     "VBAT by W3B-R1, the three flashing VBUS, the SIM supplies, the GNSS antenna feed, the PoE port's feed and return conductors) "
     "and a node where it is one part's own supply or a signal (the fourteen bootstraps, the four CP2102N regulator outputs, the "
     "three STM32H743 VCAP, the resets, nRPIBOOT, the PWR-LED feeds, the RF pads, the PoE control lines); one more net, GNSS_RF_IN, "
     "became undecided once the antenna feed was declared and is declared too; PWR-001 read PASS of 59 in the stream's scratch. "
     "Reading the TPS23861 and LG290P sheets for it found W3B-F1 and W3B-F2 (drawn) and %s to %s (open). D and E stay open. |" % (SA, SC),
     marker="**Board B (stream w3b):**")

once(PB3, '("GND", "PWR"), ("*_SW", "PWR"), ("VBAT", "PWR")]', '("GND", "PWR"), ("*_SW", "PWR"), ("VBAT_RTC", "PWR")]',
     marker='("VBAT_RTC", "PWR")]')

once(COV, """     source and J_MON as its load (board A's writer). SET 5, BOARD A (stream w3a""",
"""     source and J_MON as its load (board A's writer). SET 5, BOARD B (stream w3b, integrated in fnd/r8int5, 27 September
     2026): gen_sch_b.py declares every net named above for B (17 rails and 40 nodes, VBAT renamed VBAT_RTC by W3B-R1, and
     GNSS_RF_IN, undecided once the antenna feed was declared); on B's regenerated netlist the stream read PASS of 59 in its
     scratch, which the consolidated re-take takes in the tree; GNSS_ANT, GNSS_BIAS, GNSS_VDD_RF and the three SIM supplies
     leave SI-001's signal set as declared rails (888 to 882 signal nets), which is no closure of SI-001. SET 5, BOARD A (stream w3a""",
     marker="SET 5, BOARD B (stream w3b")

os.makedirs('v2/vendor/slkor', exist_ok=True)
pdf = 'v2/vendor/slkor/slkor-bc857b-c556165.pdf'
src_pdf = os.path.join(K, 'vendor', 'slkor', 'slkor-bc857b-c556165.pdf')
assert hashlib.sha256(open(src_pdf, 'rb').read()).hexdigest() == 'b27e6044426e3c6009ed18c960878c7838cabacc4453fdb1ec761dfda4e1323d'
if not os.path.exists(pdf): shutil.copyfile(src_pdf, pdf)
ent = open(os.path.join(K, 'sources-entries.yaml')).read().split('\n')
ent = '\n'.join(l for l in ent if not l.startswith('#')).strip('\n') + '\n'
ent = ent.replace('adopted_in: "board B\'s generator since B16; the maker\'s sheet filed by stream w3b, 27 September 2026"',
                  'adopted_in: "board B\'s generator since B16; the maker\'s sheet filed by stream w3b, 27 September 2026 (integrated in fnd/r8int5)"')
once(SRC, "\n  - id: stage-current-shunts\n", "\n" + ent + "\n  - id: stage-current-shunts\n", marker="id: pnp-led-buffer-bc857b")
t = open(STX).read()
if 'slkor/slkor-bc857b-c556165.pdf' not in t:
    t = t.rstrip('\n') + '\nslkor/slkor-bc857b-c556165.pdf   # https://datasheet.lcsc.com/datasheet/pdf/171c362deabfedc4642f786eeb3a3121.pdf?productCode=C556165 (LCSC\'s copy of the Slkor BC856-BC858 sheet; Nexperia\'s BC857_SER.pdf answered a bot challenge and Wayback holds no copy), fetched 2026-09-27T10:17Z by stream w3b, sha256 b27e6044426e3c60\n'
    open(STX, 'w').write(t)
import yaml; yaml.safe_load(open(SRC)); yaml.safe_load(open(COV))
print("page_drafts_r8int5 (w3b): applied")
