#!/bin/bash
# Script pour remplir la base de données via l'API avec curl
# Usage: ./scripts/fill_data.sh

API_URL="${API_URL:-http://localhost:8000}"

echo "🚀 Génération des données de test via l'API..."

# Calculer les dates (semaine actuelle et suivante)
# On utilise Python pour calculer les dates
CURRENT_WEEK_START=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()); print(monday.strftime('%Y-%m-%d'))")
NEXT_WEEK_START=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()) + timedelta(days=7); print(monday.strftime('%Y-%m-%d'))")

echo "📅 Semaine actuelle: $CURRENT_WEEK_START"
echo "📅 Semaine suivante: $NEXT_WEEK_START"

# Créer Alexandre
echo "👤 Création de l'utilisateur Alexandre..."
ALEXANDRE_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alexandre.videlaine@edu.esiee.fr",
    "password": "password123",
    "display_name": "Alexandre VIDELAINE",
    "timezone": "Europe/Paris"
  }')

ALEXANDRE_ID=$(echo $ALEXANDRE_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

# Créer Antoine
echo "👤 Création de l'utilisateur Antoine..."
ANTOINE_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "antoine.ritz@edu.esiee.fr",
    "password": "password123",
    "display_name": "Antoine RITZ",
    "timezone": "Europe/Paris"
  }')

ANTOINE_ID=$(echo $ANTOINE_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "2")

