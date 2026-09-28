#!/usr/bin/env python3
"""rules_status holds a reading to the models a TRACKED MANIFEST pins (MESHSAT-1357, layer 9, stream w5si2, 28
September 2026; rules_status.PINNED_INPUTS, added by v2/docs/records/w5si/apply/apply_rules_status_pinned_models.py).

The makers' IBIS models are not in the repository, so no commit dates them. These tests build a git repository of
their OWN in a temporary directory (a committed manifest, an ignore rule, a model that is present and ignored or is
absent), point rules_status at it for the length of one test, and ask what a reading reads in each state. Nothing of
this tree is read but the tools, and nothing anywhere is fetched.

Until the draft is applied rules_status has no _pinned_state and every test here is SKIPPED, saying so."""
import os, sys, hashlib, tempfile, subprocess, contextlib

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip
import rules_status as S
import ibis_manifest as IM

MODEL = b"[IBIS Ver] 3.2\n[File Name] fix.ibs\n[Copyright] Copyright 2026 a fixture.\n[Component] FIX\n[End]\n"
OTHER = MODEL + b"| a later revision\n"
FILE = "v2/vendor/fix/ibis/fix.ibs"
P16 = hashlib.sha256(MODEL).hexdigest()[:16]
TS = "2026-09-26T10:00:00Z"                       # the reading's instant
BEFORE, AFTER = "2026-09-26T09:00:00+00:00", "2026-09-26T11:00:00+00:00"
M = {"manifest_version": "test", "boards": {"x": {"project": "pcb-x", "required": True}}, "promotion": {"frozen": False}}
REGS = {"invalidated": {}, "compatibility": [], "errors": []}


def _need():
    if not hasattr(S, "_pinned_state"):
        raise Skip("rules_status has no _pinned_state: the draft v2/docs/records/w5si/apply/apply_rules_status_pinned_models.py "
                   "is not applied to this tree (rules_status.py is the integrator's file)")


