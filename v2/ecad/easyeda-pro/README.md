# EasyEDA Pro imports of the V2 carrier boards

KiCad 9 is the source of every V2 board (`v2/ecad/pcb-*` and the generators in `v2/ecad/tools/`). The projects here are one-way imports of the released deliverable snapshots into EasyEDA Pro, made on 8 Sep 2026 for the cooperation with EasyEDA and JLCPCB (MESHSAT-776). Nothing is edited on the site and nothing here feeds back into the KiCad sources; when a board is regenerated (A23, B17, C8, D9, and so on), it needs a fresh import from its new deliverable and a new folder here.

Every project on the site is Private on the shared JLCPCB login (Personal workspace), none is published on OSHWLab, and no order is placed from them.

## Boards

| Board | Revision | Source snapshot | Site project | Layers | State |
|---|---|---|---|---|---|
| PCB-A power | A22 | `v2/release/revA/boards/meshsat-pcb-a-revA-A22` | MeshSat V2 A A22 | 6 | routed, released |
| PCB-B compute | B16 | `v2/release/revA/boards/meshsat-pcb-b-revA-B16-quote` plus the working-folder schematic | MeshSat V2 B B16 | 6 | placed, unrouted, quote only (held on this placement, B17 follows) |
| PCB-C display | C7 | `v2/release/revA/boards/meshsat-pcb-c-revA-C7` | MeshSat V2 C C7 | 4 | routed, released |
| PCB-D APRS | D8 | `v2/release/revA/boards/meshsat-pcb-d-revA-D8` | MeshSat V2 D D8 | 4 | routed, released |
| PCB-E1 dock | E6 | `v2/release/revA/boards/meshsat-pcb-e-revA-E6` | MeshSat V2 E1 E6 | 4 | routed, released |
| PCB-E5 block | E5 | `v2/release/revA/boards/meshsat-pcb-e5-revA-E5` | MeshSat V2 E5 E5 | 2 | routed, released, PCB only (no schematic by design) |
| PCB-P pack | P2 | `v2/release/revA/boards/meshsat-pcb-p-revA-P2` | MeshSat V2 P P2 | 2 | routed, released |

The site projects are named "MeshSat V2 <board> <rev>"; by owner instruction nothing on the site (project names, introductions, file names) refers to the source tool.

## Folders

- `import/<board>-<rev>-import.zip`: the archive that was uploaded, built from the deliverable snapshot: `<project>.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `fp-lib-table` and the `meshsat.pretty` footprints the snapshot carries (the B16 quote snapshot has no schematic and no footprint library, so its archive takes the working-folder schematic and the shared `v2/ecad/meshsat.pretty`).
- `<board>-<rev>/`: the exports of that project: `MeshSat-V2-<x>-<rev>.epro2` (Project Save as (Local), EasyEDA Pro V3 format), `MeshSat-V2-<x>-<rev>-schematic.pdf` (File > Export > PDF, merged sheet; none for E5), `<board>-<rev>-pcb-view.jpg` (2D editor), `<board>-<rev>-3d-view.jpg` (3D view), and `import-notes.txt` with the project id, the importer log, the checks made and every warning.

## How an import is made (EasyEDA Pro V3.2.148, web editor)

1. Build the archive from the deliverable snapshot (not from the working folder): project, schematic, board, `fp-lib-table`, the snapshot's `meshsat.pretty`; name it `<board>-<rev>-import.zip` under `import/`.
2. In the editor, Start Page > Import KiCad (or File > Import), accept the notice, choose the zip, Import Document, system theme, associate footprint and 3D model automatically. In the Import Document dialog set Operation New Project, Owner Personal, Project "MeshSat V2 <board> <rev>", a one-line introduction, then Import.
3. Read the Log tab: the import step reports "Import project success" or "import failed"; warnings there (footprints moved between layers, unbound 3D models) go into `import-notes.txt`.
4. Open the PCB document and check the layer panel (copper count against the source), the outline, the footprints and the 3D view; open the schematic.
5. Export: File > Save as > Project Save as (Local) (epro2), File > Export > PDF on the schematic (Default theme, Original Size, All, Merged sheet), and a screenshot of the 2D and the 3D view; move the files into `<board>-<rev>/`.
6. Confirm on `u.easyeda.com/account/user/projects/all` that the project carries the Private tag.

## Findings of the first import (8 Sep 2026)

- Every import completed with all footprints placed and the copper intact; no missing-footprint message on any board. C7 reported four toggle-switch footprints moved to the bottom layer (see its notes).
- No 3D model is bound to any part ("N components were not generated in 3D"): the sources ship no model files, which is expected.
- The stackup does not carry over (the 3D property panel shows placeholder thicknesses); the JLC04161H-7628 and JLC06161H-3313 stackups of the boards are ordered on the JLCPCB cart lines, not read from these projects.
- The schematic arrives as one merged sheet; DRC was not run and design rules were not compared.
- The site's upload is flaky: B16 failed twice ("The upload of the project log failed!", "Network Error!") before the same archive imported on the third attempt after an editor reload; C7 and D8 each needed one retry. A failed import leaves an empty project shell under the chosen name, which has to be deleted on the projects page before the retry. Nothing about the archives caused the failures.

## Cart of the same day

The JLCPCB quote cart of this set (13 lines, all ticked: merchandise 4594.90 EUR, estimated shipping 129.22 EUR, subtotal 4724.11 EUR, nothing paid) is recorded in `v2/release/revA/order/ORDER-LOG.md` section 5.1 with the screenshot `v2/release/revA/order/cart-830-set-2026-09-08.jpg`.
