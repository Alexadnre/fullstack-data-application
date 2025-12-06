import os
import requests
import streamlit as st

from streamlit_calendar import calendar as calendar_component
from streamlit_cookies_manager import EncryptedCookieManager


# ===================== CONFIG =====================

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Manager de cookies (doit être défini tout en haut du script)
cookies = EncryptedCookieManager(
    prefix="mon-agenda/",  # préfixe pour éviter les collisions
    password=os.environ.get("COOKIES_PASSWORD", "CHANGE_THIS_SECRET"),
)

# Important : attendre que le composant soit prêt
if not cookies.ready():
    st.stop()


# ===================== UTILS AUTH =====================

def init_auth_from_cookies():
    """
    Si un JWT est présent dans les cookies, on réhydrate la session Streamlit.
    Appelé au début de main().
    """
    if st.session_state.get("logged_in"):
        # Déjà connecté en mémoire, ne touche à rien
        return

    jwt = cookies.get("jwt_token")
    token_type = cookies.get("token_type", "bearer")

    if jwt:
        st.session_state["jwt_token"] = jwt
        st.session_state["token_type"] = token_type
        st.session_state["logged_in"] = True
    else:
        st.session_state["logged_in"] = False


def save_auth_to_cookies(access_token: str, token_type: str = "bearer"):
    """
    Sauvegarde le JWT dans les cookies + session_state.
    """
    st.session_state["jwt_token"] = access_token
    st.session_state["token_type"] = token_type
    st.session_state["logged_in"] = True

    cookies["jwt_token"] = access_token
    cookies["token_type"] = token_type
    # On force la sauvegarde immédiate
    cookies.save()


def clear_auth():
    """
    Supprime l’auth côté session_state et cookies.
    """
    st.session_state.pop("jwt_token", None)
    st.session_state.pop("token_type", None)
    st.session_state["logged_in"] = False

    cookies["jwt_token"] = ""
    cookies["token_type"] = ""
    cookies.save()


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

                # Sauvegarde dans cookies + session_state
                save_auth_to_cookies(access_token, token_type)

                st.success("Connexion réussie !")
                st.rerun()

            else:
                st.error("Email ou mot de passe incorrect.")
                try:
                    error_detail = response.json().get("detail", "Aucun détail fourni.")
                    st.error(f"Erreur API ({response.status_code}) : {error_detail}")
                except Exception:
                    st.error(
                        f"Erreur API : {response.status_code}. "
                        f"(Vérifiez la réponse du serveur)"
                    )

        except requests.exceptions.ConnectionError:
            st.error(f"Impossible de se connecter à l'API à l'adresse : {API_BASE_URL}")
        except Exception as e:
            st.error(f"Une erreur inattendue est survenue : {e}")


# ===================== PAGE CALENDRIER =====================

def events_page():
    """
    Page d'affichage des événements protégée par le JWT.
    Vue type Google Calendar : semaine / créneaux de 30 minutes.
    """
    st.title("Mon agenda")

    token = st.session_state.get("jwt_token")
    token_type = st.session_state.get("token_type", "bearer")

    # Bouton de déconnexion
    if st.button("Déconnexion"):
        clear_auth()
        st.rerun()

    if not token:
        st.warning("Aucun token trouvé, veuillez vous reconnecter.")
        clear_auth()
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
                "initialView": "timeGridWeek",
                "slotDuration": "00:30:00",
                "slotMinTime": "06:00:00",
                "slotMaxTime": "22:00:00",
                "allDaySlot": False,
                "nowIndicator": True,
                "locale": "fr",
                "firstDay": 1,  # 1 = lundi
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "",
                },
            }

            # CSS custom léger (facultatif)
            custom_css = """
                .fc-toolbar-title {
                    font-size: 1.2rem;
                }
            """

            st.write("Vue hebdomadaire (style Agenda) :")

            calendar_component(
                events=calendar_events,
                options=calendar_options,
                custom_css=custom_css,
                key="calendar",
            )

        elif response.status_code == 401:
            st.warning("Session expirée ou non autorisée. Veuillez vous reconnecter.")
            clear_auth()
            st.rerun()

        else:
            st.error(
                f"Erreur lors de la récupération des événements "
                f"(Code : {response.status_code})"
            )
            try:
                st.write(response.json())
            except Exception:
                pass

    except requests.exceptions.ConnectionError:
        st.error(
            f"Erreur de connexion à l'API : {API_BASE_URL}. "
            "Vérifiez que votre service 'api' est bien démarré."
        )
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue : {e}")


# ===================== MAIN =====================

def main():
    # Init du flag logged_in si absent
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Essaye de recharger l'auth depuis les cookies
    init_auth_from_cookies()

    if st.session_state["logged_in"]:
        events_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
