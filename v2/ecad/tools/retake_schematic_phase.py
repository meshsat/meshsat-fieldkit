#!/usr/bin/env python3
"""The consolidated re-take of every schematic-phase reading, per board (MESHSAT-1357, 27 September 2026).

WHY IT EXISTS. v2/docs/CURRENT-EVIDENCE.md says, for every board, which schematic-phase rows would become current
evidence after "a re-take alone" (rules_status.retake_projection), and the handover could say what to re-take but not
how: no page gave the commands, and the only drivers that run the writers (full.sh, gate_sweep.sh) either regenerate
the schematic first or run every layout gate too. This driver runs exactly the writers the layout-entry test reads, on
the COMMITTED netlist and schematic of each board's declared phase, with the arguments the pipeline gives them, and
nothing else. It decides nothing itself: rules_status.py reads what it writes, and rules_render.py renders the page.

WHAT IT ENUMERATES, FROM THE REGISTRIES THE PAGES ALREADY USE (never a hand list of rules):
  * rules_lib.rules_for(letter) with each rule's verification_phase: every applicable rule verified at SCHEMATIC,
    plus every rule a hold's `layout_entry_requires` names as `rule_pass` (the layout-entry test counts those too);
  * pcb_rules_coverage.yaml: each rule's maturity, its verifying tool and the verdict names it reads
    (rules_status._names), so a rule verified by a desk review or with no deciding verification is listed and not run;
  * rules_status.CONFIG_INPUTS: every writer must be declared there, or its reading could never bind (CONFIG_UNDECLARED);
  * readiness_manifest.json and rules_status._phase_dir: each board's project stem, its phase directory and no_chain;
  * WRITERS below: the command each verdict's writer is run with, copied from gate_sweep.sh (and full.sh for erc_gate
    --run), except that intent_rails and edge_length use the tools' own --netlist modes, which write the SCHEMATIC-phase
    verdict alone. A verdict name the coverage map asks for and WRITERS does not know is an ERROR, never a skip.

WHERE IT WRITES.
  --in-place   in the tree itself: each board's commands run in its phase directory with VERDICT_DIR=<phase>/out, the
               place full.sh's writers write (erc_gate.py and safe_lines.py write there whatever VERDICT_DIR says).
               The tree's standing rule is that nobody runs a gate by hand in the tree, so this is refused unless asked
               for; its use is a THROWAWAY CLONE (a git bundle of main on the box), never the working checkout.
               --routed also copies the re-taken readings, and the SI-001 table edge_length writes beside its verdict
               (COMPANIONS), into <phase>/routed/, the tracked evidence home gate_sweep.sh copies to, so a clone's
               re-take can be committed. It is refused without --in-place, and a step that was skipped or timed out
               has nothing copied.
  --verdict-dir DIR  (without --in-place) the committed inputs of each board are copied to DIR/<phase dir>/ (schematic,
               project, board file, allow-lists, out/<stem>.net with its provenance sidecar, out/<stem>-intent.json)
               and every command runs there with VERDICT_DIR=DIR/<phase dir>/out: the same layout rules_status reads,
               rooted at DIR, so DIR/<phase dir>/out/*.verdict.json can be read or copied by name. DIR must lie outside
               the repository. The tree's evidence folders are snapshotted before and after, and a writer that touched
               one fails the run. A reading taken under /tmp is TEMP_INPUT to rules_status and never current, so a
               reading meant to count is taken with --in-place in a clone outside /tmp.

THE INPUT MUST BE COMMITTED. Every input a board's commands read (netlist, its provenance sidecar, intent file,
schematic, project, board file, allow-lists) must be tracked and unmodified in git, or the board is refused: a re-take
of an uncommitted netlist is evidence about nothing anybody can check out (so it needs a git clone: an extraction with
no .git is refused board by board). The netlist, schematic, board file and intent file the commands read (the tree's in
place, the staged copies otherwise) are hashed before and after, and a board whose inputs changed under the run is
reported as REFUSED.

THE SET-LEVEL WRITERS (energy_chain, check_contracts, interfaces) run once per board, as gate_sweep.sh runs them, so each
board's evidence directory carries the reading its rules are read from; they read every board's committed netlist from
the tree and write only through VERDICT_DIR.

It never touches the network: no writer in WRITERS opens a socket (the one tool here that does, jlc_certify.py, is in
NETWORK_WRITERS and refused), and the driver itself only runs local processes.

Usage:
  retake_schematic_phase.py --plan [--board <x>] [--in-place | --verdict-dir DIR] [--json]
  retake_schematic_phase.py --run  [--board <x>] (--in-place [--routed] | --verdict-dir DIR) [--json]
  (--json with --run: the result as JSON on stdout, the plan and the progress on stderr)
Exit: 0 done (a FAIL reading is the design's answer, not the driver's), 1 a step did not write its readings or a guard
fired, 2 the plan is in error or the call was refused."""
import os, sys, json, glob, shutil, subprocess, hashlib, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(HERE)
V2 = os.path.dirname(ECAD)
REPO = os.path.dirname(V2)
sys.path.insert(0, HERE)
import rules_lib as R
import rules_status as S

