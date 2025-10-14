import requests

BASE_URL = "https://lauren-extenuatory-joaquin.ngrok-free.dev"

def cerrar_sesion_api(token=None):
    url = f"{BASE_URL}/api/cerrar_sesion"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        res = requests.post(url, headers=headers)
        data = res.json()
        return data
    except Exception as e:
        return {"success":False,"message":f"Error de cerrar sesion: {str(e)}"}
