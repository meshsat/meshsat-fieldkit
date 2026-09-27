#!/usr/bin/env python3
"""Embeddings for the datasheet knowledge base: nomic-embed-text, 768 dimensions, asymmetric prefixes.

THE MODEL IS THE CONTRACT, NOT THE HOST. Every vector in `chunk_embeddings` must live in one space
or cosine distance stops meaning anything, and that degradation is silent: nothing errors, the hits
just quietly stop being the right hits. Before pointing MESHSAT_KB_OLLAMA_URL at anything new,
prove the space with `kb_verify.py --space`, which re-embeds stored chunks and requires a median
cosine of at least 0.9999 against what the store already holds.

The embedding host is shared and is stopped during board runs on the VM (the service group of the
5 September ruling includes it), and it reboots daily. An unembedded backlog is therefore a NORMAL
state: every call retries with backoff, and a failure is resumable and never fatal to a caller.
"""
import json, time, urllib.request
import kbenv

MODEL = "nomic-embed-text"
DIM = 768
DOC_PREFIX = "search_document: "     # nomic's asymmetric prefixes: documents and queries differ
QUERY_PREFIX = "search_query: "


def _url():
    return kbenv.get("MESHSAT_KB_OLLAMA_URL").rstrip("/")


def _embed(texts, retries=5):
    payload = json.dumps({"model": MODEL, "input": texts, "options": {"num_ctx": 2048}}).encode()
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(_url() + "/api/embed", data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                out = json.load(resp)
            embs = out["embeddings"]
            if len(embs) != len(texts) or any(len(e) != DIM for e in embs):
                raise ValueError("embedding shape mismatch: %d vectors for %d texts" % (len(embs), len(texts)))
            return embs
        except Exception as e:
            last = e
            time.sleep(min(60, 2 ** attempt * 5))
    raise kbenv.InfraFail("INFRA_FAIL: embedding host unreachable after %d attempts (%s)" % (retries, last))


def embed_documents(texts):
    return _embed([DOC_PREFIX + t for t in texts])


def embed_query(text):
    return _embed([QUERY_PREFIX + text])[0]


def vec_literal(embedding):
    """The argument of MariaDB's VEC_FromText()."""
    return "[" + ",".join("%.7f" % x for x in embedding) + "]"
