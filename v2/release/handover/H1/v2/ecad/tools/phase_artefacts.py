#!/usr/bin/env python3
"""The artefact a reading judged, named by content, and where the DECLARED phase keeps it (MESHSAT-1357, 26 September
2026, the tools stream's recording round).

WHY IT EXISTS. `rules_status` binds a reading to a board's current candidate by the sha of the artefact the reading
records: the netlist of the board's declared phase, or its board file where the board has no schematic (E5). Eight
tools that decide schematic-phase rules recorded something else: a project directory (erc_gate), a netlist's bare
file name that verdict.write cannot hash (power_sequence), a chain's name (energy_chain), the letters of the boards
it read (check_contracts), a sheet's name (interfaces), a path relative to the repository root (pack_protection), and
a letter alone on the board with no netlist (safe_lines and port_protect). Thirty-one rule-board rows of
v2/docs/CURRENT-EVIDENCE.md could not be made current by any re-take, because no re-take of those tools said what it
had read. Each of them now records through `record` here and finds the declared phase's artefacts through `netlist`,
`intent` and `board_file` here.

THE DECLARED PHASE, READ THE WAY `rules_status.candidate` READS IT, NEVER THE NEWEST FILE BY MTIME. The manifest
(readiness_manifest.json) names each board's stem; the routeflow profile that routes that stem names its project
directory; the directory of that name in the tree judged is the phase directory, and where it is not there the
stem's own directory is (rules_status._phase_dir, which the suite holds equal to `phase_dir`). A board the manifest
marks `no_chain` (E5) has no schematic: its board file is its design.

WHAT A RECORD IS. {"path": the file relative to v2/ecad when it lies inside this repository, else the path as given (a
fixture's temporary file stays absolute, so `rules_status._temp_input` still refuses it as not this tree),
"sha256_16": the first 16 hex of the sha256 of the bytes, and for a netlist "content16", the project's parity
identity (`regen_compare.content_hash`: components and nets, no export path, date or tool), so a netlist regenerated
in a sweep copy binds by content}. `rules_status` reads a recorded `.net` or `.kicad_pcb` as the artefact and every
other recorded file, by its name and parent directory, as a configuration input (`_recorded_sha`).

WHAT IT DOES NOT DO. It decides nothing about a board. A record says which bytes a tool read; whether the reading is
current is `rules_status`'s question, and it answers it against the candidate it computes itself.
"""
import os, json, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ECAD))          # the repository: v2/ecad/tools -> the root
MANIFEST = os.path.join(HERE, "readiness_manifest.json")


def _boards():
    """{letter: manifest entry}, or {} when the manifest cannot be read (a tool then records what it was given)."""
    try:
        return (json.load(open(MANIFEST, encoding="utf-8")) or {}).get("boards") or {}
    except (OSError, ValueError):
        return {}


def stem(letter):
    """The board's project stem from the manifest (`pcb-a-power`), or ""."""
    return str((_boards().get(str(letter or "").lower()) or {}).get("project") or "")


def letters():
    """Every board letter the manifest judges, in its order."""
    return list(_boards())


def letter_of(name):
    """The letter whose manifest stem is this file's stem (`out/pcb-a-power.net` is `a`), or ""."""
    s = os.path.basename(str(name or ""))
    for suffix in (".net.prov.json", "-intent.json", ".kicad_pcb", ".kicad_sch", ".net"):
        if s.endswith(suffix):
            s = s[:-len(suffix)]
            break
    for letter, b in _boards().items():
        if (b or {}).get("project") == s: return letter
    return ""


def no_schematic(letter):
    """True where the manifest says the board has no schematic chain (E5): its board file is its design."""
    return bool((_boards().get(str(letter or "").lower()) or {}).get("no_chain"))


def phase_dir(letter, ecad=None):
    """The project directory of the phase this board declares, in the tree `ecad` (default: this tree), or None for a
    letter the manifest does not know. See the module docstring; `rules_status._phase_dir` is the same answer."""
    st = stem(letter)
    if not st: return None
    root = os.path.abspath(ecad or ECAD)
    for pf in sorted(glob.glob(os.path.join(HERE, "routeflow", "*.json"))):
        try: p = json.load(open(pf, encoding="utf-8"))
        except (OSError, ValueError): continue
        if p.get("board") != st: continue
        d = os.path.join(root, os.path.basename(str(p.get("project", "")).rstrip("/")))
        if os.path.isdir(d): return d
    return os.path.join(root, st)


