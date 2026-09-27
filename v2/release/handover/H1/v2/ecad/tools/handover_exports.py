#!/usr/bin/env python3
"""Readable exports of the COMMITTED schematics for the engineering handover, and the regeneration check, on a KiCad
host (MESHSAT-1357, 27 September 2026).

WHY IT EXISTS. The handover (v2/docs/reviews/2026-09-27-handover-execution-prompt.md, sections 3 and 6) needs, per
board, a schematic a reader can open without KiCad and a BOM, each tied to the exact schematic it came from; and it
needs a regeneration path the recipient can follow. Neither may come from this project's working state: `exports`
reads only the committed schematic of each board's DECLARED phase (phase_artefacts.phase_dir, never a directory
listing) in the tree this file sits in, which is meant to be a clean extraction of one commit (`git archive <rev>`
or a handover ZIP), and writes nothing into that tree but what kicad-cli itself leaves beside a schematic.

  exports   for each board with a schematic chain, into <out>/<phase directory>/:
              <stem>-schematic.pdf        the readable PDF build_sch.sh makes: kicad-cli sch export pdf of the whole
                                          sheet (not kept: one page metres wide), cut into A3 pages by sch_pages.py
              NOT_FOR_FAB-<stem>-bom.csv  build_sch.sh's BOM command: Reference, Value, Footprint, LCSC, quantity,
                                          grouped by Value and Footprint
              NOT_FOR_FAB-<stem>-bom-per-reference.csv  one row per reference: Reference, Value, Footprint, LCSC, Description,
                                          Datasheet, DNP (the fields the generators write; they write no MPN field:
                                          the order code is LCSC, the part identity is in Value and Description).
                                          Both carry NOT_FOR_FAB in their names, the marker review_packet.py uses:
                                          no board of this set is released, and a copied file keeps its name
              <stem>-erc.json, <stem>-erc.rpt   kicad-cli sch erc --severity-all on the committed schematic
              <stem>-net-parity.json      regen_compare.py `pair netlist` of the committed netlist against a fresh
                                          export of the committed schematic: does the netlist belong to the schematic
              provenance.json             the commit named by --commit, the schematic's sha256, every command and
                                          its exit status, every output's sha256 and bytes, the page count and the
                                          first page's text length read back with pdfinfo and pdftotext, and the
                                          versions of kicad-cli, the KiCad packages, python, mutool and poppler
  regen     for each letter named, the pipeline's own schematic chain (tools/full.sh up to erc_gate.py): the board's
            footprint generators into ../meshsat.pretty, the generator with the board table's gen_env and PHASE set to
            the label the committed schematic carries, build_sch.sh; then regen_compare.py `pair` of the committed
            schematic, netlist, intent, BOM and ERC against the regenerated ones, and the sha256 of every
            meshsat.pretty land before and after. It WRITES INTO THE TREE (that is what regenerating is), so run it
            only in a throwaway extraction.

Usage:
  handover_exports.py exports --out <dir> --commit <rev> [--letters a,b,...]
  handover_exports.py regen --out <dir> --letters p[,b,...]
exit 0 when every command ran and every comparison read PARITY or PARITY_AFTER_NOISE; 1 otherwise (the outputs and the
provenance still say which)."""
import argparse, csv, datetime, glob, hashlib, io, json, os, platform, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase_artefacts as PA  # noqa: E402

ECAD = os.path.dirname(HERE)
BOM_PIPE = "Reference,Value,Footprint,LCSC,${QUANTITY}"
BOM_FULL = "Reference,Value,Footprint,LCSC,Description,Datasheet,${DNP}"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(argv, cwd, log, timeout=1800, env=None):
    """Run one command, record argv, directory, exit status and the tail of its output."""
    t0 = now()
    try:
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        rc, tail = r.returncode, (r.stdout + r.stderr)[-1500:]
    except (OSError, subprocess.SubprocessError) as e:
        rc, tail = -1, "%s: %s" % (type(e).__name__, e)
    log.append({"argv": argv, "cwd": os.path.relpath(cwd, os.path.dirname(os.path.dirname(ECAD))), "exit": rc,
                "started_utc": t0, "output_tail": tail})
    return rc


