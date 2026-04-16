#!/usr/bin/env python3
"""
Generiert wöchentliche Film/Serien-Empfehlungen via Claude API.
Speichert alle Empfehlungen in einem Archiv für SEO.
"""

import json
import os
import re
from datetime import datetime
from anthropic import Anthropic

# Wochennummer bestimmt den Streaming-Dienst
now = datetime.now()
week_number = now.isocalendar()[1]
year = now.year
is_netflix_week = week_number % 2 == 0

service = "Netflix" if is_netflix_week else "Amazon Prime Video"
next_service = "Prime Video" if is_netflix_week else "Netflix"

# Verschiedene Themen für Abwechslung
themes = [
    ("unterschätzte Serien, die kaum jemand kennt", "Geheimtipps"),
    ("perfekte Serien für einen Binge-Marathon", "Binge-worthy"),
    ("Serien mit überraschenden Plot-Twists", "Plot-Twists"),
    ("europäische Serien-Geheimtipps", "Europa"),
    ("Serien die nach 1-2 Folgen zünden", "Slow Burner"),
    ("beste Serien unter 8 Folgen", "Kurz & Knackig"),
    ("Serien für True Crime Fans", "True Crime"),
    ("Serien mit starken Frauenfiguren", "Starke Frauen"),
    ("beste Thriller-Serien für schlaflose Nächte", "Thriller"),
    ("herzerwärmende Serien für schlechte Tage", "Feel-Good"),
    ("visuell atemberaubende Serien", "Visuell"),
    ("Serien basierend auf wahren Geschichten", "True Stories"),
]

theme_full, theme_short = themes[week_number % len(themes)]

prompt = f"""Empfehle 5 gute {theme_full} die typischerweise auf {service} verfügbar sind.

Für jede Serie gib an:
- Titel
- Erscheinungsjahr  
- Geschätzte IMDb-Bewertung (zwischen 7.0 und 9.0)
- Genre
- Kurze Beschreibung (max 20 Wörter) warum sehenswert

Antworte AUSSCHLIESSLICH mit JSON, kein anderer Text:
{{"picks":[{{"rank":1,"title":"Titel","year":"2023","rating":8.1,"genre":"Drama","description":"Beschreibung hier."}}]}}"""

client = Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1500,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Response parsen - robuster
response_text = message.content[0].text.strip()
print(f"Raw response:\n{response_text}\n")

