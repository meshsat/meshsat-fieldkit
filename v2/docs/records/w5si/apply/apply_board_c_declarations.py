#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si2, 28 September 2026, MESHSAT-1357, layer 9, rule SI-001): declare the signal
class of board C's four nets that no entry of boards/c.json names: EMCLAMP_Y, EMCLAMP_G, EMCON_RD, EMCON_RD_R.
boards/c.json is the integrator's file; this script makes the change and the integrator runs it.

WHAT THE NETS ARE (netlist of the declared phase, read again when this runs; v2/ecad/tools/gen_sch_c.py):
  EMCLAMP_Y    U14 pin 4 (Y) to R48 pin 1. U14 is the SN74LVC1G57DBVR wired as a 2-input NOR of TX_INHIBIT_n and
               EMCON_HW: "the EMCON lamp's gate, high only while both EMCON lines read low".
  EMCLAMP_G    R48 pin 2 (100R from EMCLAMP_Y), Q7 pin 1 (the gate of the lamp's sink, a Si2300DS), R49 pin 1 (10 k
               to GND). Q7 switches D22, the amber EMCON lamp, which is lit or dark and is neither dimmed nor blinked.
  EMCON_RD     U13 pin 4 (Y) to R46 pin 1. U13 is a 74LVC1G17 Schmitt buffer whose input is EMCON_HW: "the panel
               controller's one-way copy of EMCON_HW".
  EMCON_RD_R   R46 pin 2 (1 k from EMCON_RD) to U3 pin 32, the RP2040's GPIO21, which reads the line.
All four follow ONE source: the EMCON locking toggle on the panel (APEM 5636ADKB-2V), moved by a person.

THE DECISION (W5SI2-D1, authority SESSION, ruled_by SESSION (stream w5si2), 28 September 2026, under the owner's
ruling of 21 September 2026 and his standing rule of 26 September 2026): the four nets are LOW_SPEED_OR_DC.
  WHY, from the class's own definition. signal_class.py defines the class by what a net CARRIES: "an enable, an
  inhibit, a sense line, a thermistor, an analogue level, a rail's feedback. There is no edge to speak of." and
  edge_length.py says what SI-001 does with it: "LOW_SPEED_OR_DC is not asked for an edge. It is the class this
  project declares, with a basis per entry, for an enable, a sense line or a level". These four are copies of an
  inhibit: a level that changes when a person moves a locking toggle under a hinged cover. Nothing samples them on
  their edge: EMCLAMP_G is a FET's gate behind 100R with 10 k to ground, and EMCON_RD_R is read as a level by
  firmware behind 1 k. The line they copy, EMCON_HW, is declared LOW_SPEED_OR_DC on boards A, B and C, as are
  TX_INHIBIT_n, board A's *_TXOK and board B's EMCON_SUP (the same kind of buffered copy).
  WHAT THE CLASS DOES NOT SAY, and each entry's basis says it: the DRIVERS ARE FAST. U14's output moves in 0.221 ns
  by its maker's IBIS model (TI SCEM292 Rev. A, [Model] LVC1G57_OUT_33 [Ramp] dV/dt_f max, 2.18/2.21E-10; the
  datasheet SCES414P prints propagation delays only, p. 6). U13's maker publishes no output transition (Diodes
  DS35124 Rev. 8-2, p. 6: tPD only), so its fastest edge is not known and the instantaneous bound stands for it; the
  RP2040 publishes none either (datasheet build 2025-02-20, a slew bit and a drive field). The class rests on the
  CONTENT of the nets, not on a slow driver, and it is not a claim that these nets have no edge.
  IT IS NOT CHOSEN TO PASS THE BOARD, and it does not: board C reads INCONCLUSIVE on SI-001 before and after, held by
  23 layout-bound nets a bound decides. Declared in a non-slow class instead (CLOCKED_DIGITAL) the board reads
  INCONCLUSIVE as well; what each reading is, this draft computes on the tree it runs on and prints.
  HOW TO REVERSE: change `class` in the four entries to CLOCKED_DIGITAL (and their basis), and re-take SI-001. Then
  EMCLAMP_Y and EMCLAMP_G are answered by R48 (the series screen, 10 to 150 ohm), and EMCON_RD and EMCON_RD_R are
  layout-bound and decided by a bound, because R46's 1 k is outside the screen: they would need an `edge_allow`
  entry, or a model of the 74LVC1G17.