def versions():
    v = {"python": platform.python_version(), "platform": platform.platform()}
    for k, argv in (("kicad_cli", ["kicad-cli", "version"]), ("mutool", ["mutool", "-v"]),
                    ("pdfinfo", ["pdfinfo", "-v"])):
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
            v[k] = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[0] if (r.stdout or r.stderr) else "?"
        except (OSError, subprocess.SubprocessError):
            v[k] = "not installed"
    try:
        r = subprocess.run(["dpkg-query", "-W", "kicad", "kicad-symbols", "kicad-footprints", "poppler-utils",
                            "mupdf-tools"], capture_output=True, text=True, timeout=60)
        v["packages"] = dict(ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln)
    except (OSError, subprocess.SubprocessError):
        v["packages"] = {}
    for m in ("yaml", "PIL"):
        try:
            mod = __import__(m); v["py_" + m] = getattr(mod, "__version__", "importable")
        except ImportError:
            v["py_" + m] = "not installed"
    return v


def letters(arg):
    known = [l for l in sorted(PA._boards()) if not (PA._boards()[l] or {}).get("no_chain")]
    if not arg: return known
    want = [x.strip().lower() for x in arg.split(",") if x.strip()]
    bad = [x for x in want if x not in known]
    if bad: raise SystemExit("handover_exports: unknown or chainless board letter(s): %s (known: %s)" % (bad, known))
    return want


def pdf_readback(pdf, cwd, log):
    """(pages, characters of text on page 1) read back with pdfinfo and pdftotext, or (None, None)."""
    pages = chars = None
    try:
        r = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, timeout=120)
        m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M); pages = int(m.group(1)) if m else None
        r = subprocess.run(["pdftotext", "-f", "1", "-l", "1", pdf, "-"], capture_output=True, text=True, timeout=300)
        chars = len(r.stdout.strip())
    except (OSError, subprocess.SubprocessError) as e:
        log.append({"readback_error": "%s: %s" % (type(e).__name__, e)})
    return pages, chars


