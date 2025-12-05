#!/usr/bin/env python3
"""
Script pour générer des données de test pour le calendrier.
Génère des événements pour la semaine actuelle et la suivante.
"""

from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import base64
import os

ROOT_DIR = Path(__file__).resolve().parents[1]


def hash_password(password: str, iterations: int = 600_000) -> str:
    """
    Hash un mot de passe en utilisant PBKDF2-HMAC-SHA256.
    Même algorithme que dans 04-authentication/security.py
    """
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(dk).decode("utf-8")
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"


# La fonction hash_password est importée depuis security


def get_week_start(date: datetime) -> datetime:
    """Retourne le lundi de la semaine pour une date donnée."""
    days_since_monday = date.weekday()
    return date - timedelta(days=days_since_monday)


def generate_sql():
    """Génère le SQL pour remplir la base de données."""
    
    # Date actuelle
    now = datetime.now()
    current_week_start = get_week_start(now)
    next_week_start = current_week_start + timedelta(days=7)
    
    # Hash des mots de passe (même mot de passe pour les deux : "password123")
    password_hash_alexandre = hash_password("password123")
    password_hash_antoine = hash_password("password123")
    
    sql = f"""-- ============================================================
-- Calendar Project - Données de test générées
-- Généré le {now.strftime("%Y-%m-%d %H:%M:%S")}
-- ============================================================

-- -------------------------
-- USERS
-- -------------------------
-- Note: Ces utilisateurs peuvent être créés via l'API /auth/register
-- ou insérés directement ici. Les hash sont générés pour le mot de passe "password123"

INSERT INTO users (email, password_hash, display_name, timezone)
VALUES
    ('alexandre.videlaine@edu.esiee.fr', '{password_hash_alexandre}', 'Alexandre VIDELAINE', 'Europe/Paris'),
    ('antoine.ritz@edu.esiee.fr', '{password_hash_antoine}', 'Antoine RITZ', 'Europe/Paris')
ON CONFLICT (email) DO NOTHING;

-- -------------------------
-- EVENTS pour Alexandre (user_id = 1) - Semaine actuelle
-- -------------------------
"""
    
    # Événements pour Alexandre - Semaine actuelle
    events_alexandre_current = [
        {
            "title": "Réunion Projet",
            "description": "Discussion avec l'équipe sur les objectifs du sprint.",
            "start": current_week_start.replace(hour=9, minute=0, second=0, microsecond=0),  # Lundi 9h
            "end": current_week_start.replace(hour=10, minute=30, second=0, microsecond=0),
            "all_day": False,
            "location": "Salle 203",
        },
        {
            "title": "Sport",
            "description": "Séance hebdomadaire de musculation.",
            "start": (current_week_start + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0),  # Mercredi 18h
            "end": (current_week_start + timedelta(days=2)).replace(hour=19, minute=30, second=0, microsecond=0),
            "all_day": False,
            "location": "Basic Fit Paris",
        },
        {
            "title": "Code Review",
            "description": "Review du code de la webapp avec l'équipe.",
            "start": (current_week_start + timedelta(days=4)).replace(hour=14, minute=0, second=0, microsecond=0),  # Vendredi 14h
            "end": (current_week_start + timedelta(days=4)).replace(hour=16, minute=0, second=0, microsecond=0),
            "all_day": False,
            "location": "En ligne",
        },
    ]
    
    # Événements pour Alexandre - Semaine suivante
    events_alexandre_next = [
        {
            "title": "Formation FastAPI",
            "description": "Formation sur les bonnes pratiques FastAPI.",
            "start": (next_week_start + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0),  # Mardi 10h
            "end": (next_week_start + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0),
            "all_day": False,
            "location": "Salle 101",
        },
        {
            "title": "Sport",
            "description": "Séance hebdomadaire de musculation.",
            "start": (next_week_start + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0),  # Mercredi 18h
            "end": (next_week_start + timedelta(days=2)).replace(hour=19, minute=30, second=0, microsecond=0),
            "all_day": False,
            "location": "Basic Fit Paris",
        },
    ]
    
    # Événements pour Antoine - Semaine actuelle
    events_antoine_current = [
        {
            "title": "Journée Off",
            "description": "Day off – repos et détente.",
            "start": (current_week_start + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),  # Mardi toute la journée
            "end": (current_week_start + timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0),
            "all_day": True,
            "location": None,
        },
        {
            "title": "Réunion Client",
            "description": "Présentation des nouvelles fonctionnalités.",
            "start": (current_week_start + timedelta(days=3)).replace(hour=15, minute=0, second=0, microsecond=0),  # Jeudi 15h
            "end": (current_week_start + timedelta(days=3)).replace(hour=17, minute=0, second=0, microsecond=0),
            "all_day": False,
            "location": "Bureau principal",
        },
    ]
    
    # Événements pour Antoine - Semaine suivante
    events_antoine_next = [
        {
            "title": "Workshop Docker",
            "description": "Atelier sur la conteneurisation avec Docker.",
            "start": next_week_start.replace(hour=9, minute=0, second=0, microsecond=0),  # Lundi 9h
            "end": next_week_start.replace(hour=17, minute=0, second=0, microsecond=0),
            "all_day": False,
            "location": "Salle de formation",
        },
        {
            "title": "Déjeuner Équipe",
            "description": "Déjeuner avec toute l'équipe.",
            "start": (next_week_start + timedelta(days=4)).replace(hour=12, minute=30, second=0, microsecond=0),  # Vendredi 12h30
            "end": (next_week_start + timedelta(days=4)).replace(hour=14, minute=0, second=0, microsecond=0),
            "all_day": False,
            "location": "Restaurant Le Jardin",
        },
    ]
    
    # Générer les INSERT pour les événements
    all_events = [
        (1, events_alexandre_current),
        (1, events_alexandre_next),
        (2, events_antoine_current),
        (2, events_antoine_next),
    ]
    
    sql += "INSERT INTO events (user_id, title, description, start_datetime, end_datetime, all_day, location, rrule, status)\nVALUES\n"
    
    values = []
    for user_id, events in all_events:
        for event in events:
            # Formater les dates pour PostgreSQL TIMESTAMPTZ
            # Utiliser le timezone Europe/Paris (+01:00 ou +02:00 selon l'heure d'été)
            # Pour simplifier, on utilise +01:00
            start_str = event["start"].strftime("%Y-%m-%d %H:%M:%S+01:00")
            end_str = event["end"].strftime("%Y-%m-%d %H:%M:%S+01:00")
            
            # Échapper les apostrophes dans les chaînes
            title = event['title'].replace("'", "''")
            description = event['description'].replace("'", "''")
            if event["location"]:
                location_escaped = event['location'].replace("'", "''")
                location = f"'{location_escaped}'"
            else:
                location = "NULL"
            
            values.append(
                f"    ({user_id}, '{title}', '{description}', "
                f"'{start_str}'::timestamptz, '{end_str}'::timestamptz, "
                f"{str(event['all_day']).upper()}, {location}, NULL, 'confirmed')"
            )
    
    sql += ",\n".join(values) + ";\n"
    
    sql += f"""
-- -------------------------
-- Informations
-- -------------------------
-- Semaine actuelle: {current_week_start.strftime("%Y-%m-%d")} (Lundi)
-- Semaine suivante: {next_week_start.strftime("%Y-%m-%d")} (Lundi)
-- 
-- Pour se connecter:
-- - Alexandre: alexandre.videlaine@edu.esiee.fr / password123
-- - Antoine: antoine.ritz@edu.esiee.fr / password123
"""
    
    return sql


if __name__ == "__main__":
    sql_content = generate_sql()
    
    # Écrire dans un fichier
    output_file = ROOT_DIR / "02-database" / "calendar_fill_data.sql"
    output_file.write_text(sql_content, encoding="utf-8")
    
    print(f"[OK] Fichier genere: {output_file}")
    print(f"Semaine actuelle: {get_week_start(datetime.now()).strftime('%Y-%m-%d')}")
    print(f"Semaine suivante: {(get_week_start(datetime.now()) + timedelta(days=7)).strftime('%Y-%m-%d')}")
    print("\nPour utiliser ce fichier:")
    print("  psql -U postgres -d calendar_db -f 02-database/calendar_fill_data.sql")
    print("  ou via Docker: docker compose exec db psql -U postgres -d calendar_db -f /docker-entrypoint-initdb.d/calendar_fill_data.sql")

