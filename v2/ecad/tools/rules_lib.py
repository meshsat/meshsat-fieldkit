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
  rules_lib.py requirements [<registry>] [--needs <CONOPS.md>]
                                          the requirements registry pcb_requirements.yaml (MESHSAT-1357): its
                                          vocabularies, every need, rule, decision and ruling it names, the TBD
                                          and hedged-number policy, and the needs against CONOPS; exits 0/1
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


def rule_fingerprint(rule):
    """The identity of ONE rule's demands, the same DECIDING fields the set fingerprint is built from.

    WHY A SET FINGERPRINT IS NOT ENOUGH (17 September 2026). Correcting ten rules' board lists this afternoon
    marked THREE HUNDRED readings stale, and all but fifteen of them were about rules whose demands had not
    changed: the sweep re-took them in six minutes and the set-level ones by hand in twenty, which is a tax
    paid every time the registry is corrected, on exactly the activity this audit exists to encourage. A
    reading is stale when THE RULE IT DECIDES changed, and a verdict names the rules it decides, so it can
    carry one digest per rule and be judged rule by rule.
    """
    return hashlib.sha256(json.dumps({k: rule[k] for k in DECIDING if k in rule},
                                     sort_keys=True, default=str).encode()).hexdigest()[:16]


def rule_fingerprints(reg=None):
    """{rule id: digest} for the whole registry."""
    reg = reg or load()
    return {r["id"]: rule_fingerprint(r) for r in reg.get("rules", []) if r.get("id")}


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


# ================================================================================================================
# THE REQUIREMENTS REGISTRY (MESHSAT-1357, foundation baseline, 26 September 2026).
#
# `pcb_requirements.yaml` sits ABOVE the rule registry. A rule says what a board must satisfy; a requirement says
# what the kit must do, traces to a need of v2/docs/CONOPS.md, and names the rules and decisions that judge or
# settle part of it. It never changes the rule registry, whose fingerprint pins every verdict, so nothing below
# touches `fingerprint`, `rule_fingerprint` or DECIDING. This module is its only reader, the way it is the rule
# registry's, and `rules_render.py` generates v2/docs/REQUIREMENTS-TRACE.md from it.
#
# The checks are the owner's evidence discipline made mechanical: every id a record names exists; a number that
# is not known is written TBD and carries the effect of not knowing it; a PROVISIONAL or inferred figure is never
# the pass line of a record that can block a release; a deferred record (owner ruling D-01, staged acceptance) never
# blocks; a result names the file it was read from; and the needs are the ones CONOPS publishes, pinned by content.
# ================================================================================================================
import re as _re

REQUIREMENTS = os.path.join(HERE, "pcb_requirements.yaml")
DECISIONS = os.path.join(HERE, "pcb_decisions.yaml")
INTERFACES = os.path.join(HERE, "pcb_interfaces.yaml")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))     # tools -> ecad -> v2 -> the repository
# `feasibility` (FEA-nnn, 26 September 2026): an ARCHITECTURE FEASIBILITY BLOCKER. The review of that day (section 3,
# checkpoint item 1) asks that every prototype-core function whose feasibility is not closed appear as an explicit
# blocker, not as a reviewer's question: each names its feasibility page and the page's own blocker ids, the evidence
# that closes it, its owner, and what it holds. An open one never reads PASS, and nothing it holds does either.
REQ_KINDS = {"requirement": "REQ", "constraint": "CON", "assumption": "ASM", "choice": "CHO",
             "superseded": "SPD", "conflict": "CFL", "feasibility": "FEA"}
REQ_STATUS = ("DEFINED", "TBD", "SUPERSEDED", "CONFLICT_OPEN", "CONFLICT_RESOLVED", "FEASIBILITY_OPEN",
              "FEASIBILITY_CLOSED")
REQ_RESULTS = ("PASS", "FAIL", "INCONCLUSIVE", "NOT_JUDGED", "NOT_YET_TESTED", "NOT_APPLICABLE")
REQ_EFFECTS = EFFECTS + ("NONE",)
PROTOTYPE_1 = ("core", "deferred")
# NEED_DEFAULT: the record follows its need's place in the core; NAMED: an owner ruling names the function; SESSION:
# taken by the session under the owner's standing rule of 26 September 2026 (a `session_choices` entry says which).
P1_BASIS = ("NEED_DEFAULT", "NAMED", "SESSION")
SOURCE_CHECK = ("VERIFIED", "INFERRED")
RULE_COVERAGE = ("FULL", "PARTIAL", "NONE")
# OWNER_ACTION: something the owner has ruled that he will do or set himself (D-06's mission duration), which records
# wait on. The case measurement D-08 first asked of him was withdrawn by his own reversal of 26 September 2026.
ITEM_CLASSES = ("OWNER", "OWNER_ACTION", "SESSION", "CONDITIONAL", "LATER")
# THE EVIDENCE CLASS of a record's own reading, in the six classes `rules_status.evidence_class` gives every rule-board
# reading (v2/docs/CURRENT-EVIDENCE.md; the suite holds the two lists equal). The review of 26 September 2026, section 1:
# a reading awaiting revalidation never decides, desk reviews and physical tests are kept apart, and acceptance binds to
# the exact artefact. So a record reads PASS only on a class that counts, a desk or physical reading names by content
# every file it read (`evidence_bound_to`, "path@sha256/16"), and a PHYSICAL_TEST needs built hardware.
REQ_EVIDENCE_CLASSES = ("CURRENT_CANDIDATE", "VALID_HISTORICAL", "AWAITING_REVALIDATION", "DESK_REVIEW",
                        "PHYSICAL_TEST", "NO_EVIDENCE")