def exports(a):
    rc_all = 0
    ver = versions()
    for L in letters(a.letters):
        d = PA.phase_dir(L); st = PA.stem(L); sch = os.path.join(d, st + ".kicad_sch")
        out = os.path.join(a.out, os.path.basename(d)); os.makedirs(out, exist_ok=True)
        log = []; outputs = {}
        if not os.path.exists(sch):
            print("handover_exports: %s has no schematic at %s" % (L, sch)); rc_all = 1; continue
        sch_sha = sha(sch)
        f = lambda n: os.path.join(out, n)
        sheet = os.path.join(a.out, ".%s-schematic-sheet.pdf" % st)
        steps = [
            ["kicad-cli", "sch", "export", "pdf", "--exclude-drawing-sheet", "--exclude-pdf-property-popups",
             "-o", sheet, st + ".kicad_sch"],
            [sys.executable, os.path.join(HERE, "sch_pages.py"), st + ".kicad_sch", sheet, f(st + "-schematic.pdf")],
            ["kicad-cli", "sch", "export", "bom", "--fields", BOM_PIPE, "--group-by", "Value,Footprint",
             "--sort-field", "Reference", "-o", f("NOT_FOR_FAB-" + st + "-bom.csv"), st + ".kicad_sch"],
            ["kicad-cli", "sch", "export", "bom", "--fields", BOM_FULL, "--labels",
             "Reference,Value,Footprint,LCSC,Description,Datasheet,DNP", "--group-by", "", "--ref-range-delimiter", "",
             "--sort-field", "Reference", "-o", f("NOT_FOR_FAB-" + st + "-bom-per-reference.csv"), st + ".kicad_sch"],
            ["kicad-cli", "sch", "erc", "--severity-all", "--format", "json", "-o", f(st + "-erc.json"), st + ".kicad_sch"],
            ["kicad-cli", "sch", "erc", "--severity-all", "--format", "report", "-o", f(st + "-erc.rpt"), st + ".kicad_sch"],
        ]
        tmpnet = os.path.join(a.out, ".%s.export.net" % st)
        steps.append(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", tmpnet, st + ".kicad_sch"])
        codes = [run(s, d, log) for s in steps]
        committed_net = os.path.join(d, "out", st + ".net")
        par = None
        if os.path.exists(tmpnet) and os.path.exists(committed_net):
            r = subprocess.run([sys.executable, os.path.join(HERE, "regen_compare.py"), "pair", "netlist", committed_net,
                                tmpnet], capture_output=True, text=True, timeout=600)
            open(f(st + "-net-parity.json"), "w").write(r.stdout)
            try: par = json.loads(r.stdout).get("result")
            except ValueError: par = "UNREADABLE"
            log.append({"argv": ["regen_compare.py", "pair", "netlist", "<committed out/%s.net>" % st,
                                 "<export of the committed schematic>"], "exit": r.returncode})
        if os.path.exists(tmpnet): os.remove(tmpnet)
        for n in sorted(os.listdir(out)):
            p = f(n)
            if os.path.isfile(p) and n != "provenance.json": outputs[n] = {"sha256": sha(p), "bytes": os.path.getsize(p)}
        pages, chars = pdf_readback(f(st + "-schematic.pdf"), d, log) if os.path.exists(f(st + "-schematic.pdf")) else (None, None)
        spages, schars = pdf_readback(sheet, d, log) if os.path.exists(sheet) else (None, None)
        sheet_sha = sha(sheet) if os.path.exists(sheet) else None
        if os.path.exists(sheet): os.remove(sheet)
        bom_rows = None
        if os.path.exists(f("NOT_FOR_FAB-" + st + "-bom-per-reference.csv")):
            bom_rows = sum(1 for _ in csv.reader(open(f("NOT_FOR_FAB-" + st + "-bom-per-reference.csv"), encoding="utf-8"))) - 1
        erc = None
        if os.path.exists(f(st + "-erc.json")):
            try:
                j = json.load(open(f(st + "-erc.json"), encoding="utf-8")); erc = {}
                for sh in j.get("sheets") or []:
                    for v in sh.get("violations") or []: erc[v.get("severity", "?")] = erc.get(v.get("severity", "?"), 0) + 1
            except ValueError:
                erc = "unreadable"
        label = None
        m = re.search(r'\(comment 1 "Phase ([A-Za-z0-9]+)', open(sch, encoding="utf-8", errors="replace").read())
        if m: label = m.group(1)
        ok = all(c == 0 for c in codes) and par in ("PARITY", "PARITY_AFTER_NOISE") and pages
        rc_all |= 0 if ok else 1
        prov = {"what": "exports of the committed schematic of one board, for the engineering handover",
                "commit": a.commit, "board": L, "stem": st, "phase_directory": "v2/ecad/" + os.path.basename(d),
                "schematic": "v2/ecad/%s/%s.kicad_sch" % (os.path.basename(d), st), "schematic_sha256": sch_sha,
                "schematic_phase_label": label, "board_table_phase": _table_phase(L),
                "committed_netlist_sha256": sha(committed_net) if os.path.exists(committed_net) else None,
                "netlist_parity_with_the_schematic": par, "paged_pdf_pages": pages, "paged_pdf_page1_text_chars": chars,
                "sheet_pdf_pages": spages, "sheet_pdf_page1_text_chars": schars, "sheet_pdf_sha256_not_kept": sheet_sha,
                "driver": {"path": "v2/ecad/tools/handover_exports.py", "sha256": sha(os.path.abspath(__file__))}, "bom_rows_per_reference": bom_rows,
                "erc_violations_by_severity": erc, "taken_utc": now(), "kicad_cli": ver.get("kicad_cli"),
                "python": ver.get("python"), "host": ver.get("platform"), "versions": ver, "commands": log,
                "outputs": outputs, "result": "OK" if ok else "INCOMPLETE"}
        with open(f("provenance.json"), "w", encoding="utf-8") as fh: json.dump(prov, fh, indent=1, sort_keys=True); fh.write("\n")
        print("handover_exports: %s %s: exits %s, netlist parity %s, paged pdf %s pages (%s chars on page 1), %s BOM rows, ERC %s: %s" %
              (L, os.path.basename(d), codes, par, pages, chars, bom_rows, erc, prov["result"]))
    return rc_all


def _table_phase(L):
    try: return (json.load(open(os.path.join(HERE, "boards", L + ".json"), encoding="utf-8")) or {}).get("phase")
    except (OSError, ValueError): return None


def regen(a):
    rc_all = 0
    ver = versions()
    pretty = os.path.join(ECAD, "meshsat.pretty")
    for L in letters(a.letters):
        d = PA.phase_dir(L); st = PA.stem(L); out = os.path.join(a.out, L); os.makedirs(out, exist_ok=True)
        com = os.path.join(out, "committed"); os.makedirs(com, exist_ok=True)
        log = []
        for rel in (st + ".kicad_sch", "out/%s.net" % st, "out/%s-intent.json" % st, "out/%s.net.prov.json" % st):
            if os.path.exists(os.path.join(d, rel)): shutil.copy2(os.path.join(d, rel), com)
        run(["kicad-cli", "sch", "export", "bom", "--fields", BOM_PIPE, "--group-by", "Value,Footprint", "--sort-field",
             "Reference", "-o", os.path.join(com, st + "-bom.csv"), st + ".kicad_sch"], d, log)
        run(["kicad-cli", "sch", "erc", "--severity-all", "--format", "json", "-o", os.path.join(com, st + "-erc.json"),
             st + ".kicad_sch"], d, log)
        lands0 = {os.path.basename(p): sha(p) for p in sorted(glob.glob(os.path.join(pretty, "*.kicad_mod")))}
        cfg = json.load(open(os.path.join(HERE, "boards", L + ".json"), encoding="utf-8"))
        m = re.search(r'\(comment 1 "Phase ([A-Za-z0-9]+)', open(os.path.join(com, st + ".kicad_sch"), encoding="utf-8").read())
        label = m.group(1) if m else (cfg.get("phase") or "")
        env = dict(os.environ); env["PHASE"] = label
        for k, v in (cfg.get("gen_env") or {}).items(): env.setdefault(k, str(v))   # full.sh: a caller's own value wins
        codes = []
        for g in cfg.get("footprint_generator") or []:
            codes.append(run([sys.executable, "../tools/" + g, "../meshsat.pretty"], d, log, env=env))
        codes.append(run([sys.executable, "../tools/gen_sch_%s.py" % L, st + ".kicad_sch", st], d, log, env=env))
        n = os.path.join(d, "out", st + ".net")
        if os.path.exists(n): os.remove(n)
        codes.append(run(["bash", "../tools/build_sch.sh", ".", st], d, log, env=env))
        lands1 = {os.path.basename(p): sha(p) for p in sorted(glob.glob(os.path.join(pretty, "*.kicad_mod")))}
        res = {}
        for kind, c, r in (("schematic", st + ".kicad_sch", st + ".kicad_sch"), ("netlist", st + ".net", "out/%s.net" % st),
                           ("intent", st + "-intent.json", "out/%s-intent.json" % st), ("bom", st + "-bom.csv", "out/%s-bom.csv" % st),
                           ("erc", st + "-erc.json", "out/%s-erc.json" % st)):
            cp, rp = os.path.join(com, c), os.path.join(d, r)
            if not (os.path.exists(cp) and os.path.exists(rp)): res[kind] = "MISSING"; continue
            pr = subprocess.run([sys.executable, os.path.join(HERE, "regen_compare.py"), "pair", kind, cp, rp],
                                capture_output=True, text=True, timeout=900)
            open(os.path.join(out, "parity_%s.json" % kind), "w").write(pr.stdout)
            try: res[kind] = json.loads(pr.stdout).get("result")
            except ValueError: res[kind] = "UNREADABLE: " + (pr.stderr or "")[-200:]
        for r in ("%s.kicad_sch" % st, "out/%s.net" % st, "out/%s-intent.json" % st, "out/%s.net.prov.json" % st,
                  "out/%s-bom.csv" % st, "out/%s-erc.json" % st):
            if os.path.exists(os.path.join(d, r)): shutil.copy2(os.path.join(d, r), os.path.join(out, "regen-" + os.path.basename(r)))
        moved = sorted(k for k in set(lands0) | set(lands1) if lands0.get(k) != lands1.get(k))
        ok = all(c == 0 for c in codes) and all(v in ("PARITY", "PARITY_AFTER_NOISE") for v in res.values()) and not moved
        rc_all |= 0 if ok else 1
        rec = {"board": L, "stem": st, "phase_directory": os.path.basename(d), "phase_label_used": label,
               "board_table_phase": cfg.get("phase"), "gen_env": cfg.get("gen_env"), "comparisons": res,
               "lands_changed_by_the_footprint_generators": moved, "commands": log, "versions": ver,
               "taken_utc": now(), "result": "PARITY" if ok else "DIFFERENT_OR_INCOMPLETE"}
        with open(os.path.join(out, "regen.json"), "w", encoding="utf-8") as fh: json.dump(rec, fh, indent=1, sort_keys=True); fh.write("\n")
        print("handover_exports: regen %s (%s, PHASE=%s): exits %s, %s, lands moved %d: %s" %
              (L, os.path.basename(d), label, codes, res, len(moved), rec["result"]))
    return rc_all


def main(argv):
    ap = argparse.ArgumentParser(prog="handover_exports.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("exports"); e.add_argument("--out", required=True); e.add_argument("--commit", required=True)
    e.add_argument("--letters", default="")
    r = sub.add_parser("regen"); r.add_argument("--out", required=True); r.add_argument("--letters", required=True)
    a = ap.parse_args(argv)
    a.out = os.path.abspath(a.out); os.makedirs(a.out, exist_ok=True)
    return exports(a) if a.cmd == "exports" else regen(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
