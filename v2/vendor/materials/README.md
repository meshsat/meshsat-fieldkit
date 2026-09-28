# Materials of the printed parts

Makers' data sheets for the filaments the kit's printed parts are specified in. Filed 27 September 2026 (MESHSAT-1357, the QMX lid tray
r2, S-63). Prototype work: nothing here has been printed or tested.

| File | Source | Used for |
|---|---|---|
| `prusament-pc-blend-tds-v1.1-2022-02-16.pdf` | Prusa Polymers, Prusament PC Blend technical data sheet, Version 1.1 of 16-02-2022, https://prusament.com/wp-content/uploads/2022/10/PCBlend_Prusament_TDS_2022_16_EN.pdf | the QMX lid tray r2 and its keeper (`v2/cad/lid_tray_qmx_r2.py`): heat deflection 113 C at 0.45 MPa and 93 C at 1.80 MPa (ISO 75), interlayer adhesion 21 +-2 MPa, printed-specimen tensile yield 63 +-1 MPa and flexural strength 88 +-1 (horizontal) and 94 +-2 (vertical xz) MPa at 100 percent infill and 0.20 mm layers; the retention figures of `v2/cad/lid_tray_qmx_r2_check.py` take each typical value less its stated spread |
| `prusament-petg-tds-v1.1-2022-02-16.pdf` | the same maker, Prusament PETG technical data sheet, Version 1.1 of 16-02-2022, https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf | the r1 tray's PETG (superseded): heat deflection 68 C at 0.45 MPa, under TEST-PLAN E3-S's +71 C storage, the reason the r2 tray is PC Blend |

The sheets state typical values of specimens printed on the maker's own printer and settings, and disclaim any use beyond information and
comparison: a printed part's strength depends on its print settings, so the tray's drawing (sheet 14r2-2 note 1) names the sheet's
settings, and the retention it computes stays OPEN until TEST-PLAN E1 on the built kit.
