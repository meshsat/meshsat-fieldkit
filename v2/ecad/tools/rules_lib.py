#!/usr/bin/env python3
"""The rule registry: load it, validate it, fingerprint it, and decide which rules apply to which board
(MESHSAT-862, 16 September 2026; owner instruction of 16 September 00:30).

This project accumulated its gates one incident at a time. Every one of them exists because a board taught it,
and there has never been a complete, versioned statement of what a board here must satisfy. Two consequences
were measured rather than suspected: every deliverable folder in the tree passed the final gate because
`verify_deliverable` judges a folder against ITSELF, and two heuristics ("a plane on a neighbouring layer",
"a ground via within 1.5 mm") are refusing boards today with no authority, no applicability condition and no
false-positive analysis behind them.

`pcb_rules.yaml` is the single canonical registry. Every document under v2/docs/ that describes a rule is
GENERATED from it (`rules_render.py`), every board result is computed from it (`rules_status.py`), and every
gate names the rule ids it decides. This module is the only reader: nothing else parses the YAML.

The rule shape, and what each field is for:

  id                     stable, e.g. RET-001; never reused, never renumbered
  domain                 one of DOMAINS below, the coverage axis
  short_name             a few words, for tables
  requirement            what must be true, in one sentence, as an engineering statement
  classification         REGULATORY | STANDARD | INTERFACE_REQUIREMENT | COMPONENT_REQUIREMENT | FAB_LIMIT |
                         ASSEMBLY_LIMIT | PHYSICS_PRINCIPLE | PROJECT_DECISION | HEURISTIC
  applicability          UNIVERSAL_FOR_THIS_PROJECT | CONDITIONAL | NOT_APPLICABLE
  condition              machine-readable (see `applies_to`): required for CONDITIONAL and NOT_APPLICABLE
  risk_class             one or more of RISKS
  release_effect         BLOCKER | MUST_JUSTIFY | ADVISORY
  source_status          VERIFIED | SOURCE_UNVERIFIED | CONFLICTING | NOT_REQUIRED_FOR_PROJECT_DECISION
  sources                list of {title, issuer, revision, clause, url_or_path, accessed}
  acceptance_criteria    objectively testable; need not be numeric
  rationale              why the requirement exists
  failure_mode           what goes wrong in the built hardware when it is violated
  verification_method    ERC | DRC | SCRIPT | CALCULATION | SIMULATION | MANUAL_REVIEW | VENDOR_CONFIRMATION |
                         PROTOTYPE_MEASUREMENT (one or more)
  verification_phase     SCHEMATIC | PLACED_BOARD | ROUTED_BOARD | RELEASE_PACKAGE | ASSEMBLY | PROTOTYPE
  automation_feasibility AUTOMATABLE | PARTIALLY_AUTOMATABLE | HUMAN_OR_LAB_ONLY
  boards_affected        letters, or ALL, or a condition-resolved list
  interfaces_affected    interface names, or NONE
  implementation_location where compliance is GENERATED (file[:symbol]), or NONE_YET
  evidence_scope         the identities that must match for evidence to be reusable
  owner                  who decides: SESSION | OWNER | VENDOR | LAB
  waiver_policy          {allowed, authority, evidence, scope, expiry, residual_risk} or NOT_WAIVABLE
  maturity               UNASSESSED | ENFORCED | GENERATED_ONLY | VERIFIED_MANUALLY | DOCUMENTED_ONLY | OPEN |
                         SOURCE_UNVERIFIED | OWNER_DECISION_REQUIRED

A condition is DATA, never code: {"all": [...]}, {"any": [...]}, {"not": {...}} around leaves
{"fact": "layers", "op": "ge", "value": 4} or {"fact": "interfaces", "op": "contains", "value": "PCIe"}.
`applies_to(rule, facts)` evaluates it against one board's facts; nothing is eval'd.

CLI:
  rules_lib.py validate [<registry>]      shape, allowed values, source policy; exits 0/1
  rules_lib.py fingerprint [<registry>]   the sha256 the evidence records
  rules_lib.py facts                      the board facts the conditions are resolved against
  rules_lib.py applicable <letter>        the rule ids that apply to one board
"""
import os, sys, json, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(HERE, "pcb_rules.yaml")
FACTS = os.path.join(HERE, "pcb_board_facts.yaml")
HOLDS = os.path.join(HERE, "pcb_board_holds.yaml")
# The four fields the owner named on 16 September 2026. A hold that does not carry all four is refused: a
# partial status line is how "held" turns into "nearly ready" over a few reports.
HOLD_FIELDS = ("ROUTING_STATUS", "ELECTRICAL_PROTECTION_STATUS", "FAB_READINESS", "PUBLICATION_STATUS")