REQ_PASS_CLASSES = ("CURRENT_CANDIDATE", "VALID_HISTORICAL", "DESK_REVIEW", "PHYSICAL_TEST")
REQ_BOUND_CLASSES = ("CURRENT_CANDIDATE", "DESK_REVIEW", "PHYSICAL_TEST")
BOARD_LETTERS = ("a", "b", "c", "d", "e", "e5", "p")
ELEMENTS = ("a", "b", "c", "d", "e", "e5", "p", "kit", "case", "sw", "fw_panel", "fw_sensor", "fw_ioctrl", "procedure")
REQ_REQUIRED = ("id", "kind", "parent", "statement", "acceptance", "allocated_to", "verification_method",
                "verification_phase", "status", "evidence_result", "release_effect", "source", "source_check")
REQ_TOP = ("schema_version", "sources_read_at", "needs_document", "needs_document_sha256", "needs",
           "owner_rulings", "session_choices", "open_items", "closed_items", "records")
_TBD = _re.compile(r"\bTBD\b")
# A HEDGED NUMBER: a quantity with a unit beside a word that says nobody measured it. In a BLOCKER's pass line it is
# a guess dressed as a gate, which is exactly what the foundation baseline exists to stop (standing condition 2).
_HEDGE = _re.compile(r"\b(PROVISIONAL|about|approximately|approx|roughly|circa|INFERRED|assumed|estimated?|"
                     r"expected)\b|~", _re.I)
_QUANTITY = _re.compile(r"(?<![A-Za-z0-9.])[+-]?\d+(?:\.\d+)?\s?(?:%|mV|V|mA|A|mW|W|kWh|Wh|mm|cm|km|m|K|C|ms|us|s|"
                        r"min|h|dBm|dBi|dB|kV|kHz|MHz|GHz|Hz|Mbit/s|Gbit/s|mOhm|ohm|kg|g|RH)(?![A-Za-z0-9])")
_ID = _re.compile(r"^([A-Z]{3})-(\d{3})$")
_DATE = _re.compile(r"^\d{4}-\d{2}-\d{2}$")
_NEED_ROW = _re.compile(r"^\|\s*(NEED-\d{2})\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|\s*$")
_FILE_REF = _re.compile(r"(?:v2/|README\.md)[^\s,;()]*\.(?:py|yaml|md|pdf|net|json|txt|tsv|kicad_sch|kicad_pcb)")
_BINDING = _re.compile(r"^((?:v2/|README\.md)[^\s@]*)@([0-9a-f]{16})$")
_COMMIT = _re.compile(r"^commit ([0-9a-f]+)$")


def load_requirements(path=None):
    """The requirements registry as a dict. The ONLY place pcb_requirements.yaml is parsed."""
    path = path or REQUIREMENTS
    if not os.path.exists(path): raise SystemExit("rules_lib: no requirements registry at %s" % path)
    d = _yaml().safe_load(open(path, encoding="utf-8")) or {}
    if not isinstance(d.get("records"), list):
        raise SystemExit("rules_lib: %s has no `records` list" % path)
    return d


def decisions_index(path=None):
    """{n: decision} from pcb_decisions.yaml, the owner-decision index this registry cross-checks."""
    path = path or DECISIONS
    if not os.path.exists(path): return {}
    return {int(x["n"]): x for x in (_yaml().safe_load(open(path, encoding="utf-8")) or {}).get("decisions", [])}


def interface_names(path=None):
    """The interface names of pcb_interfaces.yaml, which a record may be allocated to."""
    path = path or INTERFACES
    if not os.path.exists(path): return set()
    return set(((_yaml().safe_load(open(path, encoding="utf-8")) or {}).get("interfaces") or {}).keys())


_NEEDS_HEAD = _re.compile(r"^\|\s*ID\s*\|\s*Need\s*\|\s*Source\s*\|$")
_TABLE_SEP = _re.compile(r"^\|(\s*:?-{3,}:?\s*\|)+$")


class NeedsTableError(ValueError):
    """CONOPS's needs table cannot be read as ONE table of distinct needs."""


def conops_needs(path):
    """{NEED-nn: statement}, whitespace normalised, from THE needs table of CONOPS section 2 and nothing else.

    The needs table is the table under the header row `| ID | Need | Source |`. Its rows are read until the table
    ends, and never past the next `## ` heading. Every row of it must be `| NEED-nn | need | source |`, and a NEED id
    may appear once. Anything else is refused (NeedsTableError), never resolved by letting a later row win.

    The first version read every three-column row anywhere in the document whose first cell was NEED-nn, and a later
    row overwrote an earlier one. The round-3 challenge (MESHSAT-1357) found that a scope table in section 2a
    (`| NEED-03 | core | ... |`) was then read as six need statements. A NEED-keyed table elsewhere in the document
    is not the needs table and is not read."""
    lines = open(path, encoding="utf-8").read().split("\n")
    heads = [i for i, l in enumerate(lines) if _NEEDS_HEAD.match(l.strip())]
    if not heads:
        raise NeedsTableError("%s has no needs table: no header row '| ID | Need | Source |'" % os.path.basename(path))
    if len(heads) > 1:
        raise NeedsTableError("%s has %d needs tables (header rows at lines %s); exactly one is read"
                              % (os.path.basename(path), len(heads), ", ".join(str(i + 1) for i in heads)))
    out, i = {}, heads[0] + 1
    if i < len(lines) and _TABLE_SEP.match(lines[i].strip()): i += 1
    for k in range(i, len(lines)):
        line = lines[k].rstrip()
        if not line.startswith("|"): break     # the table ends (a `## ` heading is not a row either, so it ends it too)
        m = _NEED_ROW.match(line)
        if not m:
            raise NeedsTableError("%s line %d is a row of the needs table and not '| NEED-nn | need | source |': %r"
                                  % (os.path.basename(path), k + 1, line[:60]))
        if m.group(1) in out:
            raise NeedsTableError("%s line %d repeats %s; each need appears once in the needs table"
                                  % (os.path.basename(path), k + 1, m.group(1)))
        out[m.group(1)] = " ".join(m.group(2).split())
    if not out: raise NeedsTableError("%s's needs table has no rows" % os.path.basename(path))
    return out


