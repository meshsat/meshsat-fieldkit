#!/usr/bin/env python3
"""The engineering handover snapshot, built from ONE git commit (MESHSAT-1357, 27 September 2026).

WHY IT EXISTS. The owner's execution prompt of 27 September 2026 (v2/docs/reviews/2026-09-27-handover-execution-prompt.md,
section 6) asks for a versioned handover another engineer can use without this project's chat, memory or hosts: "A
manifest tying artifacts to one coherent source snapshot and identifying every included revision". A folder copied out
of a working tree cannot promise that: a file edited after the commit, an untracked draft or a gitignored prompt would
travel with it and nothing would say so. This tool never reads the working tree for content. Every byte it writes comes
from `git ls-tree` and `git cat-file` of the one commit named on its command line, and the specification that decides
what goes in (v2/docs/handover/pack.yaml) is read from that same commit.

WHAT IT WRITES, under --out (default v2/release/handover in the repository working tree):
  <version>/                 the included files under their repository paths, the hand-written handover pages the spec
                             names (`pages`) copied to the root, and four generated files:
    MANIFEST.tsv             path, git blob sha, sha256, bytes, layer group, role: one row per file of the snapshot
                             (every file but MANIFEST.tsv itself)
    SOURCE.txt               the commit, its date and tree, the tools tree hash (verdict.py's definition, taken over the
                             commit's blobs), the board phase directories, and the tool versions: python and kicad-cli on
                             the building host, the third-party modules the generators and the tools import with their
                             installed versions there, and the versions recorded by the committed exports' provenance
    EXCLUDED.tsv             every file of the commit the spec leaves out, with the rule's kind and reason
    REFERENCED-SOURCES.tsv   every file under a `reference` rule (maker documents and CAD, not bundled for size), with
                             the SOURCES.yaml entries that cite it, whether a citing entry is a fitted part, the sha256
                             SOURCES.yaml declares against the one at the commit, the URL, and the reason it is not bundled
  <version>.zip              the same directory, deterministic: sorted entries, fixed timestamps (1980-01-01), fixed
                             permissions (0644, 0755 where git records an executable), deflate level 9
  <version>.zip.sha256       the ZIP's sha256 in sha256sum's format
Every file of the commit is accounted for exactly once: in MANIFEST.tsv, EXCLUDED.tsv or REFERENCED-SOURCES.tsv. A file
no rule classifies refuses the build (exit 2), because an unaccounted file is exactly a handover gap.

THE SPEC. `rules` is ONE ordered list and the FIRST rule whose glob matches a path decides it (`include` with a layer
group and a role, `exclude` with a kind and a reason, `reference` with a reason). A glob is matched against the whole
repository path: `*` stays inside one directory, `**` spans directories, `?` and `[...]` as in fnmatch. The tokens
`{phase}` and `{stem}` expand once per board that has a schematic chain, to the board's DECLARED phase directory and
its stem, read from the commit the way phase_artefacts.phase_dir reads them (readiness_manifest.json names the stem, the
routeflow profile that routes the stem names the project directory), never from a directory listing.

WHAT IT DOES NOT DO. It judges nothing: a file in the snapshot is not thereby current, reviewed or correct, and the
layer status is the hand-written LAYER-STATUS.md's. It does not export schematics (that needs KiCad; see
handover_exports.py) and it never writes into the repository outside --out.

Usage:
  handover_pack.py build --commit <rev> --version <name> [--out <dir>] [--repo <path>]
  handover_pack.py plan --commit <rev> [--repo <path>] [--spec-file <working-copy pack.yaml>]
  handover_pack.py verify <snapshot dir or .zip>
exit 0 on success; 2 when a file is unclassified or the spec is invalid; 3 when the ZIP is over the spec's size cap
(the snapshot is still written, so it can be read); 4 when verify finds a difference.
"""
import argparse, ast, hashlib, io, json, os, platform, re, shutil, stat, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_PATH = "v2/docs/handover/pack.yaml"
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
META = ("MANIFEST.tsv", "SOURCE.txt", "EXCLUDED.tsv", "REFERENCED-SOURCES.tsv")


class SpecError(Exception):
    """The spec cannot be applied as written; the message says where."""


