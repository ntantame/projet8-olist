# 1. On part d'une image Python légère
FROM python:3.11-slim

# 2. Variables d'environnement pour que Python affiche les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1






# 3. On se place dans le dossier /app du conteneur
WORKDIR /app

# 4. On installe les outils système nécessaires pour PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. On copie le fichier requirements.txt et on installe les packages Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. On copie tout le reste de ton code (Django, templates, static...)
COPY . .

# 7. On expose le port 8000 (celui de Django)
EXPOSE 8000

# 8. La commande pour lancer le serveur quand le conteneur démarre
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]