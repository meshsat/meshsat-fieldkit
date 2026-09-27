#!/usr/bin/env python3
"""Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): the index lines for the files it adds, in two shared indexes
(outside its ownership; reason: a file in v2/vendor/ or v2/docs/records/ without its index line is a document nobody can
trace). Idempotent; run from the repository root after the new files are in the tree:  python3 drafts/hc5/apply_index.py

  v2/vendor/sources.txt: where the two maker documents came from.
  v2/docs/records/README.md: the hc5 and w5 folders, and the eight files."""
import hashlib, os

ROOT = os.getcwd()
log = []


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def size(rel):
    return os.path.getsize(os.path.join(ROOT, rel))


# v2/vendor/sources.txt: appended at the end (file lines override folder lines; order does not matter)
p = os.path.join(ROOT, "v2/vendor/sources.txt")
s = open(p, encoding="utf-8").read()
lines = [
    "standards/nxp-um10204-rev6-i2c-bus-specification.pdf   # NXP UM10204 Rev. 6 (4 April 2014): nxp.com answers the URL with a 3-page stub of Rev. 7 (HTTP 200 at 2026-09-27) and 404 on the older paths; the Internet Archive's capture https://web.archive.org/web/20201218225234id_/https://www.nxp.com/docs/en/user-guide/UM10204.pdf is the whole 64-page Rev. 6, sha256 b7619700e8bb9dd4 (cited by v2/docs/HW-FW-CONTRACT.md section 6)",
    "connectors/3m-3365-flat-cable-ts0080.pdf   # https://multimedia.3m.com/mws/media/22052O/3m-round-conductor-flat-cable-050in-3365-series-ts0080.pdf, fetched 2026-09-27 (TS-0080-B, 7 May 2009), sha256 1dc900fe684bd6c2 (cited by v2/docs/HW-FW-CONTRACT.md section 6)",
]
for ln in lines:
    key = ln.split()[0]
    if ("\n" + key + " ") in s or s.startswith(key + " "):
        log.append("already: " + key)
    else:
        s = s.rstrip("\n") + "\n" + ln + "\n"; log.append("added: " + key)
open(p, "w", encoding="utf-8").write(s)

# v2/docs/records/README.md: two folder rows and five file rows
p = os.path.join(ROOT, "v2/docs/records/README.md")
s = open(p, encoding="utf-8").read()
row_anchor = "| `w6/` | foundation workstream 6 (findings review), 25 September |\n"
assert s.count(row_anchor) == 1
if "| `hc5/` |" in s:
    log.append("already: folder rows")
else:
    s = s.replace(row_anchor, row_anchor
                  + "| `hc5/` | the layer 5 closer (27 September): the kit I2C bus budget, its script and two outputs, the interface contracts' field check with its output, and the USB 2.0 clauses it cites; authored in the tree, not filed from drafts |\n"
                  + "| `w5/` | foundation workstream 5 (the hardware and firmware contract, round 2), 26 September |\n")
    log.append("added: folder rows")
files = [("hc5/kit_i2c_budget.py", "authored by `fnd/hc5`", "`v2/docs/HW-FW-CONTRACT.md` section 6"),
         ("hc5/kit_i2c_budget.out.txt", "its output on the netlists at `e3aedb25`", "`v2/docs/HW-FW-CONTRACT.md` section 6"),
         ("hc5/kit_i2c_budget.round8-d.out.txt", "its output with board D's netlist of `fnd/r8int1`", "`v2/docs/HW-FW-CONTRACT.md` section 6"),
         ("hc5/check_contract_fields.py", "authored by `fnd/hc5`", "`v2/docs/ARCHITECTURE.md` section 12; `pcb_interfaces.yaml` board_to_board header"),
         ("hc5/check_contract_fields.out.txt", "its output on `pcb_interfaces.yaml` after the five `drafts/hc5` scripts, on `a8652172` (the body is the same on `84e52461`)", "`v2/docs/ARCHITECTURE.md` section 12"),
         ("hc5/usb-2-0-clauses-cited.md", "authored by `fnd/hc5` from `usb_20.pdf` (sha256 d39698a3...)", "`v2/docs/HW-FW-CONTRACT.md` SC-HF-06, HF-F06; `pcb_interfaces.yaml` IF-MON"),
         ("r4a/r4-hwfw-contract.md", "`fnd/r4a` `drafts/r4-hwfw-contract.md`", "`v2/docs/HW-FW-CONTRACT.md` section 3.1"),
         ("w5/w5-hw-fw-contract.md", "`fnd/w5` `drafts/w5-hw-fw-contract.md`", "`v2/docs/HW-FW-CONTRACT.md` sections 0 and 3")]
file_anchor = [l for l in s.split("\n") if l.startswith("| `w6/w6-findings.md` |")]
assert len(file_anchor) == 1
fa = file_anchor[0] + "\n"
new_rows = ""
for rel, src, cited in files:
    if ("| `%s` |" % rel) in s:
        log.append("already: " + rel); continue
    new_rows += "| `%s` | `%s` | %d | %s | %s |\n" % (rel, sha("v2/docs/records/" + rel), size("v2/docs/records/" + rel), src, cited)
    log.append("added: " + rel)
s = s.replace(fa, fa + new_rows)
assert chr(0x2014) not in s and chr(0x2013) not in s
open(p, "w", encoding="utf-8").write(s)
print("\n".join(log))
