# diktátOR

AI aplikace pro procvičování diktátů.

<div align="center">

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mirecekd)

</div>

## Co je diktátOR?

Inteligentní aplikace pro procvičování pravopisu pomocí diktátů. Systém automaticky generuje věty přiměřené zvolenému ročníku (1-9), přečte je českým hlasem, vyhodnotí napsaný text z fotky a poskytne detailní zpětnou vazbu.

## Jak to funguje?

### 1. Vyberte parametry
- Ročník (1-9) - ovlivňuje obtížnost vět
- Počet vět (5-20)
- Pauza mezi větami (2-10 sekund)

### 2. Generování a diktování
- AI vytvoří věty odpovídající zvolenému ročníku
- Systém přečte věty českým hlasem s pauzami
- Student píše věty na papír

### 3. Nahrání a vyhodnocení
- Nahrajte fotografii napsaného diktátu (focení je dostupné na mobilních zařízeních)
- OCR přečte text z fotky pomocí Google Gemini Vision API
- AI vyhodnotí správnost a poskytne detailní zpětnou vazbu se skóre

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

---

## Instalace a spuštění

> **Poznámka pro Windows:** Všechny příkazy níže obsahují varianty pro Windows (PowerShell/CMD), Linux i Mac. Docker Compose funguje stejně na všech platformách.

### Kterou metodu zvolit?

| Metoda | Obtížnost | Výhody | Pro koho? |
|--------|-----------|--------|-----------|
| **Docker Compose** | Nejjednodušší | Žádná ruční instalace závislostí, funguje všude stejně | **Doporučeno pro všechny** |
| Docker (bez compose) | Střední | Více kontroly, stále izolované prostředí | Pokročilejší uživatelé |
| Manuální instalace | Složité | Plná kontrola, bez Dockeru | Vývojáři, kteří Docker nechtějí |

### Co je Docker a proč ho používat?

**Docker** je nástroj, který umožňuje spouštět aplikace v izolovaných kontejnerech. Výhody:
- Není potřeba instalovat Python, ffmpeg ani jiné závislosti
- Aplikace běží stejně na všech systémech (Windows, Mac, Linux)
- Jednoduchá instalace a aktualizace
- Žádné konflikty s jinými aplikacemi

**Docker Compose** je nástroj pro snadné spouštění Docker aplikací pomocí konfiguračního souboru.

### Instalace Dockeru (pro začátečníky)

**Windows:**
1. Stáhněte **Docker Desktop** z: https://www.docker.com/products/docker-desktop/
2. Spusťte instalátor a postupujte podle instrukcí
3. Po instalaci restartujte počítač
4. Spusťte Docker Desktop (ikona se objeví v systémové liště)
5. Docker Compose je součástí Docker Desktop

**Mac:**
1. Stáhněte **Docker Desktop** z: https://www.docker.com/products/docker-desktop/
2. Přetáhněte Docker.app do složky Applications
3. Spusťte Docker Desktop
4. Docker Compose je součástí Docker Desktop

**Linux (Ubuntu/Debian):**
```bash
# Instalace Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin

# Přidání uživatele do docker skupiny (abyste nemuseli používat sudo)
sudo usermod -aG docker $USER
# Odhlaste se a znovu přihlaste, aby se změna projevila
```

**Ověření instalace:**
```bash
# Zkontrolujte verzi Docker
docker --version

# Zkontrolujte verzi Docker Compose
docker-compose --version
```

> **Tip:** Po instalaci Docker Desktop hledejte ikonu velryby v systémové liště (Windows: pravý dolní roh, Mac: horní lišta). Když je Docker aktivní, ikona je normální. Když Docker nestartuje, ikona je animovaná nebo šedá.

> **Poznámka pro Linux:** Na Linuxu není nutný Docker Desktop. Stačí nainstalovat `docker` a `docker-compose` balíčky přes správce balíčků.

### Docker Compose (doporučeno)

Nejjednodušší způsob, jak spustit aplikaci. Aplikace používá **předpřipravený Docker image** z GitHub Container Registry (`ghcr.io/mirecekd/diktator`).

#### Rychlý start (pro úplné začátečníky)

1. **Nainstalujte Docker Desktop** (viz sekce výše)
2. **Spusťte Docker Desktop** a počkejte, až naběhne (ikona v systémové liště)
3. **Otevřete terminál v této složce:**
   - **Windows:** Pravý klik ve složce → "Otevřít v terminálu" nebo "Open in Windows Terminal"
   - **Mac:** Pravý klik ve složce → Services → "New Terminal at Folder"
   - **Linux:** Pravý klik ve složce → "Open Terminal Here"
4. **Vytvořte .env soubor** a přidejte do něj svůj Gemini API klíč:
   - Zkopírujte soubor `.env.example` a přejmenujte na `.env`
   - Otevřete `.env` v textovém editoru a doplňte váš API klíč
   - Získejte klíč zde: https://aistudio.google.com/app/apikey
5. **Spusťte:** `docker-compose up -d`
6. **Otevřete prohlížeč:** http://localhost:5000

Hotovo!

---

#### Detailní postup

