#!/usr/bin/env python3
"""Independent recomputation for the AI review of fnd/energy2 3af58534 (section 9). Does NOT import
energy_architecture.py. Uses energy_budget.simulate() (and its Pack, which simulate needs) as the reference model;
the profile, node power, floor, night and search loops are this checker's own code."""
import json, math, os, sys

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))  # the repository root (filed under records/energy/checks/ by the integrator; the checker ran it from a scratch clone)
HERE = os.path.join(REPO, "v2/docs/records/energy")
sys.path.insert(0, HERE)
import yaml
import energy_budget as EB

d = yaml.safe_load(open(os.path.join(HERE, "energy_inputs.yaml")))
pvgis = json.load(open(os.path.join(REPO, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json")))
L = 42.8

# own profile: the yaml's September shape scaled to the PVGIS September mean day on the optimal plane
sep = [r["H(i_opt)_m"] for r in pvgis["outputs"]["monthly"] if r["month"] == 9]
mean_day_kwh = sum(sep) / len(sep) / 30.0
raw = d["solar"]["day_profile_w_m2"][9]
prof = [x * mean_day_kwh / (sum(raw) / 1000.0) for x in raw]
pr = d["solar"]["panel"]["performance_ratio"]["typ"]
eta = 1.0
for c in d["solar"]["chain"]:
    eta *= c["eta"]
ref = EB.profile(d, pvgis, 9)[0]
print("own profile vs EB.profile max abs diff: %.2e W/m2; Sept mean day %.3f kWh/m2 (%d years); pr %.4f eta %.4f" % (
    max(abs(a - b) for a, b in zip(prof, ref)), mean_day_kwh, len(sep), pr, eta))


def node(g, wp, win):
    return min(wp * g / 1000.0 * pr, win) * eta


# 1. demand
print("\n1. demand: 24 h %.1f Wh, 72 h %.1f Wh" % (24 * L, 72 * L))
lat = math.radians(52.160)
for doy, lab in ((258, "15 Sep"), (244, "1 Sep"), (273, "30 Sep")):
    dec = math.radians(23.44) * math.sin(2 * math.pi * (284 + doy) / 365.0)
    cosh = (math.sin(math.radians(-0.833)) - math.sin(lat) * math.sin(dec)) / (math.cos(lat) * math.cos(dec))
    day = 2 * math.degrees(math.acos(cosh)) / 15.0
    print("   %s: declination %+.2f deg, day %.2f h, sun down %.2f h, night demand %.1f Wh" % (
        lab, math.degrees(dec), day, 24 - day, (24 - day) * L))
print("   record's 11.28 h x 42.8 W = %.1f Wh" % (11.28 * L))

# 2. storage floor (own node power)
print("\n2. storage floor (sum over hours with node power under the load)")
for win in (100.0, 200.0):
    for wp in (200, 400, 800, 20000):
        p = [node(g, wp, win) for g in prof]
        deficit = sum(L - x for x in p if x < L)
        print("   window %4.0f W, %5d Wp: %2d h below, deficit %.1f Wh/day, harvest %.1f Wh/day" % (
            win, wp, sum(1 for x in p if x < L), deficit, sum(p)))

pack = EB.Pack(d)


def sim(load, wp, win, n_p, start, t_c=20.0, dod="3v00"):
    return EB.simulate(d, pack, prof, load, wp, win, eta, pr, start, t_c, pack.age80, 72, dod, n_p)


def meets(load, wp, win, n_p, t_c=20.0):
    r = [sim(load, wp, win, n_p, s, t_c)[1] for s in (6, 18)]
    return all(x["ok"] for x in r), min(x["lowest"] for x in r), [x["first_stop"] for x in r]


def smallest(load, wp, win, t_c=20.0):
    for n_p in range(1, 100):
        if meets(load, wp, win, n_p, t_c)[0]:
            return n_p
    return None


print("\n3. smallest pack (both starts, +20 C, aged 80 percent, 3.00 V line)")
for win in (100.0, 200.0):
    for wp in (400, 650):
        n = smallest(L, wp, win)
        print("   window %4.0f W, %4d Wp: 4S%dP, usable %.1f Wh" % (win, wp, n, pack.usable_wh(L, 20.0, pack.age80, "3v00", n)[0]))
print("   per string at 15..18P: " + ", ".join("%.2f" % (pack.usable_wh(L, 20.0, pack.age80, "3v00", n)[0] / n) for n in (15, 16, 17, 18)))

print("\n4. 4S18P lowest point, 42.8 W, 200 W window")
for wp in (400, 650):
    for t in (20.0, 15.0):
        ok, low, st = meets(L, wp, 200.0, 18, t)
        print("   %4d Wp, %+5.1f C: %s, lowest %.1f Wh, stops %s" % (wp, t, "MEETS" if ok else "NOT MET", low, st))
n18 = pack.usable_wh(L, 20.0, pack.age80, "3v00", 18)[0]
print("   4S18P usable %.1f Wh; nominal 72 x 144.7/12 = %.1f Wh; cells %.1f kg" % (n18, 72 * 144.7 / 12, 72 * 0.050))
pk = max(max(f for (_h, _hh, _g, _p, _l, f, _e, _r) in sim(L, 400, 200.0, 18, s)[0]) for s in (6, 18))
print("   peak stored charge 4S18P 400 Wp 200 W: %.1f W (offered %.1f W, node peak %.1f W)" % (pk, pk / 0.95, max(node(g, 400, 200.0) for g in prof)))

print("\n5. inside REQ-016's 100 W window: the pack sizes the case could hold (9f: base 4S6P + lid up to 4S13P)")
for n_p in (18, 19):
    for wp in (1000, 1300, 1500):
        for t in (20.0, 15.0):
            ok, low, st = meets(L, wp, 100.0, n_p, t)
            print("   4S%dP, %4d Wp, %+5.1f C: %s, lowest %.1f Wh, stops %s" % (n_p, wp, t, "MEETS" if ok else "NOT MET", low, st))


def maxload(n_p, wp, win):
    lo, hi = 0.0, 80.0
    for _ in range(40):
        m = 0.5 * (lo + hi)
        if meets(m, wp, win, n_p)[0]:
            lo = m
        else:
            hi = m
    return lo


print("   largest load 4S18P, 100 W window: 1000 Wp %.2f, 1300 Wp %.2f, 1500 Wp %.2f W" % tuple(maxload(18, w, 100.0) for w in (1000, 1300, 1500)))
print("   largest load 4S19P, 100 W window, 1300 Wp: %.2f W" % maxload(19, 1300, 100.0))
print("   largest load 4S3P, 200 W window, 400 Wp: %.2f W; 4S6P: %.2f W" % (maxload(3, 400, 200.0), maxload(6, 400, 200.0)))

print("\n6. lid footprint arithmetic (18.55 pitch, 66.25 rows, 346.16 x 231.86 ceiling)")
a = int(346.16 // 66.25) * int(231.86 // 18.55)
b = int(346.16 // 18.55) * int(231.86 // 66.25)
print("   rows along the long side: %d cells; along the short side: %d cells" % (a, b))

print("\n7. inside the 100 W window beyond the sweep's 1500 Wp cap: smallest pack and its lowest point")
for wp in (1500, 1600, 2000, 3000, 20000):
    n = smallest(L, wp, 100.0)
    ok, low, st = meets(L, wp, 100.0, n)
    ok15 = meets(L, wp, 100.0, n, 15.0)[0]
    print("   %5d Wp: 4S%dP, lowest %.1f Wh at +20 C, +15 C %s" % (wp, n, low, "MEETS" if ok15 else "NOT MET"))

print("\n8. no window, arrays beyond the sweep: smallest pack")
for wp in (1500, 2000, 5000, 20000):
    n = smallest(L, wp, 1e9)
    print("   %5d Wp: 4S%dP, lowest %.1f Wh at +20 C" % (wp, n, meets(L, wp, 1e9, n)[1]))

print("\n9. the lowest cell temperature at which the recommended 4S18P (400 Wp, 200 W window) meets M1")
lo, hi = 0.0, 20.0
for _ in range(30):
    m = 0.5 * (lo + hi)
    if meets(L, 400, 200.0, 18, m)[0]:
        hi = m
    else:
        lo = m
print("   threshold about %+.2f C (meets at and above)" % hi)
