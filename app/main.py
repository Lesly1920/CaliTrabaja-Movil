import sys
import os
import flet as ft
import socketio
import requests  # 👈 agregado para consumir tu backend
import urllib.parse # agregadoo para mensajeria

# -----------------------------------------------
# VARIABLES GLOBALES DE CONEXIÓN PARA MENSAJERIA
# -----------------------------------------------
sio = socketio.Client()
# El ID del usuario se actualizará cuando se obtenga el token.
user_id_global = None

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar vistas
from app.views.Inicio import pantalla_inicio
from app.views.menu import pantalla_menu
from app.views.categorias import pantalla_categorias
from app.views.mensajeria import lista_chats, chat_view
from app.views.Guardados import render_guardados
from app.views.publicaciones import publicaciones
from app.views.inicio_sesion import inicio_sesion
from app.views.registrarse import pantalla_registro
from app.views.recuperar_contrasena import recuperar_contrasena
from app.views.cambiar_contrasena import cambiar_contrasena
from app.components.ModalAcceso import mostrar_modal_acceso


def obtener_token(page):
    # Recupera el token guardado en la sesión de Flet
    return getattr(page, "session_token", None)


# 👇 Helper para consumir tu API con token automáticamente
def api_get(page, endpoint=""):
    token = obtener_token(page)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(f"https://juan200521.pythonanywhere.com/api/{endpoint}", headers=headers)
    return resp.json()


def main(page: ft.Page):
    global user_id_global  # <--- NECESARIO para modificar la variable global
    page.title = "Mi App"
    page.bgcolor = "#FFFFFF"
    page.scroll = "adaptive"
    page.padding = 0
    page.margin = 0
    page.spacing = 0
    page.window_maximized = True
    page.fonts = {
        "OswaldRegular": "assets/fonts/Oswald-Regular.ttf",
        "OswaldMedium": "assets/fonts/Oswald-Medium.ttf",
        "OswaldBold": "assets/fonts/Oswald-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="OswaldRegular")

    # Asumo que las funciones auxiliares (obtener_token, api_get,
    # mostrar_modal_acceso, pantalla_inicio, lista_chats, etc.) están definidas.



    # ----------------------
    # Cambiar entre pantallas - VERSIÓN CORREGIDA
    # ----------------------
    def cambiar_pantalla(destino: str, origen=None, receptor_id=None, receptor_nombre=None):
        global user_id_global  # Necesario si actualizas el ID aquí

        user_id_global = page.session.get("user_id")
        # 1. Limpieza y preparación inicial
        page.controls.clear()
        page.bottom_appbar = None
        page.overlay.clear()

        # CLAVE: Deshabilita el scroll a nivel de página.
        # Esto fuerza al ft.Column de chat_view a llenar la pantalla y
        # permite que el ft.ListView interno maneje el scroll.
        page.scroll = False

        page.update()

        token = obtener_token(page)

        # 2. Lógica de navegación
        if destino == "inicio":
            # Nota: Si 'inicio' necesita scroll, debes activarlo DENTRO de pantalla_inicio
            # o justo después de llamarla.
            datos = api_get(page, "")
            print("Respuesta de /api/:", datos)
            pantalla_inicio(page, cambiar_pantalla, sio, user_id_global)

        elif destino == "menu":
            pantalla_menu(page, cambiar_pantalla)

        elif destino == "mensajes":
            if token is None:
                mostrar_modal_acceso(page, cambiar_pantalla)
                return
            # PASAR sio y el ID global
            contenido = lista_chats(page, cambiar_pantalla, sio, user_id_global)
            page.controls.append(contenido)

        elif destino == "chat":
            if receptor_id is None:
                print(" ERROR: receptor_id no fue pasado a cambiar_pantalla('chat')")
                return
            contenido = chat_view(page, cambiar_pantalla, sio, user_id_global, receptor_id, receptor_nombre)
            page.controls.append(contenido)

        elif destino == "categorias":
            pantalla_categorias(page, cambiar_pantalla)

        elif destino == "guardados":
            if token is None:
                mostrar_modal_acceso(page, cambiar_pantalla)
                return
            render_guardados(page, cambiar_pantalla)

        elif destino == "publicaciones":
            publicaciones(page, cambiar_pantalla, origen=origen)

        elif destino == "login":
            inicio_sesion(page, cambiar_pantalla, sio, user_id_global)

        elif destino == "recuperar_contrasena":
            recuperar_contrasena(page, cambiar_pantalla)

        elif destino == "registro":
            pantalla_registro(page, cambiar_pantalla, origen=origen)

        elif destino == "cambiar_contrasena":
            cambiar_contrasena(page, cambiar_pantalla)

        page.update()

    # ----------------------
    # Manejo de rutas
    # ----------------------
    def route_change(e: ft.RouteChangeEvent):
        print("Ruta recibida:", page.route)

        parsed_url = urllib.parse.urlparse(page.route)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path.startswith("/cambiar_contrasena"):
            token = query_params.get("token", [None])[0]
            cambiar_pantalla("cambiar_contrasena", token=token)

        elif path == "/mensajes":
            cambiar_pantalla("mensajes")

        elif path == "/chat":
            receptor_id = query_params.get("receptor_id", [None])[0]
            if receptor_id:
                print(" receptor_id extraído:", receptor_id)
                cambiar_pantalla("chat", receptor_id=int(receptor_id))
            else:
                print(" receptor_id no encontrado en la URL")

    page.on_route_change = route_change

    # Pantalla inicial
    pantalla_inicio(page, cambiar_pantalla, sio, user_id_global)

    # Iniciar en la ruta actual (deep link)
    page.go(page.route)

    # ------------------------------------
    # PUNTO DE ENTRADA / Llamada inicial a la pantalla_inicio
    # ------------------------------------
    # Esta línea reemplaza a la anterior: pantalla_inicio(page, cambiar_pantalla)
    pantalla_inicio(page, cambiar_pantalla, sio, user_id_global)

    # Iniciar en la ruta actual (deep link)
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.environ.get("PORT", 8550)))