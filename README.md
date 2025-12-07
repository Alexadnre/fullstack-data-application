# E5 DSIA-5102A — Application Fullstack Data : Calendrier collaboratif

## Objectif du projet

Développer une application complète de gestion de calendrier, composée :

- d’une API sécurisée (FastAPI + JWT),
- d’un front Streamlit,
- d’une base PostgreSQL initialisée automatiquement,
- d’un script de seed pour générer utilisateurs + planning,
- d’une suite de tests (pytest).

L’application permet à un utilisateur de s’inscrire, se connecter, et gérer ses propres événements (CRUD complet), dans un environnement Docker reproductible.

---

## Architecture globale

![Architecture](img/Architecture.png)

---

# Modèle de données / UML

Le modèle repose sur deux entités principales : `User` et `Event`, avec une relation 1 → N.

## Diagramme de classes (simplifié)

![Architecture](img/Classes.png)


### Contraintes principales

* `User.email` est unique.
* Suppression en cascade des événements quand un utilisateur est supprimé.
* `start_datetime < end_datetime` obligatoire.
* `status` est libre mais pensé pour : `planned`, `done`, `cancelled`.

---

## Organisation du projet

### 01-api — API FastAPI

* Routes : `auth`, `events`, `health`.
* Gestion d’erreurs.
* Authentification JWT (PyJWT).
* Hash PBKDF2 pour les mots de passe.
* Dockerfile dédié.

### 02-database — Base de données

* Scripts SQL pour la création des tables.
* Seed initiale pour la démo.
* Charge automatique au démarrage du conteneur Postgres.

### 03-webapp — Front Streamlit

* Interface calendrier (vue hebdomadaire).
* Authentification via cookies chiffrés.
* CRUD d’événements via appels API.

### 04-authentication — Sécurité

* Hash PBKDF2-HMAC-SHA256.
* Génération et vérification des JWT.
* Dépendances d’auth pour protéger les routes.

### 05-tests — Tests automatisés

* Tests d’intégration de l’authentification.
* Tests unitaires.

### 06-seed — Script de remplissage

* Génère plusieurs utilisateurs.
* Crée un planning d’événements cohérent sur deux semaines.
* Exécution via Docker Compose.

---

## Stack technique

| Côté     | Technologies                                   |
| -------- | ---------------------------------------------- |
| Backend  | FastAPI, SQLAlchemy, Postgres, PyJWT, Pydantic |
| Front    | Streamlit, FullCalendar                        |
| Sécurité | PBKDF2-HMAC-SHA256, JWT                        |
| Infra    | Docker, Docker Compose, Github                 |
| Tests    | pytest                                         |

## Services et ports

| Service | Port | Description   |
| ------- | ---- | ------------- |
| API     | 8000 | FastAPI + JWT |
| Webapp  | 3000 | Streamlit     |
| DB      | 5432 | PostgreSQL    |

---

## Démarrage rapide

### 1. Prérequis

Docker + Docker Compose.

### 2. Configuration du fichier `.env`

Variables principales :

Par soucis de simplicité, le fichier `.env` est inclus dans le dépôt GitHub.

```env
API_PORT=8000
WEBAPP_PORT=3000

POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...

DATABASE_URL_PROD=postgresql://user:password@calendar_db:5432/dbname

JWT_SECRET_KEY=change-me
JWT_SECRET_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Lancer l’application

```bash
docker compose up --build -d
```

### 4. Exécuter le seed (optionnel)

```bash
docker compose run --rm filler
# ou
docker compose --profile tools run --rm filler
```

### 5. Accéder aux services

* API : [http://localhost:8000/docs](http://localhost:8000/docs)
* Webapp : [http://localhost:3000/](http://localhost:3000/)

---

## Authentification

### Routes principales

| Méthode | Route          | Rôle                                    |
| ------- | -------------- | --------------------------------------- |
| POST    | /auth/register | Création d’un compte utilisateur        |
| POST    | /auth/login    | Authentification et génération d’un JWT |

### En-tête requis pour les routes protégées

```http
Authorization: Bearer <jwt_token>
```

### Spécificités techniques

* Hash PBKDF2-HMAC-SHA256 avec 600 000 itérations.
* Token valable 30 minutes (modifiable via `.env`).
* Pas de refresh tokens pour simplifier le périmètre.

---

## Gestion des erreurs

Format uniforme renvoyé par l’API :

```json
{
  "erreur": {
    "code": "HTTP_401",
    "message": "Authentification requise ou jeton invalide.",
    "details": null
  }
}
```

Erreurs gérées :

* 401 : jeton invalide ou absent.
* 403 : accès refusé.
* 404 : ressource introuvable.
* 422 : données invalides.
* 500 : erreur interne.

---

## Routes `/events`

Fonctionnalités :

* `GET /events` : renvoie les événements de l’utilisateur connecté.
* `POST /events` : création d’un événement.
* `GET /events/{id}` : consultation d’un événement.
* `PUT /events/{id}` : mise à jour.
* `DELETE /events/{id}` : suppression.

L’API filtre systématiquement les événements par `user_id` pour garantir l’isolation des données entre utilisateurs.

---

## Webapp Streamlit

Fonctionnalités principales :

* Authentification via formulaire.
* Stockage du JWT dans des cookies chiffrés.
* Affichage d’un calendrier hebdomadaire :

  * sept colonnes,
  * créneaux de 30 minutes,
  * plage horaire 08h–18h,
  * affichage plein écran.
* CRUD complet des événements :

  * création, modification, suppression,
  * rafraîchissement automatique.

---

## Seed : génération de données

Le script de seed :

* crée plusieurs comptes utilisateurs,
* génère un planning cohérent de deux semaines,
* peut réinitialiser la base pour obtenir un état propre.

Exécution :

```bash
docker compose run --rm filler
```

---

## Tests automatisés

Lancement :

```bash
pytest 05-tests -q
```

Couverture actuelle :

* inscription (`/auth/register`),
* connexion (`/auth/login`),
* erreurs classiques :

  * email déjà utilisé,
  * mot de passe incorrect,
  * token invalide,
  * accès protégé.

Tests à compléter :

* CRUD complet `/events`,
* tests webapp → API,
* tests d’autorisations (403),
* tests end-to-end via Docker.

---

## Choix techniques et limites

### Choix réalisés

* FastAPI pour la rapidité et la documentation automatique.
* Streamlit pour une interface simple et efficace.
* JWT pour authentification stateless.
* PostgreSQL pour une structure robuste.
* Docker pour un environnement reproductible.

### Limites actuelles

* Pas de partage de calendrier entre utilisateurs.
* Validation métier limitée (chevauchement d’événements peu contrôlé).
* Interface Streamlit basique.

---

## Améliorations possibles

* Gestion de droits (lecture seule, partage de calendrier, administrateur).
* Amélioration de l'interface Streamlit (drag & drop, vues supplémentaires).

---

## Lien GitHub

[https://github.com/Alexadnre/fullstack-data-application](https://github.com/Alexadnre/fullstack-data-application)

---

## Contributeurs

* Alexandre Videlaine
* Antoine Ritz