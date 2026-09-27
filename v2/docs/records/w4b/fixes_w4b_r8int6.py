#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): the independent check's corrections of stream w4b
(w4b check 1, an AI check) that fall outside the stream's own page drafts, and the filing of its two maker documents.
Idempotent: each edit is skipped when its new text is already there, and asserts its old text exactly once otherwise.

  1. gen_sch_b.py comments: the two maker documents cited at `drafts/w4b/datasheets/` now at their v2/vendor/ paths, and
     the firmware duty named for the panel firmware (the kit I2C master that writes U6, PANEL.md section 7), where the
     comment said "the bridge". Comments only: the netlist does not move (the final regeneration proves it); board B's
     provenance sidecar is re-stamped because the generator's bytes are its identity.
  2. ARCHITECTURE.md's IF-B-RB9704 row still said U6's pull-ups hold RB_IEN high until U6 is configured.
  3. HW-FW-CONTRACT.md FW-B13 still listed RB_IEN as a U6 output, and carried none of the new firmware duty; section 4
     gains the fnd/w4b row.
  4. EMCON.md section 6, bench row E-04, still drove RB_IEN high from U6; it is the request RB_SW_IEN now.
  5. The maker documents: TI SN74LV1T08 (SCLS739F) to v2/vendor/ti/, Ground Control's RockBLOCK 9704 hardware page (and its
     plain-text rendering) to v2/vendor/rockblock/, with their SOURCES.yaml entries (the stream's sources-entries.yaml,
     the text rendering's path repointed), sources.txt and vendor-status.txt lines.
Usage: fixes_w4b_r8int6.py <repo root>"""
import hashlib, os, shutil, sys

T = sys.argv[1]
K = os.path.dirname(os.path.abspath(__file__))


def edit(path, old, new, count=1):
    p = os.path.join(T, path); s = open(p, encoding="utf-8").read()
    if new in s and old not in s:
        print("  already: %s %r" % (path, new[:60])); return
    assert s.count(old) == count, "%s: expected %d of %r, found %d" % (path, count, old[:80], s.count(old))
    s2 = s.replace(old, new); assert s2 != s
    open(p, "w", encoding="utf-8").write(s2); print("  edited: %s %r" % (path, old[:60]))


GEN = "v2/ecad/tools/gen_sch_b.py"
edit(GEN, "(Texas Instruments, SOT-23-5, 27 September 2026). Fetched by stream w4b: drafts/w4b/datasheets/ti-sn74lv1t08.pdf.",
     "(Texas Instruments, SOT-23-5, 27 September 2026). Fetched by stream w4b: v2/vendor/ti/ti-sn74lv1t08.pdf.")
edit(GEN, "hardware, section Connections, 3 - I_EN, fetched 27 September 2026, drafts/w4b/datasheets/);",
     "hardware, section Connections, 3 - I_EN, fetched 27 September 2026, v2/vendor/rockblock/);")
edit(GEN, "# bridge keeps RB_SW_IEN low after an EMCON until RB_STATUS reads low;",
     "# panel firmware keeps RB_SW_IEN low after an EMCON until RB_STATUS reads low (PANEL.md correction (17));")

edit("v2/docs/ARCHITECTURE.md",
     "SD-EMC-2 back-feed through the control lines (U6's internal pull-ups hold RB_IEN and RB_CTRL high until U6 is configured);",
     "SD-EMC-2 back-feed through the control lines (U6's internal pull-up holds RB_CTRL high until U6 is configured; since stream w4b RB_IEN is U536's output, EMCON_HW AND U6's request RB_SW_IEN, held low by R527 with U536 unpowered);")

HF = "v2/docs/HW-FW-CONTRACT.md"
edit(HF, "six radio off requests, RB_IEN, RB_CTRL; U7 0x25 inputs and eleven spares (`gen_sch_b.py:1036`, `:1040`) | Outputs before configuration (FW-A08);",
     "six radio off requests, RB_SW_IEN (the RockBLOCK's ENABLE request since stream w4b; U536 ANDs it with EMCON_HW into RB_IEN), RB_CTRL; U7 0x25 inputs and eleven spares (`gen_sch_b.py:1036`, `:1040`) | Outputs before configuration (FW-A08); the panel raises RB_SW_IEN only after +5V_RB is up, writes it low on EMCON, and after a release raises it again only once RB_STATUS reads low (Ground Control's I_EN/I_BTD order; `PANEL.md` correction (17));")
edit(HF, "| `fnd/r8bat` | FW-C09, FW-P01 | the pack readings' 10 s fallback to the reduced mode; the round-8 charge window in the golden image |\n",
     "| `fnd/r8bat` | FW-C09, FW-P01 | the pack readings' 10 s fallback to the reduced mode; the round-8 charge window in the golden image |\n"
     "| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK's ENABLE is EMCON_HW AND U6's request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |\n")

edit("v2/docs/feasibility/EMCON.md",
     "| E-04 | RockBLOCK 9704 | EMCON asserted with `RB_IEN`, `RB_CTRL` and `RB_RXD` driven high by U6 and U18;",
     "| E-04 | RockBLOCK 9704 | EMCON asserted with `RB_SW_IEN` (the ENABLE request, since stream w4b; `RB_IEN` is U536's output, 4c), `RB_CTRL` and `RB_RXD` driven high by U6 and U18;")

# 5. the maker documents
DS = os.path.join(K, "datasheets")
FILES = [("ti-sn74lv1t08.pdf", "v2/vendor/ti/ti-sn74lv1t08.pdf", "cb0644caef3b0dedec65c793a2c19707208e377caf39a12098263fe237a49a94"),
         ("groundcontrol-docs-rockblock-9704-hardware-20260927.html", "v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.html",
          "e02ea57445550ecb615f6e4fe6f5f172711184a74c07bdf10cc0e16d1a31b285"),
         ("groundcontrol-docs-rockblock-9704-hardware-20260927.txt", "v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt", None)]
for src, dst, sha in FILES:
    b = open(os.path.join(DS, src), "rb").read()
    if sha: assert hashlib.sha256(b).hexdigest() == sha, src
    d = os.path.join(T, dst)
    if os.path.exists(d): assert open(d, "rb").read() == b, dst
    else: os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(os.path.join(DS, src), d)
TXT_SHA16 = hashlib.sha256(open(os.path.join(DS, FILES[2][0]), "rb").read()).hexdigest()[:16]

SY = os.path.join(T, "v2/vendor/SOURCES.yaml")
s = open(SY, encoding="utf-8").read()
if "  - id: logic-and-lv1t08\n" not in s:
    ent = open(os.path.join(K, "sources-entries.yaml"), encoding="utf-8").read()
    ent = ent[ent.index("  - id: logic-and-lv1t08\n"):]
    old = "a plain-text rendering is beside it (drafts/w4b/datasheets/groundcontrol-docs-rockblock-9704-hardware-20260927.txt)"
    assert ent.count(old) == 1
    ent = ent.replace(old, "a plain-text rendering is beside it (v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt, sha256/16 %s)" % TXT_SHA16)
    old2 = "stock 7,904 on 27 September 2026 (drafts/w4b/evidence/jlc-query-sn74lv1t08.txt)"
    assert ent.count(old2) == 1
    ent = ent.replace(old2, "stock 7,904 on 27 September 2026 (v2/docs/records/w4b/evidence/jlc-query-sn74lv1t08.txt)")
    ent = ent.replace('on_main: false', 'on_main: true').replace(
        'adopted_in: "board B, stream w4b (fnd/w4b), 27 September 2026"',
        'adopted_in: "board B, stream w4b (fnd/w4b), integrated 27 September 2026 (the r8int6 integration, set 6 of the handover)"')
    assert "drafts/" not in ent, ent
    assert s.count("\nowed:\n") == 1
    head, tail = s.split("\nowed:\n")
    s = head.rstrip("\n") + "\n" + ent.rstrip("\n") + "\n\nowed:\n" + tail
    import yaml
    d = yaml.safe_load(s)
    ids = [e.get("id") for e in d["parts"]]
    assert "logic-and-lv1t08" in ids and "rockblock-9704-hardware-page" in ids, ids[-4:]
    open(SY, "w", encoding="utf-8").write(s); print("  SOURCES.yaml: two entries added")

ST = os.path.join(T, "v2/vendor/sources.txt")
s = open(ST, encoding="utf-8").read()
L = ["ti/ti-sn74lv1t08.pdf   # https://www.ti.com/lit/ds/symlink/sn74lv1t08.pdf, fetched 2026-09-27T14:25Z by stream w4b (SCLS739F, October 2025), sha256 cb0644caef3b0ded",
     "rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.html   # https://docs.groundcontrol.com/iot/rockblock-9704/hardware, fetched 2026-09-27T14:05Z by stream w4b, sha256 e02ea57445550ecb",
     "rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt   # the plain-text rendering of the .html beside it, made by stream w4b, sha256 %s" % TXT_SHA16]
add = [x for x in L if x.split()[0] + " " not in s]
if add:
    open(ST, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + "\n".join(add) + "\n"); print("  sources.txt: %d line(s)" % len(add))
VS = os.path.join(T, "v2/vendor/vendor-status.txt")
s = open(VS, encoding="utf-8").read()
L = ["ti/ti-sn74lv1t08.pdf   current   # SN74LV1T08DBVR, board B's card-buck enable gates U116, U216, U316 (stream w4b, W4B-D3; SOURCES.yaml logic-and-lv1t08)",
     "rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.html   current   # the RockBLOCK 9704 hardware page: I_EN, P_EN, I_BTD and the startup and shutdown sequences (stream w4b, W4B-D1)",
     "rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt   current   # the plain-text rendering of the hardware page beside it"]
add = [x for x in L if x.split()[0] + " " not in s]
if add:
    open(VS, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + "\n".join(add) + "\n"); print("  vendor-status.txt: %d line(s)" % len(add))
print("fixes_w4b_r8int6: done")
