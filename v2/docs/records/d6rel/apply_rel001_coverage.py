#!/usr/bin/env python3
"""The two shared-file changes of stream d6rel (MESHSAT-1357, finding H3-01 of the independent review of handover H3,
registry item S-89, erratum h of RELEASE-H3.md), for the INTEGRATOR to run; the stream does not edit these files.

  stage coverage    v2/ecad/tools/pcb_rules_coverage.yaml, the REL-001 entry: the fixtures name both test files, the
                    note says what the checker reads now and what this tree's artefacts read under it, the
                    remediation names what is still owed, and `evidence_not_before` puts a FLOOR under REL-001's
                    evidence at the instant the tool changed what its PASS means. The floor is what makes an old
                    word-list PASS stop counting: rules_status keeps an older reading that had its input in front of
                    a newer one that declares its input absent (v2/docs/records/d6rel/consumers-probe.txt, items 2 and
                    3). Run it BEFORE the re-take, or after: it changes no reading, it says which readings count.

  stage close-s89   v2/ecad/tools/pcb_requirements.yaml: item S-89 leaves open_items for closed_items with the commit
                    that closed it and the evidence, READ from this tree: it REFUSES to run until REL-001 has been
                    re-taken on every board of the manifest with the list this tree holds, after the floor, bound to
                    the declared phase's artefact, with every citation checked, no refusal and no missing input. The
                    re-take is the box's (gate_sweep.sh or retake_gate.sh); this script never runs a gate. The records
                    that WAIT on S-89 (on the integration tip REQ-022, REQ-024, REQ-026, REQ-028 and REQ-064) lose
                    that wait and cite the closing in their history, which is the registry's rule for a closed item
                    and what its validator asks ("cite that instead"). The item's `limits_reading` is not carried
                    into the closed entry (no closed item carries one); the closing evidence says what becomes of it.

NOTHING IN THE TEXT IT WRITES IS TYPED THAT CAN BE READ (the fresh check of 28 September 2026, m2 and m9). The counts
of the coverage note come from `reliability.judge()` on the tree the script runs in (read only: no verdict is
written), and every sentence that says what holds a board from PASS names the open items of THAT board, read from
the list for the note and from each board's own reading for the closing evidence. A board may read PASS only where
the list holds it by nothing; a PASS on a board the list holds is refused as a reading of another list.

Every stage asserts the old text is present, asserts the new text differs, re-parses the file (YAML; for the registry
also `python3 rules_lib.py requirements`, the tree's own validator, read only, before and after) and refuses a second
run. It writes nothing when an assertion fails.

Usage: apply_rel001_coverage.py --stage coverage  (--commit <merge> | --floor <ISO instant with its offset>) [--root <tree>]
       apply_rel001_coverage.py --stage close-s89 --commit <hash of the merged d6rel work> [--root <tree>] [--no-validate]
                                                  [--check]
  --check   (close-s89) ask every guard and print what the closing would say of each board; write nothing
  --root    the repository root (default: the root this script sits in, v2/docs/records/d6rel/../../../..)
  --commit  the merge that brings this stream's reliability.py into the tree: closed_by names it, and its committer
            instant (read with git in the checkout) is the floor when --floor is not given; it must be a commit the
            tree holds
  --floor   the instant before which no reliability reading counts, WITH ITS UTC OFFSET (2026-09-28T19:00:00+02:00 or
            ...Z): an instant without one is refused, because it would be read as UTC and a floor written in local
            time would then sit two hours late. NEVER A CONSTANT: the floor is the instant the repaired tool ENTERS
            THE TREE THE READINGS LIVE IN. A first draft carried the instant of the worker's last tool commit (16:46
            CEST); the integration line then re-took reliability with the UNREPAIRED tool at 16:54 CEST (1c4235ec),
            and that fixed instant would have let seven word-list PASS readings stand. Either stage refuses a floor
            that is not after every reading of the unrepaired tool the tree holds (a reading with no `candidates`
            count); the close-s89 stage reads the floor the coverage entry carries.
Prototype work: nothing here has been built or measured. An AI review, never a qualified review.
"""
import os, re, sys, json, glob, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))

