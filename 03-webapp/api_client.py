# 03-webapp/api_client.py

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from config import API_URL


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
) -> Dict[str, Any]:
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
            
            # Gestion des statuts HTTP
            if response.status_code == 401:
                raise APIError(401, "Non authentifié. Veuillez vous reconnecter.")
            elif response.status_code == 403:
                raise APIError(403, "Accès interdit.")
            elif response.status_code == 404:
                raise APIError(404, "Ressource non trouvée.")
            elif response.status_code >= 400:
                # Erreur client ou serveur
                try:
                    error_detail = response.json().get("detail", response.text)
                except:
                    error_detail = response.text
                raise APIError(response.status_code, error_detail)
            
            # Succès
            if response.status_code == 204:  # No Content
                return {}
            
            return response.json()
            
        except httpx.RequestError as e:
            raise APIError(500, f"Erreur de connexion à l'API: {str(e)}")
        except APIError:
            raise
        except Exception as e:
            raise APIError(500, f"Erreur inattendue: {str(e)}")

