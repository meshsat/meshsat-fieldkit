import json, time, urllib.request, itertools, datetime, hashlib
URL="https://jlcpcb.com/api/overseas-core-platform/shoppingCart/getImpedanceTemplateSettings"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
out={"url":URL,"method":"POST","fetched_utc_start":datetime.datetime.utcnow().isoformat()+"Z","results":[]}
for L,ply,cu,ic in itertools.product([4,6,8,10],[0.8,1,1.2,1.6,2],[1,2],[0.5,1,2]):
    body={"stencilLayer":L,"stencilPly":ply,"cuprumThickness":cu,"insideCuprumThickness":ic}
    req=urllib.request.Request(URL,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","User-Agent":UA,"Referer":"https://jlcpcb.com/impedance","Origin":"https://jlcpcb.com"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read().decode()
            st=r.status
    except Exception as e:
        raw=None; st=repr(e)
    out["results"].append({"request":body,"status":st,"at_utc":datetime.datetime.utcnow().isoformat()+"Z","raw":raw})
    time.sleep(0.4)
out["fetched_utc_end"]=datetime.datetime.utcnow().isoformat()+"Z"
json.dump(out,open("api/impedance_template_sweep_2026-09-25.json","w"),indent=1)
print("done",len(out["results"]))
