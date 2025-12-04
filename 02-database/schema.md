# Schéma de base de données - Calendar Project

## Table `users`

- `id` (PK, int)
- `email` (string, unique, not null)
- `password_hash` (string, not null)
- `display_name` (string, not null)
- `timezone` (string, not null, défaut: 'Europe/Paris')
- `created_at` (datetime, tz-aware)
- `updated_at` (datetime, tz-aware)

Un `user` possède plusieurs `events`.

---

## Table `events`

- `id` (PK, int)
- `user_id` (FK → users.id, not null, on delete cascade)
- `title` (string, not null)
- `description` (text, nullable)
- `start_datetime` (datetime, tz-aware, not null)
- `end_datetime` (datetime, tz-aware, not null)
- `all_day` (bool, défaut: false)
- `location` (string, nullable)
- `rrule` (text, nullable) — règle de récurrence au format iCalendar (ex: `FREQ=WEEKLY;BYDAY=MO,WE,FR`)
- `status` (string, défaut: 'confirmed') — valeurs possibles: `confirmed`, `tentative`, `cancelled`
- `created_at` (datetime, tz-aware)
- `updated_at` (datetime, tz-aware)
