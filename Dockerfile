FROM python:3.11-slim

# Installer ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Port écouté par Flask/Gunicorn
ENV PORT=8000

# Commande de lancement pour Render
CMD gunicorn -w 2 -b 0.0.0.0:${PORT} app:app