WHAT IT CHANGES: four entries are INSERTED into `signal_classes`, directly after the entry `EMCON_HW`, by their exact
names (a glob `EMCLAMP_*` ahead of `*_A` and `*_K` would take EMCLAMP_A and EMCLAMP_K away from their entries).
WHAT IT CHECKS before it writes, on the tree it runs on, and refuses with a sentence when one does not hold:
  * the stream is merged; boards/c.json is written as the repository writes board tables;
  * the four nets are on the netlist with exactly the nodes and parts named above, and no entry names them;
  * the three datasheets cited are held at the sha256/16 cited and say the quoted words on the pages named, and the
    manifest pins U14's model at the sha256/16 cited (the model itself need not be in the tree);
  * after the change every other net of the netlist matches the entry it matched before;
  * the table parses, every other key and every other entry is unchanged and in order, signal_class accepts the four.
A second run is refused ("already applied").

    python3 v2/docs/records/w5si/apply/apply_board_c_declarations.py [--root <tree>] [--dry-run]

Note (integration, set 7): LOW_SPEED_OR_DC is also the class the EMC return rules return_via.py and ref_change.py skip;
for these four nets (a FET gate, a NOR output and a GPIO level) that is the intended reading, as the record's section 5 says.
"""
import os, sys, json, hashlib, fnmatch, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _apply as AP

STAMP = "28 September 2026, stream w5si2, W5SI2-D1"
AFTER = "EMCON_HW"
DOC_57 = ("v2/vendor/ti/ti-sn74lvc1g57.pdf", "078364de617898af")
DOC_17 = ("v2/vendor/diodes/diodes-74lvc1g17.pdf", "029f345a1e7be917")
DOC_RP = ("v2/vendor/rp2040/rpi-rp2040-datasheet.pdf", "be56fbb75ba0ae9e")
MODEL_57 = ("v2/vendor/ti/ibis/sn74lvc1g57.ibs", "7abbc41dad6b027a")
QUOTES = [(DOC_57, 3, "Logic output"), (DOC_57, 6, "Any input to Y (output)"),
          (DOC_17, 1, "standard push-pull output"), (DOC_17, 6, "Switching Characteristics"),
          (DOC_RP, 303, "SLEWFAST: Slew rate control. 1 = Fast, 0 = Slow")]
SOURCE = ("a copy of the EMCON inhibit, a level that moves when a person moves the panel's locking toggle; nothing "
          "samples it on its edge. LOW_SPEED_OR_DC by what the net carries, NOT by a slow driver")
ENTRIES = [
    {"pattern": "EMCLAMP_Y", "class": "LOW_SPEED_OR_DC",
     "basis": "the EMCON lamp gate's output, U14 pin 4 (SN74LVC1G57DBVR as a NOR of TX_INHIBIT_n and EMCON_HW) to R48: " + SOURCE +
              ": U14's output moves in 0.221 ns by its maker's IBIS model (TI SCEM292 Rev. A, LVC1G57_OUT_33 [Ramp] dV/dt_f max; "
              "the datasheet SCES414P prints no output transition, p. 6) (" + STAMP + ")"},
    {"pattern": "EMCLAMP_G", "class": "LOW_SPEED_OR_DC",
     "basis": "the gate of Q7, the EMCON lamp's sink, behind R48 (100R) from U14's output, R49 (10 k) to GND: " + SOURCE +
              ": the driver is U14 through 100R, 0.221 ns at U14's pin by its maker's IBIS model; the lamp is lit or dark, "
              "neither dimmed nor blinked (" + STAMP + ")"},
    {"pattern": "EMCON_RD", "class": "LOW_SPEED_OR_DC",
     "basis": "the panel controller's one-way copy of EMCON_HW, U13 pin 4 (74LVC1G17 Schmitt buffer) to R46: " + SOURCE +
              ": U13's maker publishes no output transition (Diodes DS35124 Rev. 8-2, p. 6, propagation delay only), so its "
              "fastest edge is not known (" + STAMP + ")"},
    {"pattern": "EMCON_RD_R", "class": "LOW_SPEED_OR_DC",
     "basis": "the same copy behind R46 (1 k) at the RP2040's GPIO21, which reads it as a level and is never an output "
              "(HW-FW-CONTRACT FW-C07): " + SOURCE + ": neither U13's maker nor the RP2040's publishes an output transition, so "
              "the fastest edge is not known (" + STAMP + ")"},
]
# the nets as this draft read them: {net: {(reference, pin)}}, and the parts by the start of their value field
NODES = {"EMCLAMP_Y": {("U14", "4"), ("R48", "1")}, "EMCLAMP_G": {("Q7", "1"), ("R48", "2"), ("R49", "1")},
         "EMCON_RD": {("U13", "4"), ("R46", "1")}, "EMCON_RD_R": {("R46", "2"), ("U3", "32")}}
PARTS = {"U14": "SN74LVC1G57DBVR", "U13": "74LVC1G17", "U3": "RP2040", "Q7": "Si2300DS", "R48": "100R", "R49": "10k", "R46": "1k"}


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def page_says(path, page, words):
    try:
        r = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", path, "-"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0: return None
    return " ".join(words.split()) in " ".join(r.stdout.split())


def first_match(table, net):
    for i, e in enumerate(table):
        if fnmatch.fnmatchcase(net, e.get("pattern", "")) or fnmatch.fnmatchcase("/" + net, e.get("pattern", "")): return i
    return None


def reading(E, net, letter, table, repo):
    """SI-001 on board C in memory with `table` as its signal classes; nothing is written."""
    import boardtable, signal_class
    ov, od = boardtable.value, signal_class.declarations
    boardtable.value = lambda l, key, default=None: table.get(key, default) if l == letter else ov(l, key, default)
    signal_class.declarations = lambda l: ([(e["pattern"], e["class"], e["basis"]) for e in table.get("signal_classes", [])], []) \
        if l == letter else od(l)
    try: r = E.schematic_table(net, letter, repo=repo)
    finally: boardtable.value, signal_class.declarations = ov, od
    c, ms = r["counts"], r["inputs"]["model_state"]
    return ("%s: %d signal nets, %d slow, %d by a published figure, %d by a bound, %d undecided (%d no declaration, %d waiting on "
            "a model that is not in the tree, %d other), %d answered, %d layout-bound of which %d a bound decides; models %s "
            "(%d asked, %d absent)" % (E.schematic_result(r), c["signal_nets"], c["low_speed_nets"], c["maker_edge_nets"],
                                       c["bound_edge_nets"], c["undecided_nets"], c["undecided_no_declaration_nets"],
                                       c["undecided_model_absent_nets"], c["undecided_other_nets"], c["answered_nets"],
                                       c["layout_bound_nets"], c["bound_decided_nets"], ms["state"], ms["asked"], ms["absent"]))


def main():
    root = AP.root_of(HERE)
    AP.need_stream(root)
    tools = AP.tools_on_path(root)
    ecad = os.path.dirname(tools)
    target = os.path.join(tools, "boards", "c.json")
    AP.need_files(root, ["v2/ecad/tools/boards/c.json", DOC_57[0], DOC_17[0], DOC_RP[0]], "this draft reads it")
    text = open(target, encoding="utf-8").read()
    old = json.loads(text)
    AP.need(json.dumps(old, indent=1, ensure_ascii=False) + "\n" == text,
            "boards/c.json is not written as the repository writes board tables (indent 1, a final newline), so rewriting it "
            "would change more than four entries")
    sc = old.get("signal_classes")
    AP.need(isinstance(sc, list) and sc, "boards/c.json carries no signal_classes list")
    names = [e["pattern"] for e in ENTRIES]
    have = [e.get("pattern") for e in sc if e.get("pattern") in names]
    if have:
        same = all(any(e == x for x in sc) for e in ENTRIES)
        AP.need(False, "already applied" if same and len(have) == len(ENTRIES) else
                "boards/c.json already carries an entry for %s, which this draft did not write: re-read it" % ", ".join(have))
    at = [i for i, e in enumerate(sc) if e.get("pattern") == AFTER]
    AP.need(len(at) == 1, "%d entries carry the pattern %s, after which the four are inserted; expected one" % (len(at), AFTER))
    AP.need(sc[at[0]].get("class") == "LOW_SPEED_OR_DC", "the entry %s is no longer LOW_SPEED_OR_DC (it reads %s): the four nets copy "
            "that line and this draft's reason rests on its class; re-read the decision" % (AFTER, sc[at[0]].get("class")))

    # the netlist, as the tree holds it
    import phase_artefacts as PA, edge_length as E, signal_class as SC, ibis_manifest as IM
    net = PA.netlist("c", ecad)
    AP.need(net and os.path.exists(net), "board C's declared phase has no netlist in this tree (%s)" % net)
    nets, values = E.read_netlist(net)
    for n, want in NODES.items():
        AP.need(n in nets, "board C's netlist %s has no net %s: the net this draft declares is gone, re-read the board" % (os.path.relpath(net, root), n))
        got = {(r, p) for r, p, _f, _t in nets[n]["nodes"]}
        AP.need(got == want, "the net %s is not as this draft read it (it carries %s, the draft read %s): re-read what drives it "
                "before declaring its class" % (n, sorted(got), sorted(want)))
    for ref, part in PARTS.items():
        AP.need(str(values.get(ref, "")).startswith(part), "%s is not the part this draft read (%r, the draft read %s...): the basis "
                "names its maker's document, re-read it" % (ref, str(values.get(ref, ""))[:40], part))
    for n in names:
        AP.need(first_match(sc, n) is None, "the net %s already matches the entry %r: it is declared, and this draft would shadow "
                "or be shadowed by it" % (n, sc[first_match(sc, n)]["pattern"] if first_match(sc, n) is not None else ""))

    # the documents the basis cites
    for (doc, sha), page, words in QUOTES:
        p = os.path.join(root, doc)
        AP.need(sha16(p) == sha, "%s is not the file this draft read (sha256/16 %s held, %s read): re-read the pages it cites" % (doc, sha16(p), sha))
        says = page_says(p, page, words)
        AP.need(says is not None, "page %d of %s could not be read (pdftotext), so the words this draft quotes are not checked" % (page, doc))
        AP.need(says, "page %d of %s does not say %r" % (page, doc, words))
    man = IM.load(root)
    row = IM.pin(man, MODEL_57[0])
    AP.need(row is not None and row["sha256"].startswith(MODEL_57[1]),
            "the manifest %s does not pin %s at sha256/16 %s, the model the basis takes 0.221 ns from" % (man["path"], MODEL_57[0], MODEL_57[1]))
    rates, refusals = E.load_rates(os.path.join(tools, "pcb_edge_rates.yaml"))
    fam = [f for f in rates["families"] if f["id"] == "TI-SN74LVC1G57"]
    AP.need(len(fam) == 1 and abs(float(fam[0]["edge_ns"]) - 0.221) < 1e-9 and fam[0]["ibis"]["file"] == MODEL_57[0],
            "pcb_edge_rates.yaml's record TI-SN74LVC1G57 does not state 0.221 ns from %s, the figure the basis quotes" % MODEL_57[0])

    # the new table
    new = json.loads(text)
    new["signal_classes"][at[0] + 1:at[0] + 1] = [dict(e) for e in ENTRIES]
    out = json.dumps(new, indent=1, ensure_ascii=False) + "\n"
    assert out != text, "the new text does not differ from the old"
    back = json.loads(out)
    assert list(back) == list(old), "a top-level key was added, lost or moved"
    for k in old:
        if k != "signal_classes": assert back[k] == old[k], "the key %s changed and was not to" % k
    assert back["signal_classes"] == sc[:at[0] + 1] + ENTRIES + sc[at[0] + 1:], "signal_classes is not the old list with the four inserted"
    assert len(back["signal_classes"]) == len(sc) + len(ENTRIES)
    moved = []
    for n in sorted(nets):
        a, b = first_match(sc, n), first_match(back["signal_classes"], n)
        pa = sc[a]["pattern"] if a is not None else None
        pb = back["signal_classes"][b]["pattern"] if b is not None else None
        if n in names: assert pb == n, "the net %s does not match its own entry (it matches %r)" % (n, pb)
        elif pa != pb: moved.append("%s (%r, now %r)" % (n, pa, pb))
    assert not moved, "nets other than the four change the entry they match: %s" % ", ".join(moved)
    for e in ENTRIES:
        assert e["class"] in SC.CLASSES and e["class"] != "UNKNOWN" and len(e["basis"].strip()) >= 12, e["pattern"]
        assert chr(0x2014) not in e["basis"] and chr(0x2013) not in e["basis"], "a dash the house style forbids in %s" % e["pattern"]

    # what SI-001 reads on board C, in memory, on this tree: before, after, and in the class the decision did not take
    alt = json.loads(out)
    for e in alt["signal_classes"]:
        if e["pattern"] in names: e["class"] = "CLOCKED_DIGITAL"
    msg = ["boards/c.json: signal_classes %d entries (%d before): EMCLAMP_Y, EMCLAMP_G, EMCON_RD and EMCON_RD_R declared "
           "LOW_SPEED_OR_DC after %s (decision W5SI2-D1, authority SESSION)" % (len(back["signal_classes"]), len(sc), AFTER),
           "  SI-001 on board C, netlist sha256/16 %s, taken in memory on this tree, nothing written:" % sha16(net),
           "    before:                         %s" % reading(E, net, "c", old, root),
           "    after (LOW_SPEED_OR_DC):        %s" % reading(E, net, "c", back, root),
           "    had they been CLOCKED_DIGITAL:  %s" % reading(E, net, "c", alt, root),
           "  OWED after this draft: re-take SI-001 on board C with retake_gate.sh (boards/c.json is a configuration input of every "
           "reading that declares it: those readings go stale with this edit), and board C's other gates that read the table."]
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: " + "\n".join(msg)); return 0
    AP.write(target, out)
    assert json.loads(open(target, encoding="utf-8").read()) == back, "the file read back is not the table that was written"
    print("\n".join(msg))
    return 0


if __name__ == "__main__":
    AP.run(main)
