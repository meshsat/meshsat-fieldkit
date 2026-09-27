import json,sys
d=json.load(open('api/calculator_template_sweep_2026-09-25.json'))
MAT={"铜箔":"copper foil","芯板":"core","半固化片":"prepreg"}
want=[tuple(map(float,a.split(','))) for a in sys.argv[1:]]
for r in d['results']:
    q=r['request']; key=(q['plateLayerNumber'],q['plateThickness'],q['cuprumThickness'],q['innerCopperThickness'])
    if tuple(map(float,key)) not in want: continue
    j=json.loads(r['raw'])
    print(f"### calculator request {key} at {r['at_utc']}: {j['body']['total']} templates")
    for t in j['body']['list']:
        tot=0
        print(f"- {t.get('appointName')} (created {t.get('createTime')}, plateThickness {t.get('plateThickness')}, inner {t.get('innerCopperThickness')}, defaultFlag {t.get('defaultFlag')}, urgentState {t.get('urgentState')}, name '{t.get('receptionDisplayName')}')")
        for b in t['basicDataList']:
            m=MAT.get(b.get('material'),b.get('material'))
            if b.get('materialType')==1:
                print(f"    {b.get('layerName') or ''} copper {b.get('materialName')} t={b.get('topConductorThick')}")
                tot+=float(b.get('topConductorThick') or 0)
            elif m=='core':
                print(f"    core {b.get('materialName')} dielectric t={b.get('dielectricThick')} Dk={b.get('dielectricConstant')} (Cu {b.get('topConductorThick')}/{b.get('botConductorThick')})")
                tot+=float(b.get('dielectricThick') or 0)+float(b.get('topConductorThick') or 0)+float(b.get('botConductorThick') or 0)
            else:
                print(f"    {m} {b.get('materialName')} t={b.get('dielectricThick')} Dk={b.get('dielectricConstant')}")
                tot+=float(b.get('dielectricThick') or 0)
        print(f"    sum of listed thicknesses = {tot:.4f} mm")
