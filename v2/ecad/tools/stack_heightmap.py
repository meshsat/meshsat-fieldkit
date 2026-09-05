#!/usr/bin/env python3
"""Stack height map for the panel gate (5 Sep 2026, appendix 32.42): from the render scene's object bounding boxes (scene.py with DUMP_BBOX=<json>),
the highest top Z of the stack on a 5 mm grid of the case frame, leaving out everything that is not the stack (case, lid, frame, panel, its parts,
antennas, rulers, cables). Usage: stack_heightmap.py <bbox.json> <out.json>; the gate reads out.json: {"step": 5, "x0":..., "y0":..., "nx":..., "ny":..., "z": [[...]]}"""
import json, sys, math
objs = json.load(open(sys.argv[1]))
SKIP = ("case", "lid", "frame", "panel", "pcb_c", "td2", "epaper", "lens", "switch", "sw_", "led_", "ruler", "grid", "whip", "ant_", "bulkhead", "cable", "plate", "title", "floor", "hinge", "latch", "handle", "valve", "rib", "boss", "foot", "spacer_", "display_flex", "panel_ribbon", "rod", "nut", "sounder", "toggle", "button", "light")
stack = [o for o in objs if not any(k in o["name"].lower() for k in SKIP)]
step = 5.0; x0, y0 = -180.0, -130.0; nx, ny = int(360 / step) + 1, int(260 / step) + 1
z = [[0.0] * nx for _ in range(ny)]
for o in stack:
    ix0, ix1 = max(0, int((o["x"][0] - x0) // step)), min(nx - 1, int((o["x"][1] - x0) // step)); iy0, iy1 = max(0, int((o["y"][0] - y0) // step)), min(ny - 1, int((o["y"][1] - y0) // step))
    for iy in range(iy0, iy1 + 1):
        for ix in range(ix0, ix1 + 1): z[iy][ix] = max(z[iy][ix], o["z"][1])
top = sorted(stack, key=lambda o: -o["z"][1])[:8]
json.dump({"step": step, "x0": x0, "y0": y0, "nx": nx, "ny": ny, "z": z, "tallest": [(o["name"], o["z"][1]) for o in top], "source": "scene.py DUMP_BBOX", "objects": len(stack)}, open(sys.argv[2], "w"))
print("heightmap: %d stack objects, tallest %s" % (len(stack), ", ".join("%s %.1f" % t for t in [(o["name"], o["z"][1]) for o in top[:5]])))