PY = "python3"
NETLIST = "out/{N}.net"
E5_DERATE_WHY = "this board has no schematic and no BOM: it is copper, plated targets, wire lands and mounting holes"

# verdict name (with <letter> for the board) -> (writer file, argv after the interpreter, what it needs).
# `needs`: "netlist" = the board's committed out/<stem>.net; "kicad" = the netlist, the schematic and kicad-cli.
# Sources: gate_sweep.sh (the judging re-take) for every line, full.sh:83 for erc_gate --run, and the tools' own
# --netlist modes for intent_rails (intent_checks.py:1355) and edge_length (edge_length.py:655).
WRITERS = {
    "erc_gate":                 ("erc_gate.py", ["{T}/erc_gate.py", ".", "{N}", "--run"], "kicad"),
    "safe_lines_<letter>":      ("safe_lines.py", ["{T}/safe_lines.py", NETLIST], "netlist"),
    "pin_map_lands_<letter>":   ("pin_map_lands.py", ["{T}/pin_map_lands.py", NETLIST, "{L}"], "netlist"),
    "derate":                   ("derate.py", ["{T}/derate.py", NETLIST], "netlist"),
    "intent_rails":             ("intent_checks.py", ["{T}/intent_checks.py", "--netlist", NETLIST], "netlist"),
    "power_sequence":           ("power_sequence.py", ["{T}/power_sequence.py", NETLIST], "netlist"),
    "edge_length":              ("edge_length.py", ["{T}/edge_length.py", "--netlist", NETLIST], "netlist"),
    "clock_check":              ("clock_check.py", ["{T}/clock_check.py", NETLIST], "netlist"),
    "port_protect_<letter>":    ("port_protect.py", ["{T}/port_protect.py", NETLIST], "netlist"),
    "pack_protection":          ("pack_protection.py", ["{T}/pack_protection.py", "--netlist", NETLIST, "--check"], "netlist"),
    "energy_chain":             ("energy_chain.py", ["{T}/energy_chain.py", "--ecad", "{E}"], None),
    "energy_chain_<letter>":    ("energy_chain.py", ["{T}/energy_chain.py", "--ecad", "{E}"], None),
    "check_contracts":          ("check_contracts.py", ["{T}/check_contracts.py", "{E}"], None),
    "check_contracts_<letter>": ("check_contracts.py", ["{T}/check_contracts.py", "{E}"], None),
    "inhibit_chain_<letter>":   ("check_contracts.py", ["{T}/check_contracts.py", "{E}"], None),
    "interfaces_<letter>":      ("interfaces.py", ["{T}/interfaces.py"], None),
}
# A board with no schematic (manifest no_chain, board E5): the declared forms gate_sweep.sh runs when out/<stem>.net
# is absent. A netlist writer with no entry here cannot judge such a board and is an error if the map asks for it.
WRITERS_NO_NETLIST = {
    "safe_lines_<letter>":   ("safe_lines.py", ["{T}/safe_lines.py", "--board", "{L}"], None),
    "port_protect_<letter>": ("port_protect.py", ["{T}/port_protect.py", "--board", "{L}"], None),
    "derate":                ("derate.py", ["{T}/derate.py", "{N}.kicad_pcb", "--no-components", E5_DERATE_WHY], None),
}
NETWORK_WRITERS = ("jlc_certify.py",)
# Files a writer leaves beside its verdict that the verdict names, copied with it by --routed as gate_sweep.sh copies
# them (gate_sweep.sh: "the SI-001 table the edge_length verdict names, beside it").
COMPANIONS = {"edge_length.py": ("edge_length.table.json",)}
# Arguments that name the TREE as a read-only input: the set-level writers read every board's committed netlist from it
# and write only through VERDICT_DIR (check_contracts.py:699, energy_chain.py and verdict.write's default).
READ_ONLY_ARGS = ("{T}", "{E}")
STAGE_FILES = ("{N}.kicad_sch", "{N}.kicad_pro", "{N}.kicad_pcb", "fp-lib-table", "sym-lib-table", "erc-allow.txt",
               "bypass-allow.txt", "lcsc-allow.txt", "out/{N}.net", "out/{N}.net.prov.json", "out/{N}-intent.json")


