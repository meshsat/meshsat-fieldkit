#!/usr/bin/env python3
"""Connection to the meshsat_kb store. One place, so no script carries connection details."""
import kbenv

try:
    import pymysql
except ImportError as e:   # a rented box has no LAN route to the store anyway; say so plainly
    pymysql = None
    _IMPORT_ERR = e


def connect():
    if pymysql is None:
        raise kbenv.InfraFail("INFRA_FAIL: pymysql is not installed (%s)" % _IMPORT_ERR)
    try:
        return pymysql.connect(
            host=kbenv.get("MESHSAT_KB_DB_HOST"), port=int(kbenv.get("MESHSAT_KB_DB_PORT")),
            user=kbenv.get("MESHSAT_KB_DB_USER"), password=kbenv.get("MESHSAT_KB_DB_PASS"),
            database=kbenv.get("MESHSAT_KB_DB_NAME"), charset="utf8mb4", autocommit=True,
            connect_timeout=15, read_timeout=120, write_timeout=120)
    except kbenv.InfraFail:
        raise
    except Exception as e:
        raise kbenv.InfraFail("INFRA_FAIL: the knowledge base store is unreachable (%s)" % e)
