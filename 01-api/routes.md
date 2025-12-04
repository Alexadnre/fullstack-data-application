# 📚 **API Routes**

## 🔐 **Authentication**

| Méthode  | Route            | Description                                   |
| -------- | ---------------- | --------------------------------------------- |
| **POST** | `/auth/register` | Créer un nouvel utilisateur                   |
| **POST** | `/auth/login`    | Authentifier un utilisateur et générer un JWT |
| **POST** | `/auth/refresh`  | Rafraîchir le token d'accès                   |
| **GET**  | `/auth/me`       | Obtenir les informations du user connecté     |

---

## 👤 **Users**

| Méthode    | Route              | Description                            |
| ---------- | ------------------ | -------------------------------------- |
| **GET**    | `/users`           | Lister tous les utilisateurs *(admin)* |
| **GET**    | `/users/{user_id}` | Obtenir un utilisateur                 |
| **PATCH**  | `/users/{user_id}` | Modifier un utilisateur                |
| **DELETE** | `/users/{user_id}` | Supprimer un utilisateur               |

---

## 📅 **Events**

| Méthode    | Route                | Description                                          |
| ---------- | -------------------- | ---------------------------------------------------- |
| **GET**    | `/events`            | Liste des événements du user connecté (avec filtres) |
| **POST**   | `/events`            | Créer un événement                                   |
| **GET**    | `/events/{event_id}` | Obtenir un événement spécifique                      |
| **PATCH**  | `/events/{event_id}` | Modifier un événement                                |
| **DELETE** | `/events/{event_id}` | Supprimer un événement                               |

---

## 🔁 **Recurring Events**

*(Si tu implémentes `rrule`)*

| Méthode    | Route                                  | Description                                      |
| ---------- | -------------------------------------- | ------------------------------------------------ |
| **GET**    | `/events/{event_id}/instances`         | Générer les occurrences d’un événement récurrent |
| **POST**   | `/events/{event_id}/exceptions`        | Ajouter une exception à la récurrence            |
| **DELETE** | `/events/{event_id}/exceptions/{date}` | Supprimer une occurrence spécifique              |

---

## 🔍 **Search**

| Méthode | Route            | Description                                                |
| ------- | ---------------- | ---------------------------------------------------------- |
| **GET** | `/events/search` | Recherche avancée (titre, mots-clés, dates, all_day, etc.) |

---

## 📊 **Statistics** *(bonus mais très bien pour ton projet)*

| Méthode | Route                   | Description                         |
| ------- | ----------------------- | ----------------------------------- |
| **GET** | `/stats/events`         | Statistiques globales du calendrier |
| **GET** | `/stats/user/{user_id}` | Statistiques pour un utilisateur    |

---

## 🩺 **Health Check**

| Méthode | Route        | Description                           |
| ------- | ------------ | ------------------------------------- |
| **GET** | `/health`    | Vérifie que l'API est accessible      |
| **GET** | `/health/db` | Vérifie que la base de données répond |

---

# 📌 Notes

* Les routes sensibles (`/events`, `/users`, `/stats`) sont protégées par JWT.
* `/auth/register` et `/auth/login` sont publiques.
* Les routes d'intégration (`/health`, `/health/db`) permettent un monitoring propre pour Docker et CI/CD.
