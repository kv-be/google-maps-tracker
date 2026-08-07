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

def update_html_index(folder, naam, timestamp, leesbare_datum, reistijd, img_filename):
    html_path = os.path.join(folder, "index.html")
    
    # Maak het HTML bestand aan als het nog niet bestaat
    if not os.path.exists(html_path):
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>Historie - {naam}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f6f8; }}
        h1 {{ color: #1a73e8; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #1a73e8; color: white; }}
        tr:hover {{ background-color: #f1f1f1; }}
        a {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Verkeershistorie: {naam}</h1>
    <table>
        <thead>
            <tr>
                <th>Datum & Tijd</th>
                <th>Totale Reistijd / Route</th>
                <th>Screenshot</th>
            </tr>
        </thead>
        <tbody id="data">
        </tbody>
    </table>
</body>
</html>""")

    # Nieuwe rij invoegen bovenaan de tabel
    nieuwe_rij = f'            <tr><td>{leesbare_datum}</td><td><strong>{reistijd}</strong></td><td><a href="{img_filename}" target="_blank">🖼️ Bekijk Screenshot</a></td></tr>\n        <tbody id="data">'
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace('<tbody id="data">', nieuwe_rij)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

# Playwright Browser Automatisering
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='nl-NL' # Dwingt Nederlandse interface van Google Maps af voor reistijden
    )
    page = context.new_page()

    for item in ROUTES:
        # Maak specifieke directory aan per bestemming
        folder = os.path.join("screenshots", item['naam'])
        os.makedirs(folder, exist_ok=True)

        url = f"https://www.google.com/maps/dir/?api=1&origin={item['origin']}&destination={item['destination']}&travelmode=driving"
        print(f"Openen van {item['naam']}...")
        
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Grondige afhandeling van Cookie Consent Dialogs
        time.sleep(3)
        try:
            # Zoek op bekende cookie-knoppen (Nederlands/Engels)
            cookie_btn = page.locator('button:has-text("Alles accepteren"), button:has-text("Accept all"), form[action*="consent"] button').first
            if cookie_btn.is_visible():
                cookie_btn.click()
                print("Cookies geaccepteerd!")
                time.sleep(3)
        except Exception as e:
            print(f"Geen cookiebanner hoeven inklikken: {e}")

        # Extra wachttijd om de blauwe route + filelijnen volledig te laten tekenen
        time.sleep(8)

        # 2. Probeer de reistijd van het scherm af te lezen
        reistijd_tekst = "Reistijd onbekend"
        try:
            # Google Maps reistijd elementen uitlezen
            time_element = page.locator('div[class*="fontHeadlineLarge"], div.Fk3v1d').first
            if time_element.is_visible():
                reistijd_tekst = time_element.inner_text().replace('\n', ' ')
        except Exception:
            pass

        # 3. Screenshot opslaan in de eigen map
        img_filename = f"{timestamp}_{item['naam']}.png"
        img_path = os.path.join(folder, img_filename)
        page.screenshot(path=img_path)
        print(f"Opgeslagen: {img_path} | Reistijd: {reistijd_tekst}")

        # 4. HTML Index bijwerken
        update_html_index(folder, item['naam'], timestamp, leesbare_datum, reistijd_tekst, img_filename)

    browser.close()
