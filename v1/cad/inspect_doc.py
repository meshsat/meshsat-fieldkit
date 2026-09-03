"""Inspect the document hierarchy after loading the STEP."""
import FreeCAD as App
import Import

Import.open("/home/kyriakosp/Downloads/field_kit/field_kit.step")
doc = App.ActiveDocument

# Find anything labeled Case_Base and print its children structure
for o in doc.Objects:
    if getattr(o, "Label", "") == "Case_Base":
        print(f"Case_Base: Type={o.TypeId}, Name={o.Name}")
        if hasattr(o, "Group"):
            print(f"  Group has {len(o.Group)} children:")
            for c in o.Group[:5]:
                print(f"    - {c.Label} ({c.TypeId})")
        if hasattr(o, "OutList"):
            print(f"  OutList has {len(o.OutList)} items:")
            for c in o.OutList[:5]:
                print(f"    - {c.Label} ({c.TypeId})")
        break

# Also check total object breakdown by type
from collections import Counter
types = Counter(o.TypeId for o in doc.Objects)
print(f"\nDoc has {len(doc.Objects)} objects, types breakdown:")
for t, n in types.most_common():
    print(f"  {t}: {n}")

# Pick a Part::Feature and check whether it has Transparency
for o in doc.Objects:
    if "Feature" in o.TypeId:
        vo = o.ViewObject
        props = [p for p in dir(vo) if not p.startswith("_")]
        print(f"\nFirst Part::Feature: {o.Label}  ({o.TypeId})")
        trans = [p for p in props if "rans" in p.lower()]
        print(f"  transparency-related: {trans}")
        break

import sys
sys.exit(0)
