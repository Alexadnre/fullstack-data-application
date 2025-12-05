-- ============================================================
-- Calendar Project - Données de test générées
-- Généré le 2025-12-05 22:45:37
-- ============================================================

-- -------------------------
-- USERS
-- -------------------------
-- Note: Ces utilisateurs peuvent être créés via l'API /auth/register
-- ou insérés directement ici. Les hash sont générés pour le mot de passe "password123"

INSERT INTO users (email, password_hash, display_name, timezone)
VALUES
    ('alexandre.videlaine@edu.esiee.fr', 'pbkdf2_sha256$600000$sQ7kbw4GbMZka91HiTFfQw==$v4kW1Wi8KBuGAMihKtpQCOYULazPt/G5P0nTRIEZjI8=', 'Alexandre VIDELAINE', 'Europe/Paris'),
    ('antoine.ritz@edu.esiee.fr', 'pbkdf2_sha256$600000$pC3zRdYpr2vYkfZTv4mtng==$WMZQp7/PmRAMpMYXuZ1AphqAp0A4wWO4Ua49AfoNuBk=', 'Antoine RITZ', 'Europe/Paris')
ON CONFLICT (email) DO NOTHING;

-- -------------------------
-- EVENTS pour Alexandre (user_id = 1) - Semaine actuelle
-- -------------------------
INSERT INTO events (user_id, title, description, start_datetime, end_datetime, all_day, location, rrule, status)
VALUES
    (1, 'Réunion Projet', 'Discussion avec l''équipe sur les objectifs du sprint.', '2025-12-01 09:00:00+01:00'::timestamptz, '2025-12-01 10:30:00+01:00'::timestamptz, FALSE, 'Salle 203', NULL, 'confirmed'),
    (1, 'Sport', 'Séance hebdomadaire de musculation.', '2025-12-03 18:00:00+01:00'::timestamptz, '2025-12-03 19:30:00+01:00'::timestamptz, FALSE, 'Basic Fit Paris', NULL, 'confirmed'),
    (1, 'Code Review', 'Review du code de la webapp avec l''équipe.', '2025-12-05 14:00:00+01:00'::timestamptz, '2025-12-05 16:00:00+01:00'::timestamptz, FALSE, 'En ligne', NULL, 'confirmed'),
    (1, 'Formation FastAPI', 'Formation sur les bonnes pratiques FastAPI.', '2025-12-09 10:00:00+01:00'::timestamptz, '2025-12-09 12:00:00+01:00'::timestamptz, FALSE, 'Salle 101', NULL, 'confirmed'),
    (1, 'Sport', 'Séance hebdomadaire de musculation.', '2025-12-10 18:00:00+01:00'::timestamptz, '2025-12-10 19:30:00+01:00'::timestamptz, FALSE, 'Basic Fit Paris', NULL, 'confirmed'),
    (2, 'Journée Off', 'Day off – repos et détente.', '2025-12-02 00:00:00+01:00'::timestamptz, '2025-12-02 23:59:59+01:00'::timestamptz, TRUE, NULL, NULL, 'confirmed'),
    (2, 'Réunion Client', 'Présentation des nouvelles fonctionnalités.', '2025-12-04 15:00:00+01:00'::timestamptz, '2025-12-04 17:00:00+01:00'::timestamptz, FALSE, 'Bureau principal', NULL, 'confirmed'),
    (2, 'Workshop Docker', 'Atelier sur la conteneurisation avec Docker.', '2025-12-08 09:00:00+01:00'::timestamptz, '2025-12-08 17:00:00+01:00'::timestamptz, FALSE, 'Salle de formation', NULL, 'confirmed'),
    (2, 'Déjeuner Équipe', 'Déjeuner avec toute l''équipe.', '2025-12-12 12:30:00+01:00'::timestamptz, '2025-12-12 14:00:00+01:00'::timestamptz, FALSE, 'Restaurant Le Jardin', NULL, 'confirmed');

-- -------------------------
-- Informations
-- -------------------------
-- Semaine actuelle: 2025-12-01 (Lundi)
-- Semaine suivante: 2025-12-08 (Lundi)
-- 
-- Pour se connecter:
-- - Alexandre: alexandre.videlaine@edu.esiee.fr / password123
-- - Antoine: antoine.ritz@edu.esiee.fr / password123
