#!/usr/bin/env python3
"""ERC as a gate (MESHSAT-862, 8 Sep 2026, appendix 32.64): build_sch.sh used to turn kicad-cli's exit code into an echo and no chain read it.
Reads out/<name>-erc.json (kicad-cli sch erc --format json; the .rpt is kept for humans), counts every violation by type and severity, and
blocks on any error-severity violation that the project's allow-list does not cover. Warnings are printed with counts and never block.

Allow-list: <project dir>/erc-allow.txt, one rule per line  `type` or `type|substring`, a `#` reason after it (a line without a reason is
ignored, so nothing is waved through silently). Example:  power_pin_not_driven|+3V3_AB   # the gated rail comes from A22 over the harness

WHICH SCHEMATIC THE REPORT IS OF, AND SO WHICH NETLIST (MESHSAT-1357, 26 September 2026, the tools stream's recording round). This gate
recorded only the project directory, so `rules_status` could never tie a reading to the netlist of the board it is filed under, and rule
SCH-001 read UNBOUND on six boards whatever a re-take said. The netlist cannot simply be recorded beside the report, because the report
does not say which schematic it was taken on: every board's out/<name>-erc.json in the main checkout on that day was written on
11 September, before the schematics committed on 26 September, and a reading of one of them tied to today's netlist would have been
current evidence about a schematic nobody checked. So `--run` takes the ERC itself, with kicad-cli, on the schematic the directory holds,
hashes that schematic before and after, and writes out/<name>-erc.json.prov.json naming it (`schematic_sha256`, the first 32 hex of its
sha256, the form sch_prov.py writes for a netlist). Every reading, with or without --run, records the report, the schematic and the
allow-list by content, and records the NETLIST out/<name>.net only when three shas agree: the sidecar names this report, the sidecar's
schematic is the schematic here, and the netlist's own provenance (sch_prov.py) names the same schematic. Otherwise `netlist_tie` says
which link is missing and the reading stays unbound, which is the honest answer about a report of unknown origin. The verdict itself,
its counts and its evidence are judged exactly as before.

Usage: erc_gate.py <project dir> <name> [--run]  -> prints the counts, writes out/<name>-erc.status (clean | allowed N | BLOCK N | BLOCK no ERC output), exit 1 on BLOCK.
       --run  take the ERC now with kicad-cli on <project dir>/<name>.kicad_sch (replacing out/<name>-erc.json) and record which schematic it was taken on."""
import sys, os, json, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict
import phase_artefacts as _pa

def violations(d):
    out = []
    if isinstance(d, dict):
        for s in d.get("sheets", []): out += s.get("violations", [])
        out += d.get("violations", [])
    return out

def allow_rules(path):
    rules = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or "#" not in line: continue
            rule, reason = line.split("#", 1)
            t, _, sub = rule.strip().partition("|")
            if t and reason.strip(): rules.append((t.strip(), sub.strip(), reason.strip()))
    return rules

def gate(d, rules):
    """(blocking list, allowed count, counter by (type, severity)) for a parsed ERC JSON."""
    by = collections.Counter(); block = []; allowed = 0
    for v in violations(d):
        t, sev = v.get("type", "?"), v.get("severity", "error")
        if v.get("excluded"): continue
        by[(t, sev)] += 1
        if sev != "error": continue
        text = v.get("description", "") + " " + " ".join(i.get("description", "") for i in v.get("items", []))
        if any(t == rt and (not sub or sub in text) for rt, sub, _ in rules): allowed += 1
        else: block.append("%s: %s" % (t, v.get("description", "")[:110]))
    return block, allowed, by


def _sha(raw, n=64):
    return hashlib.sha256(raw).hexdigest()[:n]


def _read(path):
    try:
        with open(path, "rb") as f: return f.read()
    except OSError:
        return None


def prov_path(report):
    """The sidecar that names the schematic a report was taken on."""
    return report + ".prov.json"


