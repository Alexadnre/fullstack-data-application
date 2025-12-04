-- ============================================================
-- Calendar Project - Seed Data
-- ============================================================

-- -------------------------
-- USERS
-- -------------------------
INSERT INTO users (email, password_hash, display_name, timezone)
VALUES
    ('alexandre.videlaine@edu.esiee.fr',  'hash_pw_1', 'Alexandre VIDELAINE', 'Europe/Paris'),
    ('antoine.ritz@edu.esiee.fr',    'hash_pw_2', 'Antoine RITZ',   'Europe/Paris');

-- -------------------------
-- EVENTS for Alexandre (user_id = 1)
-- -------------------------
INSERT INTO events (
    user_id, title, description, start_datetime, end_datetime,
    all_day, location, rrule, status
)
VALUES
    (
        1,
        'Réunion Projet',
        'Discussion avec l’équipe sur les objectifs du sprint.',
        '2025-01-10 09:00:00+01',
        '2025-01-10 10:00:00+01',
        FALSE,
        'Salle 203',
        NULL,
        'confirmed'
    ),
    (
        1,
        'Sport',
        'Séance hebdo de musculation.',
        '2025-01-12 18:00:00+01',
        '2025-01-12 19:30:00+01',
        FALSE,
        'Basic Fit Paris',
        'FREQ=WEEKLY;BYDAY=MO,WE,FR',
        'confirmed'
    );

-- -------------------------
-- EVENTS for Antoine (user_id = 2)
-- -------------------------
INSERT INTO events (
    user_id, title, description, start_datetime, end_datetime,
    all_day, location, rrule, status
)
VALUES
    (
        2,
        'Journée Off',
        'Day off – repos et détente.',
        '2025-02-01 00:00:00+01',
        '2025-02-01 23:59:59+01',
        TRUE,
        NULL,
        NULL,
        'confirmed'
    );

