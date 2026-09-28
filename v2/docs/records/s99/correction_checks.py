#!/usr/bin/env python3
"""Bounded S-99 correction checks. Stdout only, except temporary scratch copies removed in finally.

No generator application, registry update or gate. AI review support for an unbuilt prototype.
Run: python3 v2/docs/records/s99/correction_checks.py
"""
import ast
from decimal import Decimal
import hashlib
import math
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
CHANGED = (
    "CORRECTION.md", "dev_stage.py", "dev_stage.out", "ANALYSIS.md",
    "RAILS-ACTIONABLE.md", "REGISTRY-DRAFT.md", "apply_d8_split_draft.py",
    "correction_checks.py", "correction_checks.out",
)


def run(path, *args):
    return subprocess.run([sys.executable, str(path), *args], cwd=ROOT,
                          env=ENV, capture_output=True)


def close(got, expected):
    assert math.isclose(got, expected, abs_tol=0.00000051), (got, expected)


def snapshot():
    # Stat all v2 entries, ignoring only this command's externally captured stdout.
    result = {}
    for directory, dirs, files in os.walk(ROOT / "v2", followlinks=False):
        for name in dirs + files:
            p = Path(directory) / name
            if p == HERE / "correction_checks.out":
                continue
            st = p.lstat()
            result[str(p.relative_to(ROOT))] = (st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    return result


def main():
    print("S-99 correction checks. Prototype, AI review support; no acceptance or physical result.")
    stage = runpy.run_path(str(HERE / "dev_stage.py"))
    first = run(HERE / "dev_stage.py")
    second = run(HERE / "dev_stage.py")
    held = (HERE / "dev_stage.out").read_bytes()
    assert first.returncode == second.returncode == 0
    assert not first.stderr and not second.stderr
    assert first.stdout == second.stdout == held
    print("(a) PASS: dev_stage.py exits 0 twice; both outputs match dev_stage.out byte for byte.")
    print("    bytes=%d sha256=%s" % (len(held), hashlib.sha256(held).hexdigest()))
    scratch = HERE / "scratch"
    assert not scratch.exists(), "Refused: scratch already exists"
    scratch.mkdir()
    try:
        copy_script = scratch / "v2/docs/records/s99/dev_stage.py"
        copy_script.parent.mkdir(parents=True)
        shutil.copyfile(HERE / "dev_stage.py", copy_script)
        for rel in stage["INPUT_SHA256"]:
            target = scratch / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        for rel in stage["INPUT_SHA256"]:
            target = scratch / rel
            original = target.read_bytes()
            target.write_bytes(bytes([original[0] ^ 1]) + original[1:])
            refused = run(copy_script)
            assert refused.returncode == 1 and not refused.stdout
            assert ("Refused: input %s: sha256 mismatch" % rel).encode() in refused.stderr
            print("    PASS one-byte refusal, exit 1, empty stdout: %s" % rel)
            target.write_bytes(original)
    finally:
        shutil.rmtree(scratch)
    assert not scratch.exists()
    print("    PASS: scratch removed; original input hashes unchanged.")
    for rel, expected in stage["INPUT_SHA256"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected

    before = snapshot()
    draft = run(HERE / "apply_d8_split_draft.py", "--check")
    after = snapshot()
    assert draft.returncode == 0 and not draft.stderr
    assert before == after, "--check changed a v2 entry"
    assert not (HERE / "apply_d8_split_draft.applied").exists()
    print("(b) PASS: draft --check exits 0; %d v2 entry metadata records unchanged; no marker." % len(before))
    print(draft.stdout.decode().rstrip())
    data = runpy.run_path(str(HERE / "apply_d8_split_draft.py"))
    result = (ROOT / data["GEN"]).read_text()
    assert len(data["CHANGES"]) == 5
    for change in data["CHANGES"]:
        result = result.replace(change["old"], change["new"], 1)
    tree = ast.parse(result)
    declarations = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute) and n.func.attr == "rail"
                    and n.args and isinstance(n.args[0], ast.Constant)
                    and n.args[0].value == "+5V_DEV"]
    assert len(declarations) == 1
    keywords = {k.arg: ast.literal_eval(k.value) for k in declarations[0].keywords}
    assert keywords["loads"] == {"J_5V_DEV": 3.8, "U32": 0.3}
    assert "D8 is supplied separately" in keywords["note"]
    assert "7.056897 A" in keywords["note"] and "7.2 A minimum" not in keywords["note"]
    print("    PASS F9: reconstructed declaration removes U23 load and replaces the stale D8/7.2 A note.")

    wall = Decimal(903) / Decimal(1000) + Decimal("0.0112")
    assert wall == Decimal("0.9142")
    assert stage["TPS2596_ILIM_1K_NOM"] == float(wall)
    print("(c) PASS: Decimal recomputation 903/1000 + 0.0112 = %s A." % wall)
    lo = .043 / (.006 * 1.01 * 1.0055)
    hi = .057 / (.006 * .99 * .9945)
    b_m, b_p, d_m, d_p = 5.442235294117647, 7.215176470588235, 1.38, 1.59
    w_high = float(wall) * 1.051 / 1.005
    w_tol = (903 / 990 + .0112) * 1.051 / 1.005
    for got, expected in [(lo, 7.056897), (hi, 9.649029),
                          (b_p + d_p + w_high, 9.761220),
                          (b_p + d_p + w_tol, 9.770759),
                          (b_p + w_high, 8.171220), (b_p + w_tol, 8.180759),
                          (lo - 6.9, .156897), (lo - b_m - .5, 1.114661)]:
        close(got, expected)
    print("    PASS F1: wall high estimates %.9f/%.9f A; P before %.9f/%.9f, after %.9f/%.9f A." %
          (w_high, w_tol, b_p+d_p+w_high, b_p+d_p+w_tol, b_p+w_high, b_p+w_tol))
    print("    PASS: conditional loop %.9f to %.9f A; split D/M margins %.9f/%.9f A." %
          (lo, hi, lo-6.9, lo-b_m-.5))
    limits = (.043/(.005*1.01), .05/.005, .057/(.005*.99),
              .043/(.005*1.01*1.0055), .057/(.005*.99*.9945))
    for got, expected in zip(limits, (8.514851, 10, 11.515152, 8.468276, 11.578835)):
        close(got, expected)
    assert 8.9 > limits[0] and 8.9 > limits[3] and limits[2] > 10 and limits[4] > 10
    print("    PASS F2 recomputation: initial %.9f/%.9f/%.9f A; hot %.9f/%.9f A; re-rating FAILS both tests." % limits)
    times = [47e-9 * (1.21-.8) / (.001 * mv*.001) * 1000 for mv in (.3, 3.4, 10.4)]
    print("    F3 illustrative onset only: %.6f/%.6f/%.6f ms; not bounds." % tuple(times))
    charge = 440e-6 * .1
    close(charge * 1e6, 44)
    print("    PASS F5 charge arithmetic: 440 uF * 100 mV = %.1f uC; %.1f us at 1 A deficit." % (charge*1e6, charge*1e6))
    s3 = 4.201346 + 3e-6
    print("    PASS F6 arithmetic: conditional %.9f A, margin %.9f A; IC shutdown only, other leakage unresolved." % (s3, 5-s3))
    m = b_m + d_m + .5
    for got, expected in [(m*m*.006, .321691), (m*m*.006*1.01, .324908),
                          (5.088*m/(15.5*.9), 2.670648)]:
        close(got, expected)
    print("    PASS F10: R43 %.9f W nominal / %.9f W +1%%; VBAT %.9f A." %
          (m*m*.006, m*m*.006*1.01, 5.088*m/(15.5*.9)))

    bad = []
    for name in CHANGED:
        path = HERE / name
        assert path.exists(), name
        for line, text in enumerate(path.read_text().splitlines(), 1):
            if any(chr(c) in text for c in (*range(0x2010, 0x2016), 0x2212)):
                bad.append((name, line))
    assert not bad, bad
    print("(d) PASS: nine changed files scanned; no Unicode dash U+2010..U+2015 or minus U+2212.")
    print("All four required checks PASS. Physical timing, collapse, current maxima and temperature remain unverified.")


if __name__ == "__main__":
    main()
