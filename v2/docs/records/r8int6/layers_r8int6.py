#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): set 6 on the layer lines, under the rules main
holds at the integration's base (the definition restructure at a9f212c7 and layer 3's re-baseline at a54b793b).

Layer 1. Since the definition restructure the brief is governed by the H2 review's rule (a circuit correction updates
DEFINITION-STATUS.md and the records it names, not the baseline), and EQ-27 option (c)'s re-read continues for the four
public pages that still state design state (README.md, v2/README.md, v2/BUILD.md, V2-SPEC.md): "a stale line there is
corrected in that page and recorded on this line". Set 6 touches EMCON (streams w4b and w4c) and feasibility records
(FEA-002's readings are rebound), so the four pages were re-read. One line is stale: V2-SPEC.md line 24 says the
RockBLOCK 9704's ENABLE is held by a firmware-driven expander with the hardware ENABLE owed; stream w4b drew it (U536).
This corrects the clause in the page, adds correction 31, and rebinds the four readings bound to V2-SPEC.md (REQ-005,
CFL-016, CFL-010 and CFL-013) with notes that start with the path.
Layer 2. CONOPS is not edited (the same rule): HOT-R1's current state is REQ-077's and EMCON's is EMCON.md section 0a
and 4c, the sources DEFINITION-STATUS.md names; the line says so.
Layer 3. The requirements baseline reopens the layer if a record's statement, acceptance, applicability, allocation,
verification or release effect changes; this asserts, against the base commit, that none did, and says what did.
FEA-002's statement still says the RockBLOCK's ENABLE is held by firmware; a statement changes only under its own
review, so it is carried as one open SESSION item at the next free S number.
Idempotent by marker. Usage: layers_r8int6.py <repo root> <base commit>"""
import json, os, re, subprocess, sys, textwrap
import yaml

T = sys.argv[1]; BASE = sys.argv[2]
sys.path.insert(0, os.path.join(T, "v2/docs/records/r8int5"))
import edlib
REG = os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml")
LS = os.path.join(T, "v2/docs/handover/LAYER-STATUS.md")
VS = "v2/docs/V2-SPEC.md"
s = open(REG, encoding="utf-8").read()
recs = [r for v in yaml.safe_load(s).values() if isinstance(v, list) for r in v if isinstance(r, dict) and "id" in r]


def find(prefix, field, start):
    hits = [r["id"] for r in recs if r["id"].startswith(prefix + "-") and " ".join(str(r.get(field, "")).split()).startswith(start)]
    assert len(hits) == 1, (prefix, start, hits)
    return hits[0]


D1 = find("SC", "why", "W4B-D1 (stream w4b)"); D3 = find("SC", "why", "W4B-D3 (stream w4b)")
HOT = json.load(open(os.path.join(T, "v2/docs/records/w4ae/ids.json")))["SC_HOT_R1"]

# ---- layer 1: V2-SPEC.md line 24 and correction 31
v = open(os.path.join(T, VS), encoding="utf-8").read()
OLD24 = ("and the RockBLOCK 9704 (with its supply cut it runs on its own supercapacitors, about 16 J, with its ENABLE held by "
         "a firmware-driven expander; the ENABLE forced low by the EMCON hardware is owed, section 4.4)")
NEW24 = ("and the RockBLOCK 9704 (with its supply cut it runs on its own supercapacitors, about 16 J; its ENABLE is held low "
         "by the EMCON hardware since board B's stream w4b, and what the Iridium module does when ENABLE falls is stated in "
         "no held document, sections 4.4 and 4c; correction 31)")
if NEW24 not in v:
    assert v.count(OLD24) == 1, "V2-SPEC.md line 24's RockBLOCK clause moved"
    v = v.replace(OLD24, NEW24)
    last = v.rstrip("\n").split("\n")[-1]
    assert last.startswith("    ") and "30. **The layer 1 release check" in v, "V2-SPEC.md's corrections end moved"
    v = v.rstrip("\n") + "\n" + textwrap.fill(
        "31. **Set 6 (line 24).** Session reading of board B's stream w4b as integrated at r8int6 (27 September 2026, "
        "MESHSAT-1357; %s and %s). The RockBLOCK 9704's ENABLE is `EMCON_HW` AND the panel's request in `U536`, held "
        "low by `R527` with the gate unpowered, so the ENABLE forced low by the EMCON hardware is drawn; the row stays "
        "open locally, because what the Iridium module does when ENABLE falls, and how long it runs on its own capacitors, "
        "is stated in no held document (`feasibility/EMCON.md` sections 4.4 and 4c). Each card buck's enable is driven "
        "from its slot's own 5 V (`U116`, `U216`, `U316`). The counts do not change: 15 of 17 close locally at desk and "
        "0 of 17 end to end. Nothing is built." % (D1, D3),
        width=120, initial_indent="", subsequent_indent="    ", break_long_words=False, break_on_hyphens=False) + "\n"
    open(os.path.join(T, VS), "w", encoding="utf-8").write(v)
    print("layers_r8int6: V2-SPEC.md line 24 corrected, correction 31 added")
    WHAT = ("%s re-read at the r8int6 integration of 27 September 2026 (set 6's re-read of the four public pages, the layer "
            "1 integrator line's rule): two places change, line 24's RockBLOCK clause (its ENABLE held low by the EMCON "
            "hardware since board B's stream w4b, %s, where it said a firmware-driven expander held it and the hardware "
            "ENABLE was owed) and correction 31 added at the end; every other line is byte-identical to the file at {OLD}" % (VS, D1))
    WHY = {"REQ-005": "line 32 and correction 6, which this reading cites, are byte-identical",
           "CFL-016": "line 24 now describes board B's RockBLOCK ENABLE as generated, which is what this record's acceptance "
                      "asks of the published documents, and lines 34, 41, 43 and 76 and the corrections it cites are "
                      "byte-identical",
           "CFL-010": "line 41 and the corrections it cites are byte-identical",
           "CFL-013": "line 35 and correction 8, which this reading rests on, are byte-identical"}
    res = {r["id"]: r.get("evidence_result") for r in recs}
    for rid, why in WHY.items():
        old = edlib.rebind(REG, rid, VS, T, WHAT + "; " + why + ", so it stands " + str(res[rid]) + " on the file at {NEW}")
        print("layers_r8int6: %s rebound from %s" % (rid, old))
    s = open(REG, encoding="utf-8").read()

# ---- the open item for FEA-002's statement
MARK = "FEA-002's statement describes the RockBLOCK 9704's ENABLE as it was before stream w4b"
if MARK not in s:
    have = {int(x) for x in re.findall(r"(?m)^  - id: S-(\d{2,3})$", s)}
    sid = "S-%02d" % (max(have) + 1)
    title = (MARK + " ('with its ENABLE held by firmware'); since stream w4b (27 September 2026, %s) the ENABLE is EMCON_HW "
             "AND the panel's request in U536, held low by R527 with the gate unpowered (feasibility/EMCON.md section 4c). "
             "Found at the r8int6 integration. The statement is part of the requirements baseline (a54b793b), whose "
             "statements change only under their own review (the registry header), so the integration leaves it and its "
             "readings say the remedy is drawn. No count changes (EMCON local 15 of 17 at desk, end to end 0 of 17; the "
             "RockBLOCK row stays open on the Iridium module's unpublished response to ENABLE). Closed when FEA-002's "
             "statement is changed under a review of the baseline by a reviewer who wrote none of the changed lines." % D1)
    blk = "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s\n" % (sid, "\n".join(textwrap.wrap(
        title, width=118, initial_indent=" " * 6, subsequent_indent=" " * 6, break_long_words=False, break_on_hyphens=False)))
    anchor = "\n\n# Items that left the open list"
    assert s.count(anchor) == 1
    s = s.replace(anchor, "\n" + blk.rstrip("\n") + anchor, 1)
    yaml.safe_load(s)
    open(REG, "w", encoding="utf-8").write(s)
    print("layers_r8int6: %s added" % sid)
else:
    sid = re.search(r"(?m)^  - id: (S-\d+)\n    class: SESSION\n    status: OPEN\n    title: >-\n      " + re.escape(MARK[:40]), s).group(1)

# ---- layer 3: the baseline's fields, computed
_old = yaml.safe_load(subprocess.run(["git", "-C", T, "show", BASE + ":v2/ecad/tools/pcb_requirements.yaml"],
                                     capture_output=True, text=True, check=True).stdout)
_new = yaml.safe_load(open(REG, encoding="utf-8"))
BASEF = ("statement", "acceptance", "applicability", "allocated_to", "verification_method", "verification_phase",
         "final_phase", "release_effect", "kind", "parent", "prototype_1")
_o = {r["id"]: r for r in _old["records"]}; _n = {r["id"]: r for r in _new["records"]}
assert set(_o) == set(_n), "records added or removed: %s" % sorted(set(_o) ^ set(_n))
moved = sorted((rid, k) for rid in _n for k in BASEF if _o[rid].get(k) != _n[rid].get(k))
assert not moved, "a baselined field moved: %s" % moved
other = sorted({k for rid in _n for k in set(_o[rid]) | set(_n[rid]) if _o[rid].get(k) != _n[rid].get(k)})
nrec = sum(1 for rid in _n if any(_o[rid].get(k) != _n[rid].get(k) for k in set(_o[rid]) | set(_n[rid])))

# ---- the three integrator lines
t = open(LS, encoding="utf-8").read(); lines = t.split("\n")
M = "**Set 6 (the r8int6 integration, 27 September 2026):**"
ADD = {
 1: (M + " streams w4r, w4b, w4c, w4ae and w4dp touch EMCON (w4b, w4c) and feasibility records (FEA-002's readings "
     "rebound), so the four public pages were re-read. One line was stale: `V2-SPEC.md` line 24 said the RockBLOCK 9704's "
     "ENABLE is held by a firmware-driven expander with the hardware ENABLE owed; stream w4b drew it (`U536`, %s). It is "
     "corrected in the page, with correction 31, and the four readings bound to V2-SPEC.md are rebound. The counts stand "
     "(EMCON local 15 of 17 at desk, end to end 0 of 17; `feasibility/EMCON.md` section 0a keeps the RockBLOCK row open on "
     "the Iridium module's unpublished response to ENABLE). `README.md`, `v2/README.md` and `v2/BUILD.md` state nothing "
     "set 6 moved. A circuit correction, so layer 1 does not reopen; the brief is not edited. Owner: the integrator." % D1),
 2: (M + " CONOPS is not edited, under the H2 review's rule: HOT-R1 is drawn on boards A and E (stream w4ae, %s), and its "
     "current state is REQ-077's, INCONCLUSIVE and held by FEA-004, the source DEFINITION-STATUS.md names; EMCON's is "
     "`feasibility/EMCON.md` sections 0a and 4c (the RockBLOCK's ENABLE forced low by hardware, and the 5G buck's enable "
     "driven by `U216` from the slot's own 5 V). Layer 2 does not reopen. Owner: the integrator." % HOT),
 3: (M + " %d records change, in %s only (readings, their bindings and notes; sources added beside the old ones; waits "
     "and choices), with session choices and open items added and S-45, S-57, S-64 and S-76 closed; no record's "
     "statement, acceptance, applicability, allocation, verification or release effect changes (computed against `%s`), "
     "so the layer does not reopen. FEA-002's statement still says the RockBLOCK's ENABLE is held by firmware, which "
     "stream w4b changed; it is carried to its own review as open item %s. HOT-R1 is drawn (stream w4ae, %s), so REQ-077 "
     "reads INCONCLUSIVE, held by FEA-004. Owner: the integrator as registry writer."
     % (nrec, ", ".join("`%s`" % k for k in other), BASE, sid, HOT)),
}
done = []
for n, add in ADD.items():
    idx = [i for i, l in enumerate(lines) if l.startswith("> **INTEGRATOR LINE, layer %d:**" % n)]
    assert len(idx) == 1, (n, idx)
    if M in lines[idx[0]]: continue
    lines[idx[0]] = lines[idx[0]].rstrip() + " " + add
    done.append(n)
if done:
    open(LS, "w", encoding="utf-8").write("\n".join(lines)); print("layers_r8int6: layer lines %s carry set 6" % done)
print("layers_r8int6: open item %s" % sid)
