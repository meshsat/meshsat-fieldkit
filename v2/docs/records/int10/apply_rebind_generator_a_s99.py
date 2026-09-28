#!/usr/bin/env python3
"""Records bound to board A's schematic generator by sha, rebound after stream s99a (MESHSAT-1357, integration set 9,
stream s99reg, 29 September 2026). AI engineering work; prototype design, nothing built, ordered or measured.

Stream s99a applied decision 55 to v2/ecad/tools/gen_sch_a.py, so four records bound to the file at set 8's sha no
longer validate (three PASS records read as errors): CON-019, CON-018, CFL-014 and REQ-077. This script PROVES from the
code, not from the diff's words, that the change leaves what each record reads alone: it parses set 8's file (git
show 20afa7a4, asserted to be the sha the records carry) and the tree's, and asserts that the calls other than
electrical-intent declarations differ ONLY in
  - the ten new parts of the mezzanine's buck (U41, L13, C227 to C232, R217, R218) and the layout class of C229 and C230,
  - U23's call, in its input net alone (+5V_DEV to +5V_D8IN),
  - U32's and U39's calls, in their ILM value text alone (TPS2596 equation 7's sign, stream s99a item 2),
  - the power-flag list, which gains +5V_D8IN and nothing else,
and that the only module assignment that differs is SECTIONS, which gains the ten references in one section. It then
asserts that none of the parts and nets each record's evidence reads (listed below from the entries, by record) is
named in any call that differs, except VBAT for CFL-014: U41 and its input capacitors are new loads on VBAT, the
charger's system side, which is where that record's reading puts the loads. It writes one evidence entry per record
and rebinds. It changes no result. Refuses a second run. Usage: python3 <this file> [--root <tree>] [--check]."""
import ast, collections, hashlib, os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _int10 as H
from _int10 import A

NAME = "apply_rebind_generator_a_s99"
GA = "v2/ecad/tools/gen_sch_a.py"
OLD_COMMIT, OLD16 = "20afa7a4", "ebb5c0f250780a48"
NEW_REFS = ["U41", "L13", "C227", "C228", "C229", "C230", "C231", "C232", "R217", "R218"]
READS = {   # the parts and nets each record's evidence names (its entries in pcb_requirements.yaml)
    "CON-019": ["U30", "U26", "U16", "U19", "U18", "R48", "U14", "OUTLET_OK", "POE_EN", "PD_EN", "TR_APRS", "PA_EN",
                "POE_SW_EN", "PD_SW_EN", "PA_KEY", "KEY"],
    "CON-018": ["U31", "PD_CC1", "PD_CC2", "C96", "C97", "J_USBC_OUT"],
    "CFL-014": ["R26", "R27", "CH_VDDA", "R17", "F1", "CELL_FUSED", "CELL+"],
    "REQ-077": ["J_DOCK", "DOCK_SPARE", "U27", "EXP_INT", "R110", "J_AB1"],
}
CURRENT_WORDS = ("typical current", "peak current", "declared current", "coincident peak", "current declaration")


def split(src):
    tree = ast.parse(src)
    other, intent = collections.Counter(), collections.Counter()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            (intent if ast.unparse(n.func).startswith("_intent.") else other)[ast.unparse(n)] += 1
    assigns = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets: assigns.setdefault(ast.unparse(t), []).append(n.value)
    fors = collections.Counter(ast.unparse(n.iter) for n in ast.walk(tree) if isinstance(n, ast.For))
    return other, intent, assigns, fors


def call_of(s): return ast.parse(s).body[0].value


def first(c):
    a = c.args[0] if c.args else None
    return a.value if isinstance(a, ast.Constant) else None


