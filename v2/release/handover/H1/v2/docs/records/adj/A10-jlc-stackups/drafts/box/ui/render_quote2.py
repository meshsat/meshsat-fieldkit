import json, datetime, re
from playwright.sync_api import sync_playwright
log=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1400,"height":1600})
    def on_resp(r):
        if "getImpedanceTemplateSettings" in r.url:
            try: body=r.text()
            except Exception as e: body=repr(e)
            log.append({"url":r.url,"status":r.status,"request_post_data":r.request.post_data,"at_utc":datetime.datetime.utcnow().isoformat()+"Z","body":body})
    pg.on("response", on_resp)
    pg.goto("https://cart.jlcpcb.com/quote", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(8000)
    lay=pg.locator("xpath=//*[normalize-space(text())='Layers']/ancestor::*[self::div][1]/..").first
    lay.locator("button", has_text=re.compile(r"^\s*8\s*$")).first.click(); pg.wait_for_timeout(3000)
    row=pg.locator("xpath=//*[normalize-space(text())='Specify Stackup']/ancestor::*[self::div][1]/..").first
    y=row.locator("button", has_text=re.compile(r"^\s*Yes\s*$"))
    print("specify-stackup yes buttons:", y.count())
    if y.count(): y.first.click(); pg.wait_for_timeout(5000)
    t=pg.inner_text("body")
    open("ui/quote_8L_specify_stackup_2026-09-25.txt","w").write(t)
    el=row
    try:
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(800)
        box=el.bounding_box()
        pg.screenshot(path="ui/quote_8L_specify_stackup_2026-09-25.png", clip={"x":0,"y":max(0,box["y"]-600),"width":1400,"height":1200} if box else None)
    except Exception as e:
        print("shot err", e); pg.screenshot(path="ui/quote_8L_specify_stackup_2026-09-25.png")
    b.close()
json.dump(log, open("ui/quote_8L_specify_xhr_2026-09-25.json","w"), indent=1)
print("xhr:", [(l["status"], l["request_post_data"]) for l in log])
