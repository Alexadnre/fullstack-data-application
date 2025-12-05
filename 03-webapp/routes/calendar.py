# 03-webapp/routes/calendar.py

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from dependencies import require_auth
from api_client import api_call, APIError

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


def get_week_range(week_str: str = None):
    """
    Calcule le début et la fin de la semaine (Lundi-Dimanche).
    
    Args:
        week_str: Format "YYYY-WW" ou None pour semaine actuelle
    
    Returns:
        (start_date, end_date) où start_date est le lundi et end_date le dimanche
    """
    if week_str:
        try:
            year, week = map(int, week_str.split("-"))
            # Premier lundi de l'année ISO
            jan4 = datetime(year, 1, 4)
            monday = jan4 - timedelta(days=jan4.weekday())
            start_date = monday + timedelta(weeks=week - 1)
        except:
            start_date = datetime.now()
            start_date = start_date - timedelta(days=start_date.weekday())
    else:
        start_date = datetime.now()
        start_date = start_date - timedelta(days=start_date.weekday())
    
    end_date = start_date + timedelta(days=6)
    return start_date, end_date


@router.get("/calendar", response_class=HTMLResponse)
async def calendar_week(
    request: Request,
    week: str = Query(None),
    user_id: int = Depends(require_auth),
):
    """
    Affiche la vue calendrier hebdomadaire.
    """
    try:
        # Calculer la plage de dates de la semaine
        start_date, end_date = get_week_range(week)
        
        # Récupérer tous les événements (lecture globale)
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Token manquant")
        
        events = await api_call("GET", "/events", token=token)
        
        # S'assurer que events est une liste
        if not isinstance(events, list):
            logger.error(f"Events n'est pas une liste: {type(events)} - {events}")
            events = []
        
        # Filtrer les événements de la semaine
        week_events = []
        for event in events:
            try:
                # Gérer différents formats de date
                start_str = event.get("start_datetime", "")
                end_str = event.get("end_datetime", "")
                
                if not start_str or not end_str:
                    continue
                
                # Normaliser le format de date
                if start_str.endswith("Z"):
                    start_str = start_str.replace("Z", "+00:00")
                if end_str.endswith("Z"):
                    end_str = end_str.replace("Z", "+00:00")
                
                event_start = datetime.fromisoformat(start_str)
                event_end = datetime.fromisoformat(end_str)
                
                # Vérifier si l'événement chevauche la semaine
                if event_start <= end_date and event_end >= start_date:
                    week_events.append(event)
            except (ValueError, KeyError) as e:
                logger.warning(f"Erreur lors du parsing d'un événement: {e} - {event}")
                continue
        
        # Organiser les événements par jour
        days_events = {i: [] for i in range(7)}  # 0 = Lundi, 6 = Dimanche
        
        for event in week_events:
            try:
                start_str = event.get("start_datetime", "")
                if start_str.endswith("Z"):
                    start_str = start_str.replace("Z", "+00:00")
                event_start = datetime.fromisoformat(start_str)
                
                # Calculer le jour de la semaine dans la plage (0 = lundi de la semaine)
                days_diff = (event_start.date() - start_date.date()).days
                if 0 <= days_diff <= 6:
                    days_events[days_diff].append(event)
            except (ValueError, KeyError) as e:
                logger.warning(f"Erreur lors de l'organisation d'un événement: {e}")
                continue
        
        # Calculer les semaines précédente et suivante
        prev_week = (start_date - timedelta(days=7)).strftime("%Y-%W")
        next_week = (start_date + timedelta(days=7)).strftime("%Y-%W")
        current_week = start_date.strftime("%Y-%W")
        
        # Préparer les dates pour chaque jour de la semaine
        week_dates = [(start_date + timedelta(days=i)) for i in range(7)]
        
        # Récupérer la liste des utilisateurs pour afficher les noms
        try:
            users = await api_call("GET", "/users", token=token)
            if isinstance(users, list):
                users_dict = {u.get("id"): u.get("display_name", "Inconnu") for u in users}
            else:
                users_dict = {}
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des utilisateurs: {e}")
            users_dict = {}
        
        return templates.TemplateResponse(
            "calendar/week.html",
            {
                "request": request,
                "start_date": start_date,
                "end_date": end_date,
                "week_dates": week_dates,
                "days_events": days_events,
                "current_week": current_week,
                "prev_week": prev_week,
                "next_week": next_week,
                "current_user_id": user_id,
                "users_dict": users_dict,
            },
        )
    except APIError as e:
        logger.error(f"APIError dans calendar: {e.status_code} - {e.detail}")
        return templates.TemplateResponse(
            "calendar/week.html",
            {
                "request": request,
                "error": e.detail,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=6),
                "week_dates": [datetime.now() + timedelta(days=i) for i in range(7)],
                "days_events": {i: [] for i in range(7)},
                "current_week": datetime.now().strftime("%Y-%W"),
                "prev_week": (datetime.now() - timedelta(days=7)).strftime("%Y-%W"),
                "next_week": (datetime.now() + timedelta(days=7)).strftime("%Y-%W"),
                "current_user_id": user_id,
                "users_dict": {},
            },
            status_code=e.status_code,
        )
    except Exception as e:
        logger.exception(f"Erreur inattendue dans calendar: {e}")
        # Ré-élever l'exception pour que le handler 500 la capture
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

