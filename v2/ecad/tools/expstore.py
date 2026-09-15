#!/usr/bin/env python3
"""The experiment store: a transactional record of cycles, arms, artefacts, metrics, reviews and promotions
(15 September 2026, red team report 1, recommendation 2; MESHSAT-862).

The agent's decisions used to rest on shared JSONL files: a cycle's rows were found by an arm name the model chose and a
sequence horizon, two processes could append the same head, and nothing made a partial or duplicate cycle impossible to
mistake for a complete one. This is SQLite in WAL mode with the constraints that make those states unrepresentable:

  cycle      (cycle_id PK, board, stage, context_hash, requested_arms, status, started, finished)
  arm        (experiment_id PK, cycle_id FK, name, knobs_json, prediction_json, status, ...)   UNIQUE (cycle_id, name)
  artifact   (sha256, experiment_id FK, role, path, size)                                     PK (sha256, experiment_id, role)
  metric     (experiment_id FK, metric, value, denominator, policy_version)                  PK (experiment_id, metric)
  review     (cycle_id FK, model, verdict, findings_json, ts)
  promotion  (candidate_sha256, gate_set_version, status, promoted_at)

The chained JSONL ledger (`ledger.py`) stays as the EXPORT (`export_jsonl`), portable and tamper-evident; it is no longer
the thing two processes race on. A `cycle_id` is minted before a proposal and travels through the spec, every arm row,
every artefact path and the review, so a result is accepted for a cycle only when it names that cycle.

Usage as a module: Store(path). CLI: expstore.py <store.db> cycles | arms <cycle_id> | export <out.jsonl>"""
import os, sys, json, time, sqlite3, hashlib, uuid

SCHEMA = """
CREATE TABLE IF NOT EXISTS cycle (
  cycle_id TEXT PRIMARY KEY, board TEXT NOT NULL, stage TEXT NOT NULL, context_hash TEXT NOT NULL,
  requested_arms INTEGER NOT NULL, status TEXT NOT NULL, started TEXT NOT NULL, finished TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS arm (
  experiment_id TEXT PRIMARY KEY, cycle_id TEXT NOT NULL REFERENCES cycle(cycle_id), name TEXT NOT NULL,
  knobs_json TEXT NOT NULL, prediction_json TEXT NOT NULL, status TEXT NOT NULL, note TEXT, tools_json TEXT, placed_md5 TEXT,
  UNIQUE (cycle_id, name));
CREATE TABLE IF NOT EXISTS artifact (
  sha256 TEXT NOT NULL, experiment_id TEXT NOT NULL REFERENCES arm(experiment_id), role TEXT NOT NULL, path TEXT NOT NULL, size INTEGER NOT NULL,
  PRIMARY KEY (sha256, experiment_id, role));
CREATE TABLE IF NOT EXISTS metric (
  experiment_id TEXT NOT NULL REFERENCES arm(experiment_id), metric TEXT NOT NULL, value REAL, denominator REAL, policy_version TEXT,
  PRIMARY KEY (experiment_id, metric));
CREATE TABLE IF NOT EXISTS review (
  cycle_id TEXT NOT NULL REFERENCES cycle(cycle_id), model TEXT, verdict TEXT NOT NULL, findings_json TEXT NOT NULL, ts TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS promotion (
  candidate_sha256 TEXT NOT NULL, gate_set_version TEXT NOT NULL, status TEXT NOT NULL, promoted_at TEXT NOT NULL,
  PRIMARY KEY (candidate_sha256, gate_set_version));
"""

TERMINAL = ("MET", "MISSED", "ILLEGAL", "UNMEASURED", "UNMEASURABLE", "INFRA_FAIL")


def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def new_cycle_id(): return uuid.uuid4().hex[:16]


