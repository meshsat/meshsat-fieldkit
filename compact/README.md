# Compact kit: the pocket-sized MeshSat node

The compact kit is the small MeshSat node: a Meshtastic LoRa radio and an Iridium modem in a case that fits a pocket, running the MeshSat fork of the Meshtastic firmware and talking to the MeshSat phone apps over one Bluetooth link. It is a kit in its own right beside the field kits of `v1/` and `v2/`, with its own version line. This folder holds the hardware side: the version table below and, under `compact/v2/`, the enclosure design. The firmware, the wiring tables, the bench tools and the Bluetooth contract live in [meshsat-esp32](https://github.com/meshsat/meshsat-esp32) and [meshsat-firmware](https://github.com/meshsat/meshsat-firmware); the user guide is [docs.meshsat.net/node/](https://docs.meshsat.net/node/).

MeshSat is a prototype. The v0 and v1 nodes are bench units. The v2 enclosure is a design: nothing of it has been printed or fitted, and its own audit response clears it for prototype printing only.

## Versions

| | v0 (bench) | v1 (prototype) | v2 (design) |
|---|---|---|---|
| Board | Seeed Studio XIAO ESP32-S3 + Wio-SX1262 | LILYGO T-Beam Supreme (ESP32-S3, SX1262, u-blox M10S GPS) | LILYGO T-Beam Supreme |
| Satellite | RockBLOCK 9603 (Iridium SBD) | RockBLOCK 9603 (Iridium SBD) | RockBLOCK 9704-SMA (Iridium IMT) with Ground Control's helical antenna |
| Power | USB power bank | one 18650 cell in the T-Beam's holder, charged over USB-C; the modem runs from the T-Beam's power chip | one 18650 cell in the T-Beam's holder; how the 9704 is fed is an open item of the design (Ground Control's battery window for it is 3.6 to 4.5 V) |
| Case | Peli 1050 | Peli 1020 with an IP68 USB-C port and a panel power button; the build is not finished | a 3D-printed stacked enclosure: the 9704 on edge rails in the lower bay, a printed separator, the T-Beam and its cell in the upper bay, an OLED window in the lid; ASA parts, a TPU button membrane, an O-ring cord seal, a polycarbonate pane, two SMA bulkheads, an IP67 panel USB-C, an M12 vent, a 12 mm IP67 switch, a MOLLE or belt plate; 62.5 x 146.0 x 62.7 mm, 154.0 mm long with the SOS guard |
| Firmware env | `meshsat-xiao-s3-rockblock` | `meshsat-tbeam-s3-rockblock` | not part of this package: firmware and app support for the 9704 on the node is not claimed here |
| State | tested on the bench, September 2026; retired from the phone role on 21 September 2026 | running since 21 September 2026 on the bench and in a garden | designed 5 October 2026 (`meshsat-enclosure` v0.6); the first test coupons are being printed in October 2026; nothing printed or fitted |

The v0 and v1 wiring (four wires between the board and the RockBLOCK) and the proven table are in the meshsat-esp32 README and on docs.meshsat.net/node/build; they are not repeated here.

## v2: the printed enclosure (`compact/v2/`)

`compact/v2/` is the OpenSCAD package `meshsat-enclosure-v0.6` as delivered on 5 October 2026, the design's response to an engineering audit of its v0.5 (findings F01 to F15, each answered in [`v2/AUDIT-RESPONSE.md`](v2/AUDIT-RESPONSE.md)). Its own [`README.md`](v2/README.md) is the print and assembly guide: the print order (three test coupons first, then one full prototype in PLA or PETG, then the ASA set), materials and orientations, the hardware list, the assembly notes and the electrical items it leaves open.

| Path | Content |
|---|---|
| `v2/source/meshsat-enclosure-v0.6.scad` | the design, one file; `PART` selects a printable part, a coupon, the assembly or the exploded view |
| `v2/print-stl/` | the eight printable parts, exported in print orientation: body, lid, separator, membrane (TPU), plungers (three), retainer, MOLLE plate, belt plate |
| `v2/coupons/` | the three test coupons: `rails` (the 9704 slot fit), `rimlid` (seal groove, inserts, lid screws), `board` (the upper bay with the separator, the real T-Beam and the lid) |
| `v2/renders/` | assembly, two exploded views (with a ruler and a 2 EUR coin) and the button detail |
| `v2/validation/` | `build_and_check.sh` regenerates every STL and reruns the checks; `clash_check.py` intersects every printed part, in assembled position, with the makers' board geometry; `mesh_report.py` writes the printability report with a SHA-256 per STL; `build/` holds the results for this release (clash 0.000 mm3 against both boards, the self-checks as expected) |
| `v2/reference-cad/` | the makers' models the boards were registered from (LilyGO, Ground Control), with their own [`README.md`](v2/reference-cad/README.md): not covered by this repository's licence |

Two files of the delivered package are not duplicated here because this repository already holds them byte for byte: the RockBLOCK 9704-SMA board STEP (`v2/vendor/rockblock/RockBLOCK 9704-SMA-2A.step`, 52.7 MB) and the mount drawing (`v2/vendor/rockblock/rb9704-sma-dims.pdf`). The validation chain reads only the tessellated meshes in `v2/reference-cad/meshes/`, so it runs without them. The package as delivered: `meshsat-enclosure-v0.6.zip`, 58 files, sha256 `002b31a9390fab535e158f40d89099b727800e5863262c885cb629dfd9aa1761`. Its README and audit response are kept as delivered, with their dashes written out under this repository's drafting rule (ranges as "a to b", empty evidence cells as "none"); nothing else in them changed.

Open before a full build, in the design's own words (the matrix in `v2/AUDIT-RESPONSE.md`): the exact panel part numbers and their cut-outs (F11); how the 9704 is powered (F12); Ground Control's certification condition that no other transmitter sits in the same housing as the 9704, where this design puts LoRa, Bluetooth and WiFi beside it (F13, their written position is owed); the leak, button and insert tests and the qualification sequence (F14); and the real-part fit of the 1.80 mm rail slot and of the 18650 holder, which is not in LilyGO's STEP. The next revision, v0.7, is owed before the full set is printed: a flip cover over the SOS button and the final panel hardware.

## Licence

The enclosure design (the `.scad` source and the STL files made from it) is released under this repository's licence, CERN-OHL-S-2.0. The files under `v2/reference-cad/` belong to their makers and are reference material only; see that folder's README.
