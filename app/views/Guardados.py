import flet as ft
from app.components.menu_inferior import menu_inferior
from app.components.ModalReporte import ModalReporte
from app.components.MenuTarjetasOpciones import menu_opciones
from app.API_services.traer_guardados import traer_guardados
from app.API_services.eliminar_guardado import eliminar_guardado_usuario

# ---------- NAV SUPERIOR ----------
def nav_superior(page_width: float, titulo="Título", on_back_click=lambda e: None):
    text_size = 24 if page_width < 400 else 28
    icon_size = 50

    return ft.SafeArea(
        top=True,
        left=False,
        right=False,
        content=ft.Container(
            width=float("inf"),
            height=100,
            bgcolor="#F5F5F5",
            padding=ft.padding.symmetric(horizontal=10),
            margin=0,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        icon_color="#3EAEB1",
                        icon_size=icon_size,
                        on_click=on_back_click
                    ),
                    ft.Text(
                        titulo,
                        color="#3EAEB1",
                        size=text_size,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(width=icon_size)
                ]
            )
        )
    )





# ---------- VISTA GUARDADOS ----------
def render_guardados(page: ft.Page, cambiar_pantalla=None):
    page.clean()
    page.title = "Mis guardados"
    page.scroll = "auto"
    page.bgcolor = "white"
    page.padding = 0
    page.spacing = 0

    # ---------- INSTANCIAMOS EL MODAL ----------
    modal_reporte = ModalReporte(
        on_guardar=lambda desc: print(f" Reporte guardado: {desc}"),
        on_cancelar=lambda: print(" Reporte cancelado")
    )

    #  Lo agregamos al overlay para que siempre esté disponible
    if modal_reporte.dialog not in page.overlay:
        page.overlay.append(modal_reporte.dialog)

    def obtener_token(page):
        return getattr(page, "session_token", None)

    def obtener_guardados():
        token = obtener_token(page)
        if not token:
            print("Inicia sesion o registrate")

        respuesta = traer_guardados(token)

        if not respuesta.get("success"):
            print("Error al traer guardados:", respuesta.get("message"))
            return []

        guardados = respuesta.get("data", [])

        lista = []

        for g in guardados:
            pub = g.get("publicacion", {})
            lista.append({
                "guardado_id": g.get("guardado_id"),
                "fecha_guardado": g.get("fecha_guardado"),
                "publicacion_id": pub.get("publicacion_id"),
                "nombre_experto": pub.get("nombre_experto"),
                "usuario_id": pub.get("usuario_id"),
                "categoria": pub.get("categoria"),
                "subcategoria": pub.get("subcategoria"),
                "descripcion": pub.get("descripcion"),
                "costo": pub.get("costo"),
                "calificacion": pub.get("calificacion"),
                "foto_perfil": pub.get("foto_perfil"),
            })
        return lista



    # ---------- Contenedor de cards dinámico ----------
    cards = ft.Column(expand=True, spacing=0)

    def recargar_guardados():
        cards.controls.clear()

        nuevos_guardados = obtener_guardados()

        if not nuevos_guardados:
            # Mostramos mensaje de "no hay guardados" centrado
            cards.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.BOOKMARK_BORDER, size=70, color="#3EAEB1"),
                            ft.Text(
                                "No tienes publicaciones guardadas",
                                size=18,
                                color="#666666",
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.ElevatedButton(
                                "Ver publicaciones",
                                bgcolor="#3EAEB1",
                                color=ft.Colors.WHITE,
                                on_click=lambda e: cambiar_pantalla("publicaciones")
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            )
        else:
            # Mostramos las cards guardadas
            for g in nuevos_guardados:
                cards.controls.append(
                    saved_card(
                        g.get("foto_perfil", "none"),
                        g.get("publicacion_id"),
                        g.get("usuario_id"),
                        g.get("nombre_experto", "Sin nombre"),
                        g.get("categoria", "Sin categoría"),
                        g.get("subcategoria", "Sin subcategoría"),
                        f"COP {g.get('costo')}" if g.get("costo") else "Precio no disponible",
                        g.get("descripcion", "Sin descripción"),
                    )
                )
        page.update()

    def mostrar_snackbar(page, mensaje, exito=True):
        """Muestra SnackBar con estilo uniforme"""
        sb = ft.SnackBar(
            content=ft.Text(
                mensaje,
                color="white",
                size=16,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=ft.Colors.GREEN if exito else ft.Colors.RED,
            duration=3000,
        )
        page.overlay.append(sb)
        sb.open = True
        page.update()

    def eliminar_guardado(page, publicacion_id):
        token = obtener_token(page)

        if not token:
            mostrar_snackbar(page, "Inicia sesión o regístrate para eliminar guardados.", exito=False)
            return

        datos = {}
        if publicacion_id:
            datos["publicacion_id"] = publicacion_id

        respuesta = eliminar_guardado_usuario(token, datos)

        if respuesta.get("success"):
            mostrar_snackbar(page, "Publicación guardada eliminada correctamente.", exito=True)
            recargar_guardados()
        else:
            mostrar_snackbar(page, respuesta.get("message", "Error al eliminar guardado."), exito=False)

    # ---------- Card factory ----------
    def saved_card(foto_perfil,publicacion_id, usuario_id, nombre, categoria, subcategoria, precio, descripcion):


        if len(descripcion) > 300:
            descripcion = descripcion[:300] + "..."

        # Menú solo con Reportar (sin opción Guardar)
        menu_solo_reportar = menu_opciones(
            page, modal_reporte, text_color="black", incluir_guardar=False, usuario_id=usuario_id, incluir_reporte=True,
        )

        base_url = "https://juan200521.pythonanywhere.com/static/uploads/perfiles/"

        if foto_perfil and foto_perfil.lower() != "none":
            img_url = f"{base_url}{foto_perfil}"
        else:

            img_url = f"{base_url}defecto.png"  # imagen por defecto

        return ft.Container(

            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.CircleAvatar(foreground_image_src=img_url, radius=30, bgcolor=ft.Colors.GREY_300),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                nombre,
                                                size=18,
                                                weight="bold",
                                                color="teal"
                                            ),
                                            ft.Row(
                                                [
                                                    menu_solo_reportar,  # Menú de opciones
                                                    ft.IconButton(
                                                        icon=ft.Icons.DELETE_OUTLINE,
                                                        icon_color="#3EAEB1",
                                                        icon_size=24,
                                                        on_click=lambda e: mostrar_modal_eliminar_guardado(
                                                            page, publicacion_id, eliminar_guardado
                                                        )
                                                    ),
                                                ],
                                                spacing=8,
                                            ),
                                        ],
                                        alignment="spaceBetween",
                                        expand=True,
                                    ),

                                    ft.Row(
                                        [
                                            ft.Text(categoria, size=14, color="black", weight="bold"),
                                            ft.Text("·", size=14),
                                            ft.Text(subcategoria, size=14, color="#666666", weight="bold"),
                                        ],
                                        spacing=4,
                                    ),
                                    ft.Text(precio, size=13, weight="bold", color="#666666"),
                                    ft.Container(
                                        width=600 if page.width > 800 else page.width * 0.9,
                                        # limitar ancho en pantallas grandes
                                        content=ft.Text(
                                            descripcion,
                                            size=13,
                                            color="black",
                                            no_wrap=False,  # permite salto de línea
                                            max_lines=None,  # muestra todas las líneas necesarias
                                            overflow=ft.TextOverflow.VISIBLE,  # evita el corte del texto
                                            text_align=ft.TextAlign.JUSTIFY,  # justifica el texto
                                            weight="bold",
                                        ),
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                        ],
                        alignment="start",
                        spacing=12,
                    ),
                    ft.Row(
                        [
                            ft.Container(width=page.width * 0.25),  # Espacio vacío a la izquierda
                            ft.Container(
                                bgcolor="#DDDDDD",
                                height=1,
                                width=page.width * 0.8,
                            ),
                        ],
                        spacing=0,
                    )
                ],
                spacing=8,
            ),
            padding=10,
            margin=ft.margin.only(left=5, right=5),
        )





    # ---------- Navegación inferior ----------
    def on_bottom_nav_click(index):
        if index == 0:  # Inicio
            cambiar_pantalla("inicio")
        elif index == 1:  # Categorias
            cambiar_pantalla("categorias")
        elif index == 2:  # Mensajes
            token = obtener_token(page)
            if token:
                cambiar_pantalla("mensajes")
            else:
                print("Inicia sesion o registrate")
        elif index == 3:  # Guardados
            token = obtener_token(page)
            if token:
                cambiar_pantalla("guardados")
            else:
                print("Inicia sesion o registrate")
        elif index == 4:  # Menú
                cambiar_pantalla("menu")


    # Barra inferior
    page.bottom_appbar = ft.BottomAppBar(
        content=menu_inferior(selected_index=3, on_bottom_nav_click=on_bottom_nav_click),
        bgcolor=ft.Colors.WHITE,
    )

    # ---------- Layout principal ----------
    page.add(
        ft.Column(
            [
                nav_superior(
                    page.width,
                    "Guardados",
                    on_back_click=lambda e: cambiar_pantalla("inicio") if cambiar_pantalla else None
                ),
                cards
            ],
            scroll="auto",
            expand=True,
        )
    )
    recargar_guardados()
    page.update()  #  aseguramos refresco de toda la UI


