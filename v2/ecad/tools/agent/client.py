#!/usr/bin/env python3
"""The one client that talks to a model, for tiers 2 and 2b (MESHSAT-862, 12 September 2026).

Everything about this file is shaped by two facts of this project.

THE REPO MIRRORS PUBLICLY WITHIN MINUTES, so the endpoint and the key live OUTSIDE the tree, in
`~/.config/meshsat-fieldkit/agent.env` at mode 600, exactly as the retrieval store's config does
(`kb.env`, 10 September). This file carries NO DEFAULT for either, and no test, fixture or doc in
the tree may name the host. A missing config is INFRA_FAIL and never a fallback: the tier-0 rule is
that a missing dependency stops the run rather than quietly changing what ran.

A BUDGET IS COUNTED IN WORK, NEVER IN SECONDS. A wall clock decided a result twice on this project
(the staircase comparison of 9 September, the pair budget of 10 September) and both readings were
wrong. So the cap here is calls and tokens; the timeout exists only to stop a hung socket.

Every call records the sha256 of what was sent and what came back, so the ledger can prove which
bytes produced a proposal. The key is never logged, never echoed and never written to `out/`.
"""
import os, sys, json, time, hashlib, urllib.request, urllib.error

CFG_PATH = os.environ.get("MESHSAT_AGENT_ENV", os.path.expanduser("~/.config/meshsat-fieldkit/agent.env"))
REQUIRED = ("MESHSAT_LLM_BASE", "MESHSAT_LLM_KEY", "MESHSAT_LLM_MODEL")


class Infra(Exception):
    """A dependency is missing or the endpoint refused. Never caught into a fallback."""


def load_config(path=None):
    """Read the config file. No defaults, no environment fallback for the key, no guessing."""
    p = path or CFG_PATH
    if not os.path.exists(p):
        raise Infra("no agent config at %s: the endpoint and key live outside the tree, see docs/AGENTIC-SYSTEM.md" % p)
    mode = os.stat(p).st_mode & 0o777
    if mode & 0o077:
        raise Infra("agent config %s is mode %o: it holds a key and must be 600" % (p, mode))
    cfg = {}
    for line in open(p, errors="replace"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    missing = [k for k in REQUIRED if not cfg.get(k)]
    if missing:
        raise Infra("agent config %s is missing %s" % (p, ", ".join(missing)))
    return cfg


def redact(text, cfg):
    """Never let a key reach a log, a verdict file or the ledger, even through an error body."""
    k = cfg.get("MESHSAT_LLM_KEY")
    return text.replace(k, "<redacted>") if k else text


def sha(s):
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:16]


class Client:
    """One conversation. A fresh Client is a fresh context, which is what makes tier 2b independent."""

    def __init__(self, role="propose", cfg=None, max_calls=None, max_tokens_total=None):
        self.cfg = cfg or load_config()
        self.role = role
        self.model = self.cfg["MESHSAT_LLM_REVIEW_MODEL"] if role == "review" and self.cfg.get("MESHSAT_LLM_REVIEW_MODEL") else self.cfg["MESHSAT_LLM_MODEL"]
        self.max_calls = int(max_calls or os.environ.get("MESHSAT_AGENT_MAX_CALLS", 8))
        self.max_tokens_total = int(max_tokens_total or os.environ.get("MESHSAT_AGENT_MAX_TOKENS", 400000))
        self.calls = 0
        self.tokens = 0
        self.log = []

    def ask(self, system, user, max_tokens=4000, temperature=0.0, timeout=600, retries=3):
        """One completion. Returns (text, meta). Raises Infra rather than returning something plausible."""
        if self.calls >= self.max_calls:
            raise Infra("agent budget: %d calls is the cap for this run" % self.max_calls)
        if self.tokens >= self.max_tokens_total:
            raise Infra("agent budget: %d tokens is the cap for this run" % self.max_tokens_total)
        body = json.dumps({
            "model": self.model, "max_tokens": max_tokens, "temperature": temperature,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }).encode()
        url = self.cfg["MESHSAT_LLM_BASE"].rstrip("/") + "/v1/chat/completions"
        last = None
        for attempt in range(1, retries + 1):
            req = urllib.request.Request(url, data=body, method="POST", headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.cfg["MESHSAT_LLM_KEY"],
            })
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    d = json.loads(r.read().decode("utf-8", "replace"))
                break
            except urllib.error.HTTPError as e:
                detail = redact(e.read().decode("utf-8", "replace")[:400], self.cfg)
                last = "HTTP %s: %s" % (e.code, detail)
                if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(min(30, 3 * 2 ** attempt)); continue
                raise Infra("%s refused: %s" % (self.role, last))
            except Exception as e:                                  # socket, DNS, timeout
                last = "%s: %s" % (type(e).__name__, redact(str(e), self.cfg))
                if attempt < retries:
                    time.sleep(min(30, 3 * 2 ** attempt)); continue
                raise Infra("%s unreachable: %s" % (self.role, last))
        ch = (d.get("choices") or [{}])[0]
        text = (ch.get("message") or {}).get("content") or ""
        if not text.strip():
            raise Infra("%s: the endpoint returned an empty completion (finish_reason %r)" % (self.role, ch.get("finish_reason")))
        usage = d.get("usage") or {}
        self.calls += 1
        self.tokens += int(usage.get("total_tokens") or 0)
        meta = {"role": self.role, "model": d.get("model") or self.model, "call": self.calls,
                "prompt_sha": sha(system + "\n" + user), "reply_sha": sha(text),
                "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                "seconds": round(time.time() - t0, 1), "finish_reason": ch.get("finish_reason")}
        self.log.append(meta)
        return text, meta


def extract_json(text):
    """Take the first JSON object out of a reply, fenced or not.

    A model that wraps its answer in prose is not a failure of the answer, but a parser that accepts
    the prose IS a failure of the gate: what is validated downstream must be the object, so anything
    that is not parseable as one object is refused here rather than repaired.
    """
    s = text.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        s = s.rsplit("```", 1)[0]
    s = s.strip()
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("no JSON object in the reply")
    return json.loads(s[i:j + 1])


def main(argv):
    """`client.py check` proves the endpoint answers, without naming it in any output."""
    if argv and argv[0] == "check":
        c = Client(role="propose")
        text, meta = c.ask("Answer with JSON only.", 'Reply exactly: {"ok": true}', max_tokens=32)
        ok = extract_json(text).get("ok") is True
        print("agent client: %s, model %s, %s prompt tokens, %s s" % (
            "OK" if ok else "UNEXPECTED REPLY", meta["model"], meta["prompt_tokens"], meta["seconds"]))
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Infra as e:
        print("INFRA_FAIL %s" % e); sys.exit(3)
