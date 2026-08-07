import time
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# 1. Routes definitie
ROUTES = [
    {"naam": "Tienen-Ingolstadt", "origin": "Tienen, Belgium", "destination": "Ingolstadt, Germany"},
    {"naam": "Ingolstadt-Bohinj", "origin": "Ingolstadt, Germany", "destination": "Bohinj, Slovenia"},
    {"naam": "Kobarid-Tienen", "origin": "Kobarid, Slovenia", "destination": "Tienen, Belgium"}
]

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
leesbare_datum = now.strftime("%d-%m-%Y om %H:%M")

def update_main_index():
    """ Maak een hoofd-index.html aan in /screenshots/ met links naar alle routes """
    main_html_path = os.path.join("screenshots", "index.html")
    
    route_cards = ""
    for item in ROUTES:
        naam = item["naam"]
        route_cards += f"""
        <a href="./{naam}/index.html" class="card">
            <h2>🚗 {naam}</h2>
            <p>Klik hier voor de volledige verkeershistorie en screenshots.</p>
            <span class="btn">Bekijk historie &rarr;</span>
        </a>"""

    html_content = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Maps Verkeersdashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 30px; background-color: #f4f6f8; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #1a73e8; margin-bottom: 5px; }}
        p.subtitle {{ color: #666; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-decoration: none; color: inherit; transition: transform 0.2s, box-shadow 0.2s; display: flex; flex-direction: column; justify-content: space-between; }}
        .card:hover {{ transform: translateY(-4px); box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
        .card h2 {{ margin-top: 0; color: #1a73e8; font-size: 1.2rem; }}
        .card p {{ color: #555; font-size: 0.9rem; line-height: 1.4; }}
        .btn {{ display: inline-block; margin-top: 15px; font-weight: bold; color: #1a73e8; font-size: 0.9rem; }}
        footer {{ margin-top: 40px; text-align: center; color: #888; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 Verkeersdashboard</h1>
        <p class="subtitle">Kies een route om de live reistijden en screenshots te bekijken.</p>
        
        <div class="grid">
            {route_cards}
        </div>

        <footer>Automatisch bijgewerkt via GitHub Actions</footer>
    </div>
</body>
</html>"""

    with open(main_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def update_html_index(folder, naam, timestamp, leesbare_datum, reistijd, img_filename):
    """ Maak of update de index.html per route-submap """
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f6f8; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
        h1 {{ color: #1a73e8; margin: 0; }}
        .back-link {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
        .back-link:hover {{ text-decoration: underline; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background-color: #1a73e8; color: white; font-weight: 600; }}
        tr:hover {{ background-color: #f8f9fa; }}
        a.btn-img {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
        a.btn-img:hover {{ text-decoration: underline; }}
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

# Hoofdmap aanmaken & Hoofd-index genereren
os.makedirs("screenshots", exist_ok=True)
update_main_index()

# Playwright Browser Automatisering
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='nl-NL'
    )
    page = context.new_page()

    for item in ROUTES:
        folder = os.path.join("screenshots", item['naam'])
        os.makedirs(folder, exist_ok=True)

        url = f"https://www.google.com/maps/dir/?api=1&origin={item['origin']}&destination={item['destination']}&travelmode=driving"
        print(f"Openen van {item['naam']}...")
        
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Cookie consent afhandeling
        try:
            page.wait_for_selector('button[aria-label="Alles accepteren"], button:has-text("Alles accepteren"), button:has-text("Accept all"), form[action*="consent"] button', timeout=8000)
            cookie_btn = page.locator('button[aria-label="Alles accepteren"], button:has-text("Alles accepteren"), button:has-text("Accept all"), form[action*="consent"] button').first
            if cookie_btn.is_visible():
                cookie_btn.click()
                print("Cookies geaccepteerd via klik.")
            else:
                page.evaluate("() => { const banner = document.querySelector('form[action*=\"consent\"], div[class*=\"consent\"]'); if(banner) banner.remove(); }")
        except Exception:
            page.evaluate("() => { const banner = document.querySelector('form[action*=\"consent\"], div[class*=\"consent\"]'); if(banner) banner.remove(); }")

        # Wachten tot de route en kaart geladen zijn
        try:
            page.wait_for_selector('div.Eg5bL, .k9LqX, div[class*="directions-route"]', timeout=12000)
        except Exception:
            pass

        time.sleep(12) 

        # Slimme reistijd-uitlezing
        reistijd_tekst = "Reistijd onbekend"
        try:
            candidates = page.locator('div[aria-label*="uur"], div[aria-label*="min"], span:has-text("uur"), span:has-text("min")').all()
            for cand in candidates:
                txt = cand.inner_text().strip()
                if re.search(r'\d+\s*(uur|u|min)', txt, re.IGNORECASE):
                    reistijd_tekst = txt.replace('\n', ' ')
                    break
        except Exception as e:
            print(f"Fout bij ophalen reistijd: {e}")

        # Screenshot opslaan
        img_filename = f"{timestamp}_{item['naam']}.png"
        img_path = os.path.join(folder, img_filename)
        page.screenshot(path=img_path)
        print(f"Opgeslagen: {img_path}")

        # Submap HTML bijwerken
        update_html_index(folder, item['naam'], timestamp, leesbare_datum, reistijd_tekst, img_filename)

    browser.close()