class PlanError(Exception):
    pass


def _canon(name, letter):
    return name[:-len(letter) - 1] + "_<letter>" if name.endswith("_" + letter) else name


def _writer_for(name, letter, has_net):
    """(writer file, argv template, needs) for one verdict name on one board, or raise PlanError."""
    key = name if name in WRITERS else _canon(name, letter)
    if not has_net and key in WRITERS_NO_NETLIST: w = WRITERS_NO_NETLIST[key]
    elif key in WRITERS: w = WRITERS[key]
    else:
        raise PlanError("verdict %s (board %s) has no writer in retake_schematic_phase.WRITERS: add the command its "
                        "writer is run with (gate_sweep.sh) before this plan can cover its rule" % (name, letter.upper()))
    if not has_net and w[2] in ("netlist", "kicad"):
        raise PlanError("verdict %s (board %s) is written from a netlist and the board has none; declare its no-netlist "
                        "form in WRITERS_NO_NETLIST" % (name, letter.upper()))
    if w[0] in NETWORK_WRITERS:
        raise PlanError("%s reaches the network and is never run by this driver" % w[0])
    if w[0] not in S.CONFIG_INPUTS:
        raise PlanError("%s is not declared in rules_status.CONFIG_INPUTS, so its reading could never bind "
                        "(CONFIG_UNDECLARED)" % w[0])
    if not os.path.exists(os.path.join(HERE, w[0])):
        raise PlanError("%s, the writer of %s, is not in this tree's tools" % (w[0], name))
    return w


def _rules_in_scope(letter, reg, facts, holds):
    """[(rule, why_in_scope)]: every applicable SCHEMATIC-phase rule, plus the rules a hold's layout_entry_requires
    names as rule_pass on this board."""
    applicable = list(R.rules_for(letter, reg, facts))
    want = set()
    h = holds.get(letter) or {}
    for q in (h.get("layout_entry_requires") or []):
        if str(q.get("kind") or "") == "rule_pass" and q.get("rule"): want.add(str(q["rule"]))
    out = []
    for rule, _why in applicable:
        if rule.get("verification_phase") == "SCHEMATIC":
            out.append((rule, "verified at SCHEMATIC"))
        elif rule["id"] in want:
            out.append((rule, "named by decision %s's layout-entry requirement (rule_pass)" % h.get("decision")))
    return out


