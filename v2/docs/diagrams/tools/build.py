#!/usr/bin/env python3
"""Rebuild every diagram of v2/docs/diagrams/ and its MANIFEST.json, or check that the committed ones are current
(MESHSAT-1357, handover layer 4).

  python3 v2/docs/diagrams/tools/build.py            extract, generate, render, then write MANIFEST.json
  python3 v2/docs/diagrams/tools/build.py --check    write nothing; exit 1 and name each diagram whose inputs changed
                                                     since MANIFEST.json was written (its sources must be re-rendered)

MANIFEST.json ties each diagram to the sha256/16 of every file it was made from and of every file it produced, the tree
revision, and the tool versions. Rendering needs Node with npx and a Chromium (CHROME_BIN, see render.sh); the Python
steps need only matplotlib and PyYAML. The readback (tools/readback.py) is a separate step, run after a build."""
import json, os, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as N

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
REL = "v2/docs/diagrams"
T = REL + "/tools/"
NET = [N.BOARDS[b] for b in ("A", "B", "C", "D", "E", "P")]
ARCH = [("arch-2-context", "v2/docs/ARCHITECTURE.md"), ("arch-3-2-board-interconnect", "v2/docs/ARCHITECTURE.md"),
        ("arch-4-1-power-tree", "v2/docs/ARCHITECTURE.md"), ("arch-4-3-power-up", "v2/docs/ARCHITECTURE.md"),
        ("arch-5-5-lanes-and-fabric", "v2/docs/ARCHITECTURE.md"),
        ("battery-protection-states", "v2/docs/review-packets/battery/PROTECTION-ARCHITECTURE.md"),
        ("battery-charger-states", "v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md")]
RENDER = [T + "render.sh", T + "mermaid.json"]
DIAGRAMS = {name: dict(inputs=[doc, T + "extract_mermaid.py"] + RENDER, outputs=["src/%s.mmd" % name, "svg/%s.svg" % name, "pdf/%s.pdf" % name])
            for name, doc in ARCH}
DIAGRAMS["control-lines"] = dict(inputs=[N.BOARDS[b] for b in "ABCDE"] + ["v2/ecad/tools/pcb_interfaces.yaml", T + "control_lines.py", T + "netlist.py"] + RENDER,
                                 outputs=["src/control-lines.mmd", "svg/control-lines.svg", "pdf/control-lines.pdf", "control-lines.md"])
DIAGRAMS["power-tree"] = dict(inputs=NET + ["v2/ecad/tools/pcb_energy_chain.yaml", T + "power_tree.py", T + "netlist.py"] + RENDER,
                              outputs=["src/power-tree.mmd", "svg/power-tree.svg", "pdf/power-tree.pdf", "power-tree.md"])
CASE_IN = ["v2/vendor/peli/frame_seat.py", "v2/vendor/peli/1450/frame_seat.out", "v2/vendor/peli/case_margins.py",
           "v2/ecad/tools/panel1450.py", "v2/ecad/tools/gen_pcb_a.py", "v2/ecad/tools/gen_pcb_e.py", "v2/ecad/tools/gen_pcb_e5.py",
           "v2/ecad/tools/gen_pcb_p.py", "v2/cad/render/scene.py", "v2/ecad/tools/pcb_board_facts.yaml", "v2/docs/CASE-MARGINS.md",
           T + "case_drawings.py"]
DIAGRAMS["case-plan"] = dict(inputs=CASE_IN, outputs=["svg/case-plan.svg", "pdf/case-plan.pdf", "case-drawings.md"])
DIAGRAMS["case-zstack"] = dict(inputs=CASE_IN, outputs=["svg/case-zstack.svg", "pdf/case-zstack.pdf", "case-drawings.md"])


def run(cmd):
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=N.REPO)


def version(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout.strip().splitlines()[0]
    except (OSError, IndexError, subprocess.SubprocessError):
        return "not found"


def check():
    man = json.load(open(os.path.join(D, "MANIFEST.json"), encoding="utf-8"))
    stale = []
    for name, rec in man["diagrams"].items():
        moved = [p for p, s in rec["inputs"].items() if not os.path.exists(os.path.join(N.REPO, p)) or N.sha16(p) != s]
        if moved:
            stale.append((name, moved))
    for name, moved in stale:
        print("STALE %-28s inputs changed: %s" % (name, ", ".join(moved)))
    print("diagrams: %d of %d current against MANIFEST.json (written at %s)" % (len(man["diagrams"]) - len(stale), len(man["diagrams"]), man["tree"]))
    return 1 if stale else 0


def build():
    py = sys.executable
    run([py, "-B", T + "extract_mermaid.py"])
    run([py, "-B", T + "control_lines.py"])
    run([py, "-B", T + "power_tree.py"])
    run([py, "-B", T + "case_drawings.py"])
    run(["bash", T + "render.sh"])
    head, dirty = N.git_rev()
    mmdc = os.environ.get("MMDC_VERSION", "11.12.0")
    man = dict(
        what="The diagrams of the MeshSat V2 field kit handover, layer 4. Design diagrams of an unbuilt prototype.",
        tree=head, inputs_differing_from_the_tree=sorted({p for rec in DIAGRAMS.values() for p in rec["inputs"] if N.modified(p)}),
        toolchain=dict(
            python=version([sys.executable, "--version"]),
            matplotlib=version([sys.executable, "-c", "import matplotlib; print(matplotlib.__version__)"]),
            pyyaml=version([sys.executable, "-c", "import yaml; print(yaml.__version__)"]),
            node=version(["node", "--version"]),
            mermaid_cli="@mermaid-js/mermaid-cli@%s (npx; bundles Mermaid and the ELK layout)" % mmdc,
            chromium=version([os.environ["CHROME_BIN"], "--version"]) if os.environ.get("CHROME_BIN") else "Puppeteer's own download"),
        diagrams={})
    for name, rec in DIAGRAMS.items():
        man["diagrams"][name] = dict(inputs={p: N.sha16(p) for p in rec["inputs"]},
                                     outputs={REL + "/" + o: N.sha16(REL + "/" + o) for o in rec["outputs"]})
    open(os.path.join(D, "MANIFEST.json"), "w", encoding="utf-8").write(json.dumps(man, indent=1, ensure_ascii=False) + "\n")
    print("MANIFEST.json: %d diagrams at %s" % (len(man["diagrams"]), head))
    return 0


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else build())
