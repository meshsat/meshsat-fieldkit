#!/usr/bin/env python3
"""The two stackup rows the owner's decisions 28 and 43 authorise, held to the fabricator's own tables
(MESHSAT-1357, 26 September 2026).

`stackup_write.STACKS` is the record every stackup rule compares a board with (STK-001's gate reads it), and it is
on the never-auto floor. On 25 September 2026 the owner ruled board P to four layers at 2 oz outer copper
(decision 28) and board B to one measured route on eight layers (decision 43, an experimental run). The
fabricator's rows for both were read that night and transcribed into
`v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md`. These tests read that transcription's own layer tables,
so a row that drifts from what the fabricator publishes fails here, and so does a transcription edited without
its row.

What they state are properties, not history: a row equals its transcription, a row carries a standing owner
ruling, and a row survives the write and read path the chains use.
"""
import os, re, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import stackup_write as W
import stackup_read as SR

V2 = os.path.dirname(os.path.dirname(TOOLS))
DOC = os.path.join(V2, "vendor", "fabricator", "jlcpcb-stackups-2026-09-25.md")
DECISIONS = os.path.join(TOOLS, "pcb_decisions.yaml")
# The rows added under an owner ruling, and the decision each one stands on.
AUTHORISED = {"JLC04162H-7628": 28, "JLC08161H-2116": 43}
TOL = 1e-6


def _section(code):
    """The text of the transcription's section whose heading names `code`."""
    txt = open(DOC, encoding="utf-8").read()
    heads = list(re.finditer(r"^## .*$", txt, re.M))
    for i, h in enumerate(heads):
        if code in h.group(0):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
            return txt[h.start():end]
    raise AssertionError("the transcription has no section headed with %s" % code)


