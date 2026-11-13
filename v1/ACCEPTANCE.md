# V1 kit acceptance checklist (tesseract and parallax)

A kit passes this checklist before it goes to a demo day. Each item says how to check it and what counts as a pass. The result of every run is published in [`acceptance/`](acceptance/), one file per kit and date, failed items included. The kits themselves are described in [BUILD.md](BUILD.md).

**MeshSat is a prototype. Do not rely on it for life safety.** A kit that passes this checklist works on the bench and at a demo, run by us. It has not been through a real deployment, and it does not replace 112 or any official emergency network.

**Contact for the kits and demo days:** Elli Zafeiridou Georgiadou, project manager, elli@meshsat.net.

## How a run works

- Kyriakos runs the checks; a second person watches and fills in the result file.
- Run it in the place the kit will work: indoors for everything except the satellite items, which need open sky.
- Start from a kit that has been switched off for at least ten minutes.
- An item is **pass**, **fail** or **not run**, with a note. A kit passes when every item in sections A to E is a pass. A failed item gets an issue in this repository (github.com/meshsat/meshsat-fieldkit) and the kit is run again after the fix.
- Commands run on the kit over SSH; `localhost:6050` is the Bridge on the kit itself. The web app is on the kit's touchscreen or at `http://<kit>:6050`.

## A. Case and antennas

| # | Check | Pass |
|---|---|---|
| A1 | Open the case and look at the plate stack, the rods and every cable. | Nothing loose, nothing pinched, every connector seated. |
| A2 | Every antenna on its bulkhead; tighten each SMA joint with the 1 Nm torque wrench, inside and outside. | All joints at 1 Nm. A loose SMA joint looks exactly like "no satellite". |
| A3 | Close the case. | Lid closes and both latches lock without force on a cable. |

## B. Power and start-up

| # | Check | Pass |
|---|---|---|
| B1 | Connect power and switch the kit on from cold. Time it. | The touchscreen shows the operator dashboard without anyone touching the kit. Write down the minutes it took. |
| B2 | `journalctl -b \| grep -ic "ordering cycle"` | `0` |
| B3 | `vcgencmd get_config usb_max_current_enable` and `vcgencmd get_throttled` | `usb_max_current_enable=1` and `throttled=0x0` |
| B4 | `uname -r` | `6.8.0-1051-raspi` (the newer kernel blanks the Touch Display 2) |
| B5 | `date` before the network is up, then `chronyc tracking` | The clock is right within a minute before sync (the RTC cell holds it) and within a second after. |
| B6 | `curl -s localhost:6050/api/system/battery` | Voltage and state of charge are numbers, `stale` is `false`. |
| B7 | Unplug the power for five minutes, then plug it back. | The kit stays up on its cells, `ac_present` goes `false` and back to `true`, `charging` turns on. |

## C. Bridge software

| # | Check | Pass |
|---|---|---|
| C1 | `docker inspect -f '{{.Image}} {{.HostConfig.RestartPolicy.Name}} {{.RestartCount}}' meshsat` | The image is the one the last pipeline on `main` built, the policy is `always`, no restarts since the start. |
| C2 | `curl -s -o /dev/null -w '%{http_code}' localhost:6050/health` | `200` |
| C3 | `curl -s localhost:6050/api/devices/health` | Every device fitted to this kit is `ok`. A device taken out of the kit shows `removed`, with the reason in its note. |
| C4 | `docker logs --since 1h meshsat 2>&1 \| grep -c ' ERR '` | `0`, or each error explained in the note. |
| C5 | Touch the screen through the operator dashboard pages. | Every page opens and touch lands where the finger is. |

## D. Every channel, one message each way

Each channel counts only with a real message, never with a "connected" flag.

| # | Channel | Check | Pass |
|---|---|---|---|
| D1 | LoRa mesh (LILYGO T-Echo, Meshtastic, 868 MHz) | Read the node id from `/api/status`. Send a text from a Meshtastic handheld on the kit's channel, answer it from the kit's web app. Read `air_util_tx` on `/api/nodes`. | Both texts arrive. `air_util_tx` is under 5 % at idle. |
| D2 | Cellular and SMS (LILYGO T-Call A7670E, KPN) | `/api/cellular/status`, then an SMS from a test phone to the kit and a reply from the web app. | Registered on LTE, both SMS arrive. |
| D3 | Iridium SBD (RockBLOCK Mk2, 9602) | Under open sky: `/api/iridium/modem` reads the IMEI, `/api/iridium/signal`, then one message out from the web app and one message in. | IMEI read, at least 2 bars, both messages delivered. |
| D4 | APRS (PicoAPRS V4, 144.800 MHz) | Look at the PicoAPRS screen. Only if it is dark, hold its PTT for 3 s to switch it on; that opens the case, so log it (section F). With the other kit running, wait 7 minutes, then read `rx`, `bad_frames` and `last_decode_at` on `/api/aprs/status` and the other kit's callsign on `/api/aprs/heard`. | `rx` climbs, `bad_frames` stays where it was, and each kit hears the other. In a quiet place, note how many frames came in. |
| D5 | MeshSat Hub | `/api/routing/hub`, then the kit on the Hub's Fleet page. Find `relay: serving through the Hub` in the log. | The kit shows online on the Hub and the relay is serving. |

## E. What visitors see on a demo day

| # | Check | Pass |
|---|---|---|
| E1 | RUN FULL DEMO on the operator dashboard. | Every leg passes except Iridium when there is no sky (Iridium is D3). |

## F. Notes for the run (not pass or fail)

- If the Community Post is part of the demo day: connect a phone to it, post a message, and check it appears on the kit.
- Battery runtime from the four cells, if there is time: about 6 to 9 hours, 5.5 W idle to 14 W busy. Write down what the kit did.
- A hands-on fix during the run (a re-seat, a button press) goes into the kit's own log the same day: web app, Interfaces > Devices > "Log a hands-on fix".

## Result file

`acceptance/<date>-<kit>.md` with: date, place, who ran and who watched, the image of C1, then one line per item: number, pass / fail / not run, note. Failed items link their issue.