def mostrar_modal_eliminar_guardado(page, publicacion_id, eliminar_guardado_callback):
    """Muestra un modal de confirmación para eliminar guardado"""

    def confirmar_eliminar(e):
        modal.open = False
        page.update()
        eliminar_guardado_callback(page, publicacion_id)

    def cancelar(e):
        modal.open = False
        page.update()

    # Botón aceptar (color #3EAEB1)
    btn_aceptar = ft.ElevatedButton(
        "Aceptar",
        bgcolor="#3EAEB1",
        color=ft.Colors.WHITE,
        width=110,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            overlay_color={"": "#C0392B"},
            text_style={"": ft.TextStyle(
                font_family="Oswald",
                size=14,
                weight=ft.FontWeight.W_600,
                color="white"
            )}
        ),
        on_click=confirmar_eliminar,
    )

    # Botón cancelar (gris claro con borde)
    btn_cancelar = ft.OutlinedButton(
        "Cancelar",
        width=110,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor="#f8f8f8",
            color="black",
            side=ft.BorderSide(1, "#E5E5E5"),
            text_style={"": ft.TextStyle(
                font_family="Oswald",
                size=14,
                weight=ft.FontWeight.W_500,
                color="black"
            )}
        ),
        on_click=cancelar,
    )

    # Modal con mismo estilo que cerrar sesión
    modal = ft.AlertDialog(
        modal=False,
        bgcolor="#FFFFFF",
        content=ft.Container(
            width=320,
            bgcolor="#FFFFFF",
            border_radius=20,
            content=ft.Column(
                [
                    ft.Text(
                        "¿Deseas eliminar esta publicación?",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align="center",
                        color="#666666",  # gris css en Flet
                        font_family="Oswald"
                    ),
                    ft.Row(
                        [btn_aceptar, btn_cancelar],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15
                    )
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if modal not in page.overlay:
        page.overlay.append(modal)

    modal.open = True
    page.update()

