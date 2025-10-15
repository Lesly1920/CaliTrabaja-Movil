# app/views/Inicio.py
import flet as ft
import asyncio
from flet import Icons
from pyexpat.errors import messages

from app.API_services.inicio import inicio_api
from app.components.nav import nav_bar
from app.components.menu_inferior import menu_inferior
from app.components.ModalReporte import ModalReporte
from app.components.ModalTarjetaCompleta import ModalTarjetaCompleta
from app.components.MenuTarjetasOpciones import menu_opciones
from app.API_services.traer_publicaciones import traer_publicaciones_usu
from app.API_services.datos_usuario import obtener_datos
from app.components.ModalAcceso import mostrar_modal_acceso
from app.components.chat_navigation import contactar_experto_y_navegar


def pantalla_inicio(page: ft.Page, cambiar_pantalla, sio=None, user_id_global=None):


    # ---------------- CONFIGURACIÓN GENERAL ----------------
    page.controls.clear()
    page.bottom_appbar = None
    page.bgcolor = "#FFFFFF"
    page.padding = 0
    page.margin = 0
    page.spacing = 0
    page.window_maximized = True

    # Fuentes y tema
    page.fonts = {
        "Oswald": "https://raw.githubusercontent.com/google/fonts/main/ofl/oswald/Oswald%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Oswald")
    page.theme_mode = "light"
    page.title = "Inicio"

    PRIMARY_COLOR = "#3EAEB1"
    TEXT_COLOR = "#000000"
    BORDER_COLOR = "#D9D9D9"

    def obtener_token(page):
        return getattr(page, "session_token", None)
    # ---------------- INSTANCIA DE MODAL REPORTE Y TARJETA ----------------
    modal_reporte = ModalReporte()
    page.overlay.append(modal_reporte.dialog)

    modal_detalle = ModalTarjetaCompleta()
    page.overlay.append(modal_detalle.dialog)


    def abrir_modal_detalle(foto_perfil, nombre, profesion, descripcion, costo, calificacion):
        print("CLICK -> abrir_modal_detalle:", nombre)  # <-- mira la consola donde corres Flet
        modal_detalle.set_content(foto_perfil, nombre, profesion, descripcion, costo, calificacion)
        page.dialog = modal_detalle.dialog
        modal_detalle.dialog.open = True
        page.update()

    token = obtener_token(page)
    usuario_autenticado = token is not None

    token = obtener_token(page)
    usuario_autenticado = token is not None

    # 🔹 Obtener nombre usuario si hay sesión
    nombre_usuario = None
    if usuario_autenticado:
        try:
            datos_usuario = obtener_datos(token)
            nombre_usuario = datos_usuario.get("usuario", {}).get("nombre")
        except Exception as e:
            print("Error obteniendo datos usuario:", e)

    # ---------------- NAV SUPERIOR ----------------
    nav = nav_bar(
        page,
        page.width,
        show_back=False,  # 👉 en Inicio NO aparece la flecha
        show_explora=False,  # 👉 en Inicio NO aparece "Explora en"
        show_login_icon=not usuario_autenticado,
        on_login_click=lambda e: cambiar_pantalla("login")  # 👈 acción del botón
    )

    # ---------------- SALUDO USUARIO LOGUEADO -------------------

    # 🔹 Texto "Hola, Nombre"
    saludo_usuario = ft.Container(
        visible=usuario_autenticado,  # solo si hay sesión
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,  # 👈 alinea a la izquierda
            controls=[
                ft.Text("Hola,", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text(
                    nombre_usuario if nombre_usuario else "",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#3EAEB1"
                ),
            ],
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=8)  # 👈 igual que categorías
    )

    # ---------------- FRASES CAMBIANTES + BOTÓN INICIO SESIÓN ----------------
    frases = [
        ("Nosotros conectamos,", "tú decides."),
        ("Conecta, trabaja,", "crece"),
        ("Conectando habilidades para un futuro", "mejor.")
    ]

    frase_texto = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(frases[0][0], size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                    ft.Text(frases[0][1], size=17, color=PRIMARY_COLOR)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    contenedor_frase = ft.Container(
        content=frase_texto,
        alignment=ft.alignment.center,
        height=90,
        bgcolor="#D9D9D9",
        border_radius=ft.border_radius.all(2),
        margin=ft.margin.symmetric(horizontal=8, vertical=5),
        padding=14
    )

    # Ajuste responsivo para móviles
    if page.width <= 768:
        contenedor_frase.width = page.width - 16  # resta los márgenes
        contenedor_frase.margin = ft.margin.symmetric(horizontal=8, vertical=5)
    else:
        contenedor_frase.width = page.width * 0.9  # en pantallas grandes ocupa el 90%
        contenedor_frase.margin = ft.margin.symmetric(horizontal=page.width * 0.05, vertical=5)


    async def cambiar_frase():
        index = 1
        while True:
            await asyncio.sleep(4)
            frase_texto.controls.clear()
            if index % len(frases) == 2:
                frase_texto.controls.append(
                    ft.Row(
                        controls=[ft.Text(frases[index][0], size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
                frase_texto.controls.append(
                    ft.Row(
                        controls=[ft.Text(frases[index][1], size=17, color=PRIMARY_COLOR)],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            else:
                frase_texto.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(frases[index][0], size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                            ft.Text(frases[index][1], size=17, color=PRIMARY_COLOR)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4
                    )
                )
            page.update()
            index = (index + 1) % len(frases)

    page.run_task(cambiar_frase)

    # ---------------- CATEGORÍAS ----------------

    categorias_titulo = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Categorías",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_COLOR
                ),

                # "Ver todos" como texto clickeable en color negro
                ft.GestureDetector(
                    on_tap=lambda e: cambiar_pantalla("categorias"),
                    content=ft.Container(
                        padding=ft.padding.symmetric(horizontal=6, vertical=4),
                        content=ft.Text(
                            "Ver todos",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color="black"  # <- forzamos negro aquí
                        )
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=8)
    )


    categorias = [
        {"nombre": "Reparación y Mantenimiento", "icono": "tecnico.svg", "id":1},
        {"nombre": "Cuidado y Asistencia", "icono": "cuidado.svg", "id":2},
        {"nombre": "Bienestar de Mascotas", "icono": "mascoteros.svg", "id":3},
        {"nombre": "Educativos y aprendizaje", "icono": "educativos.svg", "id":4},
        {"nombre": "Hogar y Limpieza", "icono": "limpieza.svg", "id":5},
        {"nombre": "Construcción y Remodelación", "icono": "construccion.png", "id":6},
        {"nombre": "Artísticos y creatividad visual", "icono": "artisticos.svg", "id":7},
        {"nombre": "Movilidad y transporte", "icono": "transporte.svg", "id":8},
        {"nombre": "Gastronomía", "icono": "culinarios.svg", "id":9},
        {"nombre": "Eventos", "icono": "eventos.svg", "id":10},
        {"nombre": "Bienestar Personal", "icono": "salud_bien.svg", "id":11}

    ]

    # --- Paginación categorías (carrusel) ---
    CAT_CARD_WIDTH = 85  # ancho aproximado de cada item (icono + texto)
    CAT_SPACING = 12  # debe coincidir con el spacing del listado
    H_PADDING = 15  # padding horizontal del contenedor de categorías

    state_paginacion = {"num_pages": 1, "active": 0}

    def _build_indicators(n, active=0):
        indicadores.controls.clear()

        # intentos de iconos válidos (fallbacks)
        filled_icon = (
                getattr(ft.Icons, "CIRCLE", None)
                or getattr(ft.Icons, "FIBER_MANUAL_RECORD", None)
                or getattr(ft.Icons, "LENS", None)
                or getattr(ft.Icons, "RADIO_BUTTON_CHECKED", None)
        )
        outline_icon = (
                getattr(ft.Icons, "CIRCLE_OUTLINE", None)
                or getattr(ft.Icons, "RADIO_BUTTON_UNCHECKED", None)
                or getattr(ft.Icons, "RADIO_BUTTON_OFF", None)
        )

        use_text_bullets = (filled_icon is None) or (outline_icon is None)

        for i in range(n):
            if use_text_bullets:
                # si no hay iconos disponibles, usar texto como fallback
                indicadores.controls.append(
                    ft.Text(
                        "●" if i == active else "○",
                        size=12,
                        color=PRIMARY_COLOR if i == active else ft.Colors.GREY_400,
                    )
                )
            else:
                icon_to_use = filled_icon if i == active else outline_icon
                # IMPORTANTE: pasar el icono como primer argumento (posicional), no name=
                indicadores.controls.append(
                    ft.Icon(icon_to_use, size=8, color=PRIMARY_COLOR if i == active else ft.Colors.GREY_400)
                )

    def _items_per_page():
        viewport = max(1, int(page.width - (H_PADDING * 2)))
        approx = CAT_CARD_WIDTH + CAT_SPACING
        return max(1, viewport // approx)

    def _config_pagination():
        items = _items_per_page()
        n = (len(categorias) + items - 1) // items
        state_paginacion["num_pages"] = max(1, n)
        state_paginacion["active"] = min(state_paginacion["active"], state_paginacion["num_pages"] - 1)
        indicadores_container.visible = state_paginacion["num_pages"] > 1
        _build_indicators(state_paginacion["num_pages"], state_paginacion["active"])
        page.update()

    def _on_cat_scroll(e: ft.OnScrollEvent):
        try:
            max_extent = float(e.max_scroll_extent or 0)
            pixels = float(e.pixels or 0)
        except Exception:
            return
        if state_paginacion["num_pages"] <= 1 or max_extent <= 0:
            return
        ratio = pixels / max_extent
        idx = int(round(ratio * (state_paginacion["num_pages"] - 1)))
        idx = max(0, min(state_paginacion["num_pages"] - 1, idx))
        if idx != state_paginacion["active"]:
            state_paginacion["active"] = idx
            _build_indicators(state_paginacion["num_pages"], idx)
            page.update()

    # --- fin helpers carrusel ---

    # --- Paginación publicaciones (carrusel) ---
    PUB_CARD_WIDTH = 195
    PUB_SPACING = 15
    PUB_PADDING = 15

    state_publi = {"num_pages": 1, "active": 0}

    indicadores_publi = ft.Row(controls=[], alignment=ft.MainAxisAlignment.CENTER, spacing=4)
    indicadores_publi_container = ft.Container(content=indicadores_publi,
                                               alignment=ft.alignment.center,
                                               padding=ft.padding.only(top=4),
                                               visible=False)

    def _build_indicators_publi(n, active=0):
        indicadores_publi.controls.clear()
        for i in range(n):
            indicadores_publi.controls.append(
                ft.Text("●" if i == active else "○",
                        size=12,
                        color=PRIMARY_COLOR if i == active else ft.Colors.GREY_400)
            )

    def _items_per_page_publi():
        viewport = max(1, int(page.width - (PUB_PADDING * 2)))
        approx = PUB_CARD_WIDTH + PUB_SPACING
        return max(1, viewport // approx)

    def _config_pagination_publi():
        items = _items_per_page_publi()
        n = (len(aleatorias) + items - 1) // items
        state_publi["num_pages"] = max(1, n)
        state_publi["active"] = min(state_publi["active"], state_publi["num_pages"] - 1)
        indicadores_publi_container.visible = state_publi["num_pages"] > 1
        _build_indicators_publi(state_publi["num_pages"], state_publi["active"])
        page.update()

    def _on_publi_scroll(e: ft.OnScrollEvent):
        try:
            max_extent = float(e.max_scroll_extent or 0)
            pixels = float(e.pixels or 0)
        except Exception:
            return
        if state_publi["num_pages"] <= 1 or max_extent <= 0:
            return
        ratio = pixels / max_extent
        idx = int(round(ratio * (state_publi["num_pages"] - 1)))
        idx = max(0, min(state_publi["num_pages"] - 1, idx))
        if idx != state_publi["active"]:
            state_publi["active"] = idx
            _build_indicators_publi(state_publi["num_pages"], idx)
            page.update()



    def filtrar_por_categoria(cat_id):
        print("filtrar_por_categoria", cat_id)

        datos={}

        if cat_id:
            datos["categoria_id"]= cat_id

        respuesta = traer_publicaciones_usu(datos)

        # Extraer publicaciones de la respuesta
        publicaciones_filtradas = respuesta.get("publicaciones_generales", [])

        # Actualizar la sección de publicaciones
        publicaciones_container.controls.clear()
        publicaciones_container.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[tarjeta_horizontal(**p) for p in publicaciones_filtradas],
                    spacing=15,
                    scroll=ft.ScrollMode.HIDDEN
                ),
                padding=ft.padding.symmetric(horizontal=15)
            )
        )

        page.update()



    cat_items = [
        ft.GestureDetector(
            on_tap=lambda e, cat_id=cat["id"]: cambiar_pantalla("publicaciones", origen={"categoria_id": cat_id}),
            content =ft.Column(
                [
                    ft.Container(
                        content=ft.Image(src=cat["icono"], width=40, height=40),
                        width=55, height=55, bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1), border_radius=ft.border_radius.all(8),
                        alignment=ft.alignment.center
                    ),
                    ft.Text(
                        cat["nombre"],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        width=70
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        for cat in categorias
    ]

    categorias_scroll = ft.ListView(
        controls=cat_items,
        horizontal=True,
        spacing=CAT_SPACING,  # usa la constante
        expand=False,
        on_scroll=_on_cat_scroll,  # <- clave para actualizar puntitos
    )

    categorias_container = ft.Container(
        content=categorias_scroll,
        padding=ft.padding.symmetric(horizontal=8),
        height=115,

    )

    # Indicadores tipo carrusel (puntitos)
    indicadores = ft.Row(
        controls=[],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=4,
    )

    indicadores_container = ft.Container(
        content=indicadores,
        alignment=ft.alignment.center,
        padding=ft.padding.only(top=4),
        visible=False  # se muestra sólo si hay más de 1 página
    )

    # ---------------- FUNCIÓN TARJETA (ESTILO VERTICAL) ----------------

    def tarjeta_horizontal(foto_perfil, nombre, categoria, descripcion, costo, calificacion, publicacion_id,
                           usuario_id):

        mostrar_boton = len(descripcion) > 70


        token = obtener_token(page)

        # Menú de opciones
        if token is None:
            # Usuario no logueado, menú abre modal de acceso
            menu = menu_opciones(
                page,
                modal_reporte,
                incluir_guardar=False,
                incluir_reporte=False,
                on_click_opcion=lambda e: mostrar_modal_acceso(page, cambiar_pantalla)
            )
        else:
            # Usuario logueado, menú completo
            menu = menu_opciones(
                page,
                modal_reporte,
                text_color=TEXT_COLOR,
                incluir_guardar=True,
                incluir_reporte=True,
                publicacion_id=publicacion_id,
                usuario_id=usuario_id
            )

        print("foto_perfil", foto_perfil)

        base_url = "https://lauren-extenuatory-joaquin.ngrok-free.dev/static/uploads/perfiles/"
        if foto_perfil and foto_perfil.lower() != "none":
            img_url = f"{base_url}{foto_perfil}"
        else:
            img_url = f"{base_url}defecto.png"  # imagen por defecto

        # Margenes dinámicos
        es_nombre_largo = len(nombre) > 20
        lineas_descripcion = 1 if es_nombre_largo else 2
        margen_boton = ft.margin.only(top=-5) if lineas_descripcion == 2 else ft.margin.only(top=-15)
        margen_descripcion = ft.margin.only(top=-10) if es_nombre_largo and mostrar_boton else ft.margin.only(top=-3)

        tarjeta_contenido = ft.Container(
            padding=ft.padding.only(top=8),
            content=ft.Column(
                [
                    ft.CircleAvatar(
                        content=ft.Icon(name=ft.Icons.PERSON, size=30, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREY_500,
                        width=60,
                        height=60,
                    ),
                    ft.Text(f"COP {costo}/h", size=11, color=TEXT_COLOR, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=3),
                    ft.Container(
                        content=ft.Text(
                            nombre,
                            weight=ft.FontWeight.BOLD,
                            size=17,
                            color=TEXT_COLOR,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        height=28,
                    ),

                    ft.Text("Descripción:", size=12, color=ft.Colors.BLACK54, text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        content=ft.Text(
                            descripcion,
                            size=11,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            color=TEXT_COLOR,
                            text_align=ft.TextAlign.CENTER
                        ),
                        height=30,
                        alignment=ft.alignment.center
                    ),
                    # Botón Ver más
                    ft.Container(
                        content=ft.TextButton(
                            "Ver más" if mostrar_boton else "",
                            on_click=(lambda e: abrir_modal_detalle(
                                foto_perfil, nombre, categoria, descripcion, costo, calificacion
                            )) if mostrar_boton else None,
                            style=ft.ButtonStyle(
                                color=PRIMARY_COLOR if mostrar_boton else "transparent",
                                padding=0,
                                text_style=ft.TextStyle(size=11)
                            )
                        ),
                        margin=margen_boton
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3
            )
        )

        # Botón Contactar experto fijo abajo
        boton_contactar = ft.Container(
            content=ft.OutlinedButton(
                text="Contactar experto",
                style=ft.ButtonStyle(
                    side={ft.ControlState.DEFAULT: ft.BorderSide(1, "#3EAEB1")},
                    bgcolor={ft.ControlState.HOVERED: "#3EAEB1"},
                    color={ft.ControlState.DEFAULT: "black", ft.ControlState.HOVERED: "white"},
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_600, font_family="Oswald"),
                ),
                # 🔹 Verifica sesión antes de actuar
                on_click=lambda e: mostrar_modal_acceso(page, cambiar_pantalla)
                if not token
                else contactar_experto_y_navegar(page, cambiar_pantalla, sio, user_id_global, usuario_id, nombre, categoria)
            ),
            bottom=8,
            left=10,
            right=10,
        )

        return ft.Container(
            width=179,
            height=295,
            padding=8,
            bgcolor="white",
            border_radius=14,
            border=ft.border.all(1, BORDER_COLOR),
            content=ft.Stack(
                controls=[
                    tarjeta_contenido,
                    ft.Container(
                        content=menu,
                        width=40,
                        height=40,
                        top=0,
                        right=0,
                        bgcolor="transparent"
                    ),
                    boton_contactar
                ]
            )
        )

    def obtener_datos_inicio(page):
        token = obtener_token(page)
        respuesta = inicio_api(token)
        print(respuesta)
        publicaciones_recientes = respuesta.get("publicaciones_recientes")
        publicaciones_aleatorias = respuesta.get("publicaciones_aleatorias")

        return {
            "recientes": publicaciones_recientes,
            "aleatorias": publicaciones_aleatorias
        }

    valores = obtener_datos_inicio(page)
    recientes=valores.get("recientes") or []
    aleatorias=valores.get("aleatorias") or []
    # ---------------- PUBLICACIONES ----------------

    publicaciones_container = ft.Column(
        [
            # Título centrado
            ft.Container(
                content=ft.Text("Te podría interesar", size=22, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=5, top=15)
            ),
            # Texto "Desliza →" alineado a la derecha
            ft.Container(
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=15, bottom=2),
                content=ft.Text("Desliza →", size=12, color=ft.Colors.GREY_500)
            ),
            # Carrusel
            ft.Container(
                content=ft.Row(
                    controls=[tarjeta_horizontal(**p) for p in recientes],
                    spacing=7,
                    scroll=ft.ScrollMode.HIDDEN
                ),
                padding=ft.padding.symmetric(horizontal=6)
            )
        ]
    )

    # ---------------- SECCIÓN CREA UNA CUENTA ----------------
    crear_cuenta_container = ft.Container(
        bgcolor="#F8F8F8",
        border_radius=10,
        padding=20,
        margin=ft.margin.symmetric(horizontal=8, vertical=20),
        visible= not usuario_autenticado,
        content=ft.Column(
            [
                ft.Text(
                    "¡Crea una cuenta y mejora tu experiencia!",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=TEXT_COLOR
                ),
                ft.ElevatedButton(
                    text="Crear cuenta",
                    bgcolor=PRIMARY_COLOR,
                    color="white",
                    height=32,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=20),
                        padding=ft.padding.symmetric(horizontal=25),
                        text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_500),
                    ),
                    on_click=lambda e: cambiar_pantalla("registro", origen="inicio")
                ),

                ft.TextButton(
                    text="Ingresar a mi cuenta",
                    style=ft.ButtonStyle(
                        color=TEXT_COLOR,
                        overlay_color=ft.Colors.GREY_200,
                        text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_500),
                    ),
                    on_click=lambda e: cambiar_pantalla("login")
                ),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Ajuste responsivo para la sección "Crear cuenta"
    if page.width <= 768:
        crear_cuenta_container.width = page.width - 16  # resta márgenes (8px a cada lado)
        crear_cuenta_container.margin = ft.margin.symmetric(horizontal=8, vertical=20)
    else:
        crear_cuenta_container.width = page.width * 0.9  # ocupa el 90% del ancho
        crear_cuenta_container.margin = ft.margin.symmetric(horizontal=page.width * 0.05, vertical=20)

    # ---------------- SERVICIOS DESTACADOS ----------------
    destacados_container = ft.Column(
        [
            # Título centrado
            ft.Container(
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=15, bottom=0),
                content=ft.Text("Servicios destacados", size=22, weight=ft.FontWeight.BOLD, color=TEXT_COLOR)
            ),
            # Texto "Desliza →" pegado a las tarjetas (debajo del título, alineado derecha)
            ft.Container(
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=15, bottom=2),
                content=ft.Text("Desliza →", size=12, color=ft.Colors.GREY_500)
            ),
            # Carrusel
            ft.Container(
                content=ft.Row(
                    controls=[tarjeta_horizontal(**p) for p in aleatorias],
                    spacing=7,
                    scroll=ft.ScrollMode.HIDDEN
                ),
                padding=ft.padding.symmetric(horizontal=6)
            )
        ]
    )

    # ---------------- MENÚ INFERIOR ----------------
    selected_index = 0

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
                mostrar_modal_acceso(page, cambiar_pantalla)

        elif index == 3:  # Guardados
            token = obtener_token(page)
            if token:
                cambiar_pantalla("guardados")
            else:
                mostrar_modal_acceso(page, cambiar_pantalla)

        elif index == 4:  # Menú
                cambiar_pantalla("menu")

    menu = menu_inferior(selected_index, on_bottom_nav_click)

    # ---------------- LAYOUT PRINCIPAL ----------------
    layout = ft.Column(
        controls=[
            nav,  # 🔹 Header / Navbar superior

            ft.Container(
                content=ft.Column(
                    controls=[
                        saludo_usuario,
                        contenedor_frase,
                        categorias_titulo,
                        categorias_container,
                        indicadores_container,
                        publicaciones_container,
                        crear_cuenta_container,
                        destacados_container,
                    ],
                    spacing=10  # 👈 Separación entre secciones
                ),
                padding=ft.padding.only(top=15)  # 👈 Espacio entre nav y contenido
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.HIDDEN  # 👈 Permite scroll del contenido
    )

    # Agregar layout a la página
    page.add(layout)
    _config_pagination()

    # ---------------- DETECTOR DE CAMBIO DE TAMAÑO (RESPONSIVE) ----------------
    def on_resize(e: ft.ControlEvent):
        # Ajusta el ancho del contenedor de frase
        if page.width <= 768:
            contenedor_frase.width = page.width - 16
            contenedor_frase.margin = ft.margin.symmetric(horizontal=8, vertical=5)
        else:
            contenedor_frase.width = page.width * 0.9
            contenedor_frase.margin = ft.margin.symmetric(horizontal=page.width * 0.05, vertical=5)

        # Vuelve a configurar la paginación de categorías y publicaciones
        _config_pagination()
        _config_pagination_publi()
        page.update()

    # Asigna el evento al cambio de tamaño
    page.on_resize = on_resize


    # ---------------- NAV INFERIOR (BottomAppBar) ----------------
    page.bottom_appbar = ft.BottomAppBar(
        content=menu,  # 🔹 Menú inferior (para navegación en móvil)
        bgcolor=ft.Colors.WHITE,
        elevation=0
    )

    # ---------------- RESPONSIVE ----------------
    def on_resize(e):
        layout.controls[0] = nav_bar(
            page,
            page.width,
            show_back=False,
            show_explora=False,
            show_login_icon=not usuario_autenticado,
            on_login_click=lambda e: cambiar_pantalla("login")
        )
        _config_pagination()
        page.update()

    if not usuario_autenticado:
        layout.controls[0].content.controls.insert(5, crear_cuenta_container)
    page.on_resize = on_resize
    page.update()