def plan(boards=None, in_place=False, verdict_dir=None, reg=None, facts=None, cov=None, m=None, holds=None):
    """{boards: [{letter, stem, phase_dir, cwd, verdict_dir, declared_phase, no_chain, rules: [...], steps: [...],
    stage: [...], errors: [...]}], errors: [...]}. Pure: reads the registries and the tree, runs nothing."""
    reg = reg or R.load(); facts = facts if facts is not None else R.facts()
    cov = cov if cov is not None else S.coverage(); m = m or S.manifest()
    holds = R.board_holds() if holds is None else holds
    letters = list(m["boards"]) if not boards else [b.lower() for b in boards]
    unknown = [b for b in letters if b not in m["boards"]]
    if unknown: raise PlanError("no board %s in readiness_manifest.json" % ", ".join(unknown))
    root = None if in_place else os.path.abspath(verdict_dir or "<VERDICT_DIR>")
    out = {"in_place": in_place, "verdict_root": root, "boards": [], "errors": []}
    for L in letters:
        b = m["boards"][L]
        stem = b.get("project") or ""
        pd = S._phase_dir(L, m)
        rel = os.path.relpath(pd, ECAD)
        net = os.path.join(pd, "out", stem + ".net")
        has_net = os.path.exists(net)
        cwd = pd if in_place else os.path.join(root, rel)
        vdir = os.path.join(cwd, "out")
        fmt = dict(T=HERE, E=ECAD, N=stem, L=L)
        bp = {"letter": L, "stem": stem, "phase_dir": rel, "cwd": cwd, "verdict_dir": vdir, "no_chain": bool(b.get("no_chain")),
              "declared_phase": S._declared_phase(L), "netlist": os.path.relpath(net, ECAD) if has_net else None,
              "rules": [], "steps": [], "stage": [], "errors": []}
        by_cmd = {}
        for rule, why in _rules_in_scope(L, reg, facts, holds):
            rid = rule["id"]; c = cov.get(rid)
            row = {"rule": rid, "why": why, "release_effect": rule.get("release_effect"), "verdicts": [], "action": None}
            if c is None:
                bp["errors"].append("%s applies to board %s and pcb_rules_coverage.yaml does not list it" % (rid, L.upper()))
                row["action"] = "ERROR: not in the coverage map"; bp["rules"].append(row); continue
            mat = c.get("maturity")
            names = S._names(c, L)
            row["verdicts"] = names
            if mat == "VERIFIED_MANUALLY":
                row["action"] = "desk review of a pinned document: re-reviewed, not re-taken"
            elif mat != "ENFORCED" or not names:
                row["action"] = "no deciding verification in the coverage map (maturity %s): nothing to re-take" % mat
            else:
                row["action"] = "re-take"
                for n in names:
                    try: wf, argv, needs = _writer_for(n, L, has_net)
                    except PlanError as e:
                        bp["errors"].append(str(e)); row["action"] = "ERROR: %s" % e; continue
                    key = (wf, tuple(argv))
                    st = by_cmd.get(key)
                    if st is None:
                        st = {"writer": wf, "argv": [PY] + [a.format(**fmt) for a in argv],
                              "argv_template": [PY] + list(argv), "needs": needs, "rules": [], "verdicts": [],
                              "cwd": cwd, "env": {"VERDICT_DIR": vdir}}
                        by_cmd[key] = st; bp["steps"].append(st)
                    if rid not in st["rules"]: st["rules"].append(rid)
                    if n not in st["verdicts"]: st["verdicts"].append(n)
            bp["rules"].append(row)
        # erc_gate first (it is the one that needs kicad-cli, and full.sh runs it first), then the rest in plan order
        bp["steps"].sort(key=lambda s: 0 if s["writer"] == "erc_gate.py" else 1)
        if not in_place:
            for f in STAGE_FILES:
                src = os.path.join(pd, f.format(N=stem))
                if os.path.exists(src):
                    bp["stage"].append({"from": src, "to": os.path.join(cwd, f.format(N=stem))})
        out["errors"] += bp["errors"]
        out["boards"].append(bp)
    return out


def inputs_of(bp):
    """The tree files a board's commands read from its phase directory (what must be committed)."""
    pd = os.path.join(ECAD, bp["phase_dir"])
    return [os.path.join(pd, f.format(N=bp["stem"])) for f in STAGE_FILES if os.path.exists(os.path.join(pd, f.format(N=bp["stem"])))]


def uncommitted(paths):
    """[(path, why)] of the paths git does not hold as committed (untracked, modified or staged)."""
    bad = []
    for p in paths:
        r = subprocess.run(["git", "-C", os.path.dirname(p), "ls-files", "--error-unmatch", os.path.basename(p)],
                           capture_output=True, text=True)
        if r.returncode != 0: bad.append((p, "not tracked")); continue
        r = subprocess.run(["git", "-C", os.path.dirname(p), "status", "--porcelain", "--", os.path.basename(p)],
                           capture_output=True, text=True)
        if r.stdout.strip(): bad.append((p, "differs from its commit (%s)" % r.stdout.strip()[:2]))
    return bad


def _sha(p):
    try: return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError: return None


def _inside(path, root):
    p, r = os.path.realpath(path), os.path.realpath(root)
    return p == r or p.startswith(r + os.sep)


