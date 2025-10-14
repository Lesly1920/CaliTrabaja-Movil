import requests

BASE_URL = "https://lauren-extenuatory-joaquin.ngrok-free.dev"

def traer_guardados(token):
    url = f"{BASE_URL}/api/mis_guardados"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.get(url, headers=headers)

        try:
            resultado_json = response.json()  # Convierte la respuesta JSON a dict
        except Exception:
            resultado_json = {
                "success": False,
                "message": f"Respuesta no válida del servidor: {response.text}"
            }

        return resultado_json

    except Exception as e:
        # Ahora devolvemos un dict incluso si hay fallo de conexión
        return {"success": False, "message": f"Error de conexión: {e}"}