import requests

def cambio_contra_usu(token,data):
    url = " https://lauren-extenuatory-joaquin.ngrok-free.dev/api/restablecer_contraseña_datos"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(url, headers=headers, json=data if data else {})

        try:
            resultado_json = response.json()  # <-- aquí se convierte a dict
        except Exception:
            resultado_json = {
                "success": False,
                "message": f"Respuesta no válida del servidor: {response.text}"
            }
        return resultado_json

    except Exception as e:
        # Ahora devolvemos un dict incluso si hay fallo de conexión
        return {"success": False, "message": f"Error de conexión: {e}"}