def netlist(letter, ecad=None):
    """The declared phase's netlist path (it may not exist), or None."""
    d = phase_dir(letter, ecad)
    return os.path.join(d, "out", stem(letter) + ".net") if d else None


def intent(letter, ecad=None):
    """The declared phase's intent file, beside its netlist (it may not exist), or None."""
    d = phase_dir(letter, ecad)
    return os.path.join(d, "out", stem(letter) + "-intent.json") if d else None


def board_file(letter, ecad=None):
    """The declared phase's board file (it may not exist), or None."""
    d = phase_dir(letter, ecad)
    return os.path.join(d, stem(letter) + ".kicad_pcb") if d else None


def rel(path):
    """`path` relative to this tree's v2/ecad when it lies inside this repository (a vendor document reads
    `../vendor/...`), else as given. Relative, because a checkout may itself sit under /tmp (a worktree, a box clone)
    and `rules_status._temp_input` refuses an absolute path there as a temporary directory."""
    a, r = os.path.abspath(str(path)), os.path.abspath(ROOT)
    if a.startswith(r + os.sep): return os.path.relpath(a, os.path.abspath(ECAD))
    return str(path)


def sha16(raw):
    return hashlib.sha256(raw).hexdigest()[:16]


def content16(raw):
    """The netlist's parity identity, or None when this tree cannot compute it (it is then simply not recorded)."""
    try:
        import regen_compare as _rc
    except ImportError:
        return None
    return _rc.content_hash(raw.decode("utf-8", "replace"))


def record(path, raw=None, content=None, **extra):
    """{"path", "sha256_16"[, "content16"], **extra} of the bytes judged, or None when the file cannot be read.

    Pass `raw` when the caller already holds the bytes it parsed, so the record is of exactly those bytes. `content`
    defaults to True for a `.net` file."""
    if raw is None:
        try:
            with open(path, "rb") as f: raw = f.read()
        except (OSError, TypeError):
            return None
    out = {"path": rel(path), "sha256_16": sha16(raw)}
    if content is None: content = str(path).endswith(".net")
    if content:
        c = content16(raw)
        if c: out["content16"] = c
    out.update(extra)
    return out


def design_of(letter, ecad=None):
    """The artefact that identifies board `letter`'s design in the tree `ecad`: its declared phase's netlist, or for a
    board with no schematic its declared phase's board file. ("netlist" | "board_file", record) or (None, None) when
    the tree holds neither."""
    if no_schematic(letter):
        p = board_file(letter, ecad)
        r = record(p) if p else None
        return ("board_file", r) if r else (None, None)
    p = netlist(letter, ecad)
    r = record(p) if p else None
    return ("netlist", r) if r else (None, None)


def reading_inputs(letter, netlist_path=None):
    """The inputs a reading of board `letter` records: {"board": letter} and, judged on a netlist, the netlist by sha and
    by content and the intent file beside it by sha (a configuration input; its rails decide what the tools treat as a
    supply); or, for a board with no schematic judged on its declaration alone (safe_lines and port_protect --board on
    E5), its declared phase's board file by sha. The declaration itself lives in the board table, a configuration
    input; nothing here reads the board file for a finding, so a re-take binds the declaration to the revision of the
    board it was taken for and a later revision of that board makes it stale. A path that cannot be read is kept as
    typed, which is what the tools recorded before."""
    inp = {"board": letter}
    if netlist_path:
        n = record(netlist_path)
        inp["netlist"] = n if n else netlist_path
        i = record(os.path.join(os.path.dirname(str(netlist_path)),
                                os.path.basename(str(netlist_path)).replace(".net", "-intent.json")), content=False)
        if i: inp["intent"] = i
    elif letter and no_schematic(letter):
        p = board_file(letter)
        b = record(p, content=False) if p else None
        if b: inp["board_file"] = b
    return inp