def prove(old, new):
    """(the names the differing calls carry, a one-line account); refuses anything outside the change described"""
    oo, oi, oa, of = split(old); no, ni, na, nf = split(new)
    added, removed = no - oo, oo - no
    names, seen = set(), collections.Counter()
    ad = {}
    for s in added.elements():
        c = call_of(s); fn = H._func(c)
        ad.setdefault((fn, first(c)), []).append(c)
    rm = {}
    for s in removed.elements():
        c = call_of(s); fn = H._func(c)
        rm.setdefault((fn, first(c)), []).append(c)
    for (fn, f0), cs in ad.items():
        if f0 in NEW_REFS and fn in ("ic", "part", "c", "r") and len(cs) == 1 and (fn, f0) not in rm:
            names |= H.const_strings(cs[0]); seen["part"] += 1; continue
        if fn == "efuse" and f0 in ("U23", "U32", "U39") and len(cs) == 1 and len(rm.get((fn, f0), [])) == 1:
            o, n = rm[(fn, f0)][0], cs[0]
            diff = [k for k, (x, y) in enumerate(zip(o.args, n.args)) if ast.unparse(x) != ast.unparse(y)]
            kws = [k.arg for k in n.keywords if ast.unparse(k.value) != ast.unparse(H.kw(o, k.arg) or ast.Constant(None))]
            if len(o.args) != len(n.args) or len(o.keywords) != len(n.keywords) or kws or diff != ([1] if f0 == "U23" else [6]):
                H.refuse(NAME, "%s's call changed beyond %s: args %s, keywords %s" % (f0, "its input" if f0 == "U23" else "its ILM text", diff, kws))
            names |= {ast.literal_eval(n.args[k]) for k in diff} | {ast.literal_eval(o.args[k]) for k in diff}; seen["efuse"] += 1; continue
        if fn == "enumerate" and len(cs) == 1 and len(rm.get((fn, None), [])) == 1:
            o, n = ast.literal_eval(rm[(fn, None)][0].args[0]), ast.literal_eval(cs[0].args[0])
            k = list(n).index("+5V_D8IN") if "+5V_D8IN" in n else -1
            if k < 0 or tuple(n[:k]) + tuple(n[k + 1:]) != tuple(o): H.refuse(NAME, "the power-flag list changed beyond +5V_D8IN")
            names |= {"+5V_D8IN"}; seen["flags"] += 1; continue
        if fn == "_cls" and len(cs) == 1 and isinstance(cs[0].args[0], ast.Name) and (fn, None) not in rm:
            if "('C229', 'C230')" not in (nf - of):
                H.refuse(NAME, "the layout class call is not the one over C229 and C230")
            names |= {"C229", "C230"}; seen["class"] += 1; continue
        H.refuse(NAME, "a call outside the described change differs: %s(%r)" % (fn, f0))
    for key in rm:
        if key not in ad: H.refuse(NAME, "a call was removed: %s(%r)" % key)
    if seen != collections.Counter({"part": 10, "efuse": 3, "flags": 1, "class": 1}): H.refuse(NAME, "the differing calls are %s" % dict(seen))
    ch = sorted(k for k in set(oa) | set(na) if [ast.unparse(v) for v in oa.get(k, [])] != [ast.unparse(v) for v in na.get(k, [])])
    if ch != ["SECTIONS"]: H.refuse(NAME, "module assignments changed: %s" % ch)
    so, sn = oa["SECTIONS"][0], na["SECTIONS"][0]
    if not (isinstance(so, ast.List) and isinstance(sn, ast.List) and len(so.elts) == len(sn.elts)):
        H.refuse(NAME, "SECTIONS is not the same list of sections")
    grew = []
    for eo, en in zip(so.elts, sn.elts):
        if ast.unparse(eo) == ast.unparse(en): continue
        if not (isinstance(en, ast.Tuple) and isinstance(eo, ast.Tuple) and ast.unparse(eo.elts[0]) == ast.unparse(en.elts[0])
                and isinstance(en.elts[1], ast.List)):
            H.refuse(NAME, "a section of SECTIONS changed its title or form")
        added = [e.value for e in en.elts[1].elts if isinstance(e, ast.Constant) and e.value in NEW_REFS]
        kept = ast.List(elts=[e for e in en.elts[1].elts if not (isinstance(e, ast.Constant) and e.value in NEW_REFS)], ctx=ast.Load())
        if ast.unparse(kept) != ast.unparse(eo.elts[1]): H.refuse(NAME, "section %r changed beyond the new references" % eo.elts[0].value)
        grew.append((eo.elts[0].value, added))
    if len(grew) != 1 or sorted(grew[0][1]) != sorted(NEW_REFS):
        H.refuse(NAME, "SECTIONS changed beyond the ten references in one section: %s" % grew)
    names |= set(NEW_REFS)
    account = ("the calls other than electrical-intent declarations differ only in the ten parts of the D8 mezzanine's buck (U41, "
               "L13, C227 to C232, R217, R218) and the layout class of C229 and C230, U23's input net (+5V_DEV to +5V_D8IN), the "
               "ILM value texts of U32 and U39 (TPS2596 equation 7's sign) and the power-flag list (+5V_D8IN added); of the module "
               "assignments only SECTIONS differs, by the ten references in section %r; of the electrical-intent declarations %d of "
               "set 8's texts are gone and %d are new (a changed declaration counts in both), which no rule this record rests "
               "on reads" % (grew[0][0].split(":")[0], sum((oi - ni).values()), sum((ni - oi).values())))
    return names, account