DOMAINS = (
    "PRODUCT_ENVELOPE", "SCHEMATIC_INTEGRITY", "COMPONENT_SELECTION", "LIFECYCLE_SUPPLY",
    "POWER_TREE", "DECOUPLING", "POWER_INTEGRITY", "GROUNDING_SHIELDING", "STACKUP",
    "RETURN_PATH", "CONTROLLED_IMPEDANCE", "DIFFERENTIAL_PAIRS", "SIGNAL_INTEGRITY",
    "CLOCKS_RESET_BOOT", "ANALOG_MIXED_SIGNAL", "RF", "INTERFACE_COMPLIANCE", "TRANSIENT_PROTECTION",
    "ISOLATION_SPACING", "THERMAL", "PLACEMENT", "ROUTING", "VIAS", "PLANES_POURS", "EMC",
    "MECHANICAL", "FABRICATION_DFM", "ASSEMBLY_DFA", "TEST_BRINGUP", "RELIABILITY",
    "ENERGY_STORAGE", "DOCUMENTATION_CONTROL", "MANUFACTURING_OUTPUTS", "VERIFICATION_SIGNOFF",
)
CLASSIFICATIONS = ("REGULATORY", "STANDARD", "INTERFACE_REQUIREMENT", "COMPONENT_REQUIREMENT", "FAB_LIMIT",
                   "ASSEMBLY_LIMIT", "PHYSICS_PRINCIPLE", "PROJECT_DECISION", "HEURISTIC")
APPLICABILITY = ("UNIVERSAL_FOR_THIS_PROJECT", "CONDITIONAL", "NOT_APPLICABLE")
RISKS = ("SAFETY", "ELECTRICAL_FUNCTION", "SIGNAL_INTEGRITY", "POWER_INTEGRITY", "EMC", "THERMAL",
         "FABRICATION", "ASSEMBLY", "YIELD", "RELIABILITY", "TESTABILITY", "MECHANICAL", "DOCUMENTATION",
         "SUPPLY_CHAIN")
EFFECTS = ("BLOCKER", "MUST_JUSTIFY", "ADVISORY")
# PARTIALLY_VERIFIED added 16 September 2026, for the state the Ethernet question is actually in: one end's
# document was read and permits the design in terms that match it exactly, the other end's document was read
# and is silent, and a third document is not obtainable at any price. The four-value vocabulary forced that to
# be recorded as VERIFIED or as SOURCE_UNVERIFIED, and both would have been false.
SOURCE_STATUS = ("VERIFIED", "PARTIALLY_VERIFIED", "SOURCE_UNVERIFIED", "CONFLICTING",
                 "NOT_REQUIRED_FOR_PROJECT_DECISION")
METHODS = ("ERC", "DRC", "SCRIPT", "CALCULATION", "SIMULATION", "MANUAL_REVIEW", "VENDOR_CONFIRMATION",
           "PROTOTYPE_MEASUREMENT")
PHASES = ("SCHEMATIC", "PLACED_BOARD", "ROUTED_BOARD", "RELEASE_PACKAGE", "ASSEMBLY", "PROTOTYPE")
FEASIBILITY = ("AUTOMATABLE", "PARTIALLY_AUTOMATABLE", "HUMAN_OR_LAB_ONLY")
MATURITY = ("UNASSESSED", "ENFORCED", "GENERATED_ONLY", "VERIFIED_MANUALLY", "DOCUMENTED_ONLY", "OPEN",
            "SOURCE_UNVERIFIED", "OWNER_DECISION_REQUIRED")
OWNERS = ("SESSION", "OWNER", "VENDOR", "LAB")
RESULTS = ("PASS", "FAIL", "INCONCLUSIVE", "WAIVED", "NOT_APPLICABLE")

