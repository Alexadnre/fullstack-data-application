import os
import requests
import streamlit as st

from datetime import datetime, date, time

from streamlit_calendar import calendar as calendar_component  # composant FullCalendar
from streamlit_cookies_manager import EncryptedCookieManager

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ===================== COOKIES (JWT PERSISTANT) =====================

# ⚠️ change bien COOKIES_PASSWORD en variable d'env en prod
cookies = EncryptedCookieManager(
    prefix="mon-app-calendrier/",
    password=os.environ.get("COOKIES_PASSWORD", "CHANGE-ME"),
)

# On attend que le composant cookies soit prêt
if not cookies.ready():
    st.stop()


def get_auth_from_storage():
    """
    Récupère le token / type depuis les cookies.
    """
    token = cookies.get("jwt_token")
    token_type = cookies.get("token_type") or "bearer"
    return token, token_type


def set_auth_in_storage(token: str, token_type: str = "bearer"):
    """
    Sauvegarde le token en cookie + met à jour la session.
    """
    cookies["jwt_token"] = token
    cookies["token_type"] = token_type
    cookies.save()

    st.session_state["jwt_token"] = token
    st.session_state["token_type"] = token_type
    st.session_state["logged_in"] = True


def clear_auth():
    """
    Supprime le token (cookies + session).
    """
    if "jwt_token" in cookies:
        del cookies["jwt_token"]
    if "token_type" in cookies:
        del cookies["token_type"]
    cookies.save()

    st.session_state.pop("jwt_token", None)
    st.session_state.pop("token_type", None)
    st.session_state["logged_in"] = False


# ===================== UTILITAIRES =====================

def parse_iso_to_date_time(iso_str: str):
    """
    Transforme une chaîne ISO 8601 en (date, time) pour Streamlit.
    Si échec, renvoie (today, 09:00).
    Gère un éventuel suffixe 'Z'.
    """
    if not iso_str:
        return date.today(), time(9, 0)

    try:
        iso_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_str)
        # On enlève les microsecondes, ça ne sert à rien ici
        return dt.date(), dt.time().replace(microsecond=0)
    except Exception:
        return date.today(), time(9, 0)


# ===================== PAGE LOGIN =====================

def login_page():
    """
    Page de connexion avec gestion du module JWT.
    """
    st.title("Connexion au Calendrier")

    with st.form("login_form"):
        email_input = st.text_input("Email")
        password_input = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    if submitted:
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "email": email_input,
                    "password": password_input,
                },
            )

            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                token_type = data.get("token_type", "bearer")

                if not access_token:
                    st.error("La réponse de l'API ne contient pas de token.")
                    st.write("Réponse brute :", data)
                    return

                # Sauvegarde dans cookies + session
                set_auth_in_storage(access_token, token_type)

                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
                try:
                    error_detail = response.json().get("detail", "Aucun détail fourni.")
                    st.error(f"Erreur API ({response.status_code}) : {error_detail}")
                except Exception:
                    st.error(
                        f"Erreur API: {response.status_code}. (Vérifiez la réponse du serveur)"
                    )

        except requests.exceptions.ConnectionError:
            st.error(f"Impossible de se connecter à l'API à l'adresse: {API_BASE_URL}")
        except Exception as e:
            st.error(f"Une erreur inattendue est survenue: {e}")


# ===================== PAGE CALENDRIER =====================

