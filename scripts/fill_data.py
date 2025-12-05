#!/usr/bin/env python3
"""
Script Python pour remplir la base de données via l'API.
Usage: python scripts/fill_data.py
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")


def get_week_start(date: datetime) -> datetime:
    """Retourne le lundi de la semaine pour une date donnée."""
    days_since_monday = date.weekday()
    return (date - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)


def create_user(email: str, password: str, display_name: str, timezone: str = "Europe/Paris"):
    """Crée un utilisateur via l'API."""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "display_name": display_name,
                "timezone": timezone,
            },
            timeout=10,
        )
        if response.status_code == 201:
            return response.json()["id"]
        elif response.status_code == 400:
            print(f"  [WARN] {display_name} existe deja")
            return None
        else:
            print(f"  [ERREUR] Erreur creation {display_name}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  [ERREUR] Erreur: {e}")
        return None


def get_token(email: str, password: str):
    """Obtient un token JWT via l'API."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            params={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"  [ERREUR] Erreur authentification {email}: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [ERREUR] Erreur: {e}")
        return None


def create_event(token: str, user_id: int, title: str, description: str, start: datetime, end: datetime, all_day: bool, location: str = None):
    """Crée un événement via l'API."""
    try:
        # Formater les dates pour l'API
        start_str = start.strftime("%Y-%m-%dT%H:%M:%S+01:00")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S+01:00")
        
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "start_datetime": start_str,
            "end_datetime": end_str,
            "all_day": all_day,
            "status": "confirmed",
        }
        
        if location:
            data["location"] = location
        
        response = requests.post(
            f"{API_URL}/events",
            json=data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"    [WARN] Erreur creation evenement '{title}': {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"    [WARN] Erreur: {e}")
        return False


def main():
    print("[OK] Generation des donnees de test via l'API...")
    print(f"API URL: {API_URL}\n")
    
    # Calculer les dates
    now = datetime.now()
    current_week_start = get_week_start(now)
    next_week_start = current_week_start + timedelta(days=7)
    
    print(f"Semaine actuelle: {current_week_start.strftime('%Y-%m-%d')} (Lundi)")
    print(f"Semaine suivante: {next_week_start.strftime('%Y-%m-%d')} (Lundi)\n")
    
    # Créer les utilisateurs
    print("Creation des utilisateurs...")
    alexandre_id = create_user(
        "alexandre.videlaine@edu.esiee.fr",
        "password123",
        "Alexandre VIDELAINE",
    )
    antoine_id = create_user(
        "antoine.ritz@edu.esiee.fr",
        "password123",
        "Antoine RITZ",
    )
    
    # Obtenir les tokens
    print("\nAuthentification...")
    alexandre_token = get_token("alexandre.videlaine@edu.esiee.fr", "password123")
    antoine_token = get_token("antoine.ritz@edu.esiee.fr", "password123")
    
    if not alexandre_token or not antoine_token:
        print("[ERREUR] Impossible d'obtenir les tokens. Verifiez que l'API est accessible.")
        sys.exit(1)
    
    # Utiliser des IDs par défaut si les utilisateurs existaient déjà
    if alexandre_id is None:
        alexandre_id = 1
    if antoine_id is None:
        antoine_id = 2
    
    print("[OK] Utilisateurs crees et authentifies\n")
    
    # Créer les événements pour Alexandre - Semaine actuelle
    print("Creation des evenements pour Alexandre (semaine actuelle)...")
    create_event(
        alexandre_token, alexandre_id,
        "Réunion Projet",
        "Discussion avec l'équipe sur les objectifs du sprint.",
        current_week_start.replace(hour=9, minute=0),
        current_week_start.replace(hour=10, minute=30),
        False, "Salle 203"
    )
    create_event(
        alexandre_token, alexandre_id,
        "Sport",
        "Séance hebdomadaire de musculation.",
        (current_week_start + timedelta(days=2)).replace(hour=18, minute=0),
        (current_week_start + timedelta(days=2)).replace(hour=19, minute=30),
        False, "Basic Fit Paris"
    )
    create_event(
        alexandre_token, alexandre_id,
        "Code Review",
        "Review du code de la webapp avec l'équipe.",
        (current_week_start + timedelta(days=4)).replace(hour=14, minute=0),
        (current_week_start + timedelta(days=4)).replace(hour=16, minute=0),
        False, "En ligne"
    )
    
    # Créer les événements pour Alexandre - Semaine suivante
    print("Creation des evenements pour Alexandre (semaine suivante)...")
    create_event(
        alexandre_token, alexandre_id,
        "Formation FastAPI",
        "Formation sur les bonnes pratiques FastAPI.",
        (next_week_start + timedelta(days=1)).replace(hour=10, minute=0),
        (next_week_start + timedelta(days=1)).replace(hour=12, minute=0),
        False, "Salle 101"
    )
    create_event(
        alexandre_token, alexandre_id,
        "Sport",
        "Séance hebdomadaire de musculation.",
        (next_week_start + timedelta(days=2)).replace(hour=18, minute=0),
        (next_week_start + timedelta(days=2)).replace(hour=19, minute=30),
        False, "Basic Fit Paris"
    )
    
    # Créer les événements pour Antoine - Semaine actuelle
    print("Creation des evenements pour Antoine (semaine actuelle)...")
    create_event(
        antoine_token, antoine_id,
        "Journée Off",
        "Day off – repos et détente.",
        (current_week_start + timedelta(days=1)).replace(hour=0, minute=0),
        (current_week_start + timedelta(days=1)).replace(hour=23, minute=59),
        True, None
    )
    create_event(
        antoine_token, antoine_id,
        "Réunion Client",
        "Présentation des nouvelles fonctionnalités.",
        (current_week_start + timedelta(days=3)).replace(hour=15, minute=0),
        (current_week_start + timedelta(days=3)).replace(hour=17, minute=0),
        False, "Bureau principal"
    )
    
    # Créer les événements pour Antoine - Semaine suivante
    print("Creation des evenements pour Antoine (semaine suivante)...")
    create_event(
        antoine_token, antoine_id,
        "Workshop Docker",
        "Atelier sur la conteneurisation avec Docker.",
        next_week_start.replace(hour=9, minute=0),
        next_week_start.replace(hour=17, minute=0),
        False, "Salle de formation"
    )
    create_event(
        antoine_token, antoine_id,
        "Déjeuner Équipe",
        "Déjeuner avec toute l'équipe.",
        (next_week_start + timedelta(days=4)).replace(hour=12, minute=30),
        (next_week_start + timedelta(days=4)).replace(hour=14, minute=0),
        False, "Restaurant Le Jardin"
    )
    
    print("\n[OK] Donnees generees avec succes!")
    print("\nIdentifiants de connexion:")
    print("  - Alexandre: alexandre.videlaine@edu.esiee.fr / password123")
    print("  - Antoine: antoine.ritz@edu.esiee.fr / password123")


if __name__ == "__main__":
    main()