REQUIRED = ("id", "domain", "short_name", "requirement", "classification", "applicability", "risk_class",
            "release_effect", "source_status", "sources", "acceptance_criteria", "rationale", "failure_mode",
            "verification_method", "verification_phase", "automation_feasibility", "boards_affected",
            "interfaces_affected", "implementation_location", "evidence_scope", "owner", "waiver_policy",
            # PHASE A's assessment, taken before any gate implementation was opened, kept as the record of what was
            # known at writing. The LIVE maturity lives in the coverage map and only there: two fields with one name
            # drifted on 51 of the 56 rules within a day, and the registry read UNASSESSED for rules that block
            # boards. A rule may not carry a bare `maturity` any more, and the validator refuses one.
            "maturity_at_writing")
OPS = ("eq", "ne", "ge", "gt", "le", "lt", "contains", "not_contains", "in", "truthy")


def _yaml():
    try:
        import yaml
        return yaml
    except ImportError:                                    # the box's KiCad python has it; a bare host may not
        raise SystemExit("rules_lib: PyYAML is required to read the registry")


def load(path=None):
    """The registry as a dict, with `rules` a list. The ONLY place this file is parsed."""
    path = path or REGISTRY
    if not os.path.exists(path): raise SystemExit("rules_lib: no registry at %s" % path)
    d = _yaml().safe_load(open(path)) or {}
    if not isinstance(d.get("rules"), list): raise SystemExit("rules_lib: %s has no `rules` list" % path)
    return d


def facts(path=None):
    """Per-board facts the conditions are resolved against (layers, interfaces, rails, energy, assembly).
    Generated in Phase A from the schematics, the board files and the mechanical generators; it is DATA about
    the product, never about the gates."""
    path = path or FACTS
    if not os.path.exists(path): return {}
    return _yaml().safe_load(open(path)) or {}


def board_facts(f=None):
    """Only the board entries of the facts file: a board is a mapping, the metadata keys are scalars, and an
    entry beginning with an underscore is product-level rather than a board."""
    f = facts() if f is None else f
    return {k: v for k, v in f.items() if isinstance(v, dict) and not k.startswith("_")}


def board_holds(path=None):
    """{letter: hold} for every board held by an open decision.

    A hold is a PROCESS state and never a rule result: the board may pass every rule it has and still not be
    promotable, because what holds it is an unanswered question. Refuses an entry that does not carry all four
    status fields and the decision it waits on, because a hold whose words drift is a hold that stops binding."""
    path = path or HOLDS
    if not os.path.exists(path): return {}
    d = _yaml().safe_load(open(path, encoding="utf-8")) or {}
    out = {}
    for letter, h in (d.get("holds") or {}).items():
        missing = [k for k in HOLD_FIELDS if not (h or {}).get(k)]
        if missing:
            raise ValueError("the hold on board %s declares no %s; a partial status is how a hold stops "
                             "binding" % (letter.upper(), ", ".join(missing)))
        if not h.get("decision"):
            raise ValueError("the hold on board %s names no decision, so nothing says what would lift it" % letter.upper())
        out[str(letter).lower()] = h
    return out


def hold_banner(h):
    """The four fields as one line, in the owner's own order, for any page or log that reports a held board."""
    return "   ".join("%s = %s" % (k, h[k]) for k in HOLD_FIELDS)


def _leaf(cond, f):
    fact = cond.get("fact"); op = cond.get("op", "truthy"); want = cond.get("value")
    if op not in OPS: raise ValueError("unknown op %r" % op)
    have = f.get(fact)
    if op == "truthy": return bool(have)
    if have is None: return False
    if op == "eq": return have == want
    if op == "ne": return have != want
    if op == "ge": return have >= want
    if op == "gt": return have > want
    if op == "le": return have <= want
    if op == "lt": return have < want
    if op == "contains": return want in (have or [])
    if op == "not_contains": return want not in (have or [])
    if op == "in": return have in (want or [])
    return False


def evaluate(cond, f):
    """A condition is DATA: all/any/not around leaves. Nothing here evaluates code."""
    if cond is None: return True
    if "all" in cond: return all(evaluate(c, f) for c in cond["all"])
    if "any" in cond: return any(evaluate(c, f) for c in cond["any"])
    if "not" in cond: return not evaluate(cond["not"], f)
    return _leaf(cond, f)


