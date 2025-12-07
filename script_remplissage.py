from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timedelta, date, time

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# ------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT_DIR.parent
API_DIR = PROJECT_ROOT / "01-api"
AUTH_DIR = PROJECT_ROOT / "04-authentication"

for p in (str(API_DIR), str(AUTH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import database
    from models import User, Event
    import security
except Exception as exc:
    print("Failed to import project modules:", exc)
    raise

# ------------------------------------------------------------------
# Data definition
# ------------------------------------------------------------------

USERS = [
    {
        "email": "alexandre@example.com",
        "display_name": "Alexandre",
        "password": "password",
        "timezone": "Europe/Paris",
    },
    {
        "email": "antoine@example.com",
        "display_name": "Antoine",
        "password": "password",
        "timezone": "Europe/Paris",
    },
]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def get_last_monday(today: date | None = None) -> date:
    """
    Renvoie la date du LUNDI PRÉCÉDENT.
    Si on est lundi, renvoie le lundi de la semaine d'avant.
    """
    if today is None:
        today = datetime.utcnow().date()

    weekday = today.weekday()  # 0 = lundi, 6 = dimanche
    days_back = weekday + (7 if weekday == 0 else 0)
    return today - timedelta(days=days_back)


def get_daily_blocks_for_user(user: User) -> dict[int, list[dict]]:
    """
    Retourne, pour chaque jour de la semaine (0 = lundi ... 4 = vendredi),
    la liste des blocs horaires à créer, en fonction du compte.
    """
    email = (user.email or "").lower()

    # Planning pour Alexandre : profil "ingé / projet / sport"
    if "alexandre@" in email:
        return {
            # Lundi
            0: [
                {
                    "title": "Deep work - Matin",
                    "description": "Focus sans interruption (code / archi)",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Projet Calendar - Dev",
                    "description": "Dev features API / Webapp",
                    "start_time": time(14, 0),
                    "end_time": time(18, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Sport - Muscu",
                    "description": "Séance haut du corps",
                    "start_time": time(19, 0),
                    "end_time": time(20, 30),
                    "location": "Salle de sport",
                },
            ],
            # Mardi
            1: [
                {
                    "title": "Révisions DS / IA",
                    "description": "Cours / exos / projets DSIA",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Projet perso / GitHub",
                    "description": "Nettoyage repos, docs, tests",
                    "start_time": time(14, 0),
                    "end_time": time(18, 0),
                    "location": "Bureau",
                },
            ],
            # Mercredi
            2: [
                {
                    "title": "Deep work - Matin",
                    "description": "Bloc de travail concentré (no meeting)",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Intégration / Tests",
                    "description": "Tests unitaires, intégration, e2e",
                    "start_time": time(14, 0),
                    "end_time": time(18, 0),
                    "location": "Bureau",
                },
            ],
            # Jeudi
            3: [
                {
                    "title": "Lecture / Veille techno",
                    "description": "Articles ML / blog posts / docs",
                    "start_time": time(9, 30),
                    "end_time": time(12, 0),
                    "location": "Maison",
                },
                {
                    "title": "Projet Calendar - Front",
                    "description": "UI/UX du calendrier type GAgenda",
                    "start_time": time(14, 0),
                    "end_time": time(18, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Sport - Cardio",
                    "description": "Séance cardio / legs",
                    "start_time": time(19, 0),
                    "end_time": time(20, 0),
                    "location": "Salle de sport",
                },
            ],
            # Vendredi
            4: [
                {
                    "title": "Admin / Organisation",
                    "description": "To-do, planning, tri mails / docs",
                    "start_time": time(9, 0),
                    "end_time": time(11, 0),
                    "location": "Maison",
                },
                {
                    "title": "Refactoring / Clean code",
                    "description": "Refacto du projet, amélioration archi",
                    "start_time": time(11, 0),
                    "end_time": time(13, 0),
                    "location": "Bureau",
                },
                {
                    "title": "Pair programming / Revue de code",
                    "description": "Revue avec Antoine, discussions archi",
                    "start_time": time(14, 0),
                    "end_time": time(17, 30),
                    "location": "Visio",
                },
            ],
        }

    # Planning pour Antoine : profil "cours / révisions / job étudiant"
    if "antoine@" in email:
        return {
            # Lundi
            0: [
                {
                    "title": "Cours - Matin",
                    "description": "Cours magistraux / TD",
                    "start_time": time(8, 30),
                    "end_time": time(12, 0),
                    "location": "Campus",
                },
                {
                    "title": "TP / Projets",
                    "description": "Travaux pratiques / projet de groupe",
                    "start_time": time(14, 0),
                    "end_time": time(17, 0),
                    "location": "Campus",
                },
            ],
            # Mardi
            1: [
                {
                    "title": "Révisions / Exercices",
                    "description": "Exos / annales",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Bibliothèque",
                },
                {
                    "title": "Job étudiant",
                    "description": "Contrat étudiant",
                    "start_time": time(16, 0),
                    "end_time": time(20, 0),
                    "location": "Magasin",
                },
            ],
            # Mercredi
            2: [
                {
                    "title": "Cours - Matin",
                    "description": "Cours / TD",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Campus",
                },
                {
                    "title": "Projet de groupe",
                    "description": "Organisation, tâches, rendu",
                    "start_time": time(14, 0),
                    "end_time": time(18, 0),
                    "location": "Campus",
                },
            ],
            # Jeudi
            3: [
                {
                    "title": "Révisions solo",
                    "description": "Travail perso",
                    "start_time": time(10, 0),
                    "end_time": time(12, 30),
                    "location": "Maison",
                },
                {
                    "title": "Sport / Club",
                    "description": "Sport universitaire / associatif",
                    "start_time": time(17, 0),
                    "end_time": time(19, 0),
                    "location": "Gymnase",
                },
            ],
            # Vendredi
            4: [
                {
                    "title": "Cours - Matin",
                    "description": "Derniers cours de la semaine",
                    "start_time": time(9, 0),
                    "end_time": time(12, 0),
                    "location": "Campus",
                },
                {
                    "title": "Job étudiant",
                    "description": "Décalé du vendredi soir",
                    "start_time": time(16, 0),
                    "end_time": time(20, 0),
                    "location": "Magasin",
                },
            ],
        }

    # Fallback si un autre utilisateur arrive plus tard
    return {
        d: [
            {
                "title": "Focus - Travail",
                "description": "Bloc de travail générique",
                "start_time": time(9, 0),
                "end_time": time(12, 0),
                "location": "Bureau",
            },
            {
                "title": "Tâches / Réunions",
                "description": "Bloc d'après-midi générique",
                "start_time": time(14, 0),
                "end_time": time(17, 0),
                "location": "Bureau",
            },
        ]
        for d in range(5)
    }


def create_timetable_events_for_user(
    user: User,
    start_monday: date,
    weeks: int = 2,
) -> list[Event]:
    """
    Génère un emploi du temps sur `weeks` semaines (jours ouvrés)
    en fonction du profil de l'utilisateur.
    """
    events: list[Event] = []

    daily_blocks_by_weekday = get_daily_blocks_for_user(user)

    for offset in range(weeks * 7):
        current_day = start_monday + timedelta(days=offset)
        weekday = current_day.weekday()  # 0 = lundi, 6 = dimanche

        # On ne remplit que du lundi au vendredi
        if weekday >= 5:
            continue

        blocks = daily_blocks_by_weekday.get(weekday, [])
        for block in blocks:
            start_dt = datetime.combine(current_day, block["start_time"])
            end_dt = datetime.combine(current_day, block["end_time"])

            events.append(
                Event(
                    user_id=user.id,
                    title=block["title"],
                    description=block["description"],
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    all_day=False,
                    location=block["location"],
                    status="confirmed",
                )
            )

    return events


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main() -> int:
    SessionLocal = getattr(database, "SessionLocal", None)
    if SessionLocal is None:
        print("database.SessionLocal not found.")
        return 2

    session = SessionLocal()

    try:
        # Point de départ du planning : lundi précédent
        today = datetime.utcnow().date()
        start_monday = get_last_monday(today)
        weeks = 2

        print(f"📅 Génération de l'emploi du temps à partir du lundi {start_monday} pour {weeks} semaine(s).")

        for u in USERS:
            # Vérifier si l'utilisateur existe déjà
            existing = session.execute(
                select(User).where(User.email == u["email"])
            ).scalar_one_or_none()

            if existing:
                print(f"👤 User already exists: {u['email']}")
                user = existing
            else:
                user = User(
                    email=u["email"],
                    password_hash=security.hash_password(u["password"]),
                    display_name=u["display_name"],
                    timezone=u["timezone"],
                )
                session.add(user)
                session.flush()
                print(f"👤 User created: {user.email}")

            # On supprime d'abord les events dans la fenêtre des 2 semaines
            schedule_start = datetime.combine(start_monday, time.min)
            schedule_end = schedule_start + timedelta(weeks=weeks)

            deleted = (
                session.query(Event)
                .filter(
                    Event.user_id == user.id,
                    Event.start_datetime >= schedule_start,
                    Event.start_datetime < schedule_end,
                )
                .delete(synchronize_session=False)
            )
            if deleted:
                print(f"  🧹 {deleted} events supprimés pour {user.email} dans la plage {schedule_start} → {schedule_end}")

            # Puis on recrée un emploi du temps complet pour ces 2 semaines
            events = create_timetable_events_for_user(user, start_monday, weeks=weeks)
            session.add_all(events)
            print(f"  ✅ {len(events)} events créés pour {user.email}")

        session.commit()
        print("✅ Database successfully populated with 2-week timetable for all users")
        return 0

    except SQLAlchemyError as exc:
        session.rollback()
        print("Database error:", exc)
        return 4
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
