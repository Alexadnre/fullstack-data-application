import os
import requests
import streamlit as st

from datetime import datetime, date, time, timedelta

from streamlit_calendar import calendar as calendar_component
from streamlit_cookies_manager import EncryptedCookieManager

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

cookies = EncryptedCookieManager(
    prefix="mon-app-calendrier/",
    password=os.environ.get("COOKIES_PASSWORD", "CHANGE-ME"),
)

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

        return dt.date(), dt.time().replace(microsecond=0)
    except Exception:
        return date.today(), time(9, 0)

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

def events_page():
    """
    Page d'affichage des événements protégée par le JWT.
    Vue type Google Calendar : semaine / créneaux de 30 minutes.
    - Clic sur un évènement : édition / suppression.
    - Clic sur un créneau vide : création d'un évènement de 1h.
    """
    st.title("Mon agenda")

    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None

    if "last_calendar_action" not in st.session_state:
        st.session_state["last_calendar_action"] = None

    token, token_type = get_auth_from_storage()

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

    @st.cache_data(show_spinner=False)
    def fetch_events(auth_header: str):
        resp = requests.get(f"{API_BASE_URL}/events", headers={"Authorization": auth_header})
        if resp.status_code == 200:
            return resp.json() or [], 200
        return [], resp.status_code

    try:
        auth_header = f"{token_type.capitalize()} {token}"
        events_data, status_code = fetch_events(auth_header)

        if status_code == 200:

            selected_event_data = st.session_state.get("selected_event", {})
            selected_id = selected_event_data.get("id") if selected_event_data else None

            calendar_events = []
            for ev in events_data:
                event_obj = {
                    "id": str(ev["id"]),
                    "title": ev["title"],
                    "start": ev["start_datetime"],
                    "end": ev["end_datetime"],
                    "allDay": ev.get("all_day", False),
                }

                if str(ev["id"]) == selected_id:
                    event_obj["backgroundColor"] = "#22C55E"
                    event_obj["borderColor"] = "#16A34A"
                    event_obj["textColor"] = "#FFFFFF"
                else:
                    event_obj["backgroundColor"] = "#3788D8"
                    event_obj["borderColor"] = "#2563EB"

                calendar_events.append(event_obj)

            calendar_options = {
                "initialView": "timeGridWeek",
                "slotDuration": "00:30:00",
                "slotMinTime": "08:00:00",
                "slotMaxTime": "20:00:00",
                "allDaySlot": False,
                "nowIndicator": True,
                "locale": "fr",
                "firstDay": 1,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "",
                },

                "selectable": False,
                "contentHeight": "auto",
            }

            custom_css = """
                .fc-toolbar-title {
                    font-size: 1.2rem;
                }
                .fc-event {
                    transition: all 0.2s ease;
                    cursor: pointer;
                }
                .fc-event:hover {
                    opacity: 0.9;
                    transform: scale(1.02);
                }
            """

            col_right, col_left = st.columns([2, 1])

            with col_right:
                st.write("Vue hebdomadaire :")
                cal_state = calendar_component(
                    events=calendar_events,
                    options=calendar_options,
                    custom_css=custom_css,
                    key="calendar",
                )

            from datetime import datetime, timedelta

            if cal_state:
                callback = cal_state.get("callback")

                if callback == "dateClick":
                    dc = cal_state.get("dateClick", {})
                    date_str = dc.get("date") or dc.get("dateStr")

                    if date_str:

                        action_id = f"dateClick:{date_str}"

                        if st.session_state["last_calendar_action"] != action_id:
                            st.session_state["last_calendar_action"] = action_id

                            try:
                                dt = datetime.fromisoformat(
                                    date_str.replace("Z", "+00:00")
                                )
                                start_dt = dt
                                end_dt = dt + timedelta(hours=1)

                                create_resp = requests.post(
                                    f"{API_BASE_URL}/events",
                                    headers=headers,
                                    json={
                                        "title": "Nouvel évènement",
                                        "start_datetime": start_dt.isoformat(),
                                        "end_datetime": end_dt.isoformat(),
                                    },
                                )

                                if create_resp.status_code in (200, 201):
                                    st.success("Évènement créé.")

                                    new_event = create_resp.json()
                                    st.session_state["selected_event"] = {
                                        "id": str(new_event["id"]),
                                        "title": new_event["title"],
                                        "start": new_event["start_datetime"],
                                        "end": new_event["end_datetime"],
                                        "allDay": new_event.get("all_day", False),
                                    }
                                    fetch_events.clear()
                                    st.rerun()
                                else:
                                    try:
                                        err = create_resp.json()
                                    except Exception:
                                        err = create_resp.text
                                    st.error(
                                        f"Échec de la création de l'évènement (code {create_resp.status_code})."
                                    )
                                    st.write(err)
                            except Exception as e:
                                st.error(f"Erreur lors de la création de l'évènement : {e}")

                if callback == "eventClick":
                    ev = cal_state["eventClick"]["event"]
                    new_id = str(ev.get("id")) if ev.get("id") is not None else None
                    current = st.session_state.get("selected_event", {})
                    current_id = current.get("id") if current else None

                    if new_id != current_id:
                        st.session_state["selected_event"] = {
                            "id": new_id,
                            "title": ev.get("title", ""),
                            "start": ev.get("start", ""),
                            "end": ev.get("end", ""),
                            "allDay": ev.get("allDay", False),
                        }
                        st.rerun()

            selected_event = st.session_state.get("selected_event")

            with col_left:
                if selected_event:
                    if not selected_event.get("id"):
                        st.error(
                            "Impossible de récupérer l'ID de l'évènement, édition désactivée."
                        )
                    else:
                        st.subheader("Éditer / supprimer l'évènement sélectionné")

                        start_date_default, start_time_default = parse_iso_to_date_time(
                            selected_event.get("start", "")
                        )
                        _, end_time_default = parse_iso_to_date_time(
                            selected_event.get("end", "")
                        )

                        with st.form("edit_event_form"):
                            title_input = st.text_input(
                                "Titre",
                                value=selected_event.get("title", ""),
                            )

                            day_input = st.date_input(
                                "Jour",
                                value=start_date_default,
                            )

                            col_t1, col_t2 = st.columns(2)
                            with col_t1:
                                start_time_input = st.time_input(
                                    "Heure de début",
                                    value=start_time_default,
                                    step=900,
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

                        if submit_update:
                            start_dt = datetime.combine(day_input, start_time_input)
                            end_dt = datetime.combine(day_input, end_time_input)

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
                                        },
                                    )
                                    if update_resp.status_code in (200, 204):
                                        st.success("Évènement mis à jour.")
                                        st.session_state["selected_event"] = None
                                        fetch_events.clear()
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

                        if submit_delete:
                            try:
                                delete_resp = requests.delete(
                                    f"{API_BASE_URL}/events/{event_id}",
                                    headers=headers,
                                )
                                if delete_resp.status_code in (200, 204):
                                    st.success("Évènement supprimé.")
                                    st.session_state["selected_event"] = None
                                    fetch_events.clear()
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

        elif status_code == 401:
            st.warning("Session expirée ou non autorisée. Veuillez vous reconnecter.")
            clear_auth()
            st.rerun()
        else:
            st.error(
                f"Erreur lors de la récupération des événements (Code: {status_code})"
            )

    except requests.exceptions.ConnectionError:
        st.error(
            f"Erreur de connexion à l'API: {API_BASE_URL}. "
            "Vérifiez que votre service 'api' est bien démarré."
        )
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue: {e}")

def main():
    st.set_page_config(page_title="Calendrier", layout="wide")

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