OLD_NOTE_MARK = "declares 25 classes over the seven boards covering all 111 parts whose value names a connector"
NEW_NOTE_MARK = "the population is an INVENTORY (wear_inventory.py)"


def fail(msg):
    print("apply_rel001_coverage: REFUSED: %s" % msg); sys.exit(2)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def reparse_yaml(path):
    import yaml
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    if not isinstance(d, dict): fail("%s does not parse as a mapping after the change" % path)
    return d


def _tools(root):
    tools = os.path.join(root, "v2", "ecad", "tools")
    if tools not in sys.path: sys.path.insert(0, tools)
    return tools


def _instant(s):
    """One instant from a verdict's clock: a verdict writes UTC, with Z or with no offset at all."""
    import datetime as _dt
    d = _dt.datetime.fromisoformat((s or "").strip().replace("Z", "+00:00"))
    if d.tzinfo is None: d = d.replace(tzinfo=_dt.timezone.utc)
    return d


def _floor_instant(s):
    """The floor's instant, which must say its own offset (the fresh check's m9d)."""
    import datetime as _dt
    try:
        d = _dt.datetime.fromisoformat((s or "").strip().replace("Z", "+00:00"))
    except ValueError:
        fail("the floor %r is not an ISO instant" % s)
    if d.tzinfo is None:
        fail("the floor %r carries no UTC offset: write it with one (for example 2026-09-28T19:00:00+02:00), because "
             "an instant without an offset would be read as UTC" % s)
    return d


def _say(text):
    """One line of plain text that can stand inside a double-quoted YAML scalar."""
    return " ".join(str(text).split()).replace("\\", "/").replace('"', "'")


def list_facts(root):
    """What the list of this tree declares, and what holds each board from PASS, read from the list and from
    `reliability.judge()` on this tree's artefacts (read only: judge writes nothing)."""
    _tools(root)
    import yaml, reliability as REL
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_reliability.yaml")
    d = yaml.safe_load(open(p, encoding="utf-8"))
    if not isinstance(d, dict) or "inventory" not in d or not hasattr(REL, "check_open_items"):
        fail("this tree does not hold the repaired tool and its list: merge stream d6rel first")
    bad = REL.check_open_items(d)
    if bad: fail("the list is refused by the tool's own check: %s" % "; ".join(bad))
    r = REL.judge(vendor=os.path.join(root, "v2", "vendor"))
    fails = [f for v in r.values() for f in v["fails"]]
    if fails: fail("the list does not dispose this tree's artefacts: %s" % "; ".join(fails[:6]))
    missing = ["%s: %s" % (k.upper(), v["missing_input"]) for k, v in sorted(r.items()) if v.get("missing_input")]
    if missing: fail("a board of this tree cannot be read against the list: %s" % "; ".join(missing))
    kinds = dict(cited=0, none_published=0, not_mated=0, owed=0)
    docs, lowest, measures, classes, exclusions = set(), None, 0, 0, 0
    for letter, b in sorted(d["boards"].items()):
        exclusions += len(b.get("exclusions") or [])
        for c in b["classes"]:
            classes += 1
            nf = c.get("no_figure") or {}
            s = c.get("source")
            for x in (s if isinstance(s, list) else ([s] if s else [])) + (nf.get("looked_in") or []): docs.add(x["document"])
            if c.get("cycles") is not None:
                kinds["cited"] += 1
                if lowest is None or c["cycles"] < lowest[0]: lowest = (c["cycles"], c["name"], letter.upper(), c.get("part") or "")
            else:
                kinds[nf["kind"]] += 1
            if c.get("measure_owed"): measures += 1
    order = [k for k in ("a", "b", "c", "d", "e", "e5", "p") if k in r] + sorted(k for k in r if k not in ("a", "b", "c", "d", "e", "e5", "p"))
    return dict(list=d, readings=r, order=order, kinds=kinds, docs=len(docs), lowest=lowest, measures=measures,
                classes=classes, exclusions=exclusions, list_sha=sha16(p),
                holds={k: list(r[k]["held_by"]) for k in order},
                undecided={k: len(r[k]["undecided"]) for k in order})


