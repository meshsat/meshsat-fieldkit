import json, datetime
from playwright.sync_api import sync_playwright
log=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1400,"height":1000})
    def on_resp(r):
        if "getImpedanceTemplateSettings" in r.url:
            try: body=r.text()
            except Exception as e: body=repr(e)
            log.append({"url":r.url,"status":r.status,"request_post_data":r.request.post_data,"at_utc":datetime.datetime.utcnow().isoformat()+"Z","body":body})
    pg.on("response", on_resp)
    pg.goto("https://jlcpcb.com/impedance", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    # the 4-layer section: find its heading and click the '2oz' button that follows 'Outer Copper Weight'
    sec=pg.locator("text=4-Layer Impedance Control Stackup").first
    sec.scroll_into_view_if_needed()
    btns=pg.locator("button", has_text="2oz")
    print("2oz buttons:", btns.count())
    btns.nth(0).click()   # first 2oz is the 4-layer Outer Copper Weight
    pg.wait_for_timeout(5000)
    txt=pg.inner_text("body")
    open("ui/impedance_4L_outer2oz_rendered_2026-09-25.txt","w").write(txt)
    pg.screenshot(path="ui/impedance_4L_outer2oz_2026-09-25.png", full_page=False)
    b.close()
json.dump(log, open("ui/impedance_4L_outer2oz_xhr_2026-09-25.json","w"), indent=1)
print("xhr captured:", len(log), [ (l["status"], l["request_post_data"]) for l in log])
