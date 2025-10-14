import requests

# Cambia esto por la URL real de tu backend Flask
BASE_URL = "https://juan200521.pythonanywhere.com"

# ===========================
# 🔹 OBTENER CONVERSACIONES
# ===========================
def obtener_conversaciones(usuario_id):
    """Obtiene todas las conversaciones del usuario desde el backend Flask."""
    url = f"{BASE_URL}/movil/conversaciones/{usuario_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("❌ Error al obtener conversaciones:", response.status_code)
            return []
    except Exception as e:
        print("⚠️ Error al conectar con el servidor:", e)
        return []

# ===========================
# 🔹 OBTENER MENSAJES DE UN CHAT
# ===========================
def obtener_mensajes(yo_id, otro_id):
    try:
        url = f"{BASE_URL}/mensajes/{yo_id}/{otro_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Error al obtener mensajes: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return []

# ===========================
# 🔹 ENVIAR MENSAJE
# ===========================
def enviar_mensaje(id_emisor, id_receptor, texto):
    try:
        url = f"{BASE_URL}/enviar_mensaje"
        payload = {
            "id_emisor": id_emisor,
            "id_receptor": id_receptor,
            "texto": texto
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Error al enviar mensaje: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None
