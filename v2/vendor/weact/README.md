# WeAct Studio e-paper module, 3.7 inch

Upstream: https://github.com/WeActStudio/WeActStudio.EpaperModule, commit `a7bf257` (clone taken 2 September 2026). Only the files for the 3.7 inch black and white module are kept here; the upstream repository holds every panel size, examples and tools.

| File | What it is |
|---|---|
| `Hardware/WeAct-EpaperModule-3.7 Board 3D.step` | the module STEP: board 105.79 x 53.80 mm, four 3.2 mm holes on 100.19 x 48.20 mm, 2x4 header on the east edge |
| `Hardware/WeAct-EpaperModule-3.7 Board Shape 外形.pdf` | the outline drawing (the 92.99 mm figure in it is the glass width) |
| `Hardware/WeAct-EpaperModule-4.2_3.7 SchDoc.pdf` | the shared 4.2 / 3.7 schematic |
| `Doc/3.7 Inch Black&Write/` | the E037A75 panel specification (glass 92.99 x 53.0 x 0.95 mm, 416 x 240 pixels, UC8253 driver) and the vendor demo C source |
| `readme.md` | the upstream readme |

These numbers drive the recessed window and the spacer ring on PCB-C (appendix section 25.13).
