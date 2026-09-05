# Concept renders of the assembled V2 kit

Blender scene of the whole kit as designed on 5 September 2026 (appendix 32.35): the Peli 1520 base and lid, the 1520PF frame with the sealed panel C5, the dock strip E4 and block E5, PCB-A A20 with the APRS mezzanine D6, the Compute Module 5 carrier B13, the battery module in its cradle, the end-wall antennas and the back-wall connector plate. Everything sits at the case-frame positions of the design record (X along the long axis, +Y the hinge wall, Z up from the cavity floor). The images in `v2/images/concept/` are concept illustrations of a design that has not been built.

What is real geometry and what is a stand-in:

- The boards are the KiCad layouts exported as GLB (pads and the library models of the parts).
- The case is modelled in the scene from Peli's numbers (drawing 1521-931 and the envelope STEP in `v2/vendor/peli/1520/`): outer 508 x 378, rim at 124.87 above the cavity floor, cavity 413.8 x 283.6 at the floor and 448.4 x 318.1 at the rim, lid 71.5. Peli's STEP is an envelope without ribs, latches or handle, so the ribs, the two double-throw latches, the folding handle, the pressure valve, the hinge, the corner bosses, the padlock protectors and the feet are drawn from the drawing and from the product photographs; they are illustration, not vendor CAD.
- The frame, the Touch Display 2, the WeAct e-paper, the RockBLOCK 9704 and the battery module are the makers' STEP models converted to STL.
- The switches follow the named parts (C&K ATP19/ATP16 anti-vandal buttons with the illuminated ring, NKK M2044 with the AT401A boot on LIGHT, APEM 5636 locking toggles on SOS, EMCON and ZEROIZE), the LEDs, the sounder, the antennas, the module cooler, the LTE card, the SDR stick and the cables are stand-in shapes.
- The display shows a mock status page (`ui.png`); the e-paper shows the QR code of https://meshsat.net with the status lines of `PANEL.md` (`epaper.png`, made by `make_epaper.py`).

Everything the scene needs is in this folder: `glb/` holds the six board exports (KiCad geometry with pads and the library models, case-frame origins), `stl/` the STL conversions of the vendor STEP models the scene uses (frame, display, e-paper, RockBLOCK, battery module), `ui.png` and `epaper.png` the screen contents, and `meshsat-v2-concept.blend` the assembled scene with the textures packed (open it in Blender 4.0 or later, pick a camera, render). `scene.py` rebuilds the scene from `glb/` and `stl/`; it reads them from `~/render3d/` and `~/render3d/stl/`, so copy or link the two folders there (or edit `R` and `STL` at its top).

Reproduce from the KiCad boards on the design laptop (Blender 4.0, KiCad 9, `~/.venv-cad` with build123d):

1. `kicad-cli pcb export glb --subst-models --include-pads --user-origin <OX>x<OY>mm -o ~/render3d/<board>.glb <board>.kicad_pcb` for the six boards (origins 150x110 for A, B, E1, E5; 297x210 for C; 100x100 for D), with `KICAD9_3DMODEL_DIR` pointing at a folder holding the library STEP models the footprints reference (fetched from `gitlab.com/kicad/libraries/kicad-packages3D`).
2. `~/.venv-cad/bin/python step2stl.py` converts the vendor STEP models (frame, display, e-paper, RockBLOCK, battery module) to STL under `~/render3d/stl/`.
3. `python3 make_epaper.py` (needs `qrcode` and Pillow) writes `epaper.png`.
4. `blender -b -P scene.py -- <out dir> all` renders the six views (overview, hero, top, detail, cutaway, closed); `SAMPLES` and `RESPCT` in the environment trade quality for time.
