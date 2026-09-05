# Concept renders of the assembled V2 kit

Blender scene of the whole kit as designed on 5 September 2026 (appendix 32.35): the Peli 1520EU base and lid, the 1520PF frame with the sealed panel C5, the dock strip E4 and block E5, PCB-A A20 with the APRS mezzanine D6, the Compute Module 5 carrier B13, the battery module in its cradle, the end-wall antennas and the back-wall connector plate. Everything sits at the case-frame positions of the design record (X along the long axis, +Y the hinge wall, Z up from the cavity floor). The images in `v2/images/concept/` are concept illustrations of a design that has not been built: the boards are the real KiCad geometry, the case and the display are the makers' STEP models, the rest (switches, antennas, the module cooler, cables) are simple stand-in shapes.

Reproduce on the design laptop (Blender 4.0, KiCad 9, `~/.venv-cad` with build123d):

1. `kicad-cli pcb export glb --subst-models --include-pads --user-origin <OX>x<OY>mm -o ~/render3d/<board>.glb <board>.kicad_pcb` for the six boards (origins 150x110 for A, B, E1, E5; 297x210 for C; 100x100 for D), with `KICAD9_3DMODEL_DIR` pointing at a folder holding the library STEP models the footprints reference (fetched from `gitlab.com/kicad/libraries/kicad-packages3D`).
2. `~/.venv-cad/bin/python step2stl.py` converts the vendor STEP models (case, lid, frame, display, e-paper, RockBLOCK, battery module) to STL under `~/render3d/stl/`.
3. `blender -b -P scene.py -- <out dir> all` renders the six views (overview, hero, top, detail, stack, closed); `SAMPLES` and `RESPCT` in the environment trade quality for time. `ui.png` is the mock screen content.