def holds_sentence(f):
    """Which open items hold which boards, board by board, and nothing about a board that the list does not say."""
    out = []
    for k in f["order"]:
        h, u = f["holds"][k], f["undecided"][k]
        if not h: out.append("%s: nothing" % k.upper()); continue
        out.append("%s: %s%s" % (k.upper(), ", ".join(h), (" (%d of its classes have no figure because the maker states none)" % u) if u else ""))
    return "; ".join(out)


def build_entry(root, floor):
    f = list_facts(root)
    r, order = f["readings"], f["order"]
    tot = lambda key: sum(r[k][key] for k in order)
    items = f["list"]["open_items"]
    passing = [k.upper() for k in order if r[k]["result"] == "PASS"]
    note = (
        "nothing considers vibration, mating cycles or moisture for any interface 16 September 2026: THE LIST EXISTS AND IS "
        "CHECKED AGAINST THE BOARDS. 28 September 2026 (stream d6rel, S-89): %s: every component of the declared phase's "
        "netlist (board E5: its board file) is read and asked for by its reference class and its land, never by the words of "
        "its value, and every candidate is in exactly one declared class or under one declared exclusion with a visible "
        "reason and the land it speaks of, or the gate refuses. The population is the NETLIST's: a footprint only a board "
        "file carries is not in it (open item REL-O-13 of the list). On this tree's artefacts: %d candidates (%s), %d "
        "classed in %d classes, %d excluded under %d exclusions, %d refused. Of the %d classes, %d cite the maker's cycle "
        "figure to a document held under v2/vendor/ by sha256, page and words (%d documents in all), %d have no figure "
        "because the maker's documents that were read state none, %d mate nothing (solder lands, screw joints) and %d owe "
        "their figure under an open item of the list; %d measures are owed. A class whose maker publishes no figure is "
        "undecided and never lets its board read PASS. What holds each board from PASS, by the list's open items: %s. %s "
        "A missing, unreadable or empty netlist reads INCONCLUSIVE with the reason, never PASS, and so does a vendor "
        "library that is not in the tree; the netlist is the declared phase's and is recorded by sha256 and by content; "
        "each board's declaration is bound to the artefact it was written against (written_against) and another sha reads "
        "INCONCLUSIVE, because the gate cannot read a part off the value text and a substitution is a mismatch until "
        "proven. The lowest figure cited is %s. What it does NOT do is test anything: this rule is verified at the "
        "PROTOTYPE, no board has been built, and the dock block's contact targets carry the open item the mate-cycle test "
        "exists for."
        % (NEW_NOTE_MARK, tot("candidates"), ", ".join("%s %d" % (k.upper(), r[k]["candidates"]) for k in order),
           tot("covered"), f["classes"], tot("excluded"), f["exclusions"], tot("refused"), f["classes"], f["kinds"]["cited"],
           f["docs"], f["kinds"]["none_published"], f["kinds"]["not_mated"], f["kinds"]["owed"], f["measures"],
           holds_sentence(f),
           ("No board reads PASS." if not passing else "Board(s) %s read PASS: the list holds them by nothing." % ", ".join(passing)),
           ("%d mating cycles (class %s, board %s%s)" % (f["lowest"][0], f["lowest"][1], f["lowest"][2],
                                                       (", " + f["lowest"][3]) if f["lowest"][3] else "")) if f["lowest"] else "none"))
    action = (
        "28 September 2026: the checker and the list are repaired (stream d6rel, S-89). What remains of the SHEET is the "
        "list's %d open items, each with its next action in pcb_reliability.yaml and the boards it holds: %s. The TEST PLAN "
        "for the prototype is the laboratory stage and belongs with it"
        % (len(items), "; ".join("%s holds %s" % (key, ", ".join(k.upper() for k in order if key in f["holds"][k]) or "no board")
                                 for key in sorted(items))))
    why = (
        "28 September 2026, stream d6rel (finding H3-01 of the independent review of handover H3, registry item S-89, erratum h "
        "of RELEASE-H3.md): reliability.py changed what its PASS means. Until then its population was the parts whose value "
        "text matched twelve words, so an RJ45 jack, the SIM sockets and the dock's spring pins (61 parts of the set 6 "
        "netlists) were in no denominator, and a board with no netlist read PASS of zero. A reading taken before this instant "
        "is a reading of the word list and is not current evidence for REL-001 whatever it says. rules_status keeps an older "
        "reading that had its input in front of a newer one that declares its input absent, so without this floor a word-list "
        "PASS would stand in front of the repaired tool's INCONCLUSIVE (v2/docs/records/d6rel/consumers-probe.txt, items 2 and "
        "3). The instant is the one the repaired tool entered this tree, checked by the apply script to be after every "
        "reading of the unrepaired tool the tree held; a fixed instant would not have been (the integration line re-took "
        "reliability with the unrepaired tool at 16:54 CEST on 28 September 2026, after the worker's last tool commit of "
        "16:46).")
    entry = (' REL-001: {implementation: NONE_YET, verification: {tool: reliability.py, verdict: reliability, fixtures: '
             '"tests/test_reliability.py, tests/test_reliability_inventory.py"}, maturity: ENFORCED, gap_category: ABSENT,\n'
             '   evidence_not_before: {"reliability": "%s"},\n'
             '   _evidence_not_before_why: "%s",\n'
             '   note: "%s",\n'
             '   remediation: {action: "%s", owner: SESSION, execution: SEQUENTIAL, depends_on: [ENV-001], p50_h: 4, p80_h: 10}}\n'
             % (floor, _say(why), _say(note), _say(action)))
    return entry, f