def evidence_folders(m=None):
    """The tree's own evidence folders: each board's phase directory's out/ and routed/, and the set-level out/."""
    m = m or S.manifest()
    ds = [os.path.join(ECAD, "out")]
    for L in m["boards"]:
        pd = S._phase_dir(L, m)
        ds += [os.path.join(pd, "out"), os.path.join(pd, "routed")]
    return ds


def _snapshot(folders):
    snap = {}
    for d in folders:
        for dp, _dn, fns in os.walk(d):
            for fn in fns:
                p = os.path.join(dp, fn)
                try: st = os.stat(p); snap[p] = (st.st_mtime_ns, st.st_size)
                except OSError: pass
    return snap


def check_call(in_place, verdict_dir, routed=False):
    """None, or the reason this call is refused (the tree's rule: never run a gate by hand in the tree)."""
    if in_place and verdict_dir:
        return "--in-place and --verdict-dir are exclusive: in place, each board's verdicts go to its phase directory's out/"
    if routed and not in_place:
        return ("--routed copies the re-taken readings into each phase directory's routed/, the tree's tracked evidence, "
                "so it is taken only with --in-place")
    if not in_place:
        if not verdict_dir:
            return ("no --verdict-dir: without --in-place this driver writes only under a verdict directory outside the "
                    "repository")
        if _inside(verdict_dir, REPO):
            return ("--verdict-dir %s is inside the repository %s; a re-take writes into the tree's evidence only with "
                    "--in-place, in a throwaway clone" % (verdict_dir, REPO))
    return None


def verdict_path(bp, name):
    return os.path.join(bp["verdict_dir"], name + ".verdict.json")