def applies_to(rule, board_facts):
    """(applies, why). UNIVERSAL applies everywhere; NOT_APPLICABLE never applies and must say why;
    CONDITIONAL applies where its condition holds against this board's facts."""
    a = rule.get("applicability")
    if a == "UNIVERSAL_FOR_THIS_PROJECT": return True, "universal for this project"
    if a == "NOT_APPLICABLE": return False, rule.get("condition", {}).get("reason", "declared not applicable")
    c = rule.get("condition")
    if not c: return False, "conditional with no condition: treated as not applying, and validate() refuses it"
    try: ok = evaluate(c, board_facts)
    except ValueError as e: return False, "condition unreadable: %s" % e
    return ok, ("the board's facts satisfy the condition" if ok else "the board's facts do not satisfy the condition")


# The fields that can change a board's RESULT. A fingerprint over these is the identity evidence records, and a
# fingerprint over everything else would make documenting a source invalidate a DRC run about another rule.
# 16 September 2026: the first version hashed the whole rule. Writing down which clause of a vendor datasheet a
# limit comes from then marked every board's evidence stale, which taxes the one activity this audit exists to
# encourage. What makes evidence stale is a change to what the rule DEMANDS, not to how it is explained.
DECIDING = ("id", "requirement", "applicability", "condition", "release_effect", "acceptance_criteria",
            "verification_method", "verification_phase", "boards_affected", "interfaces_affected",
            "waiver_policy", "threshold", "limit", "tolerance")


