# 01-api/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# On travaille à la racine du projet dans le conteneur
WORKDIR /app

# Dépendances Python (fichier dans `01-api`)
COPY 01-api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# On copie TOUT le projet dans l'image (01-api, 02-database, 04-authentication, etc.)
COPY . /app

# On se place dans le dossier de l'API
WORKDIR /app/01-api

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
