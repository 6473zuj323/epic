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

Für jede Serie/Film schreibe:
- Titel
- Erscheinungsjahr  
- Geschätzte IMDb-Bewertung (zwischen 7.0 und 9.0)
- Genre
- AUSFÜHRLICHE Beschreibung (100-150 Wörter): Worum geht es? Was macht die Serie besonders? Warum sollte man einschalten? Beschreibe die Handlung, Atmosphäre und was Zuschauer erwartet.

Antworte AUSSCHLIESSLICH mit JSON, kein anderer Text:
{{"picks":[{{"rank":1,"title":"Titel","year":"2023","rating":8.1,"genre":"Drama","description":"Ausführliche Beschreibung hier mit 100-150 Wörtern..."}}]}}"""

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
        {"rank": 1, "title": "Dark", "year": "2017", "rating": 8.7, "genre": "Sci-Fi Thriller", "description": "In der deutschen Kleinstadt Winden verschwinden Kinder unter mysteriösen Umständen. Was als lokaler Vermisstenfall beginnt, entwickelt sich zu einem generationenübergreifenden Geheimnis, das vier Familien über mehrere Zeitebenen hinweg verbindet. Die Serie verwebt geschickt Zeitreisen mit einem komplexen Familiengeflecht und philosophischen Fragen über Schicksal und freien Willen. Mit seiner düsteren Atmosphäre, den verschachtelten Handlungssträngen und der präzisen deutschen Erzählweise hebt sich Dark deutlich von amerikanischen Produktionen ab. Jede Episode enthüllt neue Puzzleteile, während die Grenzen zwischen Vergangenheit, Gegenwart und Zukunft zunehmend verschwimmen. Perfekt für Zuschauer, die anspruchsvolle Science-Fiction mit emotionaler Tiefe suchen."},
        {"rank": 2, "title": "The Crown", "year": "2016", "rating": 8.6, "genre": "Drama", "description": "Diese aufwendig produzierte Serie gewährt einen intimen Einblick in das Leben von Königin Elizabeth II. und die britische Königsfamilie über mehrere Jahrzehnte. Von ihrer überraschenden Thronbesteigung als junge Frau bis zu den Skandalen der modernen Ära erzählt The Crown von den Spannungen zwischen Pflicht und persönlichem Glück. Die Serie brilliert durch ihre historische Genauigkeit, atemberaubende Kostüme und Kulissen sowie herausragende Schauspielleistungen. Politische Krisen, Familiendramen und die sich wandelnde Rolle der Monarchie in der modernen Welt werden mit bemerkenswerter Nuance dargestellt. Ein Muss für alle, die sich für Geschichte, Politik und die menschliche Seite hinter den royalen Fassaden interessieren."},
        {"rank": 3, "title": "Mindhunter", "year": "2017", "rating": 8.6, "genre": "Krimi", "description": "Basierend auf wahren Begebenheiten folgt Mindhunter zwei FBI-Agenten in den späten 1970er Jahren, die eine revolutionäre Methode entwickeln: Sie interviewen inhaftierte Serienmörder, um deren Psyche zu verstehen und zukünftige Verbrechen zu verhindern. Die Serie von David Fincher ist ein faszinierendes Psychogramm des Bösen, das niemals auf billige Schockeffekte setzt. Stattdessen baut sie langsam eine beklemmende Atmosphäre auf, während die Ermittler tiefer in die Abgründe der menschlichen Psyche eintauchen. Die Verhörsszenen mit realen Serienmördern wie Ed Kemper sind meisterhaft inszeniert und zutiefst verstörend. Für Fans von True Crime und psychologischen Thrillern ist diese Serie ein absolutes Meisterwerk."},
        {"rank": 4, "title": "Ozark", "year": "2017", "rating": 8.5, "genre": "Thriller", "description": "Der Finanzberater Marty Byrde führt ein Doppelleben: Nach außen hin ein respektabler Familienvater, wäscht er in Wahrheit Geld für ein mexikanisches Drogenkartell. Als ein Deal schiefgeht, muss er mit seiner Familie in die Ozarks fliehen und dort ein neues Geldwäsche-Imperium aufbauen. Was folgt, ist ein atemloser Thriller über Macht, Moral und das Überleben um jeden Preis. Jason Bateman und Laura Linney liefern karrieredefinierende Leistungen als Ehepaar, das zunehmend in die Kriminalität abrutscht. Die Serie überzeugt durch ihre düstere Atmosphäre, unvorhersehbare Wendungen und die Frage, wie weit normale Menschen gehen würden, um ihre Familie zu schützen."},
        {"rank": 5, "title": "Better Call Saul", "year": "2015", "rating": 8.9, "genre": "Drama", "description": "Diese brillante Vorgeschichte zu Breaking Bad erzählt den Werdegang des Anwalts Jimmy McGill zu seinem späteren Alter Ego Saul Goodman. Was als scheinbar leichtfüßige Anwaltsserie beginnt, entwickelt sich zu einer tiefgründigen Charakterstudie über Identität, Ambitionen und moralischen Verfall. Bob Odenkirk zeigt in der Hauptrolle eine Bandbreite von Komik bis Tragik, die ihresgleichen sucht. Die Serie nimmt sich Zeit für ihre Figuren und belohnt geduldige Zuschauer mit einer der befriedigendsten Erzählungen des modernen Fernsehens. Mit ihrer cinematografischen Brillanz und dem perfekten Zusammenspiel mit dem Breaking-Bad-Universum setzt sie neue Maßstäbe für Spin-off-Serien."}
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
