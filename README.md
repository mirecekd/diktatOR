# diktátOR

AI aplikace pro procvičování diktátů.

<div align="center">

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mirecekdg)

</div>


## Funkce

- **Generování diktátů**: AI vytvoří věty přiměřené zvolenému ročníku (1-9)
- **TTS diktování**: Český hlas přečte věty s pauzami a opakováním
- **Focení/upload**: Nahrání fotky napsaného diktátu
- **OCR**: Přečtení textu z fotky pomocí Google Gemini Vision API
- **Vyhodnocení**: Detailní analýza chyb a konstruktivní zpětná vazba

## Technologie

### Backend
- Python 3.12
- Flask (API server)
- Google Gemini API (generování vět, OCR, vyhodnocení)
- gtts (Google Text-to-Speech)
- pydub (zpracování audio)
- Pillow (zpracování obrázků)

### Frontend
- HTML5/CSS3/JavaScript (vanilla)
- Canvas API (rotace a úprava fotek)
- Fetch API (komunikace s backendem)

## Instalace a spuštění

### Docker Compose (doporučeno)

Nejjednodušší způsob, jak spustit aplikaci. Aplikace používá **předpřipravený Docker image** z GitHub Container Registry (`ghcr.io/mirecekd/diktator`).

```bash
# 1. Vytvořte .env soubor s API klíčem
cp .env.example .env
# Editujte .env a přidejte váš GEMINI_API_KEY

# 2. Spuštění (automaticky stáhne image z ghcr.io)
docker-compose up -d

# 3. Aplikace běží na http://localhost:5000
```

**Příkazy pro správu:**
```bash
# Zobrazení logů
docker-compose logs -f

# Zastavení
docker-compose down

# Restart
docker-compose restart

# Rebuild po změnách
docker-compose up -d --build
```

### Docker (bez docker-compose)

Pokud nechcete používat docker-compose, můžete použít přímo Docker s **předpřipraveným image z ghcr.io**:

```bash
# 1. Vytvořte .env soubor s API klíčem
cp .env.example .env
# Editujte .env a přidejte váš GEMINI_API_KEY

# 2. Stažení a spuštění kontejneru (používá prebuildený image)
docker run -d \
  --name diktator \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  ghcr.io/mirecekd/diktator:latest

# 3. Aplikace běží na http://localhost:5000
```

**Alternativně - lokální build:**
```bash
# Pokud chcete image sestavit sami
docker build -t diktator .

# Pak spusťte s lokálním tagem
docker run -d \
  --name diktator \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  diktator
```

**Příkazy pro správu:**
```bash
# Zobrazení logů
docker logs -f diktator

# Zastavení a odstranění kontejneru
docker stop diktator
docker rm diktator

# Restart kontejneru
docker restart diktator

# Update na nejnovější verzi z ghcr.io
docker pull ghcr.io/mirecekd/diktator:latest
# Pak stop, rm a znovu run s novým image
```

### Manuální instalace (bez Dockeru)

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
│   ├── ocr_processor.py    # Google Gemini Vision OCR
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

### Environment Variables (.env)
Vytvořte soubor `.env` v rootu projektu:
```
GEMINI_API_KEY=your_api_key_here

# Gemini Models - can be configured separately for each task
GEMINI_DICTATION_MODEL=gemini-2.5-flash
GEMINI_OCR_MODEL=gemini-2.5-flash
GEMINI_EVAL_MODEL=gemini-2.5-flash
```

Získejte API klíč z: https://aistudio.google.com/app/apikey

### Gemini Models
Můžete konfigurovat různé modely pro každý úkol:
- **GEMINI_DICTATION_MODEL**: Generování vět pro diktát
- **GEMINI_OCR_MODEL**: OCR přečtení textu z fotek
- **GEMINI_EVAL_MODEL**: Vyhodnocení diktátu

Výchozí model pro všechny: `gemini-2.5-flash`

### TTS Nastavení
- Google TTS (gtts)
- Jazyk: čeština (cs)
- Pomalá řeč: ANO (slow=True)
- Speed factor: 0.85 (zpomaleno na 85% rychlosti)
- Formát: MP3

## API Endpointy

- `GET /api/health` - Health check
- `POST /api/generate` - Generování vět pro diktát
- `POST /api/dictate` - Vytvoření audio souboru
- `POST /api/upload` - Upload fotky
- `POST /api/evaluate` - Vyhodnocení diktátu
- `GET /api/audio/<filename>` - Stažení audio souboru

## Řešení problémů

### Chybějící API klíč
```bash
# Ujistěte se, že máte .env soubor s GEMINI_API_KEY
cp .env.example .env
# Pak editujte .env a přidejte svůj API klíč
```

### CORS chyby ve frontendu
- Ujistěte se, že Flask server běží
- Zkontrolujte, že CORS je povolený v `app.py`

### Gemini API quota exceeded
- Zkontrolujte využití API na: https://ai.dev/usage?tab=rate-limit
- Model `gemini-2.5-flash` má vyšší kvóty než experimental modely
