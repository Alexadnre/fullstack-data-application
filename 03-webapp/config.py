# 03-webapp/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis la racine du projet
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"
load_dotenv(ENV_FILE)

# Configuration depuis .env
API_URL = os.getenv("API_URL", "http://localhost:8000")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM", "HS256")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Nom du cookie pour le token JWT
AUTH_COOKIE_NAME = "access_token"

