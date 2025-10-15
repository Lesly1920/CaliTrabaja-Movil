# app/components/chat_navigation.py (o app/utils/chat_navigation.py)

import flet as ft
import requests
from app.components.ModalAcceso import mostrar_modal_acceso


# ❌ ELIMINAMOS la importación: from main import sio, user_id_global

def contactar_experto_y_navegar(
        page: ft.Page,
        cambiar_pantalla,
        sio,  # Ahora se recibe como argumento
        user_id_global,  # Ahora se recibe como argumento
        receptor_id,
        nombre_experto,
        categoria
):
    # Lógica de verificación de token/sesión usando user_id_global
    if user_id_global is None:
        mostrar_modal_acceso(page, cambiar_pantalla)
        print("❌ ERROR: user_id desconocido. Redireccionando a acceso.")
        return

    # -------------------------------------------------------------
    # LÓGICA DE SOCKETIO Y API
    # -------------------------------------------------------------

    # 1. Intentar reconectar SocketIO (si es necesario)
    if not sio.connected:
        print("⚠️ SocketIO no conectado. Intentando reconectar...")
        try:
            # La conexión debe usar el sio que fue pasado como argumento
            sio.connect("https://lauren-extenuatory-joaquin.ngrok-free.dev", auth={"user_id": user_id_global})
        except Exception as e:
            print(f"❌ Fallo al reconectar SocketIO antes de navegar: {e}")

    # 2. Verificar si ya existe una conversación
    try:
        url = f"https://juan200521.pythonanywhere.com/api/conversacion/existe/{user_id_global}/{receptor_id}"
        resp = requests.get(url)
        resp.raise_for_status()  # Lanza un error si el status es 4xx o 5xx
        data = resp.json()
        existe_chat = data.get("existe", False)
    except Exception as e:
        print(f"❌ Error verificando conversación con API: {e}")
        existe_chat = False

    mostrar_aviso = not existe_chat

    if not existe_chat:
        print(f"ℹ No existe conversación previa con {nombre_experto}. Se abrirá el chat vacío.")
    else:
        print(f"✅ Ya existe conversación con {nombre_experto}.")

    # 3. Abrir el chat y pasar el flag mostrar_aviso
    cambiar_pantalla("chat", receptor_id=receptor_id, receptor_nombre=nombre_experto, mostrar_aviso=mostrar_aviso)