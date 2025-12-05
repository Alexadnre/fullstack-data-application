# 03-webapp/main.py

import logging
import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import auth, users, calendar
from api_client import APIError
from config import DEBUG

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Calendar WebApp")

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Inclusion des routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(calendar.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirige vers le calendrier ou login."""
    # Vérifier si l'utilisateur est authentifié
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/calendar", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


# ============================================================
# Handlers d'erreur HTTP
# ============================================================

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: HTTPException):
    """Handler pour les erreurs 400."""
    if request.headers.get("accept", "").startswith("text/html"):
        return templates.TemplateResponse(
            "errors/400.html",
            {"request": request, "detail": exc.detail or "Requête invalide."},
            status_code=400,
        )
    return {"detail": exc.detail or "Requête invalide."}


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    """Handler pour les erreurs 401 - redirige vers login."""
    if request.headers.get("accept", "").startswith("text/html"):
        return RedirectResponse(url="/login", status_code=303)
    return {"detail": exc.detail or "Non authentifié."}


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    """Handler pour les erreurs 403."""
    if request.headers.get("accept", "").startswith("text/html"):
        return templates.TemplateResponse(
            "errors/403.html",
            {"request": request, "detail": exc.detail or "Accès interdit."},
            status_code=403,
        )
    return {"detail": exc.detail or "Accès interdit."}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler pour les erreurs 404."""
    if request.headers.get("accept", "").startswith("text/html"):
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "detail": exc.detail or "Page non trouvée."},
            status_code=404,
        )
    return {"detail": exc.detail or "Ressource non trouvée."}


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handler pour les erreurs 500."""
    error_detail = "Erreur interne du serveur."
    if DEBUG:
        error_detail = f"Erreur: {str(exc)}\n\n{traceback.format_exc()}"
        logger.exception("Erreur 500", exc_info=exc)
    else:
        logger.error(f"Erreur 500: {str(exc)}")
    
    if request.headers.get("accept", "").startswith("text/html"):
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request, "detail": error_detail},
            status_code=500,
        )
    return {"detail": error_detail}


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handler pour les erreurs API."""
    if exc.status_code == 401:
        if request.headers.get("accept", "").startswith("text/html"):
            return RedirectResponse(url="/login", status_code=303)
    
    if request.headers.get("accept", "").startswith("text/html"):
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "errors/404.html",
                {"request": request, "detail": exc.detail},
                status_code=404,
            )
        elif exc.status_code == 500:
            return templates.TemplateResponse(
                "errors/500.html",
                {"request": request, "detail": exc.detail},
                status_code=500,
            )
    
    raise HTTPException(status_code=exc.status_code, detail=exc.detail)

