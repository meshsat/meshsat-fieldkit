#!/usr/bin/env python3
"""The KiCad 9 API calls this project gets wrong in more than one place (MESHSAT-862, 17 September 2026).

One function so far, and it earned its own file by taking the interpreter down.

`PCB_VIA::GetWidth()` with no argument is an ERROR in KiCad 9: a via's width is per layer, and the bare call
raises a wxWidgets assertion ("PCB_VIA::GetWidth called without a layer argument") on every via it touches. On
a host built with assertions it prints a line per via and can end the process; the board-fixture family did
exactly that, and `return_via.py` was doing it on every via of every real board while it looked for a free
site.
"""
import pcbnew


def via_width(v, layer=None):
    """The via's copper diameter on the layer that matters, in KiCad units.

    The outer layer is the default because every keep-away, clearance and anti-pad question in this project is
    asked where the barrel meets a plane or a pad. A via whose width cannot be read at all falls back to twice
    its drill, which is never larger than the real diameter, so nothing is loosened by the fallback."""
    try: return v.GetWidth(pcbnew.F_Cu if layer is None else layer)
    except TypeError:
        pass
    except Exception:
        pass
    try: return v.GetWidth()
    except Exception:
        return v.GetDrill() * 2