def old_tool_readings_after(root, floor):
    """Every reliability reading in this tree's evidence folders that the UNREPAIRED tool wrote (no inventory count) and
    that is not before `floor`, as sentences; [] when the floor is after all of them. Every file is read, not only the
    winner rules_status would pick, because the floor is what decides which readings count."""
    _tools(root)
    import rules_status as S, phase_artefacts as PA
    m = S.manifest(); out = []
    for letter in PA.letters():
        for d in S._project_dirs(letter, m):
            for f in sorted(glob.glob(os.path.join(d, "reliability*.verdict.json"))):
                try: rec = json.load(open(f, encoding="utf-8"))
                except (OSError, ValueError): continue
                if "candidates" in (rec.get("counts") or {}): continue          # the repaired tool's reading
                try:
                    late = _instant(rec.get("ts")) >= _floor_instant(floor)
                except (ValueError, TypeError):
                    late = True
                if late:
                    out.append("board %s: the unrepaired tool's %s at %s (%s)"
                               % (letter.upper(), rec.get("verdict"), rec.get("ts"), os.path.relpath(f, root)))
    return out


def floor_for(root, floor, commit):
    """The floor: --floor as given, else the committer instant of --commit read with git in this checkout; refused unless
    it says its offset and is after every reading of the unrepaired tool this tree holds."""
    if not floor:
        if not commit:
            fail("--floor <instant> or --commit <the merge that brings reliability.py in> is required: the floor is never a constant")
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%cI", commit], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            fail("git in %s cannot give the instant of commit %s; pass --floor" % (root, commit))
        floor = r.stdout.strip()
        print("apply_rel001_coverage: the floor is the committer instant of %s: %s" % (commit, floor))
    _floor_instant(floor)
    late = old_tool_readings_after(root, floor)
    if late:
        fail("the floor %s is not after every reading of the unrepaired tool this tree holds:\n  %s\n  pass a later --floor "
             "(the instant the repaired tool entered this tree)" % (floor, "\n  ".join(late)))
    return floor


