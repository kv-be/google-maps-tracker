import time
import os
import re
from datetime import datetime
import zoneinfo
from playwright.sync_api import sync_playwright

# 1. Tijdzone voor België/Europa (UTC+2 in zomertijd)
brussels_tz = zoneinfo.ZoneInfo("Europe/Brussels")
now = datetime.now(brussels_tz)
timestamp = now.strftime("%Y-%m-%d_%H-%M")
leesbare_datum = now.strftime("%d-%m-%Y om %H:%M")

# 2. Exacte URLs met inzoom-coördinaten (voorkomt de uitgezoomde Europakaart)
ROUTES = [
    {
        "naam": "Tienen-Ingolstadt", 
        "url": "https://www.google.com/maps/dir/Tienen,+3300,+Belgium/Ingolstadt,+Germany/@49.5,7.5,7z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x47c162f27eb681ed:0x40099ab2f4d5090!2m2!1d4.9376679!2d50.8066223!1m5!1m1!1s0x479e3ec015091ff7:0x421d4b553018220!2m2!1d11.424112!2d48.7665351!3e0?hl=nl"
    },
    {
        "naam": "Ingolstadt-Bohinj", 
        "url": "https://www.google.com/maps/dir/Ingolstadt,+Germany/Bohinj,+Slovenia/@47.3,12.0,7z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x479e3ec015091ff7:0x421d4b553018220!2m2!1d11.424112!2d48.7665351!1m5!1m1!1s0x477a9416bb5a5efd:0x400451368e7f1f0!2m2!1d13.9535313!2d46.2792612!3e0?hl=nl"
    },
    {
        "naam": "Kobarid-Tienen", 
        "url": "https://www.google.com/maps/dir/Kobarid,+Slovenia/Tienen,+3300,+Belgium/@48.0,9.0,6z/data=!3m1!4b1!4m14!4m13!1m5!1m1!1s0x477a33b664d6032d:0x00021b3342672bfd!2m2!1d13.5786487!2d46.2462319!1m5!1m1!1s0x47c162f27eb681ed:0x40099ab2f4d5090!2m2!1d4.9376679!2d50.8066223!3e0?hl=nl"
    }
]

def update_main_index():
    main_html_path = os.path.join("screenshots", "index.html")
    route_cards = ""
    for item in ROUTES:
        naam = item["naam"]
        route_cards += f"""
        <a href="./{naam}/index.html" class="card">
            <h2>🚗 {naam}</h2>
            <p>Klik hier voor de live verkeershistorie en screenshots.</p>
            <span class="btn">Bekijk historie &rarr;</span>
        </a>"""

    html_content = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Maps Verkeersdashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 30px; background-color: #f4f6f8; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #1a73e8; margin-bottom: 5px; }}
        p.subtitle {{ color: #666; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-decoration: none; color: inherit; display: flex; flex-direction: column; justify-content: space-between; }}
        .card:hover {{ transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .card h2 {{ margin-top: 0; color: #1a73e8; }}
        .btn {{ font-weight: bold; color: #1a73e8; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 Verkeersdashboard</h1>
        <p class="subtitle">Kies een route om de historie te bekijken.</p>
        <div class="grid">{route_cards}</div>
    </div>
</body>
</html>"""

    with open(main_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def update_html_index(folder, naam, timestamp, leesbare_datum, reistijd, img_filename):
    html_path = os.path.join(folder, "index.html")
    
    if not os.path.exists(html_path):
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verkeershistorie - {naam}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #f4f6f8; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
        h1 {{ color: #1a73e8; margin: 0; }}
        .back-link {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background-color: #1a73e8; color: white; }}
        tr:hover {{ background-color: #f8f9fa; }}
        a.btn-img {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Verkeershistorie: {naam}</h1>
            <a href="../index.html" class="back-link">&larr; Terug naar overzicht</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Datum & Tijd</th>
                    <th>Totale Reistijd</th>
                    <th>Screenshot</th>
                </tr>
            </thead>
            <tbody id="data">
            </tbody>
        </table>
    </div>
</body>
</html>""")

    nieuwe_rij = f'            <tr><td>{leesbare_datum}</td><td><strong>{reistijd}</strong></td><td><a href="./{img_filename}" target="_blank" class="btn-img">🖼️ Bekijk Screenshot</a></td></tr>\n        <tbody id="data">'
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace('<tbody id="data">', nieuwe_rij)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

os.makedirs("screenshots", exist_ok=True)
update_main_index()

browser = p.chromium.launch(
    channel="chrome",
    headless=True
)


with sync_playwright() as p:
    # 3. GPU Hardwareversnelling voor Chromium
    browser = p.chromium.launch(
        headless=True,
        args=[
            #'--use-gl=angle',
            #'--use-angle=gl-egl',
            #'--ignore-gpu-blocklist',
            '--no-sandbox'
        ]
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='nl-NL',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    )
    
    page = context.new_page()
    # 4. Voorkom algemene timeouts
    page.set_default_timeout(90000)

    for item in ROUTES:
        folder = os.path.join("screenshots", item['naam'])
        os.makedirs(folder, exist_ok=True)

        print(f"Openen van {item['naam']}...")
        
        # 5. wait_until="commit" voorkomt de networkidle crash
        page.goto(item['url'], wait_until="commit")

        # Wacht tot het linkerpaneel in de pagina verschijnt
        try:
            page.wait_for_selector('div[role="main"]', timeout=20000)
        except Exception:
            pass

        # Cookie consent afhandelen
        time.sleep(3)
        try:
            cookie_btn = page.locator('button[aria-label="Alles accepteren"], button:has-text("Alles accepteren"), button:has-text("Accept all"), form[action*="consent"] button').first
            if cookie_btn.is_visible():
                cookie_btn.click()
                print("Cookies geaccepteerd.")
        except Exception:
            pass
            
        # Zekerheids-klik om Google Maps uit een zwevend menu te forceren
        try:
            page.keyboard.press("Enter")
        except:
            pass

        # Geef Google Maps tijd om de routekaarten (WebGL) volledig te renderen
        # time.sleep(12) 
        page.wait_for_function("""
        () => {
            const body = document.body.innerText;
            return /\d+\s*(uur|u|h).*\d+\s*min|\d+\s*min/.test(body);
        }
        """, timeout=60000)
        # Reistijd uitlezen
        reistijd_tekst = "Reistijd onbekend"
        try:
            panel_text = page.locator('div[role="main"]').inner_text()
            matches = re.findall(r'(\d+\s*(?:uur|u|h)\s*\d*\s*(?:min|m)?|\d+\s*min)', panel_text, re.IGNORECASE)
            if matches:
                reistijd_tekst = matches[0].strip()
        except Exception as e:
            print(f"Fout reistijd: {e}")

        # Screenshot opslaan
        page.evaluate("""
        () => {
            window.dispatchEvent(new Event('resize'));
        }
        """)
        
        time.sleep(3)
        img_filename = f"{timestamp}_{item['naam']}.png"
        img_path = os.path.join(folder, img_filename)
        page.screenshot(path=img_path)
        print(f"Opgeslagen: {img_path} | Tijd: {leesbare_datum} | Reistijd: {reistijd_tekst}")

        update_html_index(folder, item['naam'], timestamp, leesbare_datum, reistijd_tekst, img_filename)

    browser.close()