```bash
# 1. Vytvořte .env soubor s API klíčem
# Windows (CMD):
copy .env.example .env

# Linux/Mac:
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
# Windows (CMD):
copy .env.example .env

# Linux/Mac:
cp .env.example .env

# Editujte .env a přidejte váš GEMINI_API_KEY

# 2. Stažení a spuštění kontejneru (používá prebuildený image)
# Windows (PowerShell):
docker run -d `
  --name diktator `
  -p 5000:5000 `
  --env-file .env `
  -v ${PWD}/data:/app/data `
  ghcr.io/mirecekd/diktator:latest

# Windows (CMD):
docker run -d --name diktator -p 5000:5000 --env-file .env -v %cd%/data:/app/data ghcr.io/mirecekd/diktator:latest

# Linux/Mac:
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
# Windows (PowerShell):
docker run -d `
  --name diktator `
  -p 5000:5000 `
  --env-file .env `
  -v ${PWD}/data:/app/data `
  diktator

# Windows (CMD):
docker run -d --name diktator -p 5000:5000 --env-file .env -v %cd%/data:/app/data diktator

# Linux/Mac:
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

---

### Časté dotazy k Dockeru

**Q: Musím mít Docker zapnutý vždy, když chci používat aplikaci?**
A: Ano, Docker Desktop musí běžet, aby aplikace fungovala. Ale můžete ji nastavit, aby se spouštěla automaticky při startu systému.

**Q: Zabírá Docker hodně místa?**
A: Docker Desktop zabere cca 2-3 GB. Samotná aplikace diktátOR zabere ~500 MB. Data (audio, fotky) se ukládají mimo kontejner.

**Q: Můžu Docker používat i pro jiné aplikace?**
A: Ano! Docker je univerzální nástroj. Jakmile ho nainstalujete, můžete spouštět tisíce různých aplikací.

**Q: Jak aplikaci úplně odinstalovat?**
A: Stačí spustit `docker-compose down -v` (smaže i data) nebo jen `docker-compose down` (zachová data). Pak můžete smazat složku projektu.

**Q: Funguje to i offline?**
A: Částečně. Po prvním stažení image funguje Docker offline, ale aplikace potřebuje internet pro Gemini API (generování, OCR, hodnocení).

---

### Manuální instalace (bez Dockeru)

### 1. Příprava virtuálního prostředí

**Windows (PowerShell/CMD):**
```bash
# Vytvoření virtual environment
python -m venv venv

# Aktivace
# PowerShell:
venv\Scripts\Activate.ps1
# CMD:
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
# Vytvoření virtual environment
python -m venv venv

# Aktivace
source venv/bin/activate
```

**Alternativně (s virtualenvwrapper):**
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
# Z kořenového adresáře projektu
cd backend
python app.py
```

Server běží na: `http://localhost:5000`

### 4. Otevření aplikace

V browseru otevřete:
```
http://localhost:5000
```

**To je vše!** Frontend i backend běží na stejném serveru.

## Řešení problémů

### Chybějící API klíč
```bash
# Ujistěte se, že máte .env soubor s GEMINI_API_KEY
# Windows:
copy .env.example .env

# Linux/Mac:
cp .env.example .env

# Pak editujte .env a přidejte svůj API klíč
```

### CORS chyby ve frontendu
- Ujistěte se, že Flask server běží
- Zkontrolujte, že CORS je povolený v `app.py`

### Gemini API quota exceeded
- Zkontrolujte využití API na: https://ai.dev/usage?tab=rate-limit
- Model `gemini-2.5-flash` má vyšší kvóty než experimental modely

### Docker problémy (pro začátečníky)

**Docker Desktop neběží:**
- Ujistěte se, že Docker Desktop je spuštěný (ikona v systémové liště)
- Windows: Možná bude potřeba povolit WSL 2 (Windows Subsystem for Linux)
- Více info: https://docs.docker.com/desktop/troubleshoot/overview/

**"Cannot connect to Docker daemon":**
```bash
# Windows/Mac: Zkontrolujte, že Docker Desktop běží

# Linux: Spusťte Docker službu
sudo systemctl start docker

# Linux: Povolte automatické spuštění
sudo systemctl enable docker
```

**Port 5000 je už používaný:**
```bash
# Změňte port v docker-compose.yml z "5000:5000" na "8080:5000"
# Pak aplikace poběží na http://localhost:8080
```

**Příliš pomalé stahování image:**
- První spuštění může trvat déle (stahuje se ~500MB image)
- Následná spuštění jsou rychlá

**Problémy s přístupem k /data adresářům:**
- Docker Desktop na Windows/Mac: Jděte do Settings → Resources → File Sharing
- Zkontrolujte, že váš projekt je ve sdílené složce

### Windows-specifické problémy

**PowerShell Execution Policy:**
Pokud nemůžete aktivovat virtuální prostředí v PowerShellu:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Cesty v Dockeru:**
- Používejte lomítka `/` v cestách k volumům i na Windows
- Docker Desktop automaticky převede Windows cesty

**WSL 2 není nainstalovaný (Docker Desktop vyžaduje):**
```powershell
# Spusťte v PowerShellu jako administrátor
wsl --install
# Restartujte počítač
```

**ffmpeg v manuální instalaci:**
- Pokud instalujete bez Dockeru na Windows, musíte nainstalovat ffmpeg samostatně
- Stáhněte z: https://ffmpeg.org/download.html
- Přidejte ffmpeg do PATH