def _git(repo, *a, when=BEFORE):
    env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    r = subprocess.run(["git", "-C", repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"] + list(a),
                       capture_output=True, text=True, env=env, timeout=30)
    if r.returncode != 0: raise Skip("git cannot build the fixture repository (%s)" % (r.stderr.strip()[:120] or a))
    return r.stdout


def _repo(model=MODEL, pinned=MODEL, commit_manifest=True):
    """A repository whose manifest pins `pinned` and whose tree holds `model` (None: absent), ignored."""
    import yaml
    repo = tempfile.mkdtemp(prefix="pinned-models-")
    os.makedirs(os.path.join(repo, "v2", "vendor", "fix", "ibis"))
    os.makedirs(os.path.join(repo, "v2", "ecad", "pcb-x"))
    open(os.path.join(repo, ".gitignore"), "w").write("v2/vendor/*/ibis/*.ibs\n")
    row = {"id": "fix", "maker": "fixture", "part": "FIX", "file": FILE, "url": "https://example.invalid/fix.ibs", "container": "ibs",
           "sha256": hashlib.sha256(pinned).hexdigest(), "bytes": len(pinned), "fetched": "never: a fixture",
           "notice": {"kind": "COPYRIGHT_NO_GRANT", "says": "a fixture", "quotes": [{"lines": "3", "text": "[Copyright] Copyright 2026 a fixture."}]}}
    yaml.safe_dump({"schema_version": 1, "models": [row]}, open(os.path.join(repo, IM.MANIFEST_REL), "w"))
    if model is not None: open(os.path.join(repo, FILE), "wb").write(model)
    _git(repo, "init", "-q")
    _git(repo, "add", ".gitignore")
    if commit_manifest: _git(repo, "add", IM.MANIFEST_REL)
    _git(repo, "commit", "-q", "-m", "fixture")
    assert FILE not in _git(repo, "ls-files"), "the fixture's model is tracked"
    return repo


@contextlib.contextmanager
def _at(repo):
    """rules_status looks at the fixture repository for the length of one test; everything is put back."""
    keep = (S.ECAD, S.PINNED_INPUTS, dict(S._CFG_WHEN), dict(S._GIT_DIRTY))
    S.ECAD = os.path.join(repo, "v2", "ecad")
    S.PINNED_INPUTS = {"rules_status.py": ("../vendor/ibis-manifest.yaml",)}
    S._CFG_WHEN.clear(); S._GIT_DIRTY.clear()
    try: yield {"rules_status.py": ("../vendor/ibis-manifest.yaml",)}
    finally:
        S.ECAD, S.PINNED_INPUTS = keep[0], keep[1]
        S._CFG_WHEN.clear(); S._CFG_WHEN.update(keep[2]); S._GIT_DIRTY.clear(); S._GIT_DIRTY.update(keep[3])


def _reading(repo, model="READ", sha=P16, manifest=True, as_document=False):
    """A reading of `rules_status.py` (the fixtures' writer) that asked for the model: read at `sha`, or recorded absent,
    or not asked for at all (model None)."""
    inputs = {"netlist": {"path": "pcb-x/out/pcb-x.net", "sha256_16": "a" * 16}}
    if manifest:
        inputs["ibis_manifest"] = {"path": IM.MANIFEST_REL, "sha256_16": hashlib.sha256(open(os.path.join(repo, IM.MANIFEST_REL), "rb").read()).hexdigest()[:16]}
    if model == "READ":
        inputs["document_7" if as_document else "model_1"] = dict({"path": FILE, "sha256_16": sha}, **({} if as_document else {"pinned_sha256_16": sha}))
    elif model == "ABSENT":
        inputs["model_1"] = {"path": FILE, "absent": True, "pinned_sha256_16": P16}
    return {"tool": "gate_x", "ts": TS, "verdict": "INCONCLUSIVE", "inputs": inputs, "writer": {"file": "rules_status.py"}}


def _state(repo, rec):
    with _at(repo) as config:
        return S._config_state(rec, "x", M, "R-1", REGS, config_inputs=config)


def t_a_reading_taken_with_the_model_is_current_whether_the_model_is_in_the_checkout_or_not():
    """The state that publishes nothing reads current: the manifest is committed, the model is ignored and no commit
    holds it, and a reading that read the model at the sha pinned is BOUND, in a checkout that has the model and in
    one that has not (a clean clone, the public repository, a handover ZIP)."""
    _need()
    for model in (MODEL, None):
        repo = _repo(model=model)
        ok, cause, why, _ = _state(repo, _reading(repo))
        assert ok and cause == "BOUND", (model is not None, cause, why)
        # a reading older than the manifest recorded the model as a document: held to the pin the same way
        ok, cause, why, _ = _state(repo, _reading(repo, as_document=True))
        assert ok and cause == "BOUND", (cause, why)


def t_a_model_that_is_absent_never_reads_as_changed_by_accident():
    """A reading taken WITHOUT the model, in a checkout without it: nothing changed since, so it is BOUND; what it says
    is the tool's (INCONCLUSIVE, its nets naming the model). And a reading that never asked for the model does not
    depend on it, whatever the checkout holds."""
    _need()
    repo = _repo(model=None)
    ok, cause, why, _ = _state(repo, _reading(repo, model="ABSENT"))
    assert ok and cause == "BOUND", (cause, why)
    for model in (MODEL, OTHER, None):
        repo = _repo(model=model)
        ok, cause, why, _ = _state(repo, _reading(repo, model=None))
        assert ok and cause == "BOUND", "a reading that asked for no model was held to one: %s %s" % (cause, why)


def t_a_model_that_is_not_the_file_pinned_is_a_change_and_says_which():
    _need()
    repo = _repo(model=OTHER)                                   # the checkout holds another file than the pin
    ok, cause, why, _ = _state(repo, _reading(repo))
    assert not ok and cause == "CONFIG_CHANGED" and "is not the file" in why and FILE in why, (cause, why)
    repo = _repo(model=MODEL)                                   # the reading read another file than the pin
    ok, cause, why, _ = _state(repo, _reading(repo, sha="0" * 16))
    assert not ok and cause == "CONFIG_CHANGED" and "the reading read" in why and P16 in why, (cause, why)
    repo = _repo(model=None)                                    # the same, in a checkout without the model
    ok, cause, why, _ = _state(repo, _reading(repo, sha="0" * 16))
    assert not ok and cause == "CONFIG_CHANGED" and "the reading read" in why, (cause, why)


def t_a_reading_taken_without_a_model_that_is_here_now_is_retaken_and_says_so():
    _need()
    repo = _repo(model=MODEL)
    ok, cause, why, _ = _state(repo, _reading(repo, model="ABSENT"))
    assert not ok and cause == "CONFIG_CHANGED" and "taken without the model" in why and "re-take" in why, (cause, why)


def t_the_manifest_is_dated_like_any_input_and_a_manifest_that_cannot_be_read_pins_nothing():
    """By the sha the reading recorded; by its commit where the reading recorded none; never current when no commit
    holds it; and a manifest that does not parse leaves nothing pinned."""
    _need()
    repo = _repo()
    rec = _reading(repo)
    rec["inputs"]["ibis_manifest"]["sha256_16"] = "0" * 16
    ok, cause, why, _ = _state(repo, rec)
    assert not ok and cause == "CONFIG_CHANGED" and "ibis-manifest.yaml" in why, (cause, why)
    ok, cause, why, _ = _state(repo, _reading(repo, manifest=False))          # committed 09:00, read 10:00
    assert ok and cause == "BOUND", (cause, why)
    open(os.path.join(repo, IM.MANIFEST_REL), "a").write("# a note\n")
    _git(repo, "commit", "-q", "-a", "-m", "the manifest edited", when=AFTER)  # committed again 11:00, after the reading
    ok, cause, why, _ = _state(repo, _reading(repo, manifest=False))
    assert not ok and cause == "CONFIG_CHANGED" and "after the reading" in why, (cause, why)
    repo = _repo(commit_manifest=False)                                         # present, and no commit holds it
    ok, cause, why, _ = _state(repo, _reading(repo, manifest=False))
    assert not ok and cause == "CONFIG_CHANGED" and "cannot be dated" in why, (cause, why)
    repo = _repo()
    open(os.path.join(repo, IM.MANIFEST_REL), "w").write("models: [unclosed\n")
    rec = _reading(repo)                                                        # records the broken manifest's own sha
    with _at(repo):
        assert S._pinned_state(rec, "rules_status.py"), "a manifest that cannot be read pinned a model"


def t_the_models_are_declared_nowhere_as_an_ordinary_input():
    """In the tree itself: no entry of CONFIG_INPUTS names a maker's model, every manifest PINNED_INPUTS names is
    declared in CONFIG_INPUTS for the same writer (so the manifest is dated), exists and reads with no refusal."""
    _need()
    for w, paths in S.CONFIG_INPUTS.items():
        assert not [p for p in paths if str(p).lower().endswith(".ibs")], "%s declares a model as an ordinary input" % w
    for w, mans in S.PINNED_INPUTS.items():
        for m in mans:
            assert m in S.CONFIG_INPUTS.get(w, ()), "%s pins through %s, which CONFIG_INPUTS does not declare for it" % (w, m)
            p = os.path.normpath(os.path.join(S.ECAD, m))
            root = os.path.dirname(os.path.dirname(os.path.dirname(p)))
            man = IM.load(root, os.path.relpath(p, root))
            assert not man["why"] and not man["refusals"] and man["models"], (man["why"], man["refusals"])
