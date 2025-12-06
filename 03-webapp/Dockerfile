# Utiliser une image Python légère
FROM python:3.11-slim
# Définir le répertoire de travail dans le conteneur
WORKDIR /app
# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copier le code de l'application
COPY app.py .
# Commande pour lancer Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.enableCORS", "false"]