class Store:
    def __init__(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.path = path
        self.c = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.c.execute("PRAGMA journal_mode=WAL"); self.c.execute("PRAGMA foreign_keys=ON")
        self.c.executescript(SCHEMA)

    # --- cycles
    def new_cycle(self, board, stage, context_hash, requested_arms, note="", cycle_id=None):
        cid = cycle_id or new_cycle_id()
        self.c.execute("INSERT INTO cycle VALUES (?,?,?,?,?,?,?,?,?)", (cid, board, stage, context_hash, int(requested_arms), "OPEN", now(), None, note))
        return cid

    def finish_cycle(self, cycle_id, status, note=""):
        self.c.execute("UPDATE cycle SET status=?, finished=?, note=COALESCE(NULLIF(?, ''), note) WHERE cycle_id=?", (status, now(), note, cycle_id))

    def cycle(self, cycle_id):
        r = self.c.execute("SELECT cycle_id, board, stage, context_hash, requested_arms, status, started, finished, note FROM cycle WHERE cycle_id=?", (cycle_id,)).fetchone()
        return None if r is None else dict(zip(("cycle_id", "board", "stage", "context_hash", "requested_arms", "status", "started", "finished", "note"), r))

    # --- arms
    def add_arm(self, cycle_id, name, knobs, prediction):
        """An arm of a cycle; a second arm of the same name in one cycle is refused by the schema (sqlite3.IntegrityError)."""
        eid = hashlib.sha256(("%s:%s" % (cycle_id, name)).encode()).hexdigest()[:16]
        self.c.execute("INSERT INTO arm (experiment_id, cycle_id, name, knobs_json, prediction_json, status) VALUES (?,?,?,?,?,?)",
                       (eid, cycle_id, name, json.dumps(knobs or {}, sort_keys=True), json.dumps(prediction or {}, sort_keys=True), "PROPOSED"))
        return eid

    def finish_arm(self, cycle_id, name, status, note="", metrics=None, artifacts=None, tools=None, placed_md5=None, policy_version=None):
        """The terminal result of one arm. `status` is one of TERMINAL; a second terminal result for the same arm is refused."""
        if status not in TERMINAL: raise ValueError("%r is not a terminal arm status" % status)
        r = self.c.execute("SELECT experiment_id, status FROM arm WHERE cycle_id=? AND name=?", (cycle_id, name)).fetchone()
        if r is None: raise KeyError("no arm %r in cycle %s" % (name, cycle_id))
        eid, st = r
        if st in TERMINAL: raise ValueError("arm %r of cycle %s already has a terminal result (%s)" % (name, cycle_id, st))
        self.c.execute("BEGIN")
        try:
            self.c.execute("UPDATE arm SET status=?, note=?, tools_json=?, placed_md5=? WHERE experiment_id=?", (status, note, json.dumps(tools or {}, sort_keys=True), placed_md5, eid))
            for k, v in (metrics or {}).items():
                val, den = (v if isinstance(v, (list, tuple)) else (v, None))
                self.c.execute("INSERT INTO metric VALUES (?,?,?,?,?)", (eid, k, None if val is None else float(val), None if den is None else float(den), policy_version))
            for a in (artifacts or []):
                self.c.execute("INSERT OR IGNORE INTO artifact VALUES (?,?,?,?,?)", (a["sha256"], eid, a["role"], a["path"], int(a.get("size", 0))))
            self.c.execute("COMMIT")
        except Exception:
            self.c.execute("ROLLBACK"); raise
        return eid

    def arms(self, cycle_id):
        rows = self.c.execute("SELECT experiment_id, name, knobs_json, prediction_json, status, note, tools_json, placed_md5 FROM arm WHERE cycle_id=? ORDER BY name", (cycle_id,)).fetchall()
        out = []
        for eid, name, kj, pj, st, note, tj, pm in rows:
            m = {k: (v, d) for k, v, d in self.c.execute("SELECT metric, value, denominator FROM metric WHERE experiment_id=?", (eid,))}
            out.append({"experiment_id": eid, "arm": name, "env": json.loads(kj), "predict": json.loads(pj), "verdict": st, "note": note,
                        "tools": json.loads(tj) if tj else {}, "placed_md5": pm, "metrics": m, "cycle_id": cycle_id})
        return out

    def complete(self, cycle_id):
        """(complete, why): every requested arm has exactly one terminal result and nothing else was written to the cycle."""
        c = self.cycle(cycle_id)
        if c is None: return False, "no such cycle"
        arms = self.arms(cycle_id)
        pending = [a["arm"] for a in arms if a["verdict"] not in TERMINAL]
        if len(arms) != c["requested_arms"]: return False, "%d arm(s) for %d requested" % (len(arms), c["requested_arms"])
        if pending: return False, "no terminal result for %s" % pending
        return True, "complete"

    # --- reviews, promotions, export
    def add_review(self, cycle_id, model, verdict, findings):
        self.c.execute("INSERT INTO review VALUES (?,?,?,?,?)", (cycle_id, model, verdict, json.dumps(findings or [], sort_keys=True), now()))

    def promote(self, candidate_sha256, gate_set_version, status):
        self.c.execute("INSERT OR REPLACE INTO promotion VALUES (?,?,?,?)", (candidate_sha256, gate_set_version, status, now()))

    def export_jsonl(self, path):
        """The store as chained rows, through ledger.append, so the portable copy stays tamper-evident."""
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ledger
        n = 0
        for cid, in self.c.execute("SELECT cycle_id FROM cycle ORDER BY started"):
            c = self.cycle(cid)
            for a in self.arms(cid):
                rec = dict(a); rec.update(board=c["board"], stage=c["stage"], context_hash=c["context_hash"])
                rec["metrics"] = {k: list(v) for k, v in rec["metrics"].items()}
                ledger.append(path, {"kind": "arm", "rec": rec}); n += 1
        return n


def main(a):
    if len(a) < 2: print(__doc__); return 2
    s = Store(a[0])
    if a[1] == "cycles":
        for r in s.c.execute("SELECT cycle_id, board, stage, requested_arms, status, started, finished FROM cycle ORDER BY started"): print(*r)
    elif a[1] == "arms" and len(a) > 2:
        for r in s.arms(a[2]): print("%-16s %-12s %s %s" % (r["arm"], r["verdict"], json.dumps(r["env"]), r["note"][:80] if r["note"] else ""))
    elif a[1] == "export" and len(a) > 2:
        print("expstore: %d row(s) exported to %s" % (s.export_jsonl(a[2]), a[2]))
    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
