import requests


def registrar_usuario_api(nombre,apellido,email,password,confirm):
    url = "https://lauren-extenuatory-joaquin.ngrok-free.dev/api/registrar_usuario"

    data = {"primer_nombre": nombre, "primer_apellido": apellido, "correo": email, "contrasena": password, "confirmar_contrasena": confirm}


    try:
        response = requests.post(url, json=data if data else {})

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

