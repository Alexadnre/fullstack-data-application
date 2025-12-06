import os
import requests
import streamlit as st

from streamlit_calendar import calendar as calendar_component  # composant FullCalendar
from streamlit_cookies_manager import EncryptedCookieManager

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ===================== COOKIES MANAGER =====================

cookies = EncryptedCookieManager(
    prefix="calendar_app",
    # en prod, mets un vrai secret dans les variables d'env
    password=os.environ.get("COOKIES_PASSWORD", "dev-secret"),
)

# Le composant cookies doit être prêt avant de continuer
if not cookies.ready():
    st.stop()


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

                # Stockage en session
                st.session_state["jwt_token"] = access_token
                st.session_state["token_type"] = token_type
                st.session_state["logged_in"] = True

                # Stockage dans les cookies (persistance entre reloads)
                cookies["jwt_token"] = access_token
                cookies["token_type"] = token_type
                cookies.save()

                st.success("Connexion réussie ! Redirection...")
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")
                try:
                    error_detail = response.json().get("detail", "Aucun détail fourni.")
                    st.error(f"Erreur API ({response.status_code}): {error_detail}")
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
    """
    st.title("Mon agenda")

    token = st.session_state.get("jwt_token")
    token_type = st.session_state.get("token_type", "bearer")

    # Bouton de déconnexion
    if st.button("Déconnexion"):
        # Nettoyage session
        st.session_state.pop("jwt_token", None)
        st.session_state.pop("token_type", None)
        st.session_state["logged_in"] = False

        # Nettoyage cookies
        cookies["jwt_token"] = ""
        cookies["token_type"] = ""
        cookies.save()

        st.rerun()

    if not token:
        st.warning("Aucun token trouvé, veuillez vous reconnecter.")
        st.session_state["logged_in"] = False

        # Nettoyage cookies au cas où
        cookies["jwt_token"] = ""
        cookies["token_type"] = ""
        cookies.save()

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
                "slotMinTime": "06:00:00",             # première ligne
                "slotMaxTime": "22:00:00",             # dernière ligne
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

            st.write("Vue hebdomadaire (style Agenda) :")

            # Affiche le composant calendrier et récupère les interactions
            calendar_state = calendar_component(
                events=calendar_events,
                options=calendar_options,
                custom_css=custom_css,
                key="calendar",
            )

            # Affiche le nom de l'événement cliqué sous le calendrier
            if calendar_state and calendar_state.get("callback") == "eventClick":
                try:
                    clicked_event = calendar_state["eventClick"]["event"]
                    clicked_title = clicked_event.get("title", "")
                    if clicked_title:
                        st.markdown(f"**Événement sélectionné :** {clicked_title}")
                except Exception:
                    # Si jamais la structure n'est pas celle attendue, on ignore
                    pass

        elif response.status_code == 401:
            st.warning("Session expirée ou non autorisée. Veuillez vous reconnecter.")
            st.session_state["logged_in"] = False

            cookies["jwt_token"] = ""
            cookies["token_type"] = ""
            cookies.save()

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
            f"Erreur de connexion à l'API: {API_BASE_URL}. Vérifiez que votre service 'api' est bien démarré."
        )
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue: {e}")


# ===================== MAIN =====================

def main():
    # Au premier passage, on synchronise la session avec les cookies
    if "logged_in" not in st.session_state:
        jwt_from_cookie = cookies.get("jwt_token")
        token_type_from_cookie = cookies.get("token_type", "bearer")

        if jwt_from_cookie:
            st.session_state["jwt_token"] = jwt_from_cookie
            st.session_state["token_type"] = token_type_from_cookie
            st.session_state["logged_in"] = True
        else:
            st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        events_page()
    else:
        login_page()


if __name__ == "__main__":
    main()