def owner_core_needs(req):
    """The needs the owner's prototype-scope ruling D-01 names as prototype 1's core (the ruling carrying core_needs)."""
    for r in req.get("owner_rulings") or []:
        if r.get("core_needs"): return list(r["core_needs"])
    return []


def core_needs(req):
    """Prototype 1's core needs: the owner's list, then any need a session choice adds under the owner's standing rule
    of 26 September 2026 (`adds_core_needs`; SOS joined the core that way). The two stay distinguishable: the owner's
    list is `owner_core_needs`, and the trace page says which choice added what."""
    out = owner_core_needs(req)
    for c in req.get("session_choices") or []:
        if c.get("withdrawn_on"): continue          # a withdrawn choice adds nothing (it keeps its row as history)
        for n in c.get("adds_core_needs") or []:
            if n not in out: out.append(n)
    return out


def requirement_is_tbd(rec):
    return bool(_TBD.search(str(rec.get("acceptance") or "")))


def binding_state(binding, root=None):
    """For one `evidence_bound_to` entry "path@sha16": (path, recorded sha16, sha16 in this tree or None), or None when
    the entry is not of that form."""
    m = _BINDING.match(str(binding))
    if not m: return None
    p = os.path.join(root or REPO_ROOT, m.group(1))
    have = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.isfile(p) else None
    return m.group(1), m.group(2), have


def rule_classes_from_audit(audit_dir=None):
    """{(rule, board letter): evidence class} from out/rule-audit/<L>.json, which rules_status.py writes, or None when
    the audits are absent (a fresh worktree: they are gitignored). It reads the audit files only, never recomputes."""
    audit_dir = audit_dir or os.path.join(os.path.dirname(HERE), "out", "rule-audit")
    out, seen = {}, False
    for L in BOARD_LETTERS:
        p = os.path.join(audit_dir, "%s.json" % L)
        if not os.path.exists(p): continue
        seen = True
        for row in (json.load(open(p)).get("rows") or []):
            if row.get("evidence_class"): out[(row["rule"], L)] = row["evidence_class"]
    return out if seen else None


def _commit_exists(root, sha):
    """True or False when git can answer in `root`, None when it cannot (no git, or not a work tree)."""
    import subprocess as _sp
    try:
        r = _sp.run(["git", "-C", root, "cat-file", "-e", "%s^{commit}" % sha], capture_output=True, timeout=20)
        if r.returncode == 0: return True
        probe = _sp.run(["git", "-C", root, "rev-parse", "--git-dir"], capture_output=True, timeout=20)
    except Exception:
        return None
    return False if probe.returncode == 0 else None


