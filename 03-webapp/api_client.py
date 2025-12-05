# 03-webapp/api_client.py

import logging
import httpx
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, status

from config import API_URL

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Exception personnalisée pour les erreurs API"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")


async def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, Any], list]:
    """
    Client API centralisé qui gère tous les appels à l'API.
    
    Args:
        method: Méthode HTTP (GET, POST, PUT, DELETE)
        endpoint: Chemin de l'endpoint (ex: "/auth/login", "/events")
        data: Données à envoyer (pour POST/PUT)
        token: Token JWT pour authentification
        params: Paramètres de requête (pour GET)
    
    Returns:
        Réponse JSON de l'API
    
    Raises:
        APIError: En cas d'erreur HTTP
    """
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    logger.debug(f"API Call: {method} {url}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                # POST peut avoir à la fois params (query) et data (body)
                response = await client.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            logger.debug(f"API Response: {response.status_code} for {method} {url}")
            
            # Gestion des statuts HTTP
            if response.status_code == 401:
                logger.warning(f"401 Unauthorized pour {url}")
                raise APIError(401, "Non authentifié. Veuillez vous reconnecter.")
            elif response.status_code == 403:
                logger.warning(f"403 Forbidden pour {url}")
                raise APIError(403, "Accès interdit.")
            elif response.status_code == 404:
                logger.warning(f"404 Not Found pour {url}")
                raise APIError(404, "Ressource non trouvée.")
            elif response.status_code >= 400:
                # Erreur client ou serveur
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", str(error_json))
                except:
                    error_detail = response.text[:200]  # Limiter la taille
                logger.error(f"Erreur {response.status_code} pour {url}: {error_detail}")
                raise APIError(response.status_code, error_detail)
            
            # Succès
            if response.status_code == 204:  # No Content
                return {}
            
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Erreur parsing JSON pour {url}: {e} - Response: {response.text[:200]}")
                raise APIError(500, f"Réponse invalide de l'API: {str(e)}")
            
        except httpx.ConnectError as e:
            logger.error(f"Erreur de connexion à l'API {url}: {e}")
            raise APIError(500, f"Impossible de se connecter à l'API ({API_URL}). Vérifiez que l'API est démarrée.")
        except httpx.TimeoutException as e:
            logger.error(f"Timeout lors de l'appel à {url}: {e}")
            raise APIError(500, f"Timeout lors de l'appel à l'API.")
        except httpx.RequestError as e:
            logger.error(f"Erreur de requête à {url}: {e}")
            raise APIError(500, f"Erreur de connexion à l'API: {str(e)}")
        except APIError:
            raise
        except Exception as e:
            logger.exception(f"Erreur inattendue dans api_call: {e}")
            raise APIError(500, f"Erreur inattendue: {str(e)}")

