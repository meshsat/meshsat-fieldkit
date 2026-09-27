"""Validate W1 drafts: YAML shape, vocabularies, rule ids, NEED ids, conflict refs, no em dashes."""
import re, sys, yaml, collections, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root, "v2/ecad/tools"))
import rules_lib
d = yaml.safe_load(open(os.path.join(root, "drafts/w1-requirements.yaml")))
rules = {r["id"] for r in yaml.safe_load(open(os.path.join(root, "v2/ecad/tools/pcb_rules.yaml")))["rules"]}
conops = open(os.path.join(root, "v2/docs/CONOPS.md")).read()
needs = set(re.findall(r"^\| (NEED-\d\d) \|", conops, re.M))
conf_path = os.path.join(root, "drafts/w1-conflicts.md")
conf_ids = set(re.findall(r"^### (C-\d\d)\b", open(conf_path).read(), re.M)) if os.path.exists(conf_path) else set()
CLASSES = {"requirement", "derived_constraint", "implementation_choice", "assumption", "superseded", "conflict"}
errs = []; ids = set(); cls = collections.Counter(); cov = collections.Counter(); tbd = 0
assert tuple(d["methods"]) == rules_lib.METHODS, "methods list drifted from rules_lib"
assert tuple(d["phases"]) == rules_lib.PHASES, "phases list drifted from rules_lib"
for c in d["candidates"]:
    i = c["id"]
    if i in ids: errs.append("dup " + i)
    ids.add(i)
    for k in ("class", "parent", "statement", "acceptance", "allocated_to", "verification_method", "verification_phase", "rules", "rule_coverage", "source", "source_check"):
        if k not in c: errs.append("%s missing %s" % (i, k))
    if c.get("class") not in CLASSES: errs.append("%s class %s" % (i, c.get("class")))
    cls[c.get("class")] += 1; cov[c.get("rule_coverage")] += 1
    if c.get("parent") not in needs: errs.append("%s parent %s not in CONOPS" % (i, c.get("parent")))
    for m in c.get("verification_method", []):
        if m not in rules_lib.METHODS: errs.append("%s method %s" % (i, m))
    for ph in (c.get("verification_phase"), c.get("final_phase", c.get("verification_phase"))):
        if ph not in rules_lib.PHASES: errs.append("%s phase %s" % (i, ph))
    if "final_phase" in c and rules_lib.PHASES.index(c["final_phase"]) <= rules_lib.PHASES.index(c["verification_phase"]):
        errs.append("%s final_phase not later than verification_phase" % i)
    for r in c.get("rules", []):
        if r not in rules: errs.append("%s unknown rule %s" % (i, r))
    if c.get("rule_coverage") not in ("FULL", "PARTIAL", "NONE"): errs.append("%s coverage" % i)
    if (c.get("rule_coverage") == "NONE") != (not c.get("rules")): errs.append("%s coverage/rules mismatch" % i)
    if "TBD" in str(c.get("acceptance")):
        tbd += 1
        if c["class"] in ("requirement", "assumption", "derived_constraint", "implementation_choice") and "tbd_effect" not in c:
            errs.append("%s TBD without tbd_effect" % i)
    if c.get("class") == "superseded" and "superseded_by" not in c: errs.append("%s superseded_by missing" % i)
    if c.get("class") == "conflict" and "conflict_ref" not in c: errs.append("%s conflict_ref missing" % i)
    if "conflict_ref" in c and conf_ids and c["conflict_ref"] not in conf_ids: errs.append("%s conflict_ref %s not in conflicts" % (i, c["conflict_ref"]))
    if c.get("source_check") not in ("VERIFIED", "INFERRED"): errs.append("%s source_check" % i)
covered = collections.Counter(c["parent"] for c in d["candidates"] if c["class"] == "requirement")
for n in sorted(needs):
    if not covered[n]: errs.append("need %s has no requirement" % n)
for f in ("drafts/w1-requirements.yaml", "drafts/w1-conflicts.md", "drafts/w1-decisions.md", "v2/docs/PRODUCT-BRIEF.md", "v2/docs/CONOPS.md"):
    p = os.path.join(root, f)
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        if "\u2014" in t or "\u2013" in t: errs.append("dash character in " + f)
print("candidates", len(ids), dict(cls), "coverage", dict(cov), "with TBD", tbd)
print("needs", sorted(needs)); print("requirements per need", dict(sorted(covered.items())))
print("conflict ids in conflicts file", sorted(conf_ids))
print("ERRORS" if errs else "OK", *errs, sep="\n")
