#!/usr/bin/env python3
"""Configuration for the datasheet knowledge base (MESHSAT-862, 10 September 2026).

THERE ARE NO DEFAULTS HERE ON PURPOSE. This repository is mirrored publicly to GitHub within
minutes of every push, so no host, address or credential of the estate may appear in it. Every
value comes from ~/.config/meshsat-fieldkit/kb.env (mode 600, outside the tree) or from the
environment, and a missing value is an INFRA_FAIL that says which key is absent, never a quieter
path to a wrong answer.

Keys: MESHSAT_KB_DB_HOST, _PORT, _USER, _PASS, _NAME, MESHSAT_KB_OLLAMA_URL, MESHSAT_KB_RERANK_URL.
"""
import os

ENV_FILE = os.environ.get("MESHSAT_KB_ENV", os.path.expanduser("~/.config/meshsat-fieldkit/kb.env"))


class InfraFail(RuntimeError):
    """The store or the embedding host cannot be reached or is not configured. Never a result."""


def _file_values():
    vals = {}
    try:
        with open(ENV_FILE) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return vals


_FILE = _file_values()


def get(key, default=None):
    """Environment first, then the config file. `default` is for genuinely optional knobs only."""
    v = os.environ.get(key, _FILE.get(key, default))
    if v is None:
        raise InfraFail("INFRA_FAIL: %s is not set (env, or %s). The knowledge base is not "
                        "configured on this host; that is not an empty result." % (key, ENV_FILE))
    return v


def configured():
    """True when every required key is present, so a caller can skip rather than crash."""
    for k in ("MESHSAT_KB_DB_HOST", "MESHSAT_KB_DB_PORT", "MESHSAT_KB_DB_USER",
              "MESHSAT_KB_DB_PASS", "MESHSAT_KB_DB_NAME", "MESHSAT_KB_OLLAMA_URL"):
        try:
            get(k)
        except InfraFail:
            return False
    return True
