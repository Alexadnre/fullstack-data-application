FROM python:3.11-slim

# Évite le buffering dans les logs
ENV PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie des dépendances
COPY requirements.txt .

# Install des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le projet (nécessaire si le script importe d'autres modules)
COPY . .

# Commande exécutée au démarrage du conteneur
CMD ["python", "06-remplissage/script_remplissage.py"]
