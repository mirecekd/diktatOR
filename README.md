# diktátOR

Inteligentní systém pro procvičování diktátů pomocí AI.

## Funkce

- 🎯 **Generování diktátů**: AI vytvoří věty přiměřené zvolenému ročníku (1-9)
- 🔊 **TTS diktování**: Český hlas přečte věty s pauzami a opakováním
- 📸 **Focení/upload**: Nahrání fotky napsaného diktátu
- 🤖 **OCR**: Přečtení textu z fotky pomocí Claude Vision API
- ✅ **Vyhodnocení**: Detailní analýza chyb a konstruktivní zpětná vazba

## Technologie

### Backend
- Python 3.12
- Flask (API server)
- OpenAI API (Claude Sonnet 4.5 přes playpi4.local:4000)
- edge-tts (Text-to-Speech)
- Pillow (zpracování obrázků)

### Frontend
- HTML5/CSS3/JavaScript (vanilla)
- Canvas API (rotace a úprava fotek)
- Fetch API (komunikace s backendem)

## Instalace a spuštění

### 1. Příprava virtuálního prostředí

```bash
# Vytvoření virtual environment
mkvirtualenv diktator

# Aktivace (pokud není aktivní)
workon diktator
```

### 2. Instalace dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Spuštění Flask serveru

```bash
workon diktator
cd /home/mirdvorak/DEVEL/diktatOR/backend
python app.py
```

Server běží na: `http://localhost:5000`

### 4. Otevření aplikace

V browseru otevřete:
```
http://localhost:5000
```

**To je vše!** Frontend i backend běží na stejném serveru.

## Workflow použití

1. **Nastavení**
   - Vyberte ročník (1-9)
   - Zvolte počet vět (5-20)
   - Nastavte pauzu mezi větami (2-10 sekund)

2. **Generování a diktování**
   - Klikněte na "Vygenerovat diktát"
   - Počkejte na vygenerování textu a audio
   - Přehrajte audio a pište věty na papír

3. **Nahrání fotky**
   - Vyfotěte nebo nahrajte fotografii napsaného diktátu
   - Případně otočte fotku pomocí tlačítka rotace
   - Klikněte na "Vyhodnotit"

4. **Vyhodnocení**
   - Systém přečte text z fotky pomocí OCR
   - AI vyhodnotí správnost a poskytne zpětnou vazbu
   - Zobrazí se skóre a detailní rozbor chyb

## Struktura projektu

```
diktatOR/
├── backend/
│   ├── app.py              # Flask API server
│   ├── dictation.py        # Generování vět pomocí LLM
│   ├── tts_generator.py    # TTS s edge-tts
│   ├── ocr_processor.py    # Claude Vision OCR
│   ├── evaluator.py        # Vyhodnocení diktátu
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Hlavní stránka
│   ├── app.js             # JavaScript logika
│   └── styles.css         # Styling
├── data/
│   ├── dictations/        # Uložené diktáty (JSON)
│   ├── audio/             # MP3 soubory
│   └── uploads/           # Nahrané fotky
└── README.md
```

## Konfigurace

### API Endpoint
Backend používá: `http://playpi4.local:4000/v1`
- Model: `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- API Key: `sk-5OYzLw5vfDWnFw6HZB4vTQ`

### TTS Nastavení
- Hlas: `cs-CZ-AntoninNeural` (český mužský hlas)
- Rychlost: 80% normální rychlosti (rate: -20%)
- Formát: MP3

## API Endpointy

- `GET /api/health` - Health check
- `POST /api/generate` - Generování vět pro diktát
- `POST /api/dictate` - Vytvoření audio souboru
- `POST /api/upload` - Upload fotky
- `POST /api/evaluate` - Vyhodnocení diktátu
- `GET /api/audio/<filename>` - Stažení audio souboru

## Řešení problémů

### Edge-TTS vrací chybu 403
```bash
pip install --upgrade edge-tts
```

### CORS chyby ve frontendu
- Ujistěte se, že Flask server běží
- Zkontrolujte, že CORS je povolený v `app.py`

### Claude API nefunguje
- Ověřte dostupnost `playpi4.local:4000`
- Zkontrolujte API klíč a model

## Autor

Vytvořeno pomocí Cline s využitím Baby Steps™ metodologie.

## Licence

Interní projekt pro osobní použití.
