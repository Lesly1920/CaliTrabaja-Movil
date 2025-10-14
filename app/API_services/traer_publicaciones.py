import requests

BASE_URL = "https://juan200521.pythonanywhere.com"

def traer_publicaciones_usu(datos=None):
    url = f"{BASE_URL}/api/publicaciones"

    try:
        response = requests.post(url,  json=datos)

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