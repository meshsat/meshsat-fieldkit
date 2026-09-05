# Concept renders, the kit in the Peli 1450 (5 September 2026)

Concept illustrations of the V2 kit as designed on 5 September 2026 (design record 32.40 to 32.42): the Peli 1450 with the 1450PF frame, the 3 mm aluminium face plate with the backer board C6 under it, the stack (E4, E5, A21, D7, B15), the battery row along the west end wall, the nine end-wall antennas and the upright connector plate with both cables plugged. Rendered by `v2/cad/render/scene.py` (Blender, Cycles) from the KiCad boards, Peli's 1451-931 CAD and the makers' models; see `v2/cad/render/README.md` for what is real geometry and what is a stand-in. **Nothing in these images has been built.**

Every image carries rulers (white bars, 10 mm ticks, numerals every 50 mm) along the case's edges on the ground and standing at the front corners, a 50 mm floor grid, and a title strip with the view name. Case frame: X along the case, +Y toward the hinge wall, Z from the cavity floor (the ground plane lies under Peli's 25 mm floor-and-feet slab).

## Orbit, lid open (eight azimuths by three elevations)

Azimuth 0 looks at the front wall (handle and latches), 90 at the east end (LTE, Iridium, LoRa, WiFi P2P), 180 at the back wall (hinge, connector plate), 270 at the west end (UHF, WiFi 2.4, GNSS, SDR); elevations 20, 40 and 60 degrees.

| | el 20 | el 40 | el 60 |
|---|---|---|---|
| az 0 | ![](meshsat-1450-az000-el20-open.png) | ![](meshsat-1450-az000-el40-open.png) | ![](meshsat-1450-az000-el60-open.png) |
| az 45 | ![](meshsat-1450-az045-el20-open.png) | ![](meshsat-1450-az045-el40-open.png) | ![](meshsat-1450-az045-el60-open.png) |
| az 90 | ![](meshsat-1450-az090-el20-open.png) | ![](meshsat-1450-az090-el40-open.png) | ![](meshsat-1450-az090-el60-open.png) |
| az 135 | ![](meshsat-1450-az135-el20-open.png) | ![](meshsat-1450-az135-el40-open.png) | ![](meshsat-1450-az135-el60-open.png) |
| az 180 | ![](meshsat-1450-az180-el20-open.png) | ![](meshsat-1450-az180-el40-open.png) | ![](meshsat-1450-az180-el60-open.png) |
| az 225 | ![](meshsat-1450-az225-el20-open.png) | ![](meshsat-1450-az225-el40-open.png) | ![](meshsat-1450-az225-el60-open.png) |
| az 270 | ![](meshsat-1450-az270-el20-open.png) | ![](meshsat-1450-az270-el40-open.png) | ![](meshsat-1450-az270-el60-open.png) |
| az 315 | ![](meshsat-1450-az315-el20-open.png) | ![](meshsat-1450-az315-el40-open.png) | ![](meshsat-1450-az315-el60-open.png) |

## Lid closed, low views

| az 0 | az 45 | az 90 | az 135 |
|---|---|---|---|
| ![](meshsat-1450-az000-el20-closed.png) | ![](meshsat-1450-az045-el20-closed.png) | ![](meshsat-1450-az090-el20-closed.png) | ![](meshsat-1450-az135-el20-closed.png) |
| az 180 | az 225 | az 270 | az 315 |
| ![](meshsat-1450-az180-el20-closed.png) | ![](meshsat-1450-az225-el20-closed.png) | ![](meshsat-1450-az270-el20-closed.png) | ![](meshsat-1450-az315-el20-closed.png) |

## Details

| View | What it shows |
|---|---|
| ![](meshsat-1450-top-face.png) | the face from above: the display aperture, the e-paper lens with the meshsat.net QR, the buttons, the toggles, the light switch, the sounder, the status column, the battery bar, the nameplate and the logo |
| ![](meshsat-1450-face-detail-left.png) | the left strip: SOS, EMCON and ZEROIZE locking toggles, the light switch, the sounder, the logo |
| ![](meshsat-1450-face-detail-right.png) | the right strip: MAIN, PI and TEST buttons with their lit rings, the eleven status LEDs |
| ![](meshsat-1450-west-wall.png) | the west end wall: UHF, WiFi 2.4, GNSS puck and SDR bulkheads at 88 mm |
| ![](meshsat-1450-east-wall.png) | the east end wall: LTE, the Iridium patch, LoRa and the two WiFi P2P bulkheads |
| ![](meshsat-1450-back-wall.png) | the back wall: the upright connector plate between the ribs with the shore and USB cables plugged, the hinge |
| ![](meshsat-1450-front-wall.png) | the front wall: the handle, the latches, the pressure valve |
| ![](meshsat-1450-cutaway.png) | the front wall cut away and the face lifted: the dock strip and block, PCB-A with the APRS mezzanine, the Compute Module carrier, the battery row, the pigtails |
| ![](meshsat-1450-battery-row.png) | the battery row along the west wall under the SMA row, the face lifted clear |
| ![](meshsat-1450-face-underside.png) | the face lifted 150 mm: the backer board C6 on its standoffs under the plate, the switch bodies through its slots |
| ![](meshsat-1450-stack-no-face.png) | the stack in the case without the face |
