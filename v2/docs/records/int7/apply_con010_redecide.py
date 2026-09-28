#!/usr/bin/env python3
"""CON-010 re-decided FROM THE READINGS at the set 6 integration (MESHSAT-1357, 28 September 2026), the owner's review
of the restart plan, amendment XH-04: a verdict change is derived by a stated predicate from the verdict files, never
typed.

CON-010: "The PA's VGG is the EMCON gate of the APRS transmitter; D's KEY = PTT_ANY AND TX_INHIBIT_n", allocated to
boards D and A, satisfied by RF-002 and SCH-004. It was set FAIL at the re-take of 8ea7867e on RF-002's FAIL rows
(W3T-F1: TX_INHIBIT_n at 1.09 V with board C unpowered under the walk's worst-case Ioff, open item S-64). The rebind of
the consolidated re-take (retake6) recorded that those rows now read INCONCLUSIVE and left the re-decision to the
registry's writer. This script IS that re-decision, and it computes the result:

  the elements are the readings the record rests on, on its allocated boards: inhibit_chain_d and inhibit_chain_a
  (RF-002's walk) and safe_lines_d and safe_lines_a (SCH-004), each bound to the current candidate's netlist;
  FAIL          if any element reads a failed check (or a FAIL verdict);
  INCONCLUSIVE  if none fails and at least one check is undecided, or an element's reading is missing;
  PASS          only if every element is decided and holds.

It also: adds `waits_on: [S-92]` (S-64 is CLOSED by SC-67 on this line, so the link goes to the dependency that remains,
the SA868's PTT receive threshold, which no open item recorded until now); opens S-92; and gives S-88 and S-89 the
field `limits_reading` from which rules_render derives the LIMITED notices (the reassessment's correction 3). It
changes no statement and no acceptance (layer 3's baseline), screens every new sentence with claims_check's CLAIM
pattern, re-parses the file, asserts that only the intended fields changed, and refuses a second run.

Run from the repository root BEFORE rules_status (the registry is read at render time): python3 <this file>."""
import json, os, re, subprocess, sys, textwrap

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CE = os.path.join(TOP, "v2/docs/CURRENT-EVIDENCE.md")
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import claims_check as _cc

ELEMENTS = {  # element -> (board letter, reading path relative to v2/ecad)
    "inhibit_chain_d": ("d", "pcb-d-aprs-d9/routed/inhibit_chain_d.verdict.json"),
    "inhibit_chain_a": ("a", "pcb-a-power-a23/routed/inhibit_chain_a.verdict.json"),
    "safe_lines_d": ("d", "pcb-d-aprs-d9/routed/safe_lines_d.verdict.json"),
    "safe_lines_a": ("a", "pcb-a-power-a23/routed/safe_lines_a.verdict.json"),
}
CONTEXT = {"inhibit_chain_c": ("c", "pcb-c-display-c8/routed/inhibit_chain_c.verdict.json")}   # where W3T-F1 failed


def refuse(msg):
    print("apply_con010_redecide: REFUSED: %s" % msg); sys.exit(1)


def reading(rel):
    p = os.path.join(TOP, "v2/ecad", rel)
    if not os.path.exists(p): return None
    try: return json.load(open(p, encoding="utf-8"))
    except Exception as e: refuse("%s cannot be read (%s)" % (rel, e))


def candidate_netlists(page):
    """{board letter: netlist sha256/16} from the page's table 'The candidate each board is judged against'."""
    out = {}
    for line in page.split("\n"):
        m = re.match(r"^\| (A|B|C|D|E|P|E5) \| \S+ \| `([^`]+)` ([0-9a-f]{16}) \|", line)
        if m: out[m.group(1).lower()] = m.group(3)
    if len(out) < 6: refuse("the page's candidate table has %d rows with a netlist" % len(out))
    return out


def netlist_of(r, letter):
    inp = r.get("inputs") or {}
    n = inp.get("netlist_%s" % letter) or inp.get("netlist")
    return (n or {}).get("sha256_16")


def wrap(s, indent=10):
    words = s.split(); lines = []; cur = " " * (indent - 1)
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = " " * indent + w
        else: cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def screen(text, what):
    hit = _cc.CLAIM.search(text)
    if hit: refuse("%s carries the claim word %r, which the ENV-002 screen would count" % (what, hit.group(0)))
    if "—" in text or "–" in text: refuse("%s carries a dash" % what)


