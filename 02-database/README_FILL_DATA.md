# Données de test pour le calendrier

## 🚀 Méthode recommandée : Via l'API (une seule commande)

### Option 1 : Script Python (recommandé - multiplateforme)

```bash
python scripts/fill_data.py
```

### Option 2 : Script PowerShell (Windows)

```powershell
.\scripts\fill_data.ps1
```

### Option 3 : Script Bash (Linux/Mac/Git Bash)

```bash
bash scripts/fill_data.sh
```

**Ces scripts :**
- ✅ Créent les 2 utilisateurs (Alexandre et Antoine) via l'API
- ✅ Génèrent automatiquement les événements pour la **semaine actuelle** et la **semaine suivante**
- ✅ Calculent les dates dynamiquement
- ✅ Une seule commande à exécuter !

**Configuration :**
- Par défaut, utilise `http://localhost:8000`
- Pour changer l'URL de l'API : `$env:API_URL="http://api:8000"; python scripts/fill_data.py` (Windows) ou `API_URL=http://api:8000 python scripts/fill_data.py` (Linux/Mac)

---

## 📝 Méthode alternative : Via SQL (si vous préférez)

### 1. Générer le fichier SQL

```bash
python scripts/generate_seed_data.py
```

Cela crée le fichier `02-database/calendar_fill_data.sql` avec des dates dynamiques.

### 2. Charger les données dans la base

#### Via Docker

```bash
docker cp 02-database/calendar_fill_data.sql calendar_db:/tmp/
docker compose exec db psql -U postgres -d calendar_db -f /tmp/calendar_fill_data.sql
```

#### Via psql local

```bash
psql -U postgres -d calendar_db -f 02-database/calendar_fill_data.sql
```

## Identifiants de connexion

Une fois les données chargées, vous pouvez vous connecter avec :

- **Alexandre** :
  - Email: `alexandre.videlaine@edu.esiee.fr`
  - Mot de passe: `password123`

- **Antoine** :
  - Email: `antoine.ritz@edu.esiee.fr`
  - Mot de passe: `password123`

## Contenu des données

Le script génère :
- **Semaine actuelle** : Événements pour Alexandre et Antoine
- **Semaine suivante** : Événements pour Alexandre et Antoine
- Types d'événements variés : réunions, sport, formations, journées off, etc.

## Notes

- Les dates sont calculées dynamiquement à chaque exécution du script
- Les hash de mot de passe utilisent PBKDF2-HMAC-SHA256 (même algorithme que l'API)
- Le script utilise `ON CONFLICT DO NOTHING` pour éviter les doublons si vous réexécutez

## Régénérer les données

Si vous voulez régénérer avec de nouvelles dates (par exemple après une semaine) :

```bash
python scripts/generate_seed_data.py
# Puis recharger dans la base (voir étape 2)
```

