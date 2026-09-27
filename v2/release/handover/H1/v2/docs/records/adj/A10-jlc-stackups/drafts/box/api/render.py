import json,sys
d=json.load(open('api/impedance_template_sweep_2026-09-25.json'))
def fmt(t):
    rows=[]
    for it in t['iaminationList']:
        c=json.loads(it['content']) if isinstance(it['content'],str) else it['content']
        ty=it['iaminationType']
        if ty==1: rows.append(f"  {c.get('LineLayer')}: {c.get('lineMaterialType')} {c.get('LineThickness')}")
        elif ty==2: rows.append(f"  prepreg {c.get('preMaterialType')} {c.get('preThickness')}")
        elif ty==3:
            rows.append(f"  core block [{c.get('coreBoardRemark')}]: {c.get('coreBoardLayer1')} {c.get('coreBoardMaterialType1')} {c.get('coreBoardThickness1')} | {c.get('coreBoardLayer2')} {c.get('coreBoardMaterialType2')} {c.get('coreBoardThickness2')} | {c.get('coreBoardLayer3')} {c.get('coreBoardMaterialType3')} {c.get('coreBoardThickness3')}")
        else: rows.append(f"  type{ty}: {c}")
    return "\n".join(rows)
want=[tuple(map(float,a.split(','))) for a in sys.argv[1:]]
for r in d['results']:
    q=r['request']; key=(q['stencilLayer'],q['stencilPly'],q['cuprumThickness'],q['insideCuprumThickness'])
    if tuple(map(float,key)) not in want: continue
    j=json.loads(r['raw'])
    print(f"### request {key} at {r['at_utc']}")
    for t in j['data']:
        print(f"{t['sort']}) {t['showName']} (templateName {t['templateName']}, code {t.get('impedanceTemplateCode')}, enable {t['enableFlag']}, default {t['defaultFlag']}, expedited {t['expeditedFlag']}, compressionThickness {t.get('compressionThickness')}, laminationType {t.get('laminationType')}, plateType {t.get('plateType')}, fixedFee {t.get('fixedFee')})")
        print(fmt(t))
