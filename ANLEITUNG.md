# 🤖 Claudes Picks – Setup mit Archiv & SEO

Automatische wöchentliche AI-Empfehlungen mit durchsuchbarem Archiv.

---

## Was ist neu?

✅ **Archiv-System** – Jede Woche wird gespeichert  
✅ **Durchsuchbar** – Nach Titel, Genre, Streaming-Dienst  
✅ **SEO-optimiert** – Schema.org, Meta-Tags, keyword-reiche URLs  
✅ **Mehr Themen** – 12 verschiedene Themen rotieren  

---

## Dateistruktur

```
epicwatch-picks/
├── .github/workflows/
│   └── generate-picks.yml     ← GitHub Action (Cron)
├── archiv/
│   ├── index.json             ← Übersicht aller Wochen
│   ├── 2026-W16-netflix.json  ← Einzelne Woche
│   ├── 2026-W15-prime.json
│   └── ...
├── generate_picks.py          ← Python Script
├── picks.json                 ← Aktuelle Woche
├── all-picks.json             ← Alle Picks (für Suche)
└── archiv.html                ← Archiv-Seite (SEO)
```

---

## SEO-Vorteile

### 1. Mehr indexierbare Seiten
Jede Woche = neuer Content = neue Keywords:
- "Netflix Geheimtipps April 2026"
- "Prime Video Thriller Empfehlungen"
- "Unterschätzte Serien 2026"

### 2. Long-Tail Keywords
Die 12 rotierenden Themen decken verschiedene Suchanfragen ab:
- "Serien mit Plot-Twists"
- "Kurze Serien zum Bingen"
- "Europäische Serien Netflix"
- "True Crime Serien Prime"
- etc.

### 3. Strukturierte Daten
Die `archiv.html` enthält Schema.org Markup für bessere Google-Snippets.

### 4. Interne Verlinkung
Archiv-Seite verlinkt auf Hauptseite → besserer PageRank-Flow.

---

## Schnellstart

### 1. Claude API Key
```
https://console.anthropic.com
→ API Keys → Create Key
→ $5 Guthaben aufladen
```

### 2. GitHub Repository
```
1. github.com → New Repository
2. Name: epicwatch-picks
3. Private empfohlen
```

### 3. Dateien hochladen
Alle Dateien aus diesem ZIP in dein Repo:
- `.github/workflows/generate-picks.yml`
- `generate_picks.py`
- `picks.json`
- `all-picks.json`
- `archiv/index.json`
- `archiv/2026-W16-netflix.json`

### 4. Secret hinzufügen
```
Repository → Settings → Secrets → Actions
→ New secret
→ Name: ANTHROPIC_API_KEY
→ Value: sk-ant-api03-...
```

### 5. Workflow-Berechtigung
```
Settings → Actions → General
→ Workflow permissions
→ "Read and write permissions" ✓
```

### 6. Testen
```
Actions Tab → Generate AI Recommendations
→ Run workflow
```

---

## In epic.watch einbinden

### Claudes Picks Sektion (Startseite)

Füge in `epicwatch.html` ein:

```html
<!-- Nach dem Hero -->
<section class="picks-section" id="picksSection">
  <div class="picks-container">
    <div class="picks-header">
      <div class="picks-title-row">
        <div class="picks-icon">🤖</div>
        <div>
          <h2 class="picks-title">Claudes Picks</h2>
          <p class="picks-subtitle">Wöchentlich kuratiert von AI</p>
        </div>
      </div>
      <div class="picks-tabs">
        <span class="picks-tab active" id="currentService">Netflix</span>
        <span class="picks-tab" id="nextService">Prime</span>
      </div>
    </div>
    <div class="picks-theme" id="picksTheme"></div>
    <div class="picks-list" id="picksList"></div>
    <div class="picks-footer">
      <span id="picksDate"></span>
      <a href="archiv.html" class="archive-link">Alle Empfehlungen →</a>
    </div>
  </div>
</section>
```

### JavaScript

```javascript
// URL anpassen!
const PICKS_URL = 'https://raw.githubusercontent.com/DEIN-USERNAME/epicwatch-picks/main/picks.json';

async function loadPicks() {
  try {
    const res = await fetch(PICKS_URL);
    const data = await res.json();
    
    document.getElementById('currentService').textContent = data.service;
    document.getElementById('nextService').textContent = data.next_service;
    document.getElementById('picksTheme').innerHTML = 
      `<strong>Diese Woche:</strong> ${data.theme}`;
    
    document.getElementById('picksList').innerHTML = data.picks.map(p => `
      <div class="pick-card">
        <span class="pick-rank">${p.rank}</span>
        <div class="pick-info">
          <div class="pick-title">${p.title} <span>(${p.year})</span></div>
          <div class="pick-desc">${p.description}</div>
        </div>
        <div class="pick-meta">
          <span class="pick-genre">${p.genre}</span>
          <span class="pick-rating">★ ${p.rating}</span>
        </div>
      </div>
    `).join('');
    
    document.getElementById('picksDate').textContent = 
      `Aktualisiert: ${data.date_formatted}`;
  } catch (e) {
    document.getElementById('picksSection').style.display = 'none';
  }
}

loadPicks();
```

### Archiv-Link in Navigation

```html
<a href="archiv.html" class="nav-tab">📚 Archiv</a>
```

---

## Zeitplan

Die Action läuft jeden **Montag um 9:00 UTC** (10:00/11:00 DE).

Anpassen in `.github/workflows/generate-picks.yml`:
```yaml
schedule:
  - cron: '0 9 * * 1'   # Montag
  - cron: '0 9 * * 4'   # + Donnerstag (optional)
```

---

## Themen-Rotation

Das Script rotiert durch 12 Themen:

| Woche | Thema |
|-------|-------|
| 1 | Geheimtipps |
| 2 | Binge-worthy |
| 3 | Plot-Twists |
| 4 | Europa |
| 5 | Slow Burner |
| 6 | Kurz & Knackig |
| 7 | True Crime |
| 8 | Starke Frauen |
| 9 | Thriller |
| 10 | Feel-Good |
| 11 | Visuell |
| 12 | True Stories |

---

## Kosten

| Was | Kosten |
|-----|--------|
| Claude API (1x/Woche) | ~$0.02/Woche |
| GitHub Actions | Kostenlos |
| **Pro Jahr** | **~$1** |

---

## Troubleshooting

### Action läuft nicht
→ Settings → Actions → "Allow all actions"

### Push schlägt fehl
→ Settings → Actions → "Read and write permissions"

### JSON-Fehler
→ Prüfe API-Key und Guthaben auf console.anthropic.com

### Archiv wird nicht aktualisiert
→ Prüfe ob `archiv/` Ordner existiert und committet ist

---

## Optional: Mehr Traffic-Quellen

### RSS-Feed generieren
Füge in `generate_picks.py` hinzu, um einen RSS-Feed zu erstellen:
```python
# RSS für Podcast-Apps und Feed-Reader
```

### Social Media Auto-Post
Erweitere die GitHub Action um einen Tweet/Post mit den neuen Picks.

### Sitemap generieren
Erstelle eine `sitemap.xml` für besseres Google-Crawling.

---

## Fertig! 🎉

Jede Woche:
1. GitHub Action läuft automatisch
2. Claude generiert 5 neue Empfehlungen
3. Picks werden in `picks.json` gespeichert
4. Archiv wird erweitert (`archiv/`)
5. Deine Webseite zeigt automatisch die neuen Inhalte
6. Google indexiert die neuen Seiten

Nach einem Jahr hast du ~50 Wochen × 5 Picks = **250+ Serien-Empfehlungen** für SEO!
