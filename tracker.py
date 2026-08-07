import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# 1. Definieer de routes
ROUTES = [
    {"naam": "Tienen-Ingolstadt", "origin": "Tienen, Belgium", "destination": "Ingolstadt, Germany"},
    {"naam": "Ingolstadt-Bohinj", "origin": "Ingolstadt, Germany", "destination": "Bohinj, Slovenia"},
    {"naam": "Kobarid-Tienen", "origin": "Kobarid, Slovenia", "destination": "Tienen, Belgium"}
]

# Maak een mapje 'screenshots' aan als het nog niet bestaat
os.makedirs("screenshots", exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

with sync_playwright() as p:
    # Start een virtuele browser (HD-scherm)
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    for item in ROUTES:
        url = f"https://www.google.com/maps/dir/?api=1&origin={item['origin']}&destination={item['destination']}&travelmode=driving"
        print(f"Openen van {item['naam']}...")
        
        page.goto(url, wait_until="networkidle")

        # Accepteer automatisch de Google Cookie-melding indien aanwezig
        try:
            page.click('button:has-text("Alles accepteren")', timeout=3000)
        except Exception:
            try:
                page.click('button:has-text("Accept all")', timeout=3000)
            except Exception:
                pass

        # Wacht 6 seconden tot alle rode/oranje filelijnen en reistijden geladen zijn
        time.sleep(6)

        # Sla de screenshot op met unieke datum en tijd
        filename = f"screenshots/{timestamp}_{item['naam']}.png"
        page.screenshot(path=filename)
        print(f"Opgeslagen: {filename}")

    browser.close()
