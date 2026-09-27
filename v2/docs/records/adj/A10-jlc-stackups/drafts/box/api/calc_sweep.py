import json, time, urllib.request, datetime
URL="https://jlcpcb.com/api/jlcTools/impedance/selectPageImpedanceDefaultTemplate"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
out={"url":URL,"method":"POST","note":"endpoint the JLCPCB impedance calculator (https://jlcpcb.com/pcb-impedance-calculator) calls in getTemplateData(), cjs/d66cd4aa6d72db760a00.js","fetched_utc_start":datetime.datetime.utcnow().isoformat()+"Z","results":[]}
combos=[(4,1.6,1,0.5),(4,1.6,2,0.5),(4,1.6,2,1),(4,1.6,2,2),(6,1.6,1,0.5),(8,1.6,1,0.5),(8,1.6,1,1),(8,1.6,2,0.5),(8,1.6,2,1),(8,1.6,2,2),(8,1.6,1,2)]
for L,ply,cu,ic in combos:
    body={"pageNum":1,"pageSize":99999,"plateLayerNumber":L,"plateThickness":ply,"cuprumThickness":cu,"boardType":1,"usePurpose":1,"innerCopperThickness":ic}
    req=urllib.request.Request(URL,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","User-Agent":UA,"Referer":"https://jlcpcb.com/pcb-impedance-calculator","Origin":"https://jlcpcb.com"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: raw=r.read().decode(); st=r.status
    except Exception as e: raw=None; st=repr(e)
    out["results"].append({"request":body,"status":st,"at_utc":datetime.datetime.utcnow().isoformat()+"Z","raw":raw})
    time.sleep(0.5)
json.dump(out,open("api/calculator_template_sweep_2026-09-25.json","w"),indent=1)
for r in out["results"]:
    j=json.loads(r["raw"]); lst=j["body"]["list"]
    print(r["request"]["plateLayerNumber"],r["request"]["plateThickness"],r["request"]["cuprumThickness"],r["request"]["innerCopperThickness"],j["result"],j["body"]["total"],[x.get("appointName") for x in lst])
