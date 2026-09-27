"""verify c23's new contradictions, fixed in the documents on the integration tree (r8int4, 27 September 2026).
Each edit asserts its old text; OPERATING-ENVELOPE's two pins are re-taken after its edit. Run from the worktree root."""
import hashlib
def sub(t, a, b, n=1):
    assert t.count(a) == n, (t.count(a), a[:100]); assert a != b
    return t.replace(a, b)
# 1. CONOPS: the Heat stage row's guarantee (what acts before what) and its qualification; 4c's present tense
p = 'v2/docs/CONOPS.md'; t = open(p).read()
t = sub(t, "| SW decides, FW switches; the pack gauge's own windows and board P's second level act whatever the kit can read (the second level destructively, above the cells' limit), and the hot stop (next row) acts before them on the cells' measured temperature |",
"| SW decides, FW switches; the pack gauge's own windows and board P's second level act whatever the kit can read (the second level destructively, above the cells' limit). On the cells' measured temperature the gauge's charge window acts first (a charge start refused above 42 C, a running charge ended above 43 C, OTC at 44 C; section 4c), and the hot stop (next row) is designed to act after it and before the gauge's discharge cut (OTD, 57.5 C), board P's second level, the gauge's SOT and the PTC; as generated the hot stop has no path in this stage, whose one module does not host bank 3, until HOT-R1 is in the generators of boards A and E (its requirement reads FAIL until then, next row) |")
t = sub(t, """current, the hot stop included, which keeps the cells inside their limit at any conductance; what changes is at which
ambient each acts""",
"""current, the hot stop included: REQ-077 requires it to act before any cell passes +60 C in every mode and on every
input, and the design intends it to do so at any conductance once HOT-R1 is in the generators of boards A and E (the
requirement reads FAIL on the generated boards until then) and on the provisional error budget (H2 leaves 0.93 K for
the budget's two TBD terms, `TEST-PLAN.md` P14); whether it acts inside the envelope is FEA-004's, open. What changes is
at which ambient each acts""")
open(p, 'w').write(t)
# 2. OPERATING-ENVELOPE section 4: one release semantics with CONOPS 4c, and the present tense restated
p = 'v2/docs/OPERATING-ENVELOPE.md'; t = open(p).read()
t = sub(t, """  it, reaches +56.5 C the kit sheds to its minimum load (every module shut down), at +57.0 C it shuts itself down, and
  it restarts once the cells read +46.5 C or less; the sensor controller detects and the panel controller acts, on the
  pack and on every input. It is not a carve-out and moves no limit: it keeps idle cells on an input inside their
  +60 C where the enclosure cannot, and the kit runs no module while it acts. Whether it acts inside -20 to +40 C is""",
"""  it, reaches +56.5 C the kit sheds to its minimum load (H1, every module shut down), and at +57.0 C with H1 acting it
  shuts itself down (H2). H1 ends by itself once the hottest cell reads +46.5 C or less and at least 30 minutes have
  passed since the stop, when the kit raises the heat stage's one module; after H2 the kit restarts only when the
  operator presses MAIN, and then raises no module until the hottest cell reads +46.5 C or less (`CONOPS.md` section
  4c). The sensor controller detects and the panel controller acts, on the pack and on every input. It is not a
  carve-out and moves no limit. What it is for: REQ-077 requires the kit to act before any cell passes +60 C, idle
  cells on an input included, where the enclosure alone cannot keep them under it, and the design intends the stop to
  do that once HOT-R1 is in the generators of boards A and E (the requirement reads FAIL on the generated boards until
  then) and on the provisional error budget (`TEST-PLAN.md` P14); the kit runs no module while it acts. Whether it acts inside -20 to +40 C is""")
open(p, 'w').write(t)
doc_sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
OLD = "354bc222868bbfa93d36113bb4a1844d0bbc9f390f7818ddc266c844335f32b0"
# 3. pcb_envelope.yaml: the release semantics as data, and the document re-pinned
p = 'v2/ecad/tools/pcb_envelope.yaml'; t = open(p).read()
t = sub(t, """    released_any_cell_c: 46.5
""", """    released_any_cell_c: 46.5
    release: "H1 ends by itself once the hottest cell reads the release value or less and at least 30 minutes have passed since the stop, the kit then raising the heat stage's one module; H2 ends only by the operator's MAIN, after which no module is raised until the hottest cell reads the release value or less (CONOPS.md section 4c)"
""")
t = sub(t, 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 after pass 3' % OLD,
        'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after section 4\'s hot-stop paragraph was made to state CONOPS 4c\'s release (H1 by itself, H2 only by MAIN) and what REQ-077 requires rather than a present-tense guarantee (verify c23; no number changed), before it after pass 3' % doc_sha)
open(p, 'w').write(t)
# 4. pcb_rules_coverage.yaml: ENV-001 pins the same document
p = 'v2/ecad/tools/pcb_rules_coverage.yaml'; t = open(p).read()
t = sub(t, 'verified_sha: "%s",' % OLD, 'verified_sha: "%s",' % doc_sha)
t = sub(t, "changes no number the envelope adopts; re-pinned 27 Sep 2026.",
        "changes no number the envelope adopts; re-pinned 27 Sep 2026, and again the same day by the integrator after section 4's hot-stop paragraph was made to state CONOPS 4c's release semantics and what REQ-077 requires (no number changed).")
open(p, 'w').write(t)
print("edit_c23_contradictions: OPERATING-ENVELOPE now", doc_sha[:16])