def main():
    t = open(P, encoding="utf-8").read()
    if "\n  - id: S-92\n" in t: refuse("S-92 is in the registry already (a second run)")
    before = yaml.safe_load(t)
    page = open(CE, encoding="utf-8").read()
    cand = candidate_netlists(page)

    # --- the predicate, from the readings
    fails, undecided, missing, lines = [], [], [], []
    for name, (letter, rel) in ELEMENTS.items():
        r = reading(rel)
        if r is None: missing.append(name); lines.append("%s: no reading in the tree" % name); continue
        sha = netlist_of(r, letter)
        if sha != cand[letter]:
            refuse("%s records netlist %s for board %s where the page's candidate is %s" % (name, sha, letter.upper(), cand[letter]))
        v = r.get("verdict"); c = r.get("counts") or {}
        if v == "FAIL" or c.get("fail"): fails.append(name)
        if c.get("undecided"): undecided.append(name)
        ev = [str(e) for e in (r.get("evidence") or [])]
        und = [e.split(": ", 1)[1] if e.lower().startswith("undecided: ") else e for e in ev if e.lower().startswith("undecided")]
        if name.startswith("inhibit_chain"):
            lines.append("%s %s, %d pass, %d failed, %d undecided of %d on netlist %s%s" % (
                name, v, c.get("pass", 0), c.get("fail", 0), c.get("undecided", 0), r.get("denominator"), sha,
                (" (undecided: %s)" % "; ".join(und)) if und else ""))
        else:
            lines.append("%s %s on netlist %s (%d safety line(s), %d floating)" % (name, v, sha, c.get("lines", 0), c.get("floating", 0)))
    cc = reading(CONTEXT["inhibit_chain_c"][1])
    if cc is None: refuse("board C's inhibit_chain reading is missing; the W3T-F1 check cannot be read")
    if netlist_of(cc, "c") != cand["c"]: refuse("inhibit_chain_c is not on board C's candidate netlist")
    c_line = "inhibit_chain_c %s of %d on netlist %s" % (cc.get("verdict"), cc.get("denominator"), netlist_of(cc, "c"))
    if fails: result = "FAIL"
    elif undecided or missing: result = "INCONCLUSIVE"
    else: result = "PASS"

    # --- the record
    i, j = rec_span(t, "CON-010"); r = t[i:j]
    m = re.search(r"(?m)^    evidence_result: (\S+)\n", r)
    old_result = m.group(1)
    if "    waits_on:" in r: refuse("CON-010 already carries a waits_on")
    entry = (
        "v2/ecad/pcb-d-aprs-d9/routed/inhibit_chain_d.verdict.json, inhibit_chain_a, safe_lines_d and safe_lines_a re-read at "
        "the set 6 integration of 28 September 2026 (branch fnd/int7), and the record RE-DECIDED from them by a stated "
        "predicate (the owner's review of the restart plan, amendment XH-04): the elements are the readings this record "
        "rests on, on its allocated boards D and A; it reads FAIL if any element reads a failed check, INCONCLUSIVE if "
        "none fails and at least one check is undecided or a reading is missing, PASS only if every element is decided "
        "and holds. What set FAIL at the re-take of 8ea7867e was W3T-F1 (open item S-64: TX_INHIBIT_n at 1.09 V with "
        "board C unpowered under the walk's worst-case Ioff); set 6 remedied it on board C's generator (SC-67: R14 2.2 k "
        "and R50 10 k, the line at 0.243 V), S-64 is CLOSED by SC-67 on this line, and %s, so that check fails on no "
        "board. The elements now: %s. Failed elements: %s; undecided: %s; missing: %s. Result by the predicate: %s%s. "
        "What stays undecided is named, not judged: the SA868 exciter's PTT receive threshold, which its maker does not "
        "state (bench E-01 of v2/docs/feasibility/EMCON.md, prototype verification), and on board A the two power-fed "
        "rows (the 30 W amplifier on J_PA and the QMX on J_HF), which the walk reaches in hardware and cannot time from a "
        "held document. The record therefore waits on S-92 (opened with this entry) and no longer on S-64. A desk reading: "
        "no board has been built or measured."
        % (c_line, "; ".join(lines), ", ".join(fails) or "none", ", ".join(undecided) or "none",
           ", ".join(missing) or "none", result,
           "" if result != old_result else " (unchanged from %s)" % old_result))
    screen(entry, "CON-010's evidence entry")
    hist = (" Re-decided at the set 6 integration of 28 September 2026 by the predicate in the evidence entry of that "
            "day: the W3T-F1 check no longer fails on any board (SC-67), the walk reads 0 failed on D and A with the SA868's "
            "row and board A's two power-fed rows undecided, so it reads %s and waits on S-92." % result)
    screen(hist, "CON-010's history sentence")
    r2 = r.replace("    evidence_result: %s\n" % old_result, "    evidence_result: %s\n" % result, 1)
    r2 = r2.replace("\n    status: DEFINED\n", "\n    waits_on: [S-92]\n    status: DEFINED\n", 1)
    k = r2.index("    evidence_bound_to:")
    r2 = r2[:k] + "      - >-\n" + wrap(entry) + r2[k:]
    hm = re.search(r"(?m)^    history: >-\n((?:      .*\n)+)", r2)
    if not hm: refuse("CON-010's history block was not found")
    hist_lines = textwrap.wrap(hm.group(1).replace("\n", " ").strip() + hist, 114, break_on_hyphens=False, break_long_words=False)
    r2 = r2[:hm.start(1)] + "".join("      %s\n" % l for l in hist_lines) + r2[hm.end(1):]
    if r2 == r: refuse("CON-010 did not change")
    t2 = t[:i] + r2 + t[j:]

    # --- S-92, the open item the record now waits on
    s92 = ("The SA868 VHF exciter's PTT receive threshold, which its maker does not state: RF-002's walk on board D reads "
           "the exciter's row UNDECIDED (inhibit_chain_d: 7 pass, 0 failed, 1 undecided of 8 on the set 6 netlist; the "
           "text of the row is 'EMCON reaches it in hardware (D key on U2)'), so CON-010, the transmit gate on board D "
           "(KEY = PTT_ANY AND TX_INHIBIT_n), cannot read PASS at the desk. S-64 (W3T-F1, TX_INHIBIT_n's fail-safe level "
           "with board C unpowered) is closed by SC-67 and that check fails on no board since set 6; this item is the "
           "dependency that remains. Open until the maker states the threshold in a held document under v2/vendor/, or "
           "bench E-01 of v2/docs/feasibility/EMCON.md measures it on the module (prototype verification, on a built "
           "board), and RF-002 is re-taken on board D.")
    screen(s92, "S-92's title")
    body = "\n".join("      " + l for l in textwrap.wrap(s92, 114, break_on_hyphens=False, break_long_words=False))
    add = "\n  - id: S-92\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % body
    c = t2.index("\nclosed_items:\n")
    t2 = t2[:c].rstrip("\n") + add + "\n" + t2[c:]

    # --- limits_reading on S-88 (TRN-001 on A) and S-89 (REL-001 everywhere)
    for iid, lim in (("S-88", "      - {rule: TRN-001, boards: [a]}\n"), ("S-89", "      - {rule: REL-001, boards: all}\n")):
        a, b = rec_span(t2, iid); it = t2[a:b]
        if "limits_reading" in it: refuse("%s already carries limits_reading" % iid)
        it2 = it.replace("\n    status: OPEN\n", "\n    status: OPEN\n    limits_reading:\n" + lim, 1)
        if it2 == it: refuse("%s: status line not found" % iid)
        t2 = t2[:a] + it2 + t2[b:]

    # --- re-parse and compare
    after = yaml.safe_load(t2)
    ra = {x["id"]: x for x in before["records"]}; rb = {x["id"]: x for x in after["records"]}
    if list(ra) != list(rb): refuse("the record list changed")
    moved = [k for k in ra if ra[k] != rb[k]]
    if moved != ["CON-010"]: refuse("records changed: %s" % moved)
    x, y = ra["CON-010"], rb["CON-010"]
    keys = sorted(f for f in set(x) | set(y) if x.get(f) != y.get(f))
    want = ["evidence", "history", "waits_on"] + (["evidence_result"] if result != old_result else [])
    if keys != sorted(want): refuse("CON-010: fields changed: %s (expected %s)" % (keys, want))
    if y["waits_on"] != ["S-92"] or y["evidence"][:-1] != x["evidence"] or y["evidence_result"] != result: refuse("CON-010's new fields are not as intended")
    if y["statement"] != x["statement"] or y["acceptance"] != x["acceptance"]: refuse("the baselined statement or acceptance changed")
    oa = {x["id"]: x for x in before["open_items"]}; ob = {x["id"]: x for x in after["open_items"]}
    if list(ob) != list(oa) + ["S-92"]: refuse("open_items did not gain exactly S-92 at the end")
    for k in oa:
        if k in ("S-88", "S-89"):
            if {f for f in set(oa[k]) | set(ob[k]) if oa[k].get(f) != ob[k].get(f)} != {"limits_reading"}: refuse("%s changed beyond limits_reading" % k)
        elif oa[k] != ob[k]: refuse("open item %s changed" % k)
    if ob["S-92"]["title"] != s92: refuse("S-92's title did not round-trip")
    for sec in before:
        if sec not in ("records", "open_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    open(P, "w", encoding="utf-8").write(t2)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_con010_redecide: CON-010 %s -> %s by the predicate; elements: %s" % (old_result, result, " | ".join(lines)))
    print("apply_con010_redecide: %s; S-92 opened; CON-010 waits_on [S-92]; limits_reading on S-88 (TRN-001, a) and S-89 (REL-001, all)" % c_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