# ------------------------------------------------------------------------------------------------ git, read-only
class Git:
    """Read-only access to one repository: the tree listing of a commit and blob content by sha."""

    def __init__(self, repo):
        self.repo = os.path.abspath(repo)
        self._cat = None

    def run(self, *args):
        r = subprocess.run(["git", "-C", self.repo] + list(args), capture_output=True, timeout=300)
        if r.returncode != 0:
            raise SpecError("git %s: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace").strip()[:300]))
        return r.stdout

    def commit(self, rev):
        return self.run("rev-parse", "--verify", "%s^{commit}" % rev).decode().strip()

    def ask(self, *args):
        """(exit code, stdout) of a read-only git call whose non-zero exit is an answer (not an ancestor, no such ref)."""
        r = subprocess.run(["git", "-C", self.repo] + list(args), capture_output=True, timeout=300)
        return r.returncode, r.stdout.decode("utf-8", "replace").strip()

    def tree(self, commit):
        """{path: (mode, blob sha, size)} for every blob of the commit (paths as git stores them, -z so no quoting)."""
        out = {}
        for rec in self.run("ls-tree", "-r", "-z", "-l", "--full-tree", commit).split(b"\0"):
            if not rec: continue
            meta, path = rec.split(b"\t", 1)
            mode, typ, sha, size = meta.split()
            if typ != b"blob": continue          # a submodule is a commit, not content this snapshot can carry
            out[path.decode("utf-8", "surrogateescape")] = (mode.decode(), sha.decode(), int(size))
        return out

    def blob(self, sha):
        if self._cat is None:
            self._cat = subprocess.Popen(["git", "-C", self.repo, "cat-file", "--batch"],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._cat.stdin.write(sha.encode() + b"\n"); self._cat.stdin.flush()
        head = self._cat.stdout.readline().split()
        if len(head) != 3 or head[1] != b"blob":
            raise SpecError("git cat-file: %s is not a blob (%r)" % (sha, head))
        n = int(head[2]); data = self._cat.stdout.read(n); self._cat.stdout.read(1)
        return data

    def close(self):
        if self._cat is not None:
            self._cat.stdin.close(); self._cat.wait(timeout=60); self._cat = None


# ------------------------------------------------------------------------------------------------ globs
def glob_regex(pat):
    """A repository-path glob as an anchored regex: `**/` any directories (or none), `/**` at the end everything below,
    `*` within one directory, `?` one character, `[...]` a class (`[!x]` negated)."""
    i, out = 0, []
    while i < len(pat):
        if pat.startswith("**/", i): out.append("(?:.*/)?"); i += 3; continue
        if pat.startswith("/**", i) and i + 3 == len(pat): out.append("(?:/.*)?"); i += 3; continue
        if pat.startswith("**", i): out.append(".*"); i += 2; continue
        c = pat[i]
        if c == "*": out.append("[^/]*")
        elif c == "?": out.append("[^/]")
        elif c == "[":
            j = pat.find("]", i + 2)
            if j < 0: out.append(re.escape(c))
            else:
                body = pat[i + 1:j]
                if body.startswith("!"): body = "^" + body[1:]
                out.append("[" + body.replace("\\", "\\\\") + "]"); i = j
        else: out.append(re.escape(c))
        i += 1
    return re.compile("^" + "".join(out) + "$")


# ------------------------------------------------------------------------------------------------ the spec
def load_yaml(text, where):
    try:
        import yaml
    except ImportError:
        raise SpecError("PyYAML is needed to read %s (pip install pyyaml)" % where)
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise SpecError("%s does not parse: %s" % (where, str(e)[:300]))


def boards_at(git, commit, tree, spec):
    """[(letter, stem, phase directory basename, no_chain)] read from the commit as phase_artefacts.phase_dir reads it."""
    b = spec.get("boards") or {}
    man_path = b.get("manifest")
    if not man_path: return []
    if man_path not in tree: raise SpecError("boards.manifest %s is not in the commit" % man_path)
    man = json.loads(git.blob(tree[man_path][1]).decode("utf-8"))
    prof_re = glob_regex(b.get("profiles") or "v2/ecad/tools/routeflow/*.json")
    profiles = []
    for p in sorted(x for x in tree if prof_re.match(x)):
        try: profiles.append(json.loads(git.blob(tree[p][1]).decode("utf-8")))
        except ValueError: continue
    ecad = b.get("ecad") or "v2/ecad"
    dirs = {x.split("/")[2] for x in tree if x.startswith(ecad + "/") and x.count("/") >= 3}
    out = []
    for letter, ent in sorted((man.get("boards") or {}).items()):
        st = str(ent.get("project") or "")
        if not st: continue
        phase = st
        for p in profiles:
            if p.get("board") != st: continue
            cand = os.path.basename(str(p.get("project", "")).rstrip("/"))
            if cand in dirs: phase = cand; break
        out.append((letter, st, phase, bool(ent.get("no_chain"))))
    return out


def expand_rules(spec, boards):
    """The ordered rule list with {phase}/{stem} rules expanded once per chain board, each compiled."""
    rules = spec.get("rules")
    if not isinstance(rules, list) or not rules: raise SpecError("the spec has no `rules` list")
    groups = spec.get("groups") or {}
    out = []
    for k, r in enumerate(rules):
        act = r.get("action")
        if act not in ("include", "exclude", "reference"):
            raise SpecError("rule %d: action must be include, exclude or reference, not %r" % (k, act))
        if act == "include" and (r.get("group") not in groups or not r.get("role")):
            raise SpecError("rule %d (%s): an include names a group the spec declares and a role" % (k, r.get("glob")))
        if act != "include" and not r.get("reason"):
            raise SpecError("rule %d (%s): an %s says why" % (k, r.get("glob"), act))
        globs = r.get("glob")
        globs = globs if isinstance(globs, list) else [globs]
        for g in globs:
            if not g: raise SpecError("rule %d has an empty glob" % k)
            if "{phase}" in g or "{stem}" in g:
                for letter, st, phase, nochain in boards:
                    if nochain: continue
                    e = g.replace("{phase}", phase).replace("{stem}", st)
                    out.append(dict(r, glob=e, _rx=glob_regex(e), _n=k, _board=letter))
            else:
                out.append(dict(r, glob=g, _rx=glob_regex(g), _n=k))
    return out


def classify(tree, rules):
    """{path: rule} by first match, and the sorted list of paths no rule matches."""
    got, loose = {}, []
    for p in sorted(tree):
        for r in rules:
            if r["_rx"].match(p): got[p] = r; break
        else: loose.append(p)
    return got, loose


# ------------------------------------------------------------------------------------------------ SOURCES.yaml
def cited_documents(sources):
    """{vendor path: {"entries": set, "fitted": bool, "sha256": set, "url": set}} from every mapping in SOURCES.yaml
    that carries a `path` under v2/vendor/, attributed to the nearest part entry (`id`) or `for_entry` above it."""
    out = {}

    def fitted_of(ent):
        if not isinstance(ent, dict): return None
        if ent.get("placed_part") is False: return False
        if str(ent.get("identity", "")).upper().startswith("NOT_FITTED"): return False
        return True

    def walk(o, entry, fit):
        if isinstance(o, dict):
            if "id" in o and ("documents" in o or "function" in o): entry, fit = str(o["id"]), fitted_of(o)
            if "for_entry" in o: entry = str(o["for_entry"]); fit = None if fit is None else fit
            p = o.get("path")
            if isinstance(p, str) and p.startswith("v2/vendor/"):
                d = out.setdefault(p.strip(), {"entries": set(), "fitted": False, "sha256": set(), "url": set()})
                d["entries"].add(entry or "-")
                if fit: d["fitted"] = True
                if o.get("sha256"): d["sha256"].add(str(o["sha256"]).strip().lower())
                if o.get("url"): d["url"].add(" ".join(str(o["url"]).split()))
            for v in o.values(): walk(v, entry, fit)
        elif isinstance(o, list):
            for v in o: walk(v, entry, fit)

    walk(sources, None, None)
    # an entry named by `for_entry` (a document filed apart from its part) takes the fitted state of that part
    part_fit = {}
    for ent in (sources or {}).get("parts") or []:
        if isinstance(ent, dict) and ent.get("id"): part_fit[str(ent["id"])] = fitted_of(ent)
    for d in out.values():
        if any(part_fit.get(e) for e in d["entries"]): d["fitted"] = True
    return out


# ------------------------------------------------------------------------------------------------ provenance
def tools_tree_sha(git, tree, tools="v2/ecad/tools"):
    """verdict.py's `_tools` hash over the COMMIT's blobs: os.walk order (a directory's files sorted, then its
    subdirectories sorted, __pycache__, out and tests skipped), the content of every .py, .sh and .json."""
    kids = {}
    for p in tree:
        if not p.startswith(tools + "/"): continue
        parts = p[len(tools) + 1:].split("/")
        node = kids
        for d in parts[:-1]: node = node.setdefault(d, {})
        node.setdefault("\0files", []).append(p)
    h = hashlib.sha256()

    def walk(node):
        for p in sorted(node.get("\0files", []), key=lambda x: x.rsplit("/", 1)[-1]):
            if p.endswith((".py", ".sh", ".json")): h.update(git.blob(tree[p][1]))
        for d in sorted(k for k in node if k != "\0files" and k not in ("__pycache__", "out", "tests")):
            walk(node[d])

    walk(kids)
    return h.hexdigest()[:16]


def third_party_imports(git, tree, tools="v2/ecad/tools", roots=None):
    """{module: sorted importers} for modules that are neither the standard library nor this tools tree, over the
    .py files of `tools` (or, with `roots`, over the local-import closure of those files)."""
    std = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    local = set()          # every module or package this tools tree holds, at any depth (a sibling import inside
    for p in tree:         # agent/, kb/, routeflow/ or tests/ is a local import, not a third-party one)
        if not p.startswith(tools + "/"): continue
        parts = p[len(tools) + 1:].split("/")
        local.update(parts[:-1])
        if parts[-1].endswith(".py"): local.add(parts[-1][:-3])
    srcs = {p: None for p in tree if p.startswith(tools + "/") and p.endswith(".py")}

    def mods(p):
        """{module: True when at least one import of it is at the file's top level}."""
        if srcs[p] is None:
            try: srcs[p] = ast.parse(git.blob(tree[p][1]).decode("utf-8", "replace"))
            except SyntaxError: srcs[p] = ast.parse("")
        found = {}
        top = {id(n) for n in srcs[p].body}
        for n in ast.walk(srcs[p]):
            names = []
            if isinstance(n, ast.Import): names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and not n.level: names = [n.module.split(".")[0]]
            for m in names: found[m] = found.get(m, False) or id(n) in top
        return found

    todo = sorted(roots) if roots else sorted(srcs)
    seen, ext, uncond = set(), {}, set()
    while todo:
        p = todo.pop()
        if p in seen or p not in srcs: continue
        seen.add(p)
        for m, at_top in mods(p).items():
            if m in local:
                if roots: todo.append("%s/%s.py" % (tools, m))
            elif m not in std:
                ext.setdefault(m, set()).add(p.rsplit("/", 1)[-1])
                if at_top: uncond.add(m)
    return {(m if m in uncond else m + " (imported only inside a function or a condition)"): sorted(v)
            for m, v in sorted(ext.items())}


def installed_version(module):
    try:
        import importlib.metadata as md
        dists = (md.packages_distributions() or {}).get(module) or [module]
        for d in dists:
            try: return "%s %s" % (d, md.version(d))
            except md.PackageNotFoundError: continue
    except Exception:
        pass
    try:
        __import__(module); return "importable (no distribution metadata)"
    except Exception:
        return "not installed on this host"


def kicad_cli_version():
    exe = shutil.which("kicad-cli")
    if not exe: return "not installed on this host"
    try:
        r = subprocess.run([exe, "version"], capture_output=True, text=True, timeout=60)
        return (r.stdout or r.stderr).strip() or "unknown"
    except (OSError, subprocess.SubprocessError) as e:
        return "not runnable here (%s)" % type(e).__name__


# ------------------------------------------------------------------------------------------------ SOURCE.txt additions
COMMIT_ID = re.compile(r"(?<![0-9A-Za-z_/.-])([0-9a-f]{8}|[0-9a-f]{40})(?![0-9A-Za-z_])")


def commit_timeline(git, commit, texts, public_ref):
    """[(short id, date, public, in the snapshot's history, subject)] for every commit id the handover pages name
    (an 8- or 40-hex token with at least one letter that resolves to a commit of this repository), plus the snapshot's
    own commit. `public` is whether the commit is an ancestor of `public_ref` in the building clone (the remote-tracking
    branch of the public repository), or "unknown" when the clone has no such ref."""
    ids = {commit}
    for t in texts:
        for m in COMMIT_ID.finditer(t):
            tok = m.group(1)
            if not re.search(r"[a-f]", tok) or not re.search(r"[0-9]", tok): continue
            rc, full = git.ask("rev-parse", "--verify", "--quiet", "%s^{commit}" % tok)
            if rc == 0 and full: ids.add(full)
    rc, _ = git.ask("rev-parse", "--verify", "--quiet", public_ref) if public_ref else (1, "")
    have_pub = rc == 0
    rows = []
    for c in ids:
        rc, info = git.ask("log", "-1", "--format=%cI%x09%s", c)
        date, _, subj = info.partition("\t")
        pub = ("yes" if git.ask("merge-base", "--is-ancestor", c, public_ref)[0] == 0 else "no") if have_pub else "unknown"
        mine = "yes" if git.ask("merge-base", "--is-ancestor", c, commit)[0] == 0 else "no"
        rows.append((date, c[:8], pub, mine, re.sub(r"\s*\[MESHSAT-\d+\]\s*$", "", subj)))
    rows.sort()
    return [(c, d[:16].replace("T", " "), pub, mine, subj[:120] + ("..." if len(subj) > 120 else ""))
            for d, c, pub, mine, subj in rows]


def registry_counts(git, tree, path="v2/ecad/tools/pcb_requirements.yaml"):
    """Counts of the requirements registry at the commit, so the pages' figures can be checked against the build."""
    if path not in tree: return []
    try:
        reg = load_yaml(git.blob(tree[path][1]).decode("utf-8"), path) or {}
    except SpecError:
        return ["  %s does not parse at this commit" % path]
    out = []
    for key, label in (("needs", "needs"), ("records", "records (REQ, CON, ASM, CHO, SPD, CFL, FEA)"),
                       ("owner_rulings", "owner rulings"), ("session_choices", "session choices"),
                       ("open_items", "open items"), ("closed_items", "closed items")):
        v = reg.get(key)
        if not isinstance(v, list): continue
        ids = [str(x.get("id")) for x in v if isinstance(x, dict) and x.get("id")]
        span = " (%s to %s)" % (ids[0], ids[-1]) if key == "session_choices" and ids else ""
        out.append("  %s: %d%s" % (label, len(v), span))
    return out


# ------------------------------------------------------------------------------------------------ build
def tsv(rows):
    def cell(v):
        return str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ")
    return "".join("\t".join(cell(c) for c in r) + "\n" for r in rows).encode("utf-8")


def plan(git, commit, spec_text=None):
    """Read the commit and its spec and classify every file; nothing is written."""
    tree = git.tree(commit)
    if spec_text is None:
        if SPEC_PATH not in tree: raise SpecError("the commit has no %s" % SPEC_PATH)
        spec_text = git.blob(tree[SPEC_PATH][1]).decode("utf-8")
    spec = load_yaml(spec_text, SPEC_PATH)
    if not isinstance(spec, dict) or spec.get("schema") != 1: raise SpecError("%s: schema must be 1" % SPEC_PATH)
    boards = boards_at(git, commit, tree, spec)
    rules = expand_rules(spec, boards)
    got, loose = classify(tree, rules)
    return {"tree": tree, "spec": spec, "boards": boards, "rules": rules, "got": got, "loose": loose}


def build(git, commit, version, out_root):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", version or ""):
        raise SpecError("--version must be a plain name (letters, digits, . _ -), not %r" % version)
    pl = plan(git, commit)
    tree, spec, got = pl["tree"], pl["spec"], pl["got"]
    if pl["loose"]:
        raise SpecError("%d file(s) of %s are classified by no rule of %s, first: %s" %
                        (len(pl["loose"]), commit[:12], SPEC_PATH, ", ".join(pl["loose"][:8])))
    snap = os.path.join(out_root, version)
    zpath = snap + ".zip"
    for p in (snap, zpath, zpath + ".sha256"):
        if os.path.exists(p): raise SpecError("%s exists: a snapshot is immutable, pick a new --version" % p)

    files = {}          # snapshot path -> (bytes, blob sha, mode, group, role)
    groups = spec.get("groups") or {}
    for p, r in sorted(got.items()):
        if r["action"] != "include": continue
        mode, sha, _ = tree[p]
        files[p] = (git.blob(sha), sha, mode, r["group"], r["role"])
    page_note = []
    for pg in spec.get("pages") or []:
        name = pg.rsplit("/", 1)[-1]
        if pg in tree:
            if name in files or name in META: raise SpecError("page %s would overwrite %s at the root" % (pg, name))
            mode, sha, _ = tree[pg]
            files[name] = (git.blob(sha), sha, mode, "H0", "handover page, a copy of %s" % pg)
            page_note.append("%s: copied from %s blob %s" % (name, pg, sha))
        else:
            page_note.append("%s: ABSENT at this commit (%s is not in the tree)" % (name, pg))

    # EXCLUDED.tsv and REFERENCED-SOURCES.tsv
    excl = [("path", "git_blob_sha", "bytes", "kind", "reason")]
    refd = [("path", "git_blob_sha", "bytes", "cited_by_sources_yaml", "a_citing_entry_is_fitted",
             "sha256_declared", "sha256_at_commit", "check", "url", "not_bundled_because")]
    sources = {}
    sy = spec.get("sources_yaml")
    if sy and sy in tree: sources = cited_documents(load_yaml(git.blob(tree[sy][1]).decode("utf-8"), sy))
    counts = {"include": 0, "exclude": 0, "reference": 0}
    for p, r in sorted(got.items()):
        counts[r["action"]] += 1
        mode, sha, size = tree[p]
        if r["action"] == "exclude":
            excl.append((p, sha, size, r.get("kind", "-"), r["reason"]))
        elif r["action"] == "reference":
            c = sources.get(p)
            if c:
                have = hashlib.sha256(git.blob(sha)).hexdigest()
                decl = sorted(c["sha256"])
                check = ("NO_DECLARED_SHA256" if not decl else "MATCH" if decl == [have] else
                         "MATCH_ONE_OF_SEVERAL" if have in decl else "DIFFERS")
                refd.append((p, sha, size, ",".join(sorted(c["entries"])), "yes" if c["fitted"] else "no",
                             ",".join(decl) or "-", have, check, " | ".join(sorted(c["url"])) or "-", r["reason"]))
            else:
                refd.append((p, sha, size, "-", "-", "-", "-", "NOT_CITED_BY_SOURCES_YAML", "-", r["reason"]))
    missing = sorted(p for p in sources if p not in tree)
    for p in missing:
        c = sources[p]
        refd.append((p, "-", "-", ",".join(sorted(c["entries"])), "yes" if c["fitted"] else "no",
                     ",".join(sorted(c["sha256"])) or "-", "-", "NOT_IN_COMMIT", " | ".join(sorted(c["url"])) or "-",
                     "SOURCES.yaml cites a path this commit does not hold"))
    bundled_cited = sorted(p for p in sources if p in got and got[p]["action"] == "include")
    files["EXCLUDED.tsv"] = (tsv(excl), "-", "100644", "meta", "generated: the files this snapshot leaves out, and why")
    files["REFERENCED-SOURCES.tsv"] = (tsv(refd), "-", "100644", "meta",
                                       "generated: maker documents and CAD cited or held but not bundled")

    # SOURCE.txt
    log = git.run("log", "-1", "--format=%H%n%cI%n%T%n%s", commit).decode("utf-8", "replace").splitlines()
    pub = spec.get("public") or {}
    public_block = []
    if pub.get("repository"):
        public_block += [
            "public repository: %s (clone: git clone %s.git)" % (pub["repository"], pub["repository"]),
            "raw file at a commit: %s" % (pub.get("raw_file_url") or "-"),
            "  a file this snapshot references but does not bundle (REFERENCED-SOURCES.tsv) is fetched from that URL with",
            "  <commit> = the snapshot commit when the timeline below says it is public, else any public commit in the",
            "  timeline that holds the same blob; check it by its git blob sha (column git_blob_sha of the TSV)",
            "",
        ]
    texts = [git.blob(tree[p][1]).decode("utf-8", "replace") for p in sorted(tree)
             if p.startswith("v2/docs/handover/") and p.endswith(".md")]
    tl = commit_timeline(git, commit, texts, pub.get("public_ref"))
    public_block += [
        "commit timeline: every commit the handover pages name, and this snapshot's own (id, committed, on the public",
        "repository when this snapshot was built (ancestor of %s in the building clone), in this snapshot's history, "
        "subject):" % (pub.get("public_ref") or "no public ref configured"),
    ] + ["  %s  %s  public %-7s  in history %-3s  %s" % r for r in tl] + [""]
    rc = registry_counts(git, tree)
    if rc: public_block += ["requirements registry at this commit (v2/ecad/tools/pcb_requirements.yaml):"] + rc + [""]
    cands = sorted(p for p in tree if re.fullmatch(r"v2/docs/handover/candidates/[^/]+\.patch", p))
    if cands:
        public_block += ["candidate patches (UNACCEPTED work exported from unpushed worktrees; v2/docs/handover/candidates/README.md):"]
        public_block += ["  %s: %d bytes, sha256 %s" % (p, tree[p][2], hashlib.sha256(git.blob(tree[p][1])).hexdigest())
                         for p in cands] + [""]
    runner = os.path.abspath(__file__)
    here_sha = hashlib.sha256(open(runner, "rb").read()).hexdigest()
    me = "v2/ecad/tools/handover_pack.py"
    at_commit = hashlib.sha256(git.blob(tree[me][1])).hexdigest() if me in tree else None
    gen_roots = [p for p in tree if re.fullmatch(r"v2/ecad/tools/gen_sch_[a-z0-9]+\.py", p)]
    gen_ext = third_party_imports(git, tree, roots=gen_roots) if gen_roots else {}
    all_ext = third_party_imports(git, tree)
    prov = []
    for p in sorted(x for x in files if re.fullmatch(r"v2/release/handover/_generated/[^/]+/provenance\.json", x)):
        try:
            j = json.loads(files[p][0].decode("utf-8"))
            prov.append("  %s: kicad-cli %s, python %s, host %s, schematic sha256 %s" %
                        (p.split("/")[-2], j.get("kicad_cli", "?"), j.get("python", "?"), j.get("host", "?"),
                         str(j.get("schematic_sha256", "?"))[:16]))
        except ValueError:
            prov.append("  %s: unreadable" % p)
    lines = [
        "MeshSat field kit V2 engineering handover snapshot %s" % version,
        "",
        "commit: %s" % log[0],
        "commit_date: %s" % log[1],
        "commit_tree: %s" % log[2],
        "commit_subject: %s" % log[3],
        "spec: %s blob %s" % (SPEC_PATH, tree[SPEC_PATH][1]),
        "builder at the commit: %s" % ("%s sha256 %s" % (me, at_commit) if at_commit else "%s is not in the commit" % me),
        "builder that ran: sha256 %s (%s)" % (here_sha, "the same file" if here_sha == at_commit else
                                              "NOT the commit's copy: rebuild with the commit's builder to reproduce"),
        "tools_tree_sha: %s (verdict.py's definition: .py, .sh and .json under v2/ecad/tools, __pycache__, out and "
        "tests skipped, over the commit's blobs)" % tools_tree_sha(git, tree),
        "",
        "files of the commit: %d; included %d, excluded %d (EXCLUDED.tsv), referenced and not bundled %d "
        "(REFERENCED-SOURCES.tsv); the snapshot adds %d handover page(s) at its root and four generated files" %
        (len(tree), counts["include"], counts["exclude"], counts["reference"],
         sum(1 for x in files if files[x][3] == "H0" and "/" not in x)),
        "SOURCES.yaml documents: %d cited paths, %d of them bundled because a rule includes them, %d cited but absent "
        "from the commit" % (len(sources), len(bundled_cited), len(missing)),
        "",
    ] + public_block + [
        "boards (letter, stem, declared phase directory read from readiness_manifest.json and the routeflow profile):",
    ] + ["  %s %s -> v2/ecad/%s%s" % (l, s, ph, " (no schematic chain: the board file is the design)" if nc else "")
         for l, s, ph, nc in pl["boards"]] + [
        "",
        "handover pages:",
    ] + ["  " + x for x in page_note] + [
        "",
        "tool versions on the host that built this snapshot:",
        "  python: %s" % platform.python_version(),
        "  kicad-cli: %s" % kicad_cli_version(),
        "third-party modules imported by the schematic generators (gen_sch_*.py and their local imports): %s" %
        (", ".join("%s (%s)" % (m, installed_version(m.split(" ")[0])) for m in gen_ext) or
         "none: the standard library only. They read KiCad's symbol library (kisch.py: /usr/share/kicad/symbols, or "
         "$KICAD_SYMBOLS) and footprint libraries, so the KiCad release is part of their input"),
        "third-party modules imported anywhere under v2/ecad/tools (module: version on this host; importers):",
    ] + ["  %s: %s; %s" % (m, installed_version(m.split(" ")[0]), ", ".join(v[:6]) + (" and %d more" % (len(v) - 6) if len(v) > 6 else ""))
         for m, v in all_ext.items()] + [
        "",
        "versions recorded by the committed exports (v2/release/handover/_generated/<board>/provenance.json):",
    ] + (prov or ["  none at this commit"]) + [""]
    files["SOURCE.txt"] = ("\n".join(lines).encode("utf-8"), "-", "100644", "meta",
                           "generated: the commit, the builder and the tool versions")

    man = [("path", "git_blob_sha", "sha256", "bytes", "group", "role")]
    for p in sorted(files):
        data, sha, mode, grp, role = files[p]
        label = groups.get(grp, grp) if isinstance(groups.get(grp), str) else grp
        man.append((p, sha, hashlib.sha256(data).hexdigest(), len(data), "%s %s" % (grp, label) if label != grp else grp, role))
    files["MANIFEST.tsv"] = (tsv(man), "-", "100644", "meta", "generated")

    os.makedirs(snap)
    for p in sorted(files):
        data, _, mode, _, _ = files[p]
        dst = os.path.join(snap, *p.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as fh: fh.write(data)
        os.chmod(dst, 0o755 if mode == "100755" else 0o644)
    with zipfile.ZipFile(zpath, "w") as z:
        for p in sorted(files):
            data, _, mode, _, _ = files[p]
            zi = zipfile.ZipInfo("%s/%s" % (version, p), date_time=ZIP_EPOCH)
            zi.create_system = 3
            zi.external_attr = ((0o100755 if mode == "100755" else 0o100644) & 0xFFFF) << 16
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    zsha = hashlib.sha256(open(zpath, "rb").read()).hexdigest()
    with open(zpath + ".sha256", "w", encoding="utf-8") as fh: fh.write("%s  %s\n" % (zsha, os.path.basename(zpath)))
    zbytes = os.path.getsize(zpath)
    return {"snapshot": snap, "zip": zpath, "zip_sha256": zsha, "zip_bytes": zbytes, "files": len(files),
            "included": counts["include"], "excluded": counts["exclude"], "referenced": counts["reference"],
            "commit": commit, "cap": int(spec.get("max_zip_bytes") or 0)}


# ------------------------------------------------------------------------------------------------ verify
def verify(target):
    """Re-read a snapshot directory or ZIP against its own MANIFEST.tsv: every row's bytes and sha256, and no file
    that the manifest does not name. For a ZIP, also its .sha256 beside it when present."""
    probs = []
    if target.endswith(".zip"):
        side = target + ".sha256"
        if os.path.exists(side):
            want = open(side, encoding="utf-8").read().split()[0]
            got = hashlib.sha256(open(target, "rb").read()).hexdigest()
            if want != got: probs.append("zip sha256 %s, its .sha256 says %s" % (got, want))
        with zipfile.ZipFile(target) as z:
            names = z.namelist()
            top = {n.split("/", 1)[0] for n in names}
            if len(top) != 1: return ["the zip holds %d top-level folders, not one" % len(top)]
            root = top.pop()
            content = {n.split("/", 1)[1]: z.read(n) for n in names if not n.endswith("/")}
    else:
        root = os.path.basename(os.path.normpath(target)); content = {}
        for dp, dn, fn in os.walk(target):
            for f in fn:
                full = os.path.join(dp, f)
                content[os.path.relpath(full, target).replace(os.sep, "/")] = open(full, "rb").read()
    if "MANIFEST.tsv" not in content: return ["no MANIFEST.tsv in %s" % root]
    rows = [ln.split("\t") for ln in content["MANIFEST.tsv"].decode("utf-8").splitlines()[1:] if ln]
    named = set()
    for r in rows:
        p, sha256, size = r[0], r[2], int(r[3]); named.add(p)
        if p not in content: probs.append("%s: in the manifest, not in the snapshot" % p); continue
        if len(content[p]) != size: probs.append("%s: %d bytes, the manifest says %d" % (p, len(content[p]), size))
        if hashlib.sha256(content[p]).hexdigest() != sha256: probs.append("%s: sha256 differs from the manifest" % p)
    for p in sorted(set(content) - named - {"MANIFEST.tsv"}):
        probs.append("%s: in the snapshot, not in the manifest" % p)
    return probs


# ------------------------------------------------------------------------------------------------ main
def main(argv):
    ap = argparse.ArgumentParser(prog="handover_pack.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--commit", required=True); b.add_argument("--version", required=True)
    b.add_argument("--out", default=None); b.add_argument("--repo", default=None)
    p = sub.add_parser("plan"); p.add_argument("--commit", required=True); p.add_argument("--repo", default=None)
    p.add_argument("--spec-file", default=None)
    v = sub.add_parser("verify"); v.add_argument("target")
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        probs = verify(a.target)
        for x in probs: print("handover_pack: verify: %s" % x)
        print("handover_pack: verify %s: %s" % (a.target, "OK" if not probs else "%d problem(s)" % len(probs)))
        return 4 if probs else 0
    repo = a.repo or subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True,
                                    text=True, timeout=30).stdout.strip()
    if not repo: print("handover_pack: no repository (give --repo)"); return 2
    git = Git(repo)
    try:
        commit = git.commit(a.commit)
        if a.cmd == "plan":
            text = open(a.spec_file, encoding="utf-8").read() if a.spec_file else None
            pl = plan(git, commit, text)
            n = {"include": 0, "exclude": 0, "reference": 0}; size = {"include": 0, "exclude": 0, "reference": 0}
            for pth, r in pl["got"].items(): n[r["action"]] += 1; size[r["action"]] += pl["tree"][pth][2]
            for k in n: print("handover_pack: plan %s: %d files, %d bytes" % (k, n[k], size[k]))
            for l, s, ph, nc in pl["boards"]: print("handover_pack: board %s %s -> %s%s" % (l, s, ph, " (no chain)" if nc else ""))
            for pth in pl["loose"]: print("handover_pack: UNCLASSIFIED %s" % pth)
            print("handover_pack: plan of %s: %d unclassified" % (commit[:12], len(pl["loose"])))
            return 2 if pl["loose"] else 0
        out = a.out or os.path.join(repo, "v2", "release", "handover")
        r = build(git, commit, a.version, out)
    except SpecError as e:
        print("handover_pack: REFUSED: %s" % e); return 2
    finally:
        git.close()
    print("handover_pack: %s from %s: %d files (%d included, %d excluded, %d referenced), zip %d bytes sha256 %s" %
          (a.version, r["commit"][:12], r["files"], r["included"], r["excluded"], r["referenced"], r["zip_bytes"],
           r["zip_sha256"]))
    print("handover_pack: wrote %s and %s" % (r["snapshot"], r["zip"]))
    if r["cap"] and r["zip_bytes"] > r["cap"]:
        print("handover_pack: OVER THE CAP: the zip is %d bytes, the spec allows %d" % (r["zip_bytes"], r["cap"]))
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