def main(argv):
    root = H.root_of(argv)
    reg = H.read(root, H.REG)
    if "apply_rebind_generator_a_s99" in reg: H.refuse(NAME, "already applied (a second run)")
    old = subprocess.run(["git", "-C", H.CODE, "show", "%s:%s" % (OLD_COMMIT, GA)], capture_output=True, check=True).stdout.decode("utf-8")
    new = H.read(root, GA)
    if H.sha16_text(old) != OLD16: H.refuse(NAME, "%s's %s is not %s" % (OLD_COMMIT, GA, OLD16))
    new16 = H.sha16_text(new)
    if new16 == OLD16: H.refuse(NAME, "the tree's %s is set 8's: nothing to rebind" % GA)
    names, account = prove(old, new)
    before = yaml.safe_load(reg)
    recs = {r["id"]: r for r in before["records"]}
    bound = H.bound_records(before, GA)
    if sorted(bound) != sorted(READS): H.refuse(NAME, "records bound to %s: %s, expected %s" % (GA, sorted(bound), sorted(READS)))
    if set(bound.values()) != {OLD16}: H.refuse(NAME, "the bound records carry %s, expected %s" % (sorted(set(bound.values())), OLD16))
    out = reg
    for rid in sorted(bound):
        st = str(recs[rid].get("statement", "")).lower()
        if any(w in st for w in CURRENT_WORDS): H.refuse(NAME, "%s's statement names a declared current: read it by hand" % rid)
        ev = " ".join(str(e) for e in recs[rid].get("evidence") or [])
        missing = [x for x in READS[rid] if x not in ev]
        if missing: H.refuse(NAME, "%s's evidence does not name %s: the list of what it reads is wrong" % (rid, missing))
        hit = sorted(set(READS[rid]) & names)
        if hit: H.refuse(NAME, "%s reads %s, which the change touches: re-read it by hand" % (rid, hit))
        extra = (" U41 and its input capacitors C229 and C230 are new loads on VBAT, the charger's system side, which is where "
                 "this reading puts the loads." if rid == "CFL-014" else "")
        entry = ("v2/ecad/tools/gen_sch_a.py re-read at integration set 9 (29 September 2026, stream s99a, decision 55; "
                 "v2/docs/records/int10/apply_rebind_generator_a_s99.py): the file at %s and at %s were parsed; %s. None of "
                 "the differing calls names a part or net this reading rests on (%s), which the script asserts.%s So the "
                 "reading stands; rebound. No result changes." % (OLD16, new16, account, ", ".join(READS[rid]), extra))
        A.screen(entry, "%s's entry" % rid)
        i, j = A.span(out, rid)
        r = H.add_evidence(NAME, out[i:j], rid, entry)
        r = H.rebind_line(NAME, r, rid, GA, OLD16, new16)
        out = out[:i] + r + out[j:]
    after = yaml.safe_load(out)
    H.compare_records(NAME, before, after, {rid: {"evidence", "evidence_bound_to"} for rid in bound})
    for sec in before:
        if sec != "records" and before[sec] != after[sec]: H.refuse(NAME, "section %s changed" % sec)
    msg = "%d records rebound (%s); %s %s -> %s" % (len(bound), ", ".join(sorted(bound)), GA, OLD16, new16)
    if "--check" in argv:
        print("%s: CHECK ONLY, nothing written: %s" % (NAME, msg)); return 0
    H.write(root, H.REG, out)
    if yaml.safe_load(H.read(root, H.REG)) != after: H.refuse(NAME, "re-parse differs")
    print("%s: %s\nOWED: rules_render.py --requirements (the registry changed)" % (NAME, msg))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