# Obtenir les tokens
echo "🔑 Authentification..."
ALEXANDRE_TOKEN=$(curl -s -X POST "$API_URL/auth/login?email=alexandre.videlaine@edu.esiee.fr&password=password123" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
ANTOINE_TOKEN=$(curl -s -X POST "$API_URL/auth/login?email=antoine.ritz@edu.esiee.fr&password=password123" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ALEXANDRE_TOKEN" ] || [ -z "$ANTOINE_TOKEN" ]; then
  echo "❌ Erreur lors de l'authentification"
  exit 1
fi

echo "✅ Utilisateurs créés et authentifiés"

# Créer les événements pour Alexandre - Semaine actuelle
echo "📅 Création des événements pour Alexandre (semaine actuelle)..."
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALEXANDRE_TOKEN" \
  -d "{\"user_id\": $ALEXANDRE_ID, \"title\": \"Réunion Projet\", \"description\": \"Discussion avec l'équipe sur les objectifs du sprint.\", \"start_datetime\": \"${CURRENT_WEEK_START}T09:00:00+01:00\", \"end_datetime\": \"${CURRENT_WEEK_START}T10:30:00+01:00\", \"all_day\": false, \"location\": \"Salle 203\", \"status\": \"confirmed\"}" > /dev/null

CURRENT_WEDNESDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()); print((monday + timedelta(days=2)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALEXANDRE_TOKEN" \
  -d "{\"user_id\": $ALEXANDRE_ID, \"title\": \"Sport\", \"description\": \"Séance hebdomadaire de musculation.\", \"start_datetime\": \"${CURRENT_WEDNESDAY}T18:00:00+01:00\", \"end_datetime\": \"${CURRENT_WEDNESDAY}T19:30:00+01:00\", \"all_day\": false, \"location\": \"Basic Fit Paris\", \"status\": \"confirmed\"}" > /dev/null

CURRENT_FRIDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()); print((monday + timedelta(days=4)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALEXANDRE_TOKEN" \
  -d "{\"user_id\": $ALEXANDRE_ID, \"title\": \"Code Review\", \"description\": \"Review du code de la webapp avec l'équipe.\", \"start_datetime\": \"${CURRENT_FRIDAY}T14:00:00+01:00\", \"end_datetime\": \"${CURRENT_FRIDAY}T16:00:00+01:00\", \"all_day\": false, \"location\": \"En ligne\", \"status\": \"confirmed\"}" > /dev/null

# Créer les événements pour Alexandre - Semaine suivante
echo "📅 Création des événements pour Alexandre (semaine suivante)..."
NEXT_TUESDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()) + timedelta(days=7); print((monday + timedelta(days=1)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALEXANDRE_TOKEN" \
  -d "{\"user_id\": $ALEXANDRE_ID, \"title\": \"Formation FastAPI\", \"description\": \"Formation sur les bonnes pratiques FastAPI.\", \"start_datetime\": \"${NEXT_TUESDAY}T10:00:00+01:00\", \"end_datetime\": \"${NEXT_TUESDAY}T12:00:00+01:00\", \"all_day\": false, \"location\": \"Salle 101\", \"status\": \"confirmed\"}" > /dev/null

NEXT_WEDNESDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()) + timedelta(days=7); print((monday + timedelta(days=2)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALEXANDRE_TOKEN" \
  -d "{\"user_id\": $ALEXANDRE_ID, \"title\": \"Sport\", \"description\": \"Séance hebdomadaire de musculation.\", \"start_datetime\": \"${NEXT_WEDNESDAY}T18:00:00+01:00\", \"end_datetime\": \"${NEXT_WEDNESDAY}T19:30:00+01:00\", \"all_day\": false, \"location\": \"Basic Fit Paris\", \"status\": \"confirmed\"}" > /dev/null

# Créer les événements pour Antoine - Semaine actuelle
echo "📅 Création des événements pour Antoine (semaine actuelle)..."
CURRENT_TUESDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()); print((monday + timedelta(days=1)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ANTOINE_TOKEN" \
  -d "{\"user_id\": $ANTOINE_ID, \"title\": \"Journée Off\", \"description\": \"Day off – repos et détente.\", \"start_datetime\": \"${CURRENT_TUESDAY}T00:00:00+01:00\", \"end_datetime\": \"${CURRENT_TUESDAY}T23:59:59+01:00\", \"all_day\": true, \"location\": null, \"status\": \"confirmed\"}" > /dev/null

CURRENT_THURSDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()); print((monday + timedelta(days=3)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ANTOINE_TOKEN" \
  -d "{\"user_id\": $ANTOINE_ID, \"title\": \"Réunion Client\", \"description\": \"Présentation des nouvelles fonctionnalités.\", \"start_datetime\": \"${CURRENT_THURSDAY}T15:00:00+01:00\", \"end_datetime\": \"${CURRENT_THURSDAY}T17:00:00+01:00\", \"all_day\": false, \"location\": \"Bureau principal\", \"status\": \"confirmed\"}" > /dev/null

# Créer les événements pour Antoine - Semaine suivante
echo "📅 Création des événements pour Antoine (semaine suivante)..."
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ANTOINE_TOKEN" \
  -d "{\"user_id\": $ANTOINE_ID, \"title\": \"Workshop Docker\", \"description\": \"Atelier sur la conteneurisation avec Docker.\", \"start_datetime\": \"${NEXT_WEEK_START}T09:00:00+01:00\", \"end_datetime\": \"${NEXT_WEEK_START}T17:00:00+01:00\", \"all_day\": false, \"location\": \"Salle de formation\", \"status\": \"confirmed\"}" > /dev/null

NEXT_FRIDAY=$(python -c "from datetime import datetime, timedelta; d = datetime.now(); monday = d - timedelta(days=d.weekday()) + timedelta(days=7); print((monday + timedelta(days=4)).strftime('%Y-%m-%d'))")
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ANTOINE_TOKEN" \
  -d "{\"user_id\": $ANTOINE_ID, \"title\": \"Déjeuner Équipe\", \"description\": \"Déjeuner avec toute l'équipe.\", \"start_datetime\": \"${NEXT_FRIDAY}T12:30:00+01:00\", \"end_datetime\": \"${NEXT_FRIDAY}T14:00:00+01:00\", \"all_day\": false, \"location\": \"Restaurant Le Jardin\", \"status\": \"confirmed\"}" > /dev/null

echo ""
echo "✅ Données générées avec succès!"
echo ""
echo "Identifiants de connexion:"
echo "  - Alexandre: alexandre.videlaine@edu.esiee.fr / password123"
echo "  - Antoine: antoine.ritz@edu.esiee.fr / password123"

