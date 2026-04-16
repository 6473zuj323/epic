#!/usr/bin/env python3
"""
Generiert wöchentliche Film/Serien-Empfehlungen via Claude API.
Speichert alle Empfehlungen in einem Archiv für SEO.
"""

import json
import os
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

prompt = f"""Du bist ein Filmkritiker für eine deutsche Streaming-Guide Website.

Gib mir 5 {theme_full} auf {service} (Deutschland).

WICHTIG:
- Nur Titel die AKTUELL ({now.strftime('%B %Y')}) auf {service} Deutschland verfügbar sind
- Keine Mainstream-Hits die jeder kennt
- Kurze, prägnante Beschreibungen (max 25 Wörter)
- IMDb-Bewertung angeben
- Genre angeben

Antworte NUR mit validem JSON in diesem Format:
{{
  "picks": [
    {{
      "rank": 1,
      "title": "Serienname",
      "year": "2023",
      "rating": 8.1,
      "genre": "Thriller",
      "description": "Kurze knackige Beschreibung warum man das schauen sollte."
    }}
  ]
}}"""

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1500,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Response parsen
response_text = message.content[0].text

if "```json" in response_text:
    response_text = response_text.split("```json")[1].split("```")[0]
elif "```" in response_text:
    response_text = response_text.split("```")[1].split("```")[0]

picks_data = json.loads(response_text.strip())

# Eindeutige ID für diese Woche
week_id = f"{year}-W{week_number:02d}"
date_formatted = now.strftime("%d. %B %Y").replace("January", "Januar").replace("February", "Februar").replace("March", "März").replace("April", "April").replace("May", "Mai").replace("June", "Juni").replace("July", "Juli").replace("August", "August").replace("September", "September").replace("October", "Oktober").replace("November", "November").replace("December", "Dezember")

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
