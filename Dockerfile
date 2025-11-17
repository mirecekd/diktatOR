FROM python:3.12-slim

# Nastavení pracovního adresáře
WORKDIR /app

# Instalace systémových závislostí pro pydub (ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Kopírování requirements
COPY backend/requirements.txt /app/requirements.txt

# Instalace Python závislostí
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování aplikace
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY data/ /app/data/

# Vytvoření adresářů pro data
RUN mkdir -p /app/data/dictations /app/data/audio /app/data/uploads

# Nastavení environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Spuštění aplikace
CMD ["python", "backend/app.py"]
