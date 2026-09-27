"""pair_router: the pair pre-router split at measurable boundaries (15 September 2026). config (budgets, clearances,
layer tables, the shared epochs), occupancy (the Grid, the rasters, build_maps and the via-site test), search (the
corridor and stub searches, the timers, smoothing), geometry (segments, mitres, loops, polylines). pair_preroute.py keeps
the orchestration in main() and re-exports every name here so nothing that imports it changes."""
import os


def source():
    """The pre-router's whole source (the entry file and the four modules) for the rules that read it."""
    here = os.path.dirname(os.path.abspath(__file__)); out = []
    out.append(open(os.path.join(os.path.dirname(here), "pair_preroute.py"), errors="replace").read())
    for f in ("config", "occupancy", "search", "geometry"):
        out.append(open(os.path.join(here, f + ".py"), errors="replace").read())
    return "\n".join(out)
