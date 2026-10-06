#!/usr/bin/env python3
"""retake_pdf_text.py: take the text of the makers' PDFs a record reads, once, as committed verbatim inputs (MESHSAT-1357, Q-41
item 1, W34, 6 October 2026; the reading module is pdftext.py beside this file, whose header states the defect and the rules).

  python3 v2/docs/records/_lib/retake_pdf_text.py <record dir> [<pdf> ...]

It reads every `PDFTEXT = {<pdf>: [<options>, ...]}` table of the record's scripts (module level, a literal, read with ast: the
scripts are never imported or run), restricted to the PDFs named on the command line when any are, and for each declared
extraction runs this host's pdftotext with exactly those options (in the order pdftext.run_args gives; pdftotext's output does not
depend on the order) on the PDF, then writes, beside the PDF in pdftext/ (under held/ for a held-back sheet, which .gitignore
already excludes):
  <pdf stem>.<options tag>.txt            the text, the bytes pdftotext printed, unchanged;
  <pdf stem>.<options tag>.txt.meta.json  the PDF's path and sha256, the text's sha256 and length, the options and the command, the
                                          first line of `pdftotext -v`, the poppler-data package's version, the date (Europe/Amsterdam).
A file is replaced only after pdftotext exited 0 and printed a complete text (written to a temporary file, then os.replace); when the
text, the PDF and the tool are unchanged nothing is written (the date of an unchanged text never moves). Each extraction prints one
line: UNCHANGED, WRITTEN (new) or CHANGED (old and new sha256/16 and lengths), and whether it is to be committed or held back.

The runner is the host of record (Debian 12, pdftotext 22.12.0, poppler-data present): the text it takes is the text every host then
reads. A sheet that is absent is refused with its route (the record's fetch_held_back.py for a held-back one). Exit 0: every
declared extraction is present and current; 2: a declared PDF is absent, a table does not parse, or pdftotext failed.
Stdlib; pdftotext, git and dpkg-query on PATH."""
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("records_pdftext", os.path.join(HERE, "pdftext.py"))
PT = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(PT)


def refuse(msg):
    sys.stderr.write("retake_pdf_text: %s; refusing\n" % msg)
    sys.exit(2)


def tables(record_abs):
    """{pdf: [options, ...]} merged over the record's scripts' PDFTEXT literals."""
    out = {}
    for n in sorted(os.listdir(record_abs)):
        p = os.path.join(record_abs, n)
        if not (n.endswith(".py") and os.path.isfile(p)):
            continue
        try:
            tree = ast.parse(open(p, encoding="utf-8").read(), p)
        except SyntaxError as e:
            refuse("%s does not parse (%s)" % (n, e))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PDFTEXT" for t in node.targets):
                try:
                    d = ast.literal_eval(node.value)
                except ValueError:
                    refuse("%s's PDFTEXT is not a literal" % n)
                if not isinstance(d, dict):
                    refuse("%s's PDFTEXT is not a dict" % n)
                for pdf, opts in d.items():
                    for o in opts:
                        if PT.tag(o) not in {PT.tag(x) for x in out.get(pdf, [])}:
                            out.setdefault(pdf, []).append(list(o))
    return out


def tool_version():
    r = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
    lines = (r.stderr or r.stdout).strip().splitlines()
    if not lines:
        refuse("pdftotext -v printed nothing (is poppler-utils installed?)")
    return lines[0]


