import json, datetime, re
from playwright.sync_api import sync_playwright
log=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1400,"height":1400})
    def on_resp(r):
        if "getImpedanceTemplateSettings" in r.url:
            try: body=r.text()
            except Exception as e: body=repr(e)
            log.append({"url":r.url,"status":r.status,"request_post_data":r.request.post_data,"at_utc":datetime.datetime.utcnow().isoformat()+"Z","body":body})
    pg.on("response", on_resp)
    pg.goto("https://cart.jlcpcb.com/quote", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(8000)
    t=pg.inner_text("body")
    open("ui/quote_initial_2026-09-25.txt","w").write(t)
    # find the Layers row and click 8
    lay=pg.locator("xpath=//*[normalize-space(text())='Layers']/ancestor::*[self::div][1]/..").first
    btn=lay.locator("button", has_text=re.compile(r"^\s*8\s*$"))
    print("layer-8 buttons:", btn.count())
    if btn.count(): btn.first.click(); pg.wait_for_timeout(3000)
    # Impedance Control yes
    imp=pg.locator("xpath=//*[contains(normalize-space(.),'Impedance Control') and not(*)]").first
    print("impedance label found:", imp.count())
    yes=pg.locator("xpath=//*[contains(normalize-space(.),'Impedance Control') and not(*)]/ancestor::*[.//button][1]//button[normalize-space(.)='yes' or normalize-space(.)='Yes']")
    print("yes buttons:", yes.count())
    if yes.count(): yes.first.click(); pg.wait_for_timeout(5000)
    t2=pg.inner_text("body")
    open("ui/quote_8L_impedance_2026-09-25.txt","w").write(t2)
    pg.screenshot(path="ui/quote_8L_impedance_2026-09-25.png", full_page=True)
    b.close()
json.dump(log, open("ui/quote_8L_xhr_2026-09-25.json","w"), indent=1)
print("xhr:", [(l["status"], l["request_post_data"]) for l in log])