def stage_coverage(root, floor):
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")
    old = open(p, encoding="utf-8").read()
    if NEW_NOTE_MARK in old: fail("the REL-001 entry already carries the inventory note: this stage has run")
    if OLD_NOTE_MARK not in old: fail("the REL-001 note of 16 September is not in %s: the file is not the one this script was written for" % p)
    m = re.search(r"(?ms)^ REL-001: \{.*?\n(?=\n)", old)
    if not m: fail("the REL-001 entry could not be delimited")
    block = m.group(0)
    for must in ("tool: reliability.py", "verdict: reliability", "fixtures: tests/test_reliability.py", OLD_NOTE_MARK,
                 "The SHEET is DONE (17 September 2026)"):
        if must not in block: fail("the REL-001 entry does not carry %r" % must)
    if "evidence_not_before" in block: fail("the REL-001 entry already carries an evidence floor")
    new_block, f = build_entry(root, floor)
    new = old.replace(block, new_block, 1)
    if new == old: fail("the new text equals the old")
    if new.count(new_block) != 1 or NEW_NOTE_MARK not in new: fail("the replacement did not land once")
    tmp = p + ".d6rel.tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    d = reparse_yaml(tmp)
    e = (d.get("coverage") or {}).get("REL-001") or {}          # the rule entries sit under the file's `coverage` key
    ok = (e.get("evidence_not_before") == {"reliability": floor}
          and e.get("verification", {}).get("fixtures") == "tests/test_reliability.py, tests/test_reliability_inventory.py"
          and e.get("maturity") == "ENFORCED" and NEW_NOTE_MARK in (e.get("note") or "")
          and holds_sentence(f) in " ".join((e.get("note") or "").split()))
    if not ok:
        os.remove(tmp); fail("the patched REL-001 entry does not read back as written: %r" % {k: e.get(k) for k in ("evidence_not_before", "verification", "maturity")})
    os.replace(tmp, p)
    print("apply_rel001_coverage: coverage: REL-001 entry replaced in %s (sha256/16 %s -> %s); floor %s; re-parsed"
          % (os.path.relpath(p, root), hashlib.sha256(old.encode("utf-8")).hexdigest()[:16], sha16(p), floor))
    print("apply_rel001_coverage: what holds each board, as the note says it: %s" % holds_sentence(f))
    return 0


def retake_evidence(root, floor, f):
    """[(letter, verdict record, path)] of the current REL-001 reading of every board, found the way rules_status finds
    them (read only), each checked: after the floor, the list this tree holds, bound to the declared phase's artefact,
    every citation checked, no refusal, no missing input, held by exactly what the list holds the board by, and PASS
    only where the list holds it by nothing. The reasons it is not there yet are the second value."""
    _tools(root)
    import rules_status as S, phase_artefacts as PA
    lst = f["list_sha"]
    m = S.manifest()
    found, why = [], []
    for letter in PA.letters():
        rec = S._verdicts(letter, m).get("reliability")
        if rec is None:
            why.append("board %s: no reliability verdict in this tree" % letter.upper()); continue
        inp = rec.get("inputs") or {}
        li = inp.get("list") if isinstance(inp.get("list"), dict) else {}
        kind, design = PA.design_of(letter)
        c = rec.get("counts") or {}
        pb = (c.get("per_board") or {}).get(letter) or {}
        art = pb.get("artefact") if isinstance(pb.get("artefact"), dict) else {}   # the binding the repaired tool records
        problems = []
        try:
            if _instant(rec.get("ts")) < _floor_instant(floor): problems.append("taken %s, before the floor %s" % (rec.get("ts"), floor))
        except (ValueError, TypeError):
            problems.append("its timestamp %r cannot be read" % rec.get("ts"))
        if "candidates" not in c or not pb:
            problems.append("carries no counts of the inventory for the board (a reading of the word-list tool?)")
        else:
            if li.get("sha256_16") != lst: problems.append("read list %s, this tree holds %s" % (li.get("sha256_16"), lst))
            if not design: problems.append("this tree holds no %s for the board" % (kind or "artefact"))
            elif art.get("sha256_16") != design.get("sha256_16") or art.get("kind") != kind:
                problems.append("read %s %s, the declared phase's is %s %s" % (art.get("kind"), art.get("sha256_16"), kind, design.get("sha256_16")))
            if pb.get("bound") is not True: problems.append("its declaration is not bound to the artefact it read")
            if pb.get("citations_unjudged") != 0:
                problems.append("%s cited document(s) were not checked (the vendor library was not in the tree it was taken in)"
                                % pb.get("citations_unjudged"))
            if pb.get("refused") != 0: problems.append("refused %s part(s)" % pb.get("refused"))
            want = f["holds"].get(letter, [])
            if sorted(pb.get("held_by") or []) != sorted(want):
                problems.append("is held by %s and the list holds the board by %s" % (pb.get("held_by"), want))
            if rec.get("verdict") == "PASS" and want:
                problems.append("reads PASS while the list holds the board by %s" % ", ".join(want))
            elif rec.get("verdict") == "INCONCLUSIVE" and not want and not pb.get("classes_undecided"):
                problems.append("reads INCONCLUSIVE while the list holds the board by nothing")
            elif rec.get("verdict") not in ("PASS", "INCONCLUSIVE"):
                problems.append("reads %s" % rec.get("verdict"))
        if rec.get("missing_input"): problems.append("declares its input missing: %s" % str(rec.get("missing_input"))[:120])
        if problems: why.append("board %s: %s (%s)" % (letter.upper(), "; ".join(problems), os.path.relpath(rec["_path"], root)))
        else: found.append((letter, rec, os.path.relpath(rec["_path"], root)))
    return found, why


