#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): stream w4c's step 4, the e-paper driver's sheet
(UltraChip UC8253c A0.6, as Elecrow serves it) filed at v2/vendor/pdi/ with the stream's SOURCES.yaml entry
(sources-w4c.yaml, marked as adopted) and one line each in sources.txt and vendor-status.txt. Idempotent.
Usage: fixes_w4c_r8int6.py <repo root>"""
import hashlib, os, shutil, sys
import yaml

T = sys.argv[1]; K = os.path.dirname(os.path.abspath(__file__))
SHA = "bee25538177b8cc6f67c1ffe696d8fd09bda7842b42e021fb9bd41a3da91c125"
src = os.path.join(K, "vendor", "ultrachip-uc8253c-a0.6.pdf"); dst = os.path.join(T, "v2/vendor/pdi/ultrachip-uc8253c-a0.6.pdf")
b = open(src, "rb").read(); assert hashlib.sha256(b).hexdigest() == SHA
if os.path.exists(dst): assert open(dst, "rb").read() == b
else: shutil.copyfile(src, dst)
SY = os.path.join(T, "v2/vendor/SOURCES.yaml"); s = open(SY, encoding="utf-8").read()
if "  - id: epd-driver-uc8253c\n" not in s:
    ent = open(os.path.join(K, "sources-w4c.yaml"), encoding="utf-8").read()
    ent = ent[ent.index("  - id: epd-driver-uc8253c\n"):]
    for a, c in (('on_main: false', 'on_main: true'),
                 ('adopted_in: "fnd/w4c (27 September 2026), pending merge"',
                  'adopted_in: "board C, stream w4c (fnd/w4c), integrated 27 September 2026 (the r8int6 integration, set 6 of the handover)"')):
        assert ent.count(a) == 1, a; ent = ent.replace(a, c)
    head, tail = s.split("\nowed:\n")
    s = head.rstrip("\n") + "\n" + ent.rstrip("\n") + "\n\nowed:\n" + tail
    assert "epd-driver-uc8253c" in [e.get("id") for e in yaml.safe_load(s)["parts"]]
    open(SY, "w", encoding="utf-8").write(s); print("  SOURCES.yaml: epd-driver-uc8253c added")
for f, line in (("v2/vendor/sources.txt", "pdi/ultrachip-uc8253c-a0.6.pdf   # https://www.elecrow.com/download/product/DIE01237S/UC8253_Datasheet.pdf, fetched 2026-09-27T14:12Z by stream w4c (UltraChip 03-DTS-1891 UC8253c A0.6 as Elecrow serves it; UltraChip publishes no public copy), sha256 bee25538177b8cc6"),
                ("v2/vendor/vendor-status.txt", "pdi/ultrachip-uc8253c-a0.6.pdf   current   # UC8253c, the driver inside board C's E2370KS0C1 panel: EPD_VCC's supply currents (PWR-001, stream w4c; SOURCES.yaml epd-driver-uc8253c)")):
    p = os.path.join(T, f); t = open(p, encoding="utf-8").read()
    if line.split()[0] + " " not in t:
        open(p, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + line + "\n"); print("  %s: one line" % f)
print("fixes_w4c_r8int6: done")