def validate_requirements(req=None, path=None, root=None, rules=None, decisions=None, interfaces=None, needs_doc=None,
                          rule_classes=None):
    """(errors, warnings) for the requirements registry. Every argument has the tree's own default, and a fixture
    passes its own so a defective registry can be shown to FAIL without touching the tree.

    `needs_doc` is the CONOPS the needs are quoted from. When it is absent the needs cannot be compared, which is a
    WARNING and not a pass: a worker tree holds the registry before the document is published beside it, and the
    test that compares them says so by skipping rather than by reading green."""
    req = req if req is not None else load_requirements(path)
    root = root or REPO_ROOT
    rule_ids = set(rules) if rules is not None else {r["id"] for r in load()["rules"]}
    dec = decisions if decisions is not None else decisions_index()
    ifaces = set(interfaces) if interfaces is not None else interface_names()
    errs, warns = [], []
    for k in REQ_TOP:
        if k not in req: errs.append("the registry has no top-level %s" % k)

    # --- needs, and the document they are quoted from
    needs = {}
    for n in req.get("needs") or []:
        nid = n.get("id")
        if not _re.match(r"^NEED-\d{2}$", str(nid)): errs.append("need %r is not NEED-nn" % nid)
        if nid in needs: errs.append("need %s is listed twice" % nid)
        if not str(n.get("statement") or "").strip(): errs.append("need %s has no statement" % nid)
        needs[nid] = " ".join(str(n.get("statement") or "").split())
    doc = needs_doc or os.path.join(root, str(req.get("needs_document") or "v2/docs/CONOPS.md"))
    if os.path.exists(doc):
        import hashlib as _h
        have = _h.sha256(open(doc, "rb").read()).hexdigest()
        if have != req.get("needs_document_sha256"):
            errs.append("%s has changed since its needs were quoted here (pinned %s, now %s): re-read the needs table, "
                        "bring `needs` into line and put the new sha256 in needs_document_sha256"
                        % (req.get("needs_document"), str(req.get("needs_document_sha256"))[:16], have[:16]))
        try: published = conops_needs(doc)
        except NeedsTableError as e:
            errs.append("the needs of %s cannot be read: %s" % (req.get("needs_document"), e)); published = dict(needs)
        for nid, st in sorted(needs.items()):
            if nid not in published: errs.append("%s is quoted here and is not in %s" % (nid, req.get("needs_document")))
            elif published[nid] != st: errs.append("%s is quoted differently from %s" % (nid, req.get("needs_document")))
        for nid in sorted(set(published) - set(needs)):
            errs.append("%s is in %s and not quoted here, so nothing can trace to it" % (nid, req.get("needs_document")))
    else:
        warns.append("%s is not in this tree, so the quoted needs are not compared with it"
                     % (req.get("needs_document") or "the needs document"))

    # --- owner rulings, cross-checked with the decision index
    rulings = {}
    for r in req.get("owner_rulings") or []:
        rid = r.get("id")
        if rid in rulings: errs.append("owner ruling %s is listed twice" % rid)
        rulings[rid] = r
        if r.get("authority") != "OWNER": errs.append("owner ruling %s: authority %r is not OWNER" % (rid, r.get("authority")))
        if not _DATE.match(str(r.get("ruled_on") or "")): errs.append("owner ruling %s: ruled_on is not a date" % rid)
        if not str(r.get("ruling") or "").strip(): errs.append("owner ruling %s says nothing" % rid)
        for n in r.get("core_needs") or []:
            if n not in needs: errs.append("owner ruling %s names %s in the core, and no such need exists" % (rid, n))
        if r.get("decision") is not None:
            d = dec.get(int(r["decision"]))
            if d is None:
                errs.append("owner ruling %s names decision %s, which pcb_decisions.yaml does not hold" % (rid, r["decision"]))
            elif d.get("status") == "open":
                warns.append("owner ruling %s (%s) is decision %s, which pcb_decisions.yaml still reads open: record the "
                             "ruling there with authority OWNER" % (rid, r.get("ruled_on"), r["decision"]))
            elif d.get("status") != "ruled" or d.get("authority") != "OWNER" or str(d.get("ruled_on")) != str(r.get("ruled_on")):
                errs.append("owner ruling %s says decision %s was ruled by the owner on %s; pcb_decisions.yaml says %s, %s, %s"
                            % (rid, r["decision"], r.get("ruled_on"), d.get("status"), d.get("authority"), d.get("ruled_on")))
    # A REVERSED RULING (D-08, 26 September 2026: the owner withdrew the case measurement he had ruled that morning)
    # keeps its row so the history reads true, names the ruling that reversed it, and is cited by nothing as current.
    for rid, r in rulings.items():
        rb = r.get("reversed_by")
        if rb is None: continue
        if rb not in rulings:
            errs.append("owner ruling %s is reversed by %r, which is not an owner ruling here" % (rid, rb))
        elif str(rulings[rb].get("ruled_on")) < str(r.get("ruled_on")):
            errs.append("owner ruling %s is reversed by %s, which was ruled before it" % (rid, rb))
        if r.get("core_needs"): errs.append("owner ruling %s carries the core and is reversed" % rid)
    reversed_ = {rid for rid, r in rulings.items() if r.get("reversed_by")}
    if not owner_core_needs(req):
        errs.append("no owner ruling names prototype 1's core (core_needs), so no record can say core or deferred")

    # --- session choices: what the session took under the owner's standing rule of 26 September 2026. Each is the
    # session's, never the owner's, and names the owner ruling that lets the session take it, so it can be reversed.
    choices = {}
    for c in req.get("session_choices") or []:
        cid = c.get("id")
        if not _re.match(r"^SC-\d{2}$", str(cid)): errs.append("session choice %r is not SC-nn" % cid)
        if cid in choices: errs.append("session choice %s is listed twice" % cid)
        choices[cid] = c
        if c.get("authority") != "SESSION": errs.append("session choice %s: authority %r is not SESSION" % (cid, c.get("authority")))
        if c.get("under") not in rulings:
            errs.append("session choice %s is taken under %r, which is not an owner ruling here" % (cid, c.get("under")))
        if not _DATE.match(str(c.get("taken_on") or "")): errs.append("session choice %s: taken_on is not a date" % cid)
        for k in ("question", "taken"):
            if not str(c.get(k) or "").strip(): errs.append("session choice %s has no %s" % (cid, k))
        if len(str(c.get("why") or "").strip()) < 20: errs.append("session choice %s says no why" % cid)
        for n in c.get("adds_core_needs") or []:
            if n not in needs: errs.append("session choice %s adds %s to the core, and no such need exists" % (cid, n))
        # A WITHDRAWN CHOICE (SC-06, the pack's road route, withdrawn on 26 September 2026 after the review of that
        # day): its row stays with the date and the reason, and nothing may rest on it.
        if c.get("withdrawn_on") is not None or c.get("withdrawn_why") is not None:
            if not _DATE.match(str(c.get("withdrawn_on") or "")): errs.append("session choice %s: withdrawn_on is not a date" % cid)
            elif str(c["withdrawn_on"]) < str(c.get("taken_on")): errs.append("session choice %s is withdrawn before it was taken" % cid)
            if len(str(c.get("withdrawn_why") or "").strip()) < 20: errs.append("session choice %s is withdrawn with no reason" % cid)
            if c.get("closes"): errs.append("session choice %s is withdrawn and still closes %s" % (cid, ", ".join(c["closes"])))
    withdrawn = {cid for cid, c in choices.items() if c.get("withdrawn_on")}
    core = set(core_needs(req))

    # --- open items
    items = {}
    for it in req.get("open_items") or []:
        iid = it.get("id")
        if iid in items: errs.append("open item %s is listed twice" % iid)
        items[iid] = it
        if it.get("class") not in ITEM_CLASSES: errs.append("open item %s: class %r is not one of %s" % (iid, it.get("class"), ", ".join(ITEM_CLASSES)))
        if it.get("status") != "OPEN": errs.append("open item %s is not OPEN; a closed item leaves this list and becomes a ruling" % iid)
        if iid in rulings: errs.append("%s is both an open item and an owner ruling" % iid)

    # --- closed items: every item that left the open list, and the ruling or session choice that closed it
    closed = {}
    for it in req.get("closed_items") or []:
        iid = it.get("id")
        if iid in closed: errs.append("closed item %s is listed twice" % iid)
        closed[iid] = it
        if iid in items: errs.append("%s is both open and closed" % iid)
        by = it.get("closed_by")
        cm = _COMMIT.match(str(by or ""))
        if cm:
            # CLOSED BY A COMMIT (the round-4 challenge: S-06, S-17 and S-25 were answered on main by 4ec785d8 and
            # 68bc9e8f, and a registry that can only close by a ruling kept them open). The commit must be one this
            # tree holds and the closing evidence must name the file it was read in.
            if len(cm.group(1)) < 8: errs.append("closed item %s names commit %s; give at least 8 hex digits" % (iid, cm.group(1)))
            ev = str(it.get("closing_evidence") or "")
            if len(ev.strip()) < 20 or not _FILE_REF.search(ev):
                errs.append("closed item %s is closed by a commit with no closing_evidence naming the file it was read in" % iid)
            there = _commit_exists(root, cm.group(1))
            if there is False: errs.append("closed item %s is closed by commit %s, which this tree does not hold" % (iid, cm.group(1)))
            elif there is None: warns.append("closed item %s: git cannot say here whether commit %s exists" % (iid, cm.group(1)))
        elif by not in rulings and by not in choices:
            errs.append("closed item %s is closed by %r, which is neither an owner ruling, a session choice nor a commit here" % (iid, by))
        elif by in withdrawn:
            errs.append("closed item %s is closed by %s, which is withdrawn" % (iid, by))
    for cid, c in choices.items():
        for x in c.get("closes") or []:
            if (closed.get(x) or {}).get("closed_by") != cid:
                errs.append("session choice %s closes %s, and the closed items do not say so" % (cid, x))

    rule_prefixes = {str(x).split("-")[0] for x in rule_ids}
    seen = set()
    for i, r in enumerate(req.get("records") or []):
        rid = r.get("id", "<record %d>" % i)
        for k in REQ_REQUIRED:
            if k not in r: errs.append("%s: missing %s" % (rid, k))
        if rid in seen: errs.append("%s: duplicate id" % rid)
        seen.add(rid)
        kind = r.get("kind")
        m = _ID.match(str(rid))
        if kind not in REQ_KINDS: errs.append("%s: kind %r is not one of %s" % (rid, kind, ", ".join(REQ_KINDS)))
        elif not m or m.group(1) != REQ_KINDS[kind]:
            errs.append("%s: a %s is numbered %s-nnn" % (rid, kind, REQ_KINDS[kind]))
        if m and m.group(1) in rule_prefixes: errs.append("%s: its prefix is a rule-id prefix of pcb_rules.yaml" % rid)
        if r.get("parent") not in needs: errs.append("%s: parent %r is not a need of %s" % (rid, r.get("parent"), req.get("needs_document")))

        def vocab(field, allowed, many=False):
            v = r.get(field)
            if v is None: return
            for x in (v if isinstance(v, list) else [v]) if many else [v]:
                if x not in allowed: errs.append("%s: %s %r is not one of %s" % (rid, field, x, ", ".join(map(str, allowed))))
        vocab("verification_method", METHODS, many=True); vocab("verification_phase", PHASES)
        vocab("final_phase", PHASES); vocab("status", REQ_STATUS); vocab("evidence_result", REQ_RESULTS)
        vocab("release_effect", REQ_EFFECTS); vocab("source_check", SOURCE_CHECK); vocab("rule_coverage", RULE_COVERAGE)
        vocab("prototype_1_basis", P1_BASIS); vocab("evidence_phase", PHASES)
        if not r.get("verification_method"): errs.append("%s: no verification method" % rid)
        if r.get("final_phase") in PHASES and r.get("verification_phase") in PHASES \
           and PHASES.index(r["final_phase"]) < PHASES.index(r["verification_phase"]):
            errs.append("%s: final_phase %s comes before verification_phase %s" % (rid, r["final_phase"], r["verification_phase"]))
        alloc = r.get("allocated_to") or []
        if not alloc: errs.append("%s: allocated to nothing" % rid)
        for a in alloc:
            if a not in ELEMENTS and a not in ifaces:
                errs.append("%s: allocated_to %r is neither an element (%s) nor an interface of pcb_interfaces.yaml"
                            % (rid, a, " ".join(ELEMENTS)))
        sb = r.get("satisfied_by") or {}
        for x in sb.get("rules") or []:
            if x not in rule_ids: errs.append("%s: satisfied_by names rule %s, which pcb_rules.yaml does not hold" % (rid, x))
        for x in sb.get("decisions") or []:
            if int(x) not in dec: errs.append("%s: satisfied_by names decision %s, which pcb_decisions.yaml does not hold" % (rid, x))
        cov = r.get("rule_coverage")
        if kind != "superseded" and cov is None: errs.append("%s: no rule_coverage" % rid)
        if cov == "NONE" and sb.get("rules"): errs.append("%s: rule_coverage NONE while it names rules" % rid)
        if cov in ("FULL", "PARTIAL") and not sb.get("rules"): errs.append("%s: rule_coverage %s and no rule named" % (rid, cov))
        for x in r.get("rulings") or []:
            if x not in rulings: errs.append("%s: ruling %s is not an owner ruling of this registry" % (rid, x))
            elif x in reversed_:
                errs.append("%s: cites %s, which %s reversed; cite the reversal" % (rid, x, rulings[x]["reversed_by"]))
        for x in r.get("choices") or []:
            if x not in choices: errs.append("%s: choice %s is not a session choice of this registry" % (rid, x))
            elif x in withdrawn: errs.append("%s: rests on %s, which the session withdrew on %s" % (rid, x, choices[x]["withdrawn_on"]))
        if r.get("prototype_1_choice") in withdrawn:
            errs.append("%s: its scope rests on %s, which is withdrawn" % (rid, r["prototype_1_choice"]))
        for x in r.get("waits_on") or []:
            dm = _re.match(r"^decision-(\d+)$", str(x))
            if dm:
                d = dec.get(int(dm.group(1)))
                if d is None: errs.append("%s: waits on %s, which pcb_decisions.yaml does not hold" % (rid, x))
                elif d.get("status") != "open": errs.append("%s: waits on %s, which is no longer open" % (rid, x))
                elif any(str(o.get("decision")) == dm.group(1) for o in rulings.values()):
                    errs.append("%s: waits on %s, which an owner ruling here has ruled; cite the ruling" % (rid, x))
            elif x in closed: errs.append("%s: waits on %s, which %s closed; cite that instead" % (rid, x, closed[x].get("closed_by")))
            elif x in rulings: errs.append("%s: waits on %s, which is ruled; cite it under rulings" % (rid, x))
            elif x in choices: errs.append("%s: waits on %s, which the session has taken; cite it under choices" % (rid, x))
            elif x not in items: errs.append("%s: waits on %s, which is not an open item" % (rid, x))

        # --- status, TBD and the numbers in a pass line
        acc = str(r.get("acceptance") or "")
        tbd = requirement_is_tbd(r)
        st = r.get("status")
        if kind == "superseded" and st != "SUPERSEDED": errs.append("%s: a superseded record has status %s" % (rid, st))
        if kind != "superseded" and st == "SUPERSEDED": errs.append("%s: status SUPERSEDED on a %s" % (rid, kind))
        if kind == "conflict" and st not in ("CONFLICT_OPEN", "CONFLICT_RESOLVED"):
            errs.append("%s: a conflict is CONFLICT_OPEN or CONFLICT_RESOLVED, not %s" % (rid, st))
        if kind != "conflict" and st in ("CONFLICT_OPEN", "CONFLICT_RESOLVED"):
            errs.append("%s: %s on a %s" % (rid, st, kind))
        if kind == "feasibility" and st not in ("FEASIBILITY_OPEN", "FEASIBILITY_CLOSED"):
            errs.append("%s: a feasibility blocker is FEASIBILITY_OPEN or FEASIBILITY_CLOSED, not %s" % (rid, st))
        if kind != "feasibility" and st in ("FEASIBILITY_OPEN", "FEASIBILITY_CLOSED"):
            errs.append("%s: %s on a %s" % (rid, st, kind))
        if kind not in ("superseded", "conflict", "feasibility"):
            if tbd and st != "TBD": errs.append("%s: its acceptance carries a TBD and its status is %s" % (rid, st))
            if not tbd and st == "TBD": errs.append("%s: status TBD with no TBD in its acceptance" % rid)
        if kind != "superseded":
            if tbd and len(str(r.get("tbd_effect") or "").strip()) < 20:
                errs.append("%s: a TBD with no effect. Say what not knowing it blocks, or state the number with its source" % rid)
            if not tbd and r.get("tbd_effect"):
                errs.append("%s: a tbd_effect on a record whose acceptance has no TBD" % rid)
        if st in ("CONFLICT_RESOLVED", "FEASIBILITY_CLOSED") and not r.get("resolved_by"):
            errs.append("%s: resolved, and nothing says by what" % rid)
        if kind == "superseded" and not str(r.get("superseded_by") or "").strip(): errs.append("%s: superseded, and nothing says by what" % rid)
        eff = r.get("release_effect")
        if eff == "BLOCKER":
            qs = _QUANTITY.findall(acc)
            if qs and _HEDGE.search(acc):
                errs.append("%s: a BLOCKER's pass line carries a hedged number (%s beside %r). A PROVISIONAL figure goes "
                            "in `provisional`, which gates nothing; the pass line says TBD with its effect instead"
                            % (rid, ", ".join(qs[:3]), _HEDGE.search(acc).group(0)))
            if qs and r.get("source_check") == "INFERRED" and not tbd:
                errs.append("%s: a BLOCKER whose source is INFERRED states a number in its pass line (%s): verify the "
                            "source or write the number TBD with its effect" % (rid, ", ".join(qs[:3])))

        # --- prototype 1 scope (owner ruling D-01: staged acceptance)
        p1 = r.get("prototype_1")
        if kind == "superseded":
            if p1 is not None: errs.append("%s: a superseded record carries no prototype_1" % rid)
            if eff != "NONE": errs.append("%s: a superseded record has release_effect NONE, not %s" % (rid, eff))
            if r.get("evidence_result") != "NOT_APPLICABLE": errs.append("%s: a superseded record reads NOT_APPLICABLE" % rid)
        else:
            if p1 not in PROTOTYPE_1: errs.append("%s: prototype_1 %r is not core or deferred" % (rid, p1))
            basis = r.get("prototype_1_basis")
            default = "core" if r.get("parent") in core else "deferred"
            if basis == "NEED_DEFAULT" and p1 != default:
                errs.append("%s: prototype_1 %s by NEED_DEFAULT, and %s's default is %s" % (rid, p1, r.get("parent"), default))
            if basis in ("NAMED", "SESSION") and len(str(r.get("prototype_1_why") or "").strip()) < 20:
                errs.append("%s: prototype_1 by %s with no prototype_1_why" % (rid, basis))
            if basis == "SESSION" and r.get("prototype_1_choice") not in choices:
                errs.append("%s: prototype_1 taken by the session, and prototype_1_choice %r names no session choice"
                            % (rid, r.get("prototype_1_choice")))
            if basis != "SESSION" and r.get("prototype_1_choice") is not None:
                errs.append("%s: a prototype_1_choice on a record whose scope is not the session's" % rid)
            if basis is None: errs.append("%s: prototype_1 with no prototype_1_basis" % rid)
            if eff == "NONE": errs.append("%s: release_effect NONE is for superseded records" % rid)
            if p1 == "deferred" and eff == "BLOCKER":
                errs.append("%s: a deferred record is a BLOCKER. D-01 accepts prototype 1 on its core and reports the "
                            "rest NOT_YET_TESTED" % rid)
            if kind == "assumption" and eff == "BLOCKER":
                errs.append("%s: an assumption is validated or accepted, never passed, so it is not a BLOCKER" % rid)

        # --- the record's own reading
        res = r.get("evidence_result")
        if res == "NOT_YET_TESTED" and r.get("verification_phase") not in ("ASSEMBLY", "PROTOTYPE"):
            errs.append("%s: NOT_YET_TESTED is for a record that needs hardware; this one is judgeable at %s, so it is "
                        "NOT_JUDGED until it is read" % (rid, r.get("verification_phase")))
        if res == "NOT_APPLICABLE" and kind != "superseded": errs.append("%s: NOT_APPLICABLE on a live record" % rid)
        if res in ("PASS", "FAIL", "INCONCLUSIVE"):
            if r.get("evidence_phase") not in PHASES: errs.append("%s: %s with no evidence_phase" % (rid, res))
            evs = r.get("evidence") or []
            if kind != "conflict" and not evs: errs.append("%s: %s with no evidence" % (rid, res))
            for e in evs:
                if not _FILE_REF.search(str(e)): errs.append("%s: an evidence entry names no file: %r" % (rid, str(e)[:80]))
        if st == "CONFLICT_OPEN" and res != "FAIL":
            errs.append("%s: an open conflict reads FAIL on its own sources, not %s" % (rid, res))
        if res == "PASS" and st in ("TBD", "CONFLICT_OPEN", "FEASIBILITY_OPEN"):
            errs.append("%s: PASS on a record whose pass line is not settled" % rid)

        # --- the evidence class of the reading (CURRENT-EVIDENCE.md's six classes) and what it is bound to
        ec = r.get("evidence_class")
        if ec is not None and ec not in REQ_EVIDENCE_CLASSES:
            errs.append("%s: evidence_class %r is not one of %s" % (rid, ec, ", ".join(REQ_EVIDENCE_CLASSES)))
        # An open conflict with no evidence entry reads FAIL on its own cited sources by definition, which is not a
        # reading of an artefact and so carries no class; every other reading says what class it is.
        own_sources = kind == "conflict" and st == "CONFLICT_OPEN" and not r.get("evidence")
        if res in ("PASS", "FAIL", "INCONCLUSIVE") and ec is None and not own_sources:
            errs.append("%s: %s with no evidence_class: say whether the reading is current, historical, awaiting "
                        "revalidation, a desk review or a physical test" % (rid, res))
        if res not in ("PASS", "FAIL", "INCONCLUSIVE") and ec is not None:
            errs.append("%s: an evidence_class on a record that reads %s" % (rid, res))
        if res == "PASS" and ec is not None and ec not in REQ_PASS_CLASSES:
            errs.append("%s: PASS on evidence classed %s, which does not count (review of 26 September 2026, "
                        "section 1: evidence awaiting revalidation never decides)" % (rid, ec))
        if ec == "PHYSICAL_TEST" and r.get("evidence_phase") not in ("ASSEMBLY", "PROTOTYPE"):
            errs.append("%s: a PHYSICAL_TEST at %s; nothing is measured before ASSEMBLY" % (rid, r.get("evidence_phase")))
        bound = r.get("evidence_bound_to") or []
        if ec in REQ_BOUND_CLASSES and not bound:
            errs.append("%s: a %s reading names no file it is bound to (evidence_bound_to, path@sha256/16)" % (rid, ec))
        for b in bound:
            bs = binding_state(b, root)
            if bs is None:
                errs.append("%s: evidence_bound_to %r is not path@sha256/16" % (rid, str(b)[:60])); continue
            bp, want, have = bs
            if have is None:
                errs.append("%s: evidence_bound_to names %s, which is not in this tree" % (rid, bp))
            elif have != want:
                msg = ("%s: its reading is bound to %s at %s and the tree holds %s: re-read it before it decides"
                       % (rid, bp, want, have))
                (errs if res == "PASS" else warns).append(msg)
        # A PASS whose rules judge the WHOLE record rests on those rules: they must be current on its boards.
        if res == "PASS" and rule_classes is not None and r.get("rule_coverage") == "FULL":
            for x in sb.get("rules") or []:
                for L in [a for a in alloc if a in BOARD_LETTERS]:
                    c = rule_classes.get((x, L))
                    if c is not None and c not in REQ_PASS_CLASSES:
                        errs.append("%s: PASS while %s, which judges the whole record, reads %s on board %s"
                                    % (rid, x, c, L.upper()))

        # --- a feasibility blocker names its page, the page's own ids, the closing evidence, its owner and its hold
        if kind == "feasibility":
            page = str(r.get("feasibility_page") or "")
            pp = os.path.join(root, page)
            if not page or not os.path.isfile(pp):
                errs.append("%s: feasibility_page %r is not in this tree" % (rid, page))
            else:
                text = open(pp, encoding="utf-8", errors="replace").read()
                for b in r.get("blocker_ids") or []:
                    if str(b) not in text: errs.append("%s: blocker id %s is not on %s" % (rid, b, page))
            if not r.get("blocker_ids"): errs.append("%s: a feasibility blocker names none of its page's blocker ids" % rid)
            for k in ("closing_evidence", "owner"):
                if len(str(r.get(k) or "").strip()) < 20: errs.append("%s: a feasibility blocker with no %s" % (rid, k))
            if not (r.get("blocks") or r.get("holds_layout_entry")):
                errs.append("%s: a feasibility blocker that holds nothing (blocks, holds_layout_entry)" % rid)
            for L in r.get("holds_layout_entry") or []:
                if L not in BOARD_LETTERS: errs.append("%s: holds_layout_entry %r is not a board" % (rid, L))
            if st == "FEASIBILITY_OPEN" and res not in ("FAIL", "INCONCLUSIVE"):
                errs.append("%s: an open feasibility blocker reads FAIL or INCONCLUSIVE on its page, not %s" % (rid, res))
            if st == "FEASIBILITY_OPEN" and r.get("prototype_1") == "core" and eff != "BLOCKER":
                errs.append("%s: an open feasibility blocker on the core is a BLOCKER, not %s" % (rid, eff))

        rr = r.get("residual_risk_accepted")
        if rr is not None:
            if rr.get("by") != "OWNER": errs.append("%s: a residual risk is accepted by the OWNER, not %r" % (rid, rr.get("by")))
            if rr.get("ruling") not in rulings: errs.append("%s: residual risk accepted under %r, which is not a ruling here" % (rid, rr.get("ruling")))
            if not _DATE.match(str(rr.get("ruled_on") or "")): errs.append("%s: residual risk acceptance has no date" % rid)

        # --- sources
        srcs = r.get("source") or []
        if not srcs: errs.append("%s: no source" % rid)
        companions = set(req.get("companion_documents") or [])
        for s in srcs:
            s = str(s)
            if s.startswith("none (gap)"): continue
            om = _re.match(r"^owner ruling (\S+)", s)
            if om:
                if om.group(1) not in rulings: errs.append("%s: source cites %s, which is not an owner ruling here" % (rid, om.group(1)))
                continue
            cm = _re.match(r"^session choice (\S+)", s)
            if cm:
                if cm.group(1) not in choices: errs.append("%s: source cites %s, which is not a session choice here" % (rid, cm.group(1)))
                continue
            pm = _re.match(r"^((?:v2/|README\.md)[^\s:()]*)", s)
            if not pm: errs.append("%s: source %r is not a path, an owner ruling, a session choice or 'none (gap)'" % (rid, s[:60])); continue
            if not os.path.exists(os.path.join(root, pm.group(1))) and pm.group(1) not in companions:
                errs.append("%s: source %s does not exist in this tree" % (rid, pm.group(1)))
    recs = {r.get("id"): r for r in req.get("records") or []}
    for r in req.get("records") or []:
        if r.get("kind") != "feasibility": continue
        for x in r.get("blocks") or []:
            t = recs.get(x)
            if t is None: errs.append("%s: blocks %s, which is not a record here" % (r["id"], x)); continue
            if t.get("kind") in ("superseded", "feasibility"):
                errs.append("%s: blocks %s, a %s record" % (r["id"], x, t.get("kind")))
            if r.get("status") == "FEASIBILITY_OPEN" and t.get("evidence_result") == "PASS":
                errs.append("%s reads PASS while %s, which holds it, is open" % (x, r["id"]))
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
    if cmd == "requirements":
        # rules_lib.py requirements [<registry>] [--needs <CONOPS.md>]: the requirements registry's checks
        needs = argv[argv.index("--needs") + 1] if "--needs" in argv and argv.index("--needs") + 1 < len(argv) else None
        rpath = path if path and path != needs else None
        req = load_requirements(rpath); rc = rule_classes_from_audit()
        errs, warns = validate_requirements(req, needs_doc=needs, rule_classes=rc)
        if rc is None: print("warn  out/rule-audit is not in this tree: a PASS is not checked against its rules' classes")
        for w in warns: print("warn  %s" % w)
        for e in errs: print("ERROR %s" % e)
        print("rules_lib: %d requirement record(s), %d error(s), %d warning(s)" % (len(req["records"]), len(errs), len(warns)))
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
