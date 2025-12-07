# Conteneur du script de remplissage

Image qui execute `06-seed/script_remplissage.py` pour remplir la base Postgres avec les utilisateurs et evenements par defaut. Les dependances sont declarees dans `06-seed/requirements.txt`.

## Construction et execution
- Construire l'image : `docker compose build filler`
- Executer le remplissage (le conteneur est detruit a la fin) : `docker compose run --rm filler`

Le service utilise `DATABASE_URL_PROD` comme chaine de connexion (definie dans `.env`) et se connecte au Postgres du docker-compose.