def _table(code):
    """The layer table of that section as [('cu', t, None) | ('di', t, dk)], in the fabricator's order, and the
    layer sum the section states in its own words."""
    sec = _section(code)
    rows = []
    for line in sec.splitlines():
        if not line.startswith("|"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "layer" or set(cells[0]) <= set("-"): continue
        t = float(cells[2])
        # by the LAYER column: the fabricator's core names carry the word copper ("1.1mm H/HOZ with copper",
        # "0.3mm H/HOZ without copper"), so the material column cannot tell a core from a copper layer
        if cells[0] in ("core", "prepreg"):
            rows.append(("di", t, float(cells[3])))
        else:
            rows.append(("cu", t, None))
    m = re.search(r"Layer sum ([0-9.]+) mm", sec)
    assert m, "the %s section states no layer sum" % code
    return rows, float(m.group(1))


def _gaps(seq):
    """Copper thicknesses and, per copper gap, the dielectrics between: ([t], [[(t, dk)]])."""
    cu, gaps, cur = [], [], None
    for kind, t, dk in seq:
        if kind == "cu":
            if cur is not None: gaps.append(cur)
            cu.append(t); cur = []
        else:
            assert cur is not None, "a dielectric before the first copper layer"
            cur.append((t, dk))
    return cu, gaps


def _row(code):
    return [("cu", it[1], None) if len(it) == 2 else ("di", it[2], it[3]) for it in W.STACKS[code]]


def t_each_authorised_row_equals_its_fabricator_transcription_layer_by_layer():
    """THE LAYER SUM, and every layer under it. The row's total is what `stackup_write` prints and what a board's
    thickness is judged by, so it must be the transcription's own sum, and the transcription's stated sum must be
    its own table's. Layer by layer: the same copper thicknesses in the same order and, in every gap between two
    copper layers, the same dielectric thickness and constant. Two plies of one material in one gap may be one
    KiCad dielectric (the eight-layer row's 2 x 1080), and they compare as one: the same distance and the same
    constant, which is all the impedance tools read between two copper layers."""
    bad = []
    for code in AUTHORISED:
        assert code in W.STACKS, "decision %d's row %s is not in STACKS" % (AUTHORISED[code], code)
        table, stated = _table(code)
        tsum = round(sum(t for _k, t, _d in table), 4)
        if abs(tsum - stated) > TOL:
            bad.append("%s: the transcription's table sums to %.4f and its text says %.4f" % (code, tsum, stated))
        if abs(W.total(code) - stated) > TOL:
            bad.append("%s: the row sums to %.4f and the transcription to %.4f" % (code, W.total(code), stated))
        tcu, tgaps = _gaps(table)
        rcu, rgaps = _gaps(_row(code))
        if len(tcu) != len(rcu):
            bad.append("%s: %d copper layers in the row, %d in the transcription" % (code, len(rcu), len(tcu))); continue
        for i, (a, b) in enumerate(zip(rcu, tcu)):
            if abs(a - b) > TOL: bad.append("%s copper %d: %.4f in the row, %.4f transcribed" % (code, i + 1, a, b))
        for i, (rg, tg) in enumerate(zip(rgaps, tgaps), 1):
            rt, tt = sum(t for t, _ in rg), sum(t for t, _ in tg)
            if abs(rt - tt) > TOL:
                bad.append("%s gap %d: %.4f mm of dielectric in the row, %.4f transcribed" % (code, i, rt, tt))
            if {d for _, d in rg} != {d for _, d in tg}:
                bad.append("%s gap %d: Dk %s in the row, %s transcribed" % (code, i, sorted({d for _, d in rg}), sorted({d for _, d in tg})))
            rw = sum(t * d for t, d in rg) / rt if rt else 0
            tw = sum(t * d for t, d in tg) / tt if tt else 0
            if abs(rw - tw) > 1e-9:
                bad.append("%s gap %d: thickness-weighted Dk %.4f in the row, %.4f transcribed" % (code, i, rw, tw))
    assert not bad, "\n".join(bad)


def t_each_authorised_row_carries_a_standing_owner_ruling():
    """STACKS is on the never-auto floor, so a row in it is an owner's decision with its authority beside it. The
    comment above each row names the decision, and the decisions register must still hold that decision as ruled
    by the owner: a row whose ruling has been reopened has lost its authority and needs a new one or removal."""
    import rules_lib as R
    src = open(os.path.join(TOOLS, "stackup_write.py"), encoding="utf-8").read().splitlines()
    with open(DECISIONS, encoding="utf-8") as fh:
        ds = {d.get("n"): d for d in ((R._yaml().safe_load(fh) or {}).get("decisions") or [])}
    bad = []
    for code, n in AUTHORISED.items():
        at = [i for i, l in enumerate(src) if l.strip().startswith('"%s": [' % code)]
        if len(at) != 1: bad.append("%s: %d rows in the source" % (code, len(at))); continue
        j = at[0] - 1; block = []
        while j >= 0 and src[j].strip().startswith("#"):
            block.append(src[j]); j -= 1
        text = " ".join(block)
        for need in ("AUTHORITY", "OWNER RULING", "decision %d" % n, "SOURCE", "jlcpcb-stackups-2026-09-25.md"):
            if need not in text: bad.append("%s: the comment above the row does not say %r" % (code, need))
        d = ds.get(n) or {}
        if str(d.get("status")) != "ruled" or str(d.get("authority")) != "OWNER":
            bad.append("%s: decision %d reads status %r, authority %r in the register, not a standing owner ruling"
                       % (code, n, d.get("status"), d.get("authority")))
    assert not bad, "\n".join(bad)


FIXTURE = """(kicad_pcb (version 20241229) (generator "pcbnew")
  (layers
%s
    (25 "Edge.Cuts" user)
  )
  (setup
    (pad_to_mask_clearance 0)
  )
)
"""


def _fixture(ncu):
    names = ["F.Cu"] + ["In%d.Cu" % i for i in range(1, ncu - 1)] + ["B.Cu"]
    return FIXTURE % "\n".join('    (%d "%s" signal)' % (i * 2, n) for i, n in enumerate(names))


def t_each_authorised_row_survives_the_write_and_read_path():
    """The rows are only useful if a chain can write them into a board and every reader gets them back. Each row is
    written by name into a board of its own copper count and read back by `stackup_read` (the gate's reader) and
    by `impedance_check.read_stackup` (the impedance and current tools' reader). Board P's row must read back as
    2 oz outer copper, which is what decision 28 and ruling 7 are about."""
    from impedance_check import read_stackup
    for code in AUTHORISED:
        ncu = len([it for it in W.STACKS[code] if len(it) == 2])
        fd, p = tempfile.mkstemp(suffix=".kicad_pcb"); os.write(fd, _fixture(ncu).encode()); os.close(fd)
        try:
            assert W.write(p, code) == code
            cu = SR.copper_layers(p); di = SR.dielectrics(p)
            want_cu = [(it[0], it[1]) for it in W.STACKS[code] if len(it) == 2]
            want_di = [(it[1], it[2], it[3]) for it in W.STACKS[code] if len(it) == 4]
            assert [(c["name"], c["thickness"]) for c in cu] == want_cu, "%s copper read back as %s" % (code, cu)
            assert [(d["material"], d["thickness"], d["epsilon_r"]) for d in di] == want_di, "%s dielectrics read back as %s" % (code, di)
            st = read_stackup(p)
            assert round(sum(t for _n, _k, t, _e in st), 4) == W.total(code), "%s: impedance_check reads a different total" % code
            if code == "JLC04162H-7628":
                assert SR.outer_copper_oz(p) == 2.0, "board P's row does not read back as 2 oz outer copper"
        finally:
            os.unlink(p)
