"""verify c5's contradictions and hc5 review 2's minor items that are wording, fixed on the r8int4 tree after fnd/hc5's
scripts. Each edit asserts its old text. Run from the worktree root."""
def edit(p, pairs):
    t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (p, t.count(a), a[:90]); assert a != b; t = t.replace(a, b)
    assert chr(0x2014) not in t; open(p, 'w').write(t)
edit('v2/docs/ARCHITECTURE.md', [
    # section 2, Messaging over 5G (verify c5, third new contradiction)
    ("ANT3's site on A and clamp on E are in no generator (D-07).",
     "ANT3's site on A is in no generator, and board E's clamp cavity at X 46 is drawn since `45f6d83f` (D-07)."),
    # section 13, W4-F10 (hc5's hand-off to the integrator)
    ("the condition read on paper (section 9.2); wiring on A and E owed |",
     "the condition read on paper (section 9.2); board E's clamp cavity at X 46 drawn since `45f6d83f`; board A's site at X +46 and its wiring owed |"),
])
Y = 'v2/ecad/tools/pcb_interfaces.yaml'
edit(Y, [
    # IF-AE-RF, round 8 staleness (hc5's hand-off; board E's clamp bar since 45f6d83f)
    ('        - {board: e, what: "mechanical float clamps only; no RF net on E", src: "v2/ecad/tools/gen_pcb_e.py:16-30"}',
     '        - {board: e, what: "the float clamp bar, one bar with twelve cavities, D-07\'s at X 46 among them (since 45f6d83f); no RF net on E", src: "v2/ecad/tools/gen_pcb_e.py:44-48, 110-131"}'),
    ('''      nests: "the float_clamp.py nest is 16 mm along X and the sites are 14 mm apart (12 mm from IRIDIUM to LORA): neighbouring
        nests overlap and the LORA nest reaches the rod keep-out (A09, recorded in gen_pcb_e.py:22-29); R4E-07 proposes one
        clamp bar for all sites, owed"''',
     '''      nests: "the separate float_clamp.py nests (16 mm along X at a 14 mm pitch, 12 mm from IRIDIUM to LORA) overlapped and
        the LORA nest reached the rod keep-out (A09); since 45f6d83f one clamp bar with twelve cavities and M3 holes at
        mid-pitch replaces them (R4E-07, gen_pcb_e.py:44-48 and 110-131)"'''),
    ('''        picked); the board half is board A's site at X +46 and a board E clamp there, neither in a generator yet. The three''',
     '''        picked); the board half is board A's site at X +46, in no generator yet, and board E's cavity there, drawn since
        45f6d83f. The three'''),
    ('      judged_by: "check_pcb_e.py (the clamp sites against board A\'s RF_X); nothing judges the twelfth site"',
     '      judged_by: "check_pcb_e.py (the clamp sites against board A\'s RF_X, and the cavity at X 46 required on E, check_pcb_e.py:75-84); nothing judges board A\'s twelfth site, which is in no generator"'),
    # IF-E-WATER: a 1 M over 1 M divider never exceeds half the rail (review 2)
    ('''        1.65 V and above as the water's resistance falls below 1 M (INFERRED on the netlist); read on ADC0, 0 to 3.3 V"''',
     '''        1.65 V as the water's resistance falls (about 1.1 V at 1 M of water and 1.65 V at none; it cannot exceed 1.65 V,
        INFERRED on the netlist); read on ADC0, 0 to 3.3 V"'''),
    # IF-DA-VHF: K1 is also board D's T/R relay (review 2)
    ("keyed at most 60 s (K1);", "keyed at most 60 s (key-down rule K1);"),
    # IF-MON: the touch exists only while the panel holds D8_EN on (review 2)
    ('''        arrives (manual: auto power-on); the touch enumerates when board D's hub is up (D's 5 V comes from A's eFuse U23 with
        the device rail) and is shared after bank 3's owner boots (FW-B19)"''',
     '''        arrives (manual: auto power-on); the touch enumerates when board D's hub is up, which is only while the panel holds
        D8_EN on (D's 5 V comes from A's eFuse U23, enabled by D8_EN from U27, held off by R113 at power-up) and is shared
        after bank 3's owner boots (FW-B19)"'''),
    # IF-EXT-DC: owner ruling D-16 (review 2)
    ('''        40 V (R23 6.65 k)); solar: a 36-cell 12 V class panel, about 22 V open circuit, 100 W (J_SOLAR's value text)"''',
     '''        40 V (R23 6.65 k)); no vehicle surge claim: the entry is recorded as not qualified and is not for 24 V military
        vehicle buses (owner ruling D-16); solar: a 36-cell 12 V class panel, about 22 V open circuit, 100 W (J_SOLAR's value
        text)"'''),
])
# IF-E-SENSORS judged_by: check_contracts section 16 checks R48's topology (review 2)
t = open(Y).read()
i = t.index('\n    IF-E-SENSORS:\n'); j = t.index('      judged_by: "none"\n', i)
assert t.find('\n    IF-', i + 5) > j
t = t[:j] + '      judged_by: "check_contracts.py section 16, for topology only: R48, the Geiger pulse\'s series resistor, has a real pin on both of its nets; nothing judges a level"\n' + t[j + len('      judged_by: "none"\n'):]
open(Y, 'w').write(t)
H = 'v2/docs/HW-FW-CONTRACT.md'
t = open(H).read()
row = [l for l in t.split('\n') if l.startswith('| V-B19 |')]
assert len(row) == 1; row = row[0]
t = t.replace(row + '\n', '', 1)
anchor = '| V-B17 | FW-B17 | holdover drift over 24 h with GNSS off |\n'
assert t.count(anchor) == 1; t = t.replace(anchor, anchor + row + '\n')
open(H, 'w').write(t)
edit(H, [
    ("| FW-A08 | three PCA9555 with output registers FFh at power-on (TI SCPS131J): `A:U27`, `A:U28`, `B:U6` (and C's U1, U2, D's U16) |",
     "| FW-A08 | six PCA9555 with output registers FFh at power-on (TI SCPS131J): `A:U27`, `A:U28`, `B:U6`, and C's U1, U2 and D's U16 |"),
    ("| HF-F06 | minor | Board D's spare hub port `J_USB3`,", "| HF-F06 | major (raised from minor at integration, after hc5's second review: a fault on the touch lead removes board D, whose APRS path is a prototype 1 core function under D-01) | Board D's spare hub port `J_USB3`,"),
    ("| board D's author: a current-limited switch on J_USB3's VBUS (the TPS2065C, held as `ti-tps2065c-slvsau6i.pdf`, is the kit's existing part for this) and the budget line at the touch's measured draw (V-B19) |",
     "| board D's author, before board D's layout entry (open item S-61): a current-limited switch on J_USB3's VBUS (the TPS2065C, held as `ti-tps2065c-slvsau6i.pdf`, is the kit's existing part for this) and the budget line at the touch's measured draw (V-B19) |"),
])
print("edit_c5_wording: done")
