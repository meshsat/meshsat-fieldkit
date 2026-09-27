"""REQ-052 and CFL-006: the two warnings left after fnd/hc3's apply script on the r8int4 tree, re-read by hand and
rebound. Edits by record id with asserted old text. Run from the worktree root."""
import hashlib
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))
def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == 1, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
GB, EC = sha('v2/ecad/tools/gen_sch_b.py'), sha('v2/ecad/tools/pcb_energy_chain.yaml')
assert GB == 'af6e5821e21b70ef', GB
t = sub_in(t, 'REQ-052', '"v2/ecad/tools/gen_sch_b.py@dedaf34ce285e5ff"]', '"v2/ecad/tools/gen_sch_b.py@%s"]' % GB)
t = sub_in(t, 'REQ-052', """          (6c3c93b7f32f953a), so it stands on the file at 08d44b37fa8e2717
""", """          (6c3c93b7f32f953a), so it stands on the file at 08d44b37fa8e2717
      - >-
          v2/ecad/tools/gen_sch_b.py re-read by hand at the r8int4 integration of 27 September 2026 (main 38dcd764,
          board B's round 8, b76c18cb): the hub ports (PORTS, line 903: bank 1 the LimeSDR, the panel controller's
          USB_PNL, the camera and the RockBLOCK; bank 2 GNSS, both E72 and the QMX; bank 3 board D8, board E6, the
          wall port and the 5G module's USB), the bank ring (f = s % 3 + 1, line 936) and the LoRa module on S3's SPI
          (J_SPI3, U12) are unchanged from the file at dedaf34ce285e5ff; round 8 changed the fabric's control plane,
          the EMCON stages and the parts, none of which moves a device between banks, so the FAIL stands on the file
          at {GB}
""".replace("{GB}", GB))
t = sub_in(t, 'CFL-006', '      - "v2/ecad/tools/pcb_energy_chain.yaml@39feae15de45d37e"\n', '      - "v2/ecad/tools/pcb_energy_chain.yaml@%s"\n' % EC)
t = sub_in(t, 'CFL-006', """          on the file at 1cd670d6c7685645
""", """          on the file at 1cd670d6c7685645
      - >-
          v2/ecad/tools/pcb_energy_chain.yaml re-read by hand at the r8int4 integration of 27 September 2026 (main
          38dcd764 with the layer-3 closer's correction applied by its script): the header (line 19) and the pack
          source (line 46) name the one 4S3P block of Samsung INR18650-35E, about 145 Wh, as the reading says; board
          B's round 8 (b76c18cb) changed other chains of the file, not the pack's, so the reading stands on the file
          at %s
""" % EC)
open(P, 'w').write(t)
print("post_c23_registry2: REQ-052 on gen_sch_b.py %s, CFL-006 on pcb_energy_chain.yaml %s" % (GB, EC))