def poppler_data():
    r = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "poppler-data"], capture_output=True, text=True)
    return ("poppler-data " + r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else "poppler-data not installed (or no dpkg)"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    rec = os.path.abspath(argv[0])
    if not os.path.isdir(rec):
        refuse("%s is not a directory" % argv[0])
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=rec, capture_output=True, text=True).stdout.strip()
    if not top:
        refuse("%s is not inside a git checkout" % argv[0])
    rec_rel = os.path.relpath(rec, top)
    decl = tables(rec)
    if not decl:
        refuse("no script of %s declares a PDFTEXT table" % rec_rel)
    only = argv[1:]
    if only:
        names = {os.path.normpath(os.path.relpath(os.path.abspath(x), top)) if os.path.exists(x) else x for x in only}
        sel = {p: o for p, o in decl.items() if p in names or os.path.basename(p) in names}
        unknown = [x for x in names if x not in sel and not any(os.path.basename(p) == x for p in sel)]
        if unknown:
            refuse("not declared by %s: %s" % (rec_rel, ", ".join(sorted(unknown))))
        decl = sel
    version, pdata = tool_version(), poppler_data()
    today = datetime.datetime.now(ZoneInfo("Europe/Amsterdam")).date().isoformat()
    print("retake_pdf_text: %s, %d PDF(s), %s, %s" % (rec_rel, len(decl), version, pdata))
    counts = {"UNCHANGED": 0, "WRITTEN": 0, "CHANGED": 0}
    for pdf in sorted(decl):
        src = os.path.join(top, pdf)
        if not os.path.isfile(src):
            route = "fetch it with %s/fetch_held_back.py" % rec_rel if PT.held(pdf) else "it is not in this tree"
            refuse("%s is absent (%s)" % (pdf, route))
        pdf_sha = sha(open(src, "rb").read())
        for o in decl[pdf]:
            args = PT.run_args(o)
            txt_rel = PT.text_path(pdf, o)
            dst = os.path.join(top, txt_rel)
            r = subprocess.run(["pdftotext"] + args + [src, "-"], capture_output=True)
            if r.returncode != 0 or not r.stdout:
                refuse("pdftotext %s %s exited %d with %d bytes (%s)" % (" ".join(args), pdf, r.returncode, len(r.stdout),
                                                                      r.stderr.decode("utf-8", "replace").strip()[:200]))
            body = r.stdout
            try:
                body.decode("utf-8")
                enc = ""
            except UnicodeDecodeError:
                enc = " (NOT valid UTF-8: the readers replace the bad bytes, as before)"
            cr = " (carries a carriage return: text=True readers translate it, as before)" if b"\r" in body else ""
            meta = {"pdf": pdf, "pdf_sha256": pdf_sha, "text": txt_rel, "text_sha256": sha(body), "text_bytes": len(body),
                    "options": args, "command": "pdftotext %s%s -" % (" ".join(args) + " " if args else "", pdf),
                    "pdftotext": version, "poppler_data": pdata, "taken": today, "held_back": PT.held(pdf),
                    "taken_by": "v2/docs/records/_lib/retake_pdf_text.py"}
            old = open(dst, "rb").read() if os.path.isfile(dst) else None
            mp = PT.meta_path(dst)
            om = json.load(open(mp, encoding="utf-8")) if os.path.isfile(mp) else None
            same = old == body and om is not None and all(om.get(k) == meta[k] for k in
                                                          ("pdf", "pdf_sha256", "text_sha256", "options", "pdftotext", "poppler_data"))
            if same:
                st = "UNCHANGED"
            else:
                st = "WRITTEN" if old is None else "CHANGED"
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                _write(dst, body)
                _write(mp, (json.dumps(meta, indent=1, sort_keys=True) + "\n").encode("utf-8"))
            counts[st] += 1
            ign = subprocess.run(["git", "-C", top, "check-ignore", "-q", txt_rel]).returncode == 0
            where = "held back (ignored by .gitignore)" if ign else "to commit"
            if PT.held(pdf) and not ign:
                refuse("%s is a held-back sheet's text but .gitignore does not exclude it" % txt_rel)
            if not PT.held(pdf) and ign:
                refuse("%s is a committed sheet's text but .gitignore excludes it" % txt_rel)
            chg = "" if st != "CHANGED" else " (was %s, %d bytes)" % (sha(old)[:16], len(old))
            print("   %-9s %s %7d bytes %s [%s]%s%s%s" % (st, meta["text_sha256"][:16], len(body), txt_rel, where, chg, enc, cr))
    print("retake_pdf_text: %d extraction(s): %d unchanged, %d written, %d changed" % (
        sum(counts.values()), counts["UNCHANGED"], counts["WRITTEN"], counts["CHANGED"]))
    return 0


def _write(dst, data):
    tmp = dst + ".tmp-retake"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dst)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