def run_erc(proj, name, timeout=1800):
    """(True, why) after taking the ERC on <proj>/<name>.kicad_sch with kicad-cli and writing the report and its sidecar;
    (False, why) when it could not. The previous report and sidecar are removed first, as build_sch.sh does, so a run
    that fails leaves no report at all (INCONCLUSIVE, never an old report read as a new one). The command is the one
    build_sch.sh runs, from the project directory, so the report is the same kicad-cli output."""
    import shutil, subprocess, datetime
    rel_out = os.path.join("out", name + "-erc.json")
    out = os.path.join(proj, rel_out)
    for p in (out, prov_path(out)):
        if os.path.exists(p): os.remove(p)
    sch = os.path.join(proj, name + ".kicad_sch")
    cli = shutil.which("kicad-cli")
    if not cli: return False, "kicad-cli is not on this host"
    before = _read(sch)
    if before is None: return False, "there is no schematic at %s" % sch
    r = subprocess.run([cli, "sch", "erc", "--severity-all", "--format", "json", "-o", rel_out, name + ".kicad_sch"],
                       cwd=proj, capture_output=True, text=True, timeout=timeout)
    report = _read(out)
    if report is None:
        return False, "kicad-cli wrote no report (exit %d: %s)" % (r.returncode, (r.stderr or r.stdout).strip()[-160:])
    after = _read(sch)
    if after != before:
        return False, "the schematic changed while the ERC ran, so the report is not of one schematic"
    ver = subprocess.run([cli, "version"], capture_output=True, text=True, timeout=60).stdout.strip()
    json.dump({"what": "the schematic this ERC report was taken on, by content (erc_gate.py --run)",
               "report": os.path.basename(out), "report_sha256_16": _sha(report, 16),
               "schematic": name + ".kicad_sch", "schematic_sha256": _sha(before, 32),
               "kicad_version": ver,
               "taken": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")},
              open(prov_path(out), "w"), indent=1)
    return True, "ERC taken on schematic %s with kicad-cli %s" % (_sha(before, 12), ver)


def netlist_tie(proj, name, report_raw):
    """(True, why) when the ERC report is proved to be of the schematic the netlist beside it was exported from; (False,
    why) naming the missing link otherwise. See the docstring: three shas must agree."""
    report = os.path.join(proj, "out", name + "-erc.json")
    if report_raw is None:
        return False, "there is no ERC report, so there is nothing to tie"
    try:
        rec = json.load(open(prov_path(report), encoding="utf-8"))
    except (OSError, ValueError):
        return False, ("the ERC report carries no provenance sidecar (erc_gate.py --run writes one), so which schematic it "
                       "was taken on is not known")
    if str(rec.get("report_sha256_16") or "") != _sha(report_raw, 16):
        return False, "the sidecar names report %s and the report here is %s" % (rec.get("report_sha256_16"), _sha(report_raw, 16))
    sch = _read(os.path.join(proj, name + ".kicad_sch"))
    if sch is None:
        return False, "there is no schematic beside the report to compare it with"
    here = _sha(sch, 32)
    if str(rec.get("schematic_sha256") or "") != here:
        return False, ("the report was taken on schematic %s and this directory holds %s"
                       % (str(rec.get("schematic_sha256"))[:12], here[:12]))
    import sch_prov as _sp
    net = os.path.join(proj, "out", name + ".net")
    if not os.path.exists(net):
        return False, "there is no netlist at %s" % os.path.join("out", name + ".net")
    nrec = _sp.read(net)
    if not nrec or not nrec.get("schematic_sha256"):
        return False, "the netlist carries no provenance naming its schematic (sch_prov.py)"
    if nrec["schematic_sha256"] != here:
        return False, ("the netlist was exported from schematic %s and the report is of %s"
                       % (str(nrec["schematic_sha256"])[:12], here[:12]))
    return True, "the report, the schematic and the netlist's own provenance agree on schematic %s" % here[:12]


def recorded_inputs(proj, name, report_raw):
    """What the reading judged, by content, and the netlist it is tied to where the tie is proved."""
    inputs = {"project": proj}
    report = os.path.join(proj, "out", name + "-erc.json")
    if report_raw is not None:
        inputs["erc_report"] = _pa.record(report, report_raw, content=False)
    for key, p in (("schematic", os.path.join(proj, name + ".kicad_sch")), ("allow_list", os.path.join(proj, "erc-allow.txt"))):
        r = _pa.record(p, content=False)
        if r: inputs[key] = r
    ok, why = netlist_tie(proj, name, report_raw)
    if ok:
        n = _pa.record(os.path.join(proj, "out", name + ".net"))
        if n: inputs["netlist"] = n
        else: ok, why = False, "the netlist could not be read"
    inputs["netlist_tie"] = {"proved": bool(ok), "why": why}
    return inputs


def main(a):
    run = "--run" in a
    a = [x for x in a if x != "--run"]
    if len(a) < 2: print(__doc__); return 2
    proj, name = a[0], a[1]; path = os.path.join(proj, "out", name + "-erc.json"); status = os.path.join(proj, "out", name + "-erc.status")
    os.makedirs(os.path.join(proj, "out"), exist_ok=True)
    if run:
        ok, why = run_erc(proj, name)
        print("erc_gate: --run %s" % why)
    raw = _read(path)
    try: d = json.loads(raw) if raw is not None else json.load(open(path))
    except Exception as e:
        print("erc_gate: BLOCK no ERC output (%s: %s)" % (path, e)); open(status, "w").write("BLOCK no ERC output\n")
        # No ERC output is not an ERC failure: nothing was judged. INCONCLUSIVE still blocks, and says why.
        return verdict.write("erc_gate", verdict.INCONCLUSIVE, denominator=0, inputs=recorded_inputs(proj, name, None),
                             note="no ERC output at %s (%s)" % (path, e), out_dir=os.path.join(proj, "out"))
    rules = allow_rules(os.path.join(proj, "erc-allow.txt"))
    block, allowed, by = gate(d, rules)
    for (t, sev), n in sorted(by.items()): print("erc_gate: %-8s %-40s %d" % (sev, t, n))
    inputs = recorded_inputs(proj, name, raw)
    print("erc_gate: netlist %s: %s" % ("tied" if inputs["netlist_tie"]["proved"] else "NOT tied", inputs["netlist_tie"]["why"]))
    if block:
        print("erc_gate: BLOCK %d error(s) not allow-listed (of %d violations; %d allowed by %s):" % (len(block), sum(by.values()), allowed, os.path.basename(proj) + "/erc-allow.txt"))
        for line in block[:12]: print("   " + line)
        open(status, "w").write("BLOCK %d\n" % len(block))
        return verdict.write("erc_gate", verdict.FAIL,
                             counts={"blocking": len(block), "allowed": allowed, "violations": sum(by.values())},
                             denominator=sum(by.values()), evidence=block[:30], inputs=inputs,
                             out_dir=os.path.join(proj, "out"))
    print("erc_gate: %s (%d violations, %d error(s) allow-listed with a reason, warnings %d)" % ("clean" if not by else "no blocking error", sum(by.values()), allowed, sum(n for (t, s), n in by.items() if s != "error")))
    open(status, "w").write(("allowed %d\n" % allowed) if allowed else "clean\n")
    return verdict.write("erc_gate", verdict.PASS,
                         counts={"blocking": 0, "allowed": allowed, "violations": sum(by.values())},
                         denominator=sum(by.values()), inputs=inputs,
                         note=("%d error(s) allow-listed with a reason" % allowed) if allowed else "",
                         out_dir=os.path.join(proj, "out"))

if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("erc_gate", main, sys.argv[1:]))
