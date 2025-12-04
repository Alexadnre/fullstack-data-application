# ✅ **Pyramide des Tests – Calendar Project**

---

# 🟩 **1. Tests Unitaires (base – nombreux, rapides)**

### ## **1.1. Modèles SQLAlchemy**

* [ ] Création d’un utilisateur valide
* [ ] Contrainte d’unicité sur l’email
* [ ] Valeurs par défaut (`timezone`, `created_at`, `updated_at`)
* [ ] Hachage du mot de passe
* [ ] Vérification du mot de passe (hash check)

### ## **1.2. Modèle Event**

* [ ] Création d’un event valide
* [ ] Valeurs par défaut (`status = confirmed`, `all_day = False`)
* [ ] Lien user → event (clé étrangère)
* [ ] Cascade delete : suppression d’un user supprime ses events

### ## **1.3. Logique métier / fonctions utilitaires**

* [ ] Génération d’un token JWT
* [ ] Vérification d’un token invalide
* [ ] Parsing / validation de règles de récurrence (si tu implémentes)

### ## **1.4. Validation Pydantic**

* [ ] Email invalide → `422`
* [ ] Format datetime invalide → `422`
* [ ] Champ manquant → `422`

---

# 🟦 **2. Tests d’Intégration (API + vraie DB Docker)**

> ⚠️ Tests lancés avec docker-compose, utilisant *Postgres réel*.

### ## **2.1. API Users**

* [ ] `/auth/register` insère bien un user dans Postgres
* [ ] Email dupliqué → erreur `409` ou `400` dans Postgres
* [ ] `/auth/login` retourne un token valide
* [ ] `/users/me` retourne les informations du user authentifié

### ## **2.2. API Events**

* [ ] Création d’un event stocké dans Postgres
* [ ] Lecture des events d’un utilisateur
* [ ] Mise à jour d’un event
* [ ] Suppression d’un event
* [ ] User A ne peut pas voir les events de user B

### ## **2.3. Sécurité / Auth réelle**

* [ ] Requête sans token → `401`
* [ ] Token invalide → `401`
* [ ] Token expiré (si tu gères) → `401`
* [ ] Event créé avec token d’un autre user → `403`

### ## **2.4. Erreurs HTTP**

* [ ] Route inexistante → `404`
* [ ] Mauvais JSON → `422`
* [ ] Payload vide → `422`

---

# 🔺 **3. Tests End-to-End (E2E – très peu, scénario complet)**

### ## **3.1. Scénario “Créer un compte et ajouter un event”**

* [ ] Register
* [ ] Login
* [ ] Récupération token
* [ ] Création d’un event (auth)
* [ ] Récupérer la liste → event visible
* [ ] Supprimer l’event → vérification après suppression

### ## **3.2. Scénario “Accès interdit”**

* [ ] Essayer d’accéder à `/events` sans token → `401`
* [ ] Essayer de modifier un event d’un autre user → `403`