# Verschiedene Methoden um JSON zu extrahieren
def extract_json(text):
    # Methode 1: Markdown Code-Block
    if "```json" in text:
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    if "```" in text:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # Methode 2: Finde JSON-Objekt mit picks
    match = re.search(r'\{\s*"picks"\s*:\s*\[.*?\]\s*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    
    # Methode 3: Finde erstes { bis letztes }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1:
        return text[first_brace:last_brace+1]
    
    return text

json_text = extract_json(response_text)
print(f"Extracted JSON:\n{json_text}\n")

try:
    picks_data = json.loads(json_text)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    # Fallback: Beispiel-Empfehlungen
    picks_data = {"picks": [
        {"rank": 1, "title": "Dark", "year": "2017", "rating": 8.7, "genre": "Sci-Fi Thriller", "description": "Deutsche Mystery-Serie über Zeitreisen und Familiengeheimnisse in einer Kleinstadt."},
        {"rank": 2, "title": "The Crown", "year": "2016", "rating": 8.6, "genre": "Drama", "description": "Einblick in das Leben der britischen Königsfamilie über mehrere Jahrzehnte."},
        {"rank": 3, "title": "Mindhunter", "year": "2017", "rating": 8.6, "genre": "Krimi", "description": "FBI-Agenten interviewen inhaftierte Serienmörder um neue Fälle zu lösen."},
        {"rank": 4, "title": "Ozark", "year": "2017", "rating": 8.5, "genre": "Thriller", "description": "Ein Finanzberater muss für ein Drogenkartell Geld waschen um zu überleben."},
        {"rank": 5, "title": "Better Call Saul", "year": "2015", "rating": 8.9, "genre": "Drama", "description": "Die Vorgeschichte des Anwalts Saul Goodman aus Breaking Bad."}
    ]}

# Eindeutige ID für diese Woche
week_id = f"{year}-W{week_number:02d}"

# Deutsche Monatsnamen
month_names = {
    "January": "Januar", "February": "Februar", "March": "März",
    "April": "April", "May": "Mai", "June": "Juni",
    "July": "Juli", "August": "August", "September": "September",
    "October": "Oktober", "November": "November", "December": "Dezember"
}
date_formatted = now.strftime("%d. %B %Y")
for en, de in month_names.items():
    date_formatted = date_formatted.replace(en, de)

# Aktuelle Picks
current_picks = {
    "id": week_id,
    "generated": now.isoformat(),
    "date_formatted": date_formatted,
    "week": week_number,
    "year": year,
    "service": service,
    "service_slug": "netflix" if is_netflix_week else "prime",
    "next_service": next_service,
    "theme": theme_full,
    "theme_short": theme_short,
    "picks": picks_data.get("picks", [])
}

# Als aktuelle picks.json speichern
with open("picks.json", "w", encoding="utf-8") as f:
    json.dump(current_picks, f, ensure_ascii=False, indent=2)

# ===== ARCHIV AKTUALISIEREN =====

# Archiv-Ordner erstellen falls nicht vorhanden
os.makedirs("archiv", exist_ok=True)

# Diese Woche als einzelne Datei speichern (für SEO)
archive_filename = f"archiv/{week_id}-{current_picks['service_slug']}.json"
with open(archive_filename, "w", encoding="utf-8") as f:
    json.dump(current_picks, f, ensure_ascii=False, indent=2)

# Archiv-Index laden oder erstellen
archive_index_path = "archiv/index.json"
if os.path.exists(archive_index_path):
    with open(archive_index_path, "r", encoding="utf-8") as f:
        archive_index = json.load(f)
else:
    archive_index = {"weeks": [], "stats": {}}

# Prüfen ob diese Woche schon existiert
existing_ids = [w["id"] for w in archive_index["weeks"]]
if week_id not in existing_ids:
    # Neue Woche hinzufügen
    archive_index["weeks"].insert(0, {
        "id": week_id,
        "date": date_formatted,
        "service": service,
        "service_slug": current_picks["service_slug"],
        "theme": theme_full,
        "theme_short": theme_short,
        "file": f"{week_id}-{current_picks['service_slug']}.json"
    })

# Statistiken aktualisieren
all_picks = []
for week in archive_index["weeks"]:
    week_file = f"archiv/{week['file']}"
    if os.path.exists(week_file):
        with open(week_file, "r", encoding="utf-8") as f:
            week_data = json.load(f)
            all_picks.extend(week_data.get("picks", []))

# Genres zählen
genre_counts = {}
for pick in all_picks:
    genre = pick.get("genre", "Sonstige")
    genre_counts[genre] = genre_counts.get(genre, 0) + 1

archive_index["stats"] = {
    "total_picks": len(all_picks),
    "total_weeks": len(archive_index["weeks"]),
    "genres": genre_counts,
    "last_updated": now.isoformat()
}

# Archiv-Index speichern
with open(archive_index_path, "w", encoding="utf-8") as f:
    json.dump(archive_index, f, ensure_ascii=False, indent=2)

# ===== ALL PICKS DATEI FÜR SUCHE =====

# Alle Picks in einer Datei für Suchfunktion
all_picks_data = {
    "last_updated": now.isoformat(),
    "total": len(all_picks),
    "picks": []
}

for week in archive_index["weeks"]:
    week_file = f"archiv/{week['file']}"
    if os.path.exists(week_file):
        with open(week_file, "r", encoding="utf-8") as f:
            week_data = json.load(f)
            for pick in week_data.get("picks", []):
                all_picks_data["picks"].append({
                    **pick,
                    "week_id": week["id"],
                    "week_date": week["date"],
                    "service": week["service"],
                    "theme": week["theme_short"]
                })

with open("all-picks.json", "w", encoding="utf-8") as f:
    json.dump(all_picks_data, f, ensure_ascii=False, indent=2)

print(f"✅ Generated {len(current_picks['picks'])} picks for {service}")
print(f"   Theme: {theme_full}")
print(f"   Week ID: {week_id}")
print(f"   Archive total: {archive_index['stats']['total_picks']} picks from {archive_index['stats']['total_weeks']} weeks")