def run(p, routed=False, log=print):
    """Execute a plan. Returns {boards: [{letter, refused, steps: [{..., rc, seconds, readings}]}], ok}."""
    have_kicad = bool(shutil.which("kicad-cli"))
    folders = evidence_folders()
    before = None if p["in_place"] else _snapshot(folders)
    res = {"boards": [], "ok": True, "kicad_cli": shutil.which("kicad-cli") or None,
           "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    for bp in p["boards"]:
        br = {"letter": bp["letter"], "phase_dir": bp["phase_dir"], "refused": None, "steps": [], "seconds": 0.0}
        res["boards"].append(br)
        if bp["errors"]:
            br["refused"] = "plan errors: " + "; ".join(bp["errors"]); res["ok"] = False; continue
        ins = inputs_of(bp)
        bad = uncommitted(ins)
        if bad:
            br["refused"] = "inputs not committed: " + "; ".join("%s %s" % (os.path.relpath(x, ECAD), w) for x, w in bad)
            res["ok"] = False; continue
        if not p["in_place"]:
            for s in bp["stage"]:
                assert _inside(s["to"], p["verdict_root"]), s
                os.makedirs(os.path.dirname(s["to"]), exist_ok=True)
                shutil.copy2(s["from"], s["to"])
        # THE FILES THE COMMANDS READ are hashed before and after: the tree's own in place, the staged copies otherwise
        # (a writer that rewrote its staged netlist would otherwise judge one file and leave the tree's unchanged).
        read = ins if p["in_place"] else [s["to"] for s in bp["stage"]]
        watch = [x for x in read if x.endswith((".net", ".kicad_sch", ".kicad_pcb", "-intent.json"))]
        sha0 = {x: _sha(x) for x in watch}
        os.makedirs(bp["verdict_dir"], exist_ok=True)
        t_board = time.time()
        for st in bp["steps"]:
            sr = {"writer": st["writer"], "rules": st["rules"], "argv": st["argv"], "rc": None, "seconds": 0.0,
                  "readings": {}, "skipped": None, "tail": ""}
            br["steps"].append(sr)
            if st["needs"] == "kicad" and not have_kicad:
                sr["skipped"] = "kicad-cli is not on this host; a skip is not a pass, run it on the box"
                res["ok"] = False; continue
            env = dict(os.environ, **st["env"])
            env.pop("VERDICT_ADVISORY", None)          # a re-take is a judging reading, never advisory
            t0 = sr["t0"] = time.time()
            try:
                r = subprocess.run(st["argv"], cwd=st["cwd"], env=env, capture_output=True, text=True, timeout=1800)
                sr["rc"] = r.returncode
                sr["tail"] = "\n".join(((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-4:])
            except subprocess.TimeoutExpired:
                sr["rc"] = "timeout"
            sr["seconds"] = round(time.time() - t0, 1)
            for n in st["verdicts"]:
                vp = verdict_path(bp, n)
                try:
                    rec = json.load(open(vp, encoding="utf-8"))
                    fresh = os.stat(vp).st_mtime >= t0 - 1
                    # verdict.write names the answer `verdict`; `result` is what rules_status calls it on a row
                    sr["readings"][n] = {"result": rec.get("verdict") or rec.get("result") or "UNREADABLE",
                                         "ts": rec.get("ts"), "written": fresh,
                                         "denominator": rec.get("denominator"),
                                         "missing_input": rec.get("missing_input") or None}
                    if not fresh: res["ok"] = False
                except (OSError, ValueError):
                    sr["readings"][n] = {"result": "NOT WRITTEN", "written": False}
                    res["ok"] = False
            log("  %-3s %-18s rc %-4s %6.1fs  %s" % (bp["letter"].upper(), st["writer"], sr["rc"], sr["seconds"],
                ", ".join("%s %s%s" % (n, v["result"], "" if v.get("written") else " (not written by this run)")
                          for n, v in sr["readings"].items())))
        br["seconds"] = round(time.time() - t_board, 1)
        moved = [os.path.relpath(x, ECAD) for x in watch if _sha(x) != sha0[x]]
        if moved:
            br["refused"] = "an input changed under the run: %s" % ", ".join(moved); res["ok"] = False
        br["routed"] = []
        if routed and p["in_place"] and not moved:
            rd = os.path.join(bp["cwd"], "routed")          # in place, cwd IS the phase directory
            os.makedirs(rd, exist_ok=True)
            for sr in br["steps"]:
                if sr.get("rc") in (None, "timeout"): continue      # skipped or killed: nothing of it is copied
                for n, v in sr["readings"].items():
                    if v.get("written"):
                        shutil.copy2(verdict_path(bp, n), os.path.join(rd, n + ".verdict.json"))
                        br["routed"].append(n + ".verdict.json")
                for c in COMPANIONS.get(sr["writer"], ()):
                    # only a companion this step wrote: an older one beside a fresh verdict describes another reading
                    src = os.path.join(bp["verdict_dir"], c)
                    if os.path.exists(src) and os.stat(src).st_mtime >= sr["t0"] - 1:
                        shutil.copy2(src, os.path.join(rd, c)); br["routed"].append(c)
    if before is not None:
        after = _snapshot(folders)
        touched = sorted(os.path.relpath(k, ECAD) for k in set(before) | set(after) if before.get(k) != after.get(k))
        res["tree_touched"] = touched
        if touched:
            res["ok"] = False
            log("retake: REFUSED, a writer changed the tree's own evidence folders outside --in-place: %s" % ", ".join(touched[:10]))
    return res


def _short(a):
    """An argument as the plan prints it: the tools directory as $T and the ecad directory as $E."""
    if a == ECAD: return "$E"
    if a.startswith(HERE + os.sep): return "$T/" + a[len(HERE) + 1:]
    return a


def render_plan(p, have_kicad):
    lines = []
    lines.append("retake_schematic_phase: %s; verdicts to %s" % (
        "IN PLACE (each board's phase directory out/)" if p["in_place"] else "a verdict directory",
        "<phase>/out" if p["in_place"] else p["verdict_root"] + "/<phase>/out"))
    lines.append("  T=%s  E=%s  (every command: cd <cwd>; VERDICT_DIR=<cwd>/out python3 ...)" % (HERE, ECAD))
    for bp in p["boards"]:
        lines.append("")
        lines.append("board %s  %s  declared phase %s  netlist %s" % (bp["letter"].upper(), bp["phase_dir"],
                     bp["declared_phase"] or "-", bp["netlist"] or "none (no schematic)"))
        for r in bp["rules"]:
            lines.append("  %-8s %-12s %-40s %s" % (r["rule"], r["release_effect"] or "", ",".join(r["verdicts"])[:40], r["action"]))
        lines.append("  %d command(s), cwd %s" % (len(bp["steps"]), bp["cwd"]))
        for st in bp["steps"]:
            note = ""
            if st["needs"] == "kicad" and not have_kicad: note = "   [kicad-cli absent here: SKIPPED on --run]"
            lines.append("    $ " + " ".join(_q(_short(a)) for a in st["argv"]) + "   # " + ", ".join(st["rules"]) + note)
        for e in bp["errors"]:
            lines.append("  ERROR " + e)
    n = sum(len(b["steps"]) for b in p["boards"])
    lines.append("")
    lines.append("plan: %d command(s) over %d board(s): %s; %d error(s)" % (
        n, len(p["boards"]), ", ".join("%s %d" % (b["letter"].upper(), len(b["steps"])) for b in p["boards"]), len(p["errors"])))
    return "\n".join(lines)


def _q(a):
    return a if a and all(ch.isalnum() or ch in "/._-=<>:$" for ch in a) else "'%s'" % a.replace("'", "'\\''")


KNOWN = {"--plan": 0, "--run": 0, "--in-place": 0, "--routed": 0, "--json": 0, "--board": 1, "--verdict-dir": 1}


def main(argv):
    def opt(k):
        return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None
    i, bad = 0, []
    while i < len(argv):                      # an unknown or incomplete option is refused, never ignored
        k = argv[i]
        if k not in KNOWN: bad.append(k); i += 1; continue
        if KNOWN[k] and (i + 1 >= len(argv) or argv[i + 1].startswith("--")): bad.append(k + " (needs a value)")
        i += 1 + KNOWN[k]
    do_run, do_plan = "--run" in argv, "--plan" in argv
    if bad or do_run == do_plan:
        if bad: print("retake_schematic_phase: REFUSED, unknown or incomplete argument(s): %s" % ", ".join(bad))
        print(__doc__.split("Usage:")[1].split("Exit:")[0].rstrip()); return 2
    in_place, routed, as_json = "--in-place" in argv, "--routed" in argv, "--json" in argv
    vdir = opt("--verdict-dir")
    boards = [opt("--board")] if opt("--board") else None
    why = check_call(in_place, vdir, routed) if do_run else (check_call(in_place, vdir, routed) if (in_place or vdir or routed) else None)
    if why:
        print("retake_schematic_phase: REFUSED, %s" % why); return 2
    try: p = plan(boards, in_place=in_place, verdict_dir=vdir)
    except PlanError as e:
        print("retake_schematic_phase: %s" % e); return 2
    have_kicad = bool(shutil.which("kicad-cli"))
    if do_plan:
        print(json.dumps(p, indent=1, default=str) if as_json else render_plan(p, have_kicad))
        return 2 if p["errors"] else 0
    # with --json the result is the only thing on stdout; the plan and the progress go to stderr
    say = (lambda *a: print(*a, file=sys.stderr)) if as_json else print
    if p["errors"]:
        say(render_plan(p, have_kicad)); say("retake_schematic_phase: the plan is in error, nothing run"); return 2
    say(render_plan(p, have_kicad))
    say("")
    t0 = time.time()
    res = run(p, routed=routed, log=say)
    res["seconds"] = round(time.time() - t0, 1)
    say("")
    for br in res["boards"]:
        rd = {}
        for sr in br["steps"]:
            for n, v in sr["readings"].items(): rd[n] = v["result"] if v.get("written") else "NOT WRITTEN"
        sk = [sr["writer"] for sr in br["steps"] if sr.get("skipped")]
        say("board %-3s %s%s %d reading(s) in %.1fs: %s%s%s" % (br["letter"].upper(), br["phase_dir"],
            (" REFUSED (%s)" % br["refused"]) if br["refused"] else "", len(rd), br["seconds"],
            ", ".join("%s %s" % kv for kv in sorted(rd.items())), ("; skipped %s" % ", ".join(sk)) if sk else "",
            ("; %d file(s) copied to routed/" % len(br.get("routed") or [])) if routed else ""))
    say("retake_schematic_phase: %s in %.1fs" % ("done" if res["ok"] else "INCOMPLETE (see above)", res["seconds"]))
    if as_json:
        print(json.dumps(res, indent=1, default=str))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