def events_page():
    """
    Page d'affichage des événements protégée par le JWT.
    Vue type Google Calendar : semaine / créneaux de 30 minutes.
    Permet d'éditer / supprimer un événement en cliquant dessus.
    Édition via : jour + heure début + heure fin (plus de toggle 'jour complet').
    """
    st.title("Mon agenda")

    # Init état pour l'évènement sélectionné
    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None

    # Récup du token depuis les cookies
    token, token_type = get_auth_from_storage()

    # Ligne avec bouton de déconnexion
    col_left_header, col_right_header = st.columns([1, 3])
    with col_left_header:
        if st.button("Déconnexion"):
            clear_auth()
            st.rerun()

    if not token:
        st.warning("Aucun token trouvé, veuillez vous reconnecter.")
        st.session_state["logged_in"] = False
        st.rerun()
        return

    headers = {
        "Authorization": f"{token_type.capitalize()} {token}"
    }

    try:
        response = requests.get(
            f"{API_BASE_URL}/events",
            headers=headers,
        )

        if response.status_code == 200:
            events_data = response.json() or []

            # Transforme les événements de l'API -> format FullCalendar
            calendar_events = []
            for ev in events_data:
                calendar_events.append(
                    {
                        "id": str(ev["id"]),
                        "title": ev["title"],
                        "start": ev["start_datetime"],  # ISO8601
                        "end": ev["end_datetime"],
                        "allDay": ev.get("all_day", False),
                    }
                )

            # Options FullCalendar pour une vue semaine avec créneaux 30 min
            calendar_options = {
                "initialView": "timeGridWeek",         # vue semaine en colonnes
                "slotDuration": "00:30:00",            # créneaux de 30 minutes
                "slotMinTime": "08:00:00",             # première ligne
                "slotMaxTime": "20:00:00",             # dernière ligne
                "allDaySlot": False,
                "nowIndicator": True,
                "locale": "fr",
                "firstDay": 1,                         # 1 = lundi
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "",                       # pas de switch de vue
                },
            }

            # CSS custom léger (facultatif)
            custom_css = """
                .fc-toolbar-title {
                    font-size: 1.2rem;
                }
            """

            # Layout : colonne gauche = édition, colonne droite = calendrier
            col_right,col_left = st.columns([2, 1])


            # ===================== CALENDRIER (DROITE) =====================
            with col_right:
                st.write("Vue hebdomadaire :")
                cal_state = calendar_component(
                    events=calendar_events,
                    options=calendar_options,
                    custom_css=custom_css,
                    key="calendar",
                )

            # ===================== GESTION DU CLIC SUR ÉVÈNEMENT =====================
            # cal_state ressemble à :
            # {
            #   "callback": "eventClick",
            #   "eventClick": { "event": { ... }, "view": { ... } }
            # }
            if cal_state and cal_state.get("callback") == "eventClick":
                ev = cal_state["eventClick"]["event"]
                selected_event = {
                    "id": str(ev.get("id")) if ev.get("id") is not None else None,
                    "title": ev.get("title", ""),
                    "start": ev.get("start", ""),
                    "end": ev.get("end", ""),
                    "allDay": ev.get("allDay", False),
                }
                st.session_state["selected_event"] = selected_event

            selected_event = st.session_state.get("selected_event")

            # ===================== FORMULAIRE D'ÉDITION / SUPPRESSION (GAUCHE) =====================
            with col_left:
                # Aucun formulaire tant qu'aucun événement n'a été cliqué
                if selected_event:
                    if not selected_event.get("id"):
                        st.error(
                            "Impossible de récupérer l'ID de l'évènement, édition désactivée."
                        )
                    else:
                        st.subheader("Éditer / supprimer l'évènement sélectionné")

                        # Parsing de la date / heure à partir des champs ISO
                        start_date_default, start_time_default = parse_iso_to_date_time(
                            selected_event.get("start", "")
                        )
                        # On récupère uniquement l'heure pour la fin
                        _, end_time_default = parse_iso_to_date_time(
                            selected_event.get("end", "")
                        )

                        with st.form("edit_event_form"):
                            title_input = st.text_input(
                                "Titre",
                                value=selected_event.get("title", ""),
                            )

                            # Jour
                            day_input = st.date_input(
                                "Jour",
                                value=start_date_default,
                            )

                            # Heures début / fin
                            col_t1, col_t2 = st.columns(2)
                            with col_t1:
                                start_time_input = st.time_input(
                                    "Heure de début",
                                    value=start_time_default,
                                    step=900,  # 15 min
                                )
                            with col_t2:
                                end_time_input = st.time_input(
                                    "Heure de fin",
                                    value=end_time_default,
                                    step=900,
                                )

                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                submit_update = st.form_submit_button("Mettre à jour")
                            with col_b2:
                                submit_delete = st.form_submit_button("Supprimer")

                        event_id = selected_event["id"]

                        # ----- UPDATE -----
                        if submit_update:
                            # Reconstruction des datetimes à partir de jour + heures
                            start_dt = datetime.combine(day_input, start_time_input)
                            end_dt = datetime.combine(day_input, end_time_input)

                            # Vérification stricte : début < fin
                            if start_dt >= end_dt:
                                st.error(
                                    "L'heure de début doit être strictement avant l'heure de fin."
                                )
                            else:
                                try:
                                    update_resp = requests.put(
                                        f"{API_BASE_URL}/events/{event_id}",
                                        headers=headers,
                                        json={
                                            "title": title_input,
                                            "start_datetime": start_dt.isoformat(),
                                            "end_datetime": end_dt.isoformat(),
                                            # plus de champ all_day dans l'édition
                                        },
                                    )
                                    if update_resp.status_code in (200, 204):
                                        st.success("Évènement mis à jour.")
                                        # On force le refresh des données
                                        st.session_state["selected_event"] = None
                                        st.rerun()
                                    else:
                                        try:
                                            err = update_resp.json()
                                        except Exception:
                                            err = update_resp.text
                                        st.error(
                                            f"Échec de la mise à jour (code {update_resp.status_code})"
                                        )
                                        st.write(err)
                                except Exception as e:
                                    st.error(f"Erreur lors de la mise à jour : {e}")

                        # ----- DELETE -----
                        if submit_delete:
                            try:
                                delete_resp = requests.delete(
                                    f"{API_BASE_URL}/events/{event_id}",
                                    headers=headers,
                                )
                                if delete_resp.status_code in (200, 204):
                                    st.success("Évènement supprimé.")
                                    st.session_state["selected_event"] = None
                                    st.rerun()
                                else:
                                    try:
                                        err = delete_resp.json()
                                    except Exception:
                                        err = delete_resp.text
                                    st.error(
                                        f"Échec de la suppression (code {delete_resp.status_code})"
                                    )
                                    st.write(err)
                            except Exception as e:
                                st.error(f"Erreur lors de la suppression : {e}")

        elif response.status_code == 401:
            st.warning("Session expirée ou non autorisée. Veuillez vous reconnecter.")
            clear_auth()
            st.rerun()
        else:
            st.error(
                f"Erreur lors de la récupération des événements (Code: {response.status_code})"
            )
            try:
                st.write(response.json())
            except Exception:
                pass

    except requests.exceptions.ConnectionError:
        st.error(
            f"Erreur de connexion à l'API: {API_BASE_URL}. "
            "Vérifiez que votre service 'api' est bien démarré."
        )
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue: {e}")


# ===================== MAIN =====================

def main():
    st.set_page_config(page_title="Calendrier", layout="wide")

    # Init état de connexion en fonction des cookies
    if "logged_in" not in st.session_state:
        token, token_type = get_auth_from_storage()
        if token:
            st.session_state["logged_in"] = True
            st.session_state["jwt_token"] = token
            st.session_state["token_type"] = token_type
        else:
            st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        events_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
