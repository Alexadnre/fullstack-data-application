# 03-webapp/routes/users.py

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from dependencies import require_auth
from api_client import api_call, APIError

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, user_id: int = Depends(require_auth)):
    """
    Affiche la liste des utilisateurs avec formulaire de création.
    """
    try:
        # Récupérer tous les utilisateurs
        users = await api_call("GET", "/users", token=request.cookies.get("access_token"))
        
        return templates.TemplateResponse(
            "users/list.html",
            {
                "request": request,
                "users": users,
                "current_user_id": user_id,
            },
        )
    except APIError as e:
        return templates.TemplateResponse(
            "users/list.html",
            {
                "request": request,
                "users": [],
                "error": e.detail,
                "current_user_id": user_id,
            },
            status_code=e.status_code,
        )


@router.post("/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(...),
    timezone: str = Form("Europe/Paris"),
    user_id: int = Depends(require_auth),
):
    """
    Crée un nouvel utilisateur via l'API.
    """
    try:
        new_user = await api_call(
            "POST",
            "/auth/register",
            data={
                "email": email,
                "password": password,
                "display_name": display_name,
                "timezone": timezone,
            },
            token=request.cookies.get("access_token"),
        )
        
        # Rafraîchir la liste des utilisateurs
        users = await api_call("GET", "/users", token=request.cookies.get("access_token"))
        
        return templates.TemplateResponse(
            "users/list.html",
            {
                "request": request,
                "users": users,
                "success": f"Utilisateur {new_user['display_name']} créé avec succès.",
                "current_user_id": user_id,
            },
        )
    except APIError as e:
        # Récupérer la liste même en cas d'erreur
        try:
            users = await api_call("GET", "/users", token=request.cookies.get("access_token"))
        except:
            users = []
        
        return templates.TemplateResponse(
            "users/list.html",
            {
                "request": request,
                "users": users,
                "error": e.detail,
                "current_user_id": user_id,
            },
            status_code=e.status_code,
        )