def ref_prefix(ref):
    """The LETTERS of a reference designator, which is its prefix: `TP6` -> TP, `LED11` -> LED, `D2` -> D.

    It lives here because three tools now decide something by a prefix and each of them got it wrong the same
    way first, by taking the first CHARACTER: `derate.py` read a test point as a tantalum and an indicator as
    an inductor, and `reliability.py` read a transient suppressor as a mechanical part. A prefix is compared
    EXACTLY against a list, and a prefix nobody has classified falls out of the list rather than into it.
    """
    if not ref: return ""
    return ref[:len(ref) - len(ref.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ_"))].rstrip("_")


def fingerprint(reg=None):
    """The identity evidence records: a digest of every rule's DECIDING fields. Change what a rule demands and
    evidence taken under the old demand is stale by construction rather than by anyone remembering. Change a
    rationale, a source citation or a short name and the evidence stands, because the board was not asked
    anything different."""
    reg = reg or load()
    body = json.dumps({"schema": reg.get("schema_version"),
                       "rules": [{k: r[k] for k in DECIDING if k in r} for r in reg.get("rules", [])]},
                      sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def documentation_digest(reg=None):
    """The whole registry, deciding fields and prose alike. Not an evidence identity: a change marker for the
    record, so a document can say which text it was generated from."""
    reg = reg or load()
    return hashlib.sha256(json.dumps(reg, sort_keys=True, default=str).encode()).hexdigest()[:16]


def by_id(reg=None):
    reg = reg or load()
    return {r["id"]: r for r in reg["rules"]}


def rules_for(letter, reg=None, f=None):
    """[(rule, why)] for the rules that apply to one board letter."""
    reg = reg or load(); f = (f if f is not None else facts()).get(letter, {})
    out = []
    for r in reg["rules"]:
        b = r.get("boards_affected")
        if isinstance(b, list) and b and letter not in b and "ALL" not in b: continue
        ok, why = applies_to(r, f)
        if ok: out.append((r, why))
    return out


def condition_facts(cond, out=None):
    """Every fact name a condition reads, at any depth. Used by validate to prove a rule can apply at all."""
    out = set() if out is None else out
    if not isinstance(cond, dict): return out
    for k in ("all", "any"):
        for c in (cond.get(k) or []): condition_facts(c, out)
    if isinstance(cond.get("not"), dict): condition_facts(cond["not"], out)
    if cond.get("fact"): out.add(cond["fact"])
    return out


def validate(reg=None, path=None):
    """(errors, warnings). The shape, the allowed values, and the source policy: a BLOCKER that claims a
    VERIFIED source must name one, a CONDITIONAL rule must carry a machine-readable condition, a rule whose
    source is unverified may not also claim to be ENFORCED as a blocker without saying so."""
    reg = reg or load(path)
    errs, warns = [], []
    seen = set()

    _cov = [None]

    def cov_maturity(rid):
        """The LIVE maturity, from the coverage map, which owns it. Read once and lazily.

        ABSENT IS TOLERATED AND UNREADABLE IS NOT (16 September 2026). This caught everything with one
        `except BaseException: {}`, so a coverage file that would not PARSE became an empty map and every
        maturity read None: the false-positive-analysis policy, which is the only thing standing between an
        ENFORCED blocker and a board refused for a reason nobody wrote down, quietly stopped being checked and
        `validate` printed 0 errors. It happened today, on a missing comma in a flow mapping, and the validator
        said the registry was fine while `rules_status` could not read the file at all. A tree that has no
        coverage map is a tree being set up; a tree whose coverage map is broken is a tree lying to itself."""
        if _cov[0] is None:
            path_ = os.path.join(HERE, "pcb_rules_coverage.yaml")
            if not os.path.exists(path_):
                _cov[0] = {}
            else:
                try:
                    _cov[0] = (_yaml().safe_load(open(path_)) or {}).get("coverage", {})
                except BaseException as e:
                    _cov[0] = {}
                    errs.append("pcb_rules_coverage.yaml exists and does not parse (%s: %s). Every rule's LIVE "
                                "maturity is read from it, so the policy that an ENFORCED blocker must carry a "
                                "false-positive analysis cannot be checked at all while this stands"
                                % (type(e).__name__, str(e).splitlines()[0][:120]))
        return ((_cov[0].get(rid) or {}).get("maturity"))
    for i, r in enumerate(reg.get("rules", [])):
        rid = r.get("id", "<no id at index %d>" % i)
        for k in REQUIRED:
            if k not in r: errs.append("%s: missing %s" % (rid, k))
        if rid in seen: errs.append("%s: duplicate id" % rid)
        seen.add(rid)
        def one_of(field, allowed):
            v = r.get(field)
            vs = v if isinstance(v, list) else [v]
            for x in vs:
                if x not in allowed: errs.append("%s: %s %r is not one of %s" % (rid, field, x, ", ".join(allowed)))
        one_of("domain", DOMAINS); one_of("classification", CLASSIFICATIONS); one_of("applicability", APPLICABILITY)
        one_of("risk_class", RISKS); one_of("release_effect", EFFECTS); one_of("source_status", SOURCE_STATUS)
        one_of("verification_method", METHODS); one_of("verification_phase", PHASES)
        one_of("automation_feasibility", FEASIBILITY); one_of("maturity_at_writing", MATURITY); one_of("owner", OWNERS)
        if r.get("applicability") == "CONDITIONAL" and not r.get("condition"):
            errs.append("%s: CONDITIONAL with no machine-readable condition" % rid)
        if r.get("applicability") == "NOT_APPLICABLE" and not (r.get("condition") or {}).get("reason"):
            errs.append("%s: NOT_APPLICABLE with no recorded reason" % rid)
        if r.get("condition") and r.get("applicability") == "CONDITIONAL":
            try: evaluate(r["condition"], {})
            except ValueError as e: errs.append("%s: condition is unreadable (%s)" % (rid, e))
        srcs = r.get("sources") or []
        if r.get("source_status") == "VERIFIED":
            if not srcs: errs.append("%s: source_status VERIFIED with no source" % rid)
            for s in srcs:
                for k in ("title", "issuer", "url_or_path"):
                    if not s.get(k): errs.append("%s: a VERIFIED source is missing %s" % (rid, k))
        if r.get("release_effect") == "BLOCKER" and r.get("source_status") == "SOURCE_UNVERIFIED" \
           and r.get("maturity_at_writing") not in ("SOURCE_UNVERIFIED", "OWNER_DECISION_REQUIRED"):
            errs.append("%s: a BLOCKER on an unverified source must carry maturity SOURCE_UNVERIFIED or "
                        "OWNER_DECISION_REQUIRED, so the gap is visible" % rid)
        if r.get("classification") == "HEURISTIC" and r.get("release_effect") == "BLOCKER":
            errs.append("%s: a HEURISTIC may not be a BLOCKER; raise its classification with a source or "
                        "lower its release effect" % rid)
        if r.get("automation_feasibility") == "AUTOMATABLE" and r.get("implementation_location") in (None, "", "NONE_YET") \
           and r.get("maturity_at_writing") == "ENFORCED":
            errs.append("%s: ENFORCED with no implementation location" % rid)
        # PROCESS CONTROL 4 (owner instruction, 16 September 2026): no hard gate without authority, applicability,
        # acceptance criteria AND A FALSE-POSITIVE ANALYSIS. This project has shipped gates that refused correct
        # boards five times in a week: a predictor that called 244 normal plane pads a defect, a DRC judgement that
        # failed a pre-route board for being unrouted, a netlist comparison that read KiCad's unconnected-pin
        # placeholder as a net, a pour coverage measured against a rectangle the board is not, and a return-path
        # rule that refused an opto inhibit. A rule that can refuse a board has to say what a WRONG refusal would
        # look like and what stops it, or the next one is found by a board being wrong for a week.
        if r.get("release_effect") == "BLOCKER" and cov_maturity(rid) == "ENFORCED" \
           and len(str(r.get("false_positive_analysis") or "").strip()) < 80:
            errs.append("%s: an ENFORCED BLOCKER with no false-positive analysis. Say what a wrong refusal would "
                        "look like and what stops it" % rid)
        w = r.get("waiver_policy")
        if isinstance(w, dict) and w.get("allowed") and not w.get("authority"):
            errs.append("%s: a waivable rule must name the authority" % rid)
        if r.get("release_effect") == "BLOCKER" and r.get("risk_class") and "SAFETY" in (
                r["risk_class"] if isinstance(r["risk_class"], list) else [r["risk_class"]]):
            if isinstance(w, dict) and w.get("allowed") and r.get("classification") == "REGULATORY":
                errs.append("%s: a regulatory safety requirement is not waivable" % rid)
        if r.get("maturity_at_writing") == "ENFORCED" and not (r.get("evidence_scope")):
            warns.append("%s: ENFORCED without an evidence scope: evidence cannot be shown to be current" % rid)
    bf = board_facts()
    for letter in (reg.get("manifest") or {}).get("boards", []):
        if letter not in bf: warns.append("manifest board %s has no facts entry" % letter)
    # A CONDITION THAT NAMES A FACT NOBODY DECLARES APPLIES TO NOBODY, SILENTLY (17 September 2026).
    # `_leaf` answers False for a fact a board does not carry, which is the safe answer for a leaf and the
    # wrong one for a rule: SCH-001 and SCH-002, both BLOCKERS, are conditional on `has_schematic` and only
    # board E5 declared it (false), so "the schematic's ERC is clean" and "the board is the netlist it was
    # placed from" applied to NO BOARD AT ALL and neither appeared on any board's page. Board A's committed
    # board is missing the six charger filter parts its own schematic gained, and nothing said so. It is the
    # TRN-001 shape of the same morning, one level down: an applicability nobody can satisfy is indistinguishable
    # from a rule that does not exist. A board that a rule names must DECLARE every fact the rule asks about,
    # with the answer, so "does not apply" is a statement rather than an accident.
    for r in reg["rules"]:
        names = condition_facts(r.get("condition") or {})
        if not names: continue
        aff = r.get("boards_affected") or []
        for letter in sorted(bf):
            if not isinstance(bf.get(letter), dict) or str(letter).startswith("_"): continue
            if isinstance(aff, list) and aff and letter not in aff and "ALL" not in aff: continue
            for n in sorted(names):
                if n not in bf[letter]:
                    errs.append("%s: its condition reads fact %r and board %s does not declare it, so the rule "
                                "cannot apply to that board and its absence is invisible" % (r["id"], n, letter))
    return errs, warns


def main(argv):
    cmd = (argv[0] if argv else "validate")
    path = argv[1] if len(argv) > 1 and not argv[1].startswith("-") else None
    if cmd == "validate":
        reg = load(path); errs, warns = validate(reg, path)
        for w in warns: print("warn  %s" % w)
        for e in errs: print("ERROR %s" % e)
        print("rules_lib: %d rule(s), %d error(s), %d warning(s), fingerprint %s"
              % (len(reg["rules"]), len(errs), len(warns), fingerprint(reg)))
        return 1 if errs else 0
    if cmd == "fingerprint":
        print(fingerprint(load(path))); return 0
    if cmd == "facts":
        print(json.dumps(facts(), indent=1, sort_keys=True)); return 0
    if cmd == "applicable" and len(argv) > 1:
        rs = rules_for(argv[1])
        for r, why in rs: print("%-10s %-22s %s" % (r["id"], r["domain"], why))
        print("rules_lib: %d rule(s) apply to board %s" % (len(rs), argv[1]))
        return 0
    print(__doc__); return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