def stage_close_s89(root, commit, validate=True, check_only=False):
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_requirements.yaml")
    old = open(p, encoding="utf-8").read()
    # THE FLOOR IS THE COVERAGE ENTRY'S, so the two stages cannot disagree; and it is checked again against the tree.
    cov = reparse_yaml(os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml"))
    floor = (((cov.get("coverage") or {}).get("REL-001") or {}).get("evidence_not_before") or {}).get("reliability")
    if not floor: fail("pcb_rules_coverage.yaml's REL-001 entry carries no evidence floor for reliability: run --stage coverage first")
    late = old_tool_readings_after(root, floor)
    if late: fail("the coverage entry's floor %s is not after every reading of the unrepaired tool this tree holds:\n  %s"
                  % (floor, "\n  ".join(late)))
    if not commit or not re.fullmatch(r"[0-9a-f]{7,40}", commit): fail("--commit <hash> is required: the commit closed_by names")
    if os.path.isdir(os.path.join(root, ".git")) or os.path.isfile(os.path.join(root, ".git")):
        r = subprocess.run(["git", "-C", root, "cat-file", "-e", commit + "^{commit}"], capture_output=True)
        if r.returncode != 0: fail("this tree does not hold commit %s" % commit)
    else:
        print("apply_rel001_coverage: note: %s is not a git checkout, so the commit is not checked here" % root)
    if re.search(r"(?m)^  - id: S-89\n    closed_by:", old): fail("S-89 is already in closed_items: this stage has run")
    m = re.search(r"(?ms)^  - id: S-89\n    class: SESSION\n    status: OPEN\n(.*?)(?=^  - id: |^closed_items:)", old)
    if not m: fail("open item S-89 is not in %s as this script expects it" % p)
    block, body = m.group(0), m.group(1)
    t = body.find("    title: >-\n")
    if t < 0: fail("the S-89 block carries no folded title")
    title_body = body[t + len("    title: >-\n"):]
    # Whatever stands before the title (on the integration tip: `limits_reading: [{rule: REL-001, boards: all}]`) is an
    # OPEN item's field; no closed item of the registry carries one, and the closing evidence says what becomes of it.
    limits = body[:t].strip()
    if "REL-001's completeness can be false" not in title_body: fail("the S-89 block does not carry its title")
    if old.count("\nclosed_items:\n") != 1: fail("closed_items: is not exactly once in the registry")
    f = list_facts(root)
    found, why = retake_evidence(root, floor, f)
    if why: fail("REL-001 has not been re-taken as this closure needs:\n  " + "\n  ".join(why)
                 + "\n  Re-take reliability on every board (the box: gate_sweep.sh, or retake_gate.sh), then run this stage again.")
    if check_only:
        # --check: every guard above was asked and nothing is written. What the closing would say of each board:
        for letter, rec, path in found:
            pb = rec["counts"]["per_board"][letter]
            print("apply_rel001_coverage: check: %s %s, %s %s, held by %s (%s)"
                  % (letter.upper(), rec.get("verdict"), str(pb["artefact"]["kind"]).replace("_", " "), pb["artefact"]["sha256_16"],
                     ", ".join(pb.get("held_by") or []) or "nothing", path))
        print("apply_rel001_coverage: check: the closure's conditions hold on %d board(s); nothing was written" % len(found))
        return 0
    # THE VALIDATOR IS READ BEFORE THE CHANGE AND AFTER IT: a tree may carry errors of its own (a copy without every
    # page a record names), so the bar is that this change adds none, and that none of the errors names S-89.
    tools = os.path.join(root, "v2", "ecad", "tools")
    before_errs = _validator(tools) if validate else None
    ev_rows, held_rows = [], []
    for letter, rec, path in found:
        pb = rec["counts"]["per_board"][letter]
        ev_rows.append("%s %s (%s candidates, %s classed, %s excluded, %s refused; %s %s; %s)"
                       % (letter.upper(), rec.get("verdict"), pb.get("candidates"), pb.get("classed"), pb.get("excluded"),
                          pb.get("refused"), str(pb["artefact"]["kind"]).replace("_", " "), pb["artefact"]["sha256_16"], path))
        held_rows.append("%s %s" % (letter.upper(), ("held by " + ", ".join(pb["held_by"])) if pb.get("held_by") else "held by nothing, PASS"))
    closing = (
        "Stream d6rel, merged as commit %s (v2/docs/records/d6rel/README.md). reliability.py reads an inventory by reference class "
        "and land (wear_inventory.py; pcb_reliability.yaml section inventory), every candidate classed or excluded with a visible "
        "reason and the land it speaks of; a missing, unreadable or empty netlist reads INCONCLUSIVE with the reason (verdict.write's "
        "missing_input, which rules_status reads as INCONCLUSIVE: v2/docs/records/d6rel/consumers-probe.txt); the netlist is the "
        "declared phase's (phase_artefacts) and the reading records it by sha256 and by content; each board's declaration is bound "
        "to the artefact it was written against (written_against) and another sha reads INCONCLUSIVE; the reviewer's four cases read "
        "PASS, FAIL, FAIL, INCONCLUSIVE on the repaired tool (v2/docs/records/d6rel/matrix-on-repaired-tool.txt; 2 of 4 on the "
        "unrepaired tool, matrix-on-unrepaired-tool.txt) and are tests/test_reliability.py t_matrix_1 to t_matrix_4, with fixtures "
        "for a connector whose value carries no wear word, the empty netlist, a class with no cycle figure and the sha mismatch "
        "(inventory-before-after.txt has the inventory of the set 6 artefacts before and after). REL-001 re-taken on every board "
        "of the manifest with list sha256/16 %s after the evidence floor %s of pcb_rules_coverage.yaml: %s. What holds each board, "
        "read from its own reading and equal to what the list holds it by: %s. A board reads PASS only where the list holds it by "
        "nothing; a class whose maker publishes no figure, an owed figure, an owed measure and an open item that names the board "
        "each keep it INCONCLUSIVE. REL-001 stays a desk reading that tests nothing and replaces no physical verification. The "
        "item's limit on the readings (%s) ends with it: a reading taken after the floor is the repaired tool's and is not LIMITED; "
        "one taken before it is, and the floor makes it not current."
        % (commit, f["list_sha"], floor, "; ".join(ev_rows), "; ".join(held_rows), " ".join(limits.split()) or "none declared"))
    entry = ("  - id: S-89\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s"
             % (commit, _fold(closing), title_body))
    new = old.replace(block, "", 1).replace("\nclosed_items:\n", "\nclosed_items:\n" + entry, 1)
    if new == old: fail("the new text equals the old")
    if new.count("  - id: S-89\n") != 1: fail("S-89 is not exactly once after the change")
    # A RECORD NEVER WAITS ON A CLOSED ITEM; IT CITES WHAT CLOSED IT (the registry's own rule, and the validator's:
    # "waits on S-89, which commit X closed; cite that instead"). Every record whose waits_on names S-89 loses that wait
    # and gains the citation in its history, the field the registry uses for what an earlier reading said and what
    # changed it. The record's result fields are not touched: what REL-001 reads is the re-take's to say.
    new, cited = _cite_instead_of_wait(new, commit, floor, "; ".join(held_rows))
    if not cited: fail("no record waits on S-89, which the registry of fnd/int7 does not match (five records did)")
    tmp = p + ".d6rel.tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    d = reparse_yaml(tmp)
    open_ids = [x.get("id") for x in d.get("open_items") or []]
    closed = {x.get("id"): x for x in d.get("closed_items") or []}
    if "S-89" in open_ids or "S-89" not in closed or closed["S-89"].get("closed_by") != "commit %s" % commit:
        os.remove(tmp); fail("the registry does not read back with S-89 closed by commit %s" % commit)
    for rid in cited:
        rec = next((x for x in d.get("records") or [] if x.get("id") == rid), None)
        if rec is None or "S-89" in (rec.get("waits_on") or []) or ("S-89" not in (rec.get("history") or "")):
            os.remove(tmp); fail("record %s does not read back with its wait on S-89 cited instead" % rid)
    os.replace(tmp, p)
    print("apply_rel001_coverage: close-s89: S-89 moved to closed_items in %s (closed_by commit %s); the wait on it cited "
          "instead in %s; re-parsed" % (os.path.relpath(p, root), commit, ", ".join(cited)))
    print("apply_rel001_coverage: what holds each board, as the closing evidence says it: %s" % "; ".join(held_rows))
    if validate:
        after_errs = _validator(tools)
        new_errs = [e for e in after_errs if e not in before_errs]
        print("apply_rel001_coverage: rules_lib.py requirements: %d error(s) before this change, %d after, %d new"
              % (len(before_errs), len(after_errs), len(new_errs)))
        if new_errs or any("S-89" in e for e in after_errs):
            open(p, "w", encoding="utf-8").write(old)
            fail("the registry validator reads new errors after the change; the file is restored to the text before this stage:\n  "
                 + "\n  ".join((new_errs or [e for e in after_errs if "S-89" in e])[:10]))
    return 0


def _validator(tools):
    """The ERROR lines of `python3 rules_lib.py requirements` in this tree's tools directory (read only)."""
    r = subprocess.run([sys.executable, "rules_lib.py", "requirements"], cwd=tools, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return sorted(l for l in (r.stdout + r.stderr).split("\n") if l.startswith("ERROR"))


def _cite_instead_of_wait(text, commit, floor, held):
    """(text, [record ids]) with S-89 removed from every record's `waits_on` and the closing cited in its `history`."""
    sentence = ("28 September 2026: S-89 (REL-001's population, inputs and binding: the independent review of handover H3, "
                "finding H3-01) closed by commit %s, stream d6rel, v2/docs/records/d6rel/README.md; this record cited the wait "
                "on it and cites the closing instead. REL-001's readings taken after the evidence floor %s are the repaired "
                "tool's (an inventory by reference class and land, the netlist bound by sha) and are not LIMITED; what holds "
                "each board from PASS at the closing, by the open items of pcb_reliability.yaml: %s." % (commit, floor, held))
    i = text.find("\nrecords:\n")
    if i < 0: fail("the registry carries no records: section")
    head, body = text[:i + len("\nrecords:\n")], text[i + len("\nrecords:\n"):]
    parts = re.split(r"(?m)(?=^  - id: )", body)
    cited = []
    for k, blk in enumerate(parts):
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", blk)
        if not m: continue
        waits = [w.strip() for w in m.group(1).split(",") if w.strip()]
        if "S-89" not in waits: continue
        rid = re.match(r"  - id: (\S+)", blk).group(1)
        rest = [w for w in waits if w != "S-89"]
        line = ("    waits_on: [%s]\n" % ", ".join(rest)) if rest else ""
        blk = blk.replace(m.group(0), line, 1)
        h = re.search(r"(?ms)^    history: >-\n((?:      .*\n)+)", blk)
        if h:
            blk = blk.replace(h.group(0), h.group(0) + _fold(sentence), 1)
        else:
            sc = re.search(r"(?m)^    source_check: \S+\n", blk)
            if not sc: fail("record %s carries no source_check line to anchor its history to" % rid)
            blk = blk.replace(sc.group(0), sc.group(0) + "    history: >-\n" + _fold(sentence), 1)
        parts[k] = blk
        cited.append(rid)
    return head + "".join(parts), cited


def _fold(text, width=118, indent="      "):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: lines.append(cur)
    return "".join(indent + l + "\n" for l in lines)


def main(argv):
    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    stage = opt("--stage")
    root = os.path.abspath(opt("--root", DEFAULT_ROOT))
    if not os.path.isfile(os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")): fail("%s is not the repository root" % root)
    if stage == "coverage": return stage_coverage(root, floor_for(root, opt("--floor"), opt("--commit")))
    if stage == "close-s89":
        return stage_close_s89(root, opt("--commit"), validate="--no-validate" not in argv, check_only="--check" in argv)
    fail("--stage coverage or --stage close-s89")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
