# 03-webapp/routes/auth.py

from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from config import AUTH_COOKIE_NAME
from api_client import api_call, APIError

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de connexion."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Authentifie l'utilisateur et stocke le token JWT dans un cookie.
    """
    try:
        # Appel à l'API pour obtenir le token (l'API utilise query params)
        response = await api_call(
            "POST",
            "/auth/login",
            params={"email": email, "password": password},
        )
        
        token = response.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token non reçu de l'API.",
            )
        
        # Redirection vers le calendrier avec cookie HttpOnly
        redirect_response = RedirectResponse(url="/calendar", status_code=303)
        redirect_response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=False,  # True en production avec HTTPS
            samesite="lax",
            max_age=1800,  # 30 minutes
        )
        
        return redirect_response
        
    except APIError as e:
        if e.status_code == 401:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Email ou mot de passe incorrect.",
                },
                status_code=401,
            )
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": f"Erreur lors de la connexion: {str(e)}",
            },
            status_code=500,
        )


@router.get("/logout")
async def logout():
    """
    Déconnecte l'utilisateur en supprimant le cookie.
    """
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key=AUTH_COOKIE_NAME)
    return response

