import flet as ft
from flet import Icons
from app.components.ModalReporte import ModalReporte
from app.components.nav import nav_bar
from app.components.menu_inferior import menu_inferior
from app.components.ModalTarjetaCompleta import ModalTarjetaCompleta
from app.components.MenuTarjetasOpciones import menu_opciones
from app.API_services.traer_publicaciones import traer_publicaciones_usu
from app.components.ModalAcceso import mostrar_modal_acceso
from app.components.chat_navigation import contactar_experto_y_navegar

def custom_expansion(page, title, controls_list):
    toggle_icon = ft.Icon(name=ft.Icons.KEYBOARD_ARROW_DOWN, color="#3EAEB1")

    styled_controls = []
    for control in controls_list:
        if isinstance(control, ft.Radio):
            control.label_style = ft.TextStyle(
                color="#666666",
                weight=ft.FontWeight.W_500
            )
        elif isinstance(control, ft.Checkbox):
            control.label_style = ft.TextStyle(
                color="#666666",
                weight=ft.FontWeight.W_500
            )
        styled_controls.append(control)

    content_column = ft.Column(styled_controls, visible=False, spacing=5)

    def toggle_visibility(e):
        content_column.visible = not content_column.visible
        toggle_icon.name = (
            ft.Icons.KEYBOARD_ARROW_UP if content_column.visible else ft.Icons.KEYBOARD_ARROW_DOWN
        )
        page.update()

    return ft.Column(
        [
            ft.GestureDetector(
                on_tap=toggle_visibility,
                content=ft.Row(
                    [
                        ft.Text(
                            title,
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color="black"
                        ),
                        toggle_icon,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            content_column
        ],
        spacing=8
    )

def publicaciones(page: ft.Page, cambiar_pantalla, sio=None, user_id_global=None, origen=None):
    # ---------------- CONFIGURACIÓN GENERAL ----------------
    page.fonts = {
        "Oswald": "https://raw.githubusercontent.com/google/fonts/main/ofl/oswald/Oswald%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Oswald")
    page.theme_mode = "light"
    page.bgcolor = "#F8F8F8"
    page.title = "Inicio"
    page.scroll = ft.ScrollMode.HIDDEN
    page.padding = 1

    PRIMARY_COLOR = "#3EAEB1"
    TEXT_COLOR = "#000000"
    BORDER_COLOR = "#D9D9D9"

    #---------------------------------------------

    def obtener_token(page):
        return getattr(page, "session_token", None)

    def obtener_publicaciones(categoria_id=None, subcategoria_id=None, tiempo=None):
        datos = {}
        if categoria_id and categoria_id !="Todas":
            datos["categoria_id"] = categoria_id

        if subcategoria_id:
            datos["subcategoria_id"] = subcategoria_id

        if tiempo and tiempo !="Todas":
            datos["tiempo"] = tiempo

        publicaciones = traer_publicaciones_usu(datos)
        print(publicaciones)

        lista = []
        for pub in publicaciones.get("publicaciones_generales", []):
            lista.append({
                "nombre": pub.get("nombre_experto"),
                "profesion": pub.get("subcategoria"),
                "descripcion": pub.get("descripcion"),
                "costo": pub.get("costo"),
                "usuario_id":pub.get("usuario_id"),
                "publicacion_id":pub.get("publicacion_id"),
                "foto_perfil": pub.get("foto_perfil")
            })

        return {
            "lista": lista,
            "categorias": publicaciones.get("categorias", []),
            "total_resultados": publicaciones.get("total_resultados", 0),
            "categoria_seleccionada": publicaciones.get("categoria_selecionada")
        }

    if origen and "categoria_id" in origen:
        cat_id = origen["categoria_id"]
        resultado = obtener_publicaciones(categoria_id=cat_id)
    else:
        resultado = obtener_publicaciones()

    publicaciones_filtradas = resultado["lista"]

    # ---------------- REFERENCIAS PARA FILTROS ----------------
    categoria_ref = ft.Ref[ft.RadioGroup]()
    fecha_ref = ft.Ref[ft.RadioGroup]()

    # ---------------- INSTANCIA DEL MODAL ----------------
    modal_reporte = ModalReporte()
    page.overlay.append(modal_reporte.dialog)

    modal_detalle = ModalTarjetaCompleta()
    page.overlay.append(modal_detalle.dialog)

    def abrir_modal_detalle(foto_perfil, nombre, profesion, descripcion, costo, calificacion):
        print("CLICK -> abrir_modal_detalle:", nombre)
        modal_detalle.set_content(foto_perfil, nombre, profesion, descripcion, costo, calificacion, page)
        modal_detalle.dialog.open = True  # ✅ solo controlamos el .open
        page.update()

    overlay = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        width=page.width,
        height=page.height,
        visible=False,
        on_click=lambda e: cerrar_filtros(),
    )

    def aplicar_filtros(e):
        categoria = categorias.value
        fecha = fechas.value
        print(f"Categoria seleccionada: {categoria}, fecha seleccionada: {fecha}")

        filtrar_publicaciones = obtener_publicaciones(categoria_id=categoria, subcategoria_id=None, tiempo=fecha)

        publicaciones_filtradas = filtrar_publicaciones["lista"]
        total_filtradas = len(publicaciones_filtradas)
        print(f"Publicaciones filtradas: {publicaciones_filtradas}")

        grid_column.controls.clear()
        for i in range(0, len(publicaciones_filtradas), 2):
            fila = ft.Container(
                content=ft.Row(
                    controls=[tarjeta_horizontal(**publicaciones_filtradas[i])] +
                             ([tarjeta_horizontal(**publicaciones_filtradas[i + 1])]
                              if i + 1 < len(publicaciones_filtradas) else []),
                    spacing=7,
                    alignment=ft.MainAxisAlignment.START
                ),
                padding=ft.padding.symmetric(horizontal=5)
            )
            grid_column.controls.append(fila)

        resultado_texto.value = f"{total_filtradas} resultados"
        page.update()
        cerrar_filtros()

    categorias = ft.RadioGroup(
        ref=categoria_ref,
        content=ft.Column(
            [
                ft.Radio(value="Todas", label="Todas"),
                ft.Radio(value="1", label="Reparación y Mantenimiento"),
                ft.Radio(value="2", label="Cuidado y Asistencia"),
                ft.Radio(value="3", label="Bienestar de Mascotas"),
                ft.Radio(value="4", label="Educativos y aprendizaje"),
                ft.Radio(value="5", label="Hogar y Limpieza"),
                ft.Radio(value="6", label="Construcción y Remodelación"),
                ft.Radio(value="7", label="Artísticos y creatividad visual"),
                ft.Radio(value="8", label="Movilidad y transporte"),
                ft.Radio(value="9", label="Gastronomía"),
                ft.Radio(value="10", label="Eventos"),
                ft.Radio(value="11", label="Bienestar Personal"),
            ]
        )
    )

    fechas = ft.RadioGroup(
        ref=fecha_ref,
        content=ft.Column(
            [
                ft.Radio(value="Todas", label="Todas"),
                ft.Radio(value="24h", label="Últimas 24 horas"),
                ft.Radio(value="semana", label="Esta semana"),
                ft.Radio(value="mes", label="Este mes"),
            ],
            spacing=5
        )
    )

    # ⚡ Panel de filtros lateral
    filtros_panel = ft.Container(
        bgcolor="white",
        width=250,
        height=page.height,  # ahora sí ocupa todo
        right=page.width,
        top=0,
        animate_position=300,
        content=ft.Column(
            [
                # Header fijo arriba
                ft.Container(
                    bgcolor="#F8F8F8",
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    content=ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.ARROW_BACK,
                                on_click=lambda e: cerrar_filtros(),
                                icon_color="#3EAEB1",
                            ),
                            ft.Text(
                                "Filtrar",
                                size=20,
                                weight=ft.FontWeight.W_500,
                                font_family="Oswald",
                                color="black"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ),

                # Contenido con scroll
                ft.Container(
                    expand=True,  # 🔹 ocupa todo el espacio intermedio
                    padding=ft.padding.all(15),
                    content=ft.Column(
                        [
                            custom_expansion(page, "Categorías", [categorias]),
                            ft.Text(
                                "Fecha de publicación",
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color="black"
                            ),
                            fechas
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO  # ✅ solo esta parte hace scroll
                    )
                ),

                # Footer fijo con botones
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                "Aplicar",
                                width=100,
                                height=40,
                                bgcolor=PRIMARY_COLOR,
                                color="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=30),
                                    padding=8
                                ),
                                on_click=aplicar_filtros
                            ),
                            ft.OutlinedButton(
                                "Limpiar filtros",
                                width=100,
                                height=40,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=30),
                                    padding=8,
                                    color="black"
                                ),
                                on_click=lambda e: (
                                    setattr(categorias, "value", None),
                                    setattr(fechas, "value", None),
                                    page.update(),
                                    print("Filtros limpiados")
                                )
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20
                    ),
                    padding=ft.padding.all(10),
                    bgcolor="white",
                    height=60  # 🔹 altura fija para que siempre quede visible
                ),
            ],
            spacing=0,
            expand=True
        )
    )

    def abrir_filtros(e=None):
        nonlocal saved_bottom
        # Guardamos y ocultamos el bottom appbar para que el panel se sobreponga
        saved_bottom = page.bottom_appbar
        page.bottom_appbar = None

        filtros_panel.right = page.width - 250  # mueve el panel a la vista
        overlay.visible = True
        page.update()

    def cerrar_filtros(e=None):
        nonlocal saved_bottom
        # Restauramos el bottom appbar
        page.bottom_appbar = saved_bottom

        filtros_panel.right = page.width
        overlay.visible = False
        page.update()

    resultado_texto = ft.Text(
        f"{len(publicaciones_filtradas)} resultados",
        weight=ft.FontWeight.BOLD,
        size=14,
        color="#666666"
    )

    header_resultados = ft.Container(
        content=ft.Column(
            [
                ft.ElevatedButton(
                    "Filtros",
                    bgcolor=PRIMARY_COLOR,
                    color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=6)
                    ),
                    on_click=abrir_filtros
                ),
                resultado_texto,
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=10,
        alignment=ft.alignment.top_left
    )

    # ---------------- FUNCIÓN TARJETAS ----------------
    def tarjeta_horizontal(foto_perfil, nombre, profesion, descripcion, costo, usuario_id, publicacion_id,
                           calificacion=4):
        mostrar_boton = len(descripcion) > 70


        token = obtener_token(page)

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

        base_url = "https://lauren-extenuatory-joaquin.ngrok-free.dev/static/uploads/perfiles/"
        if foto_perfil and foto_perfil.lower() != "none":
            img_url = f"{base_url}{foto_perfil}"
        else:
            img_url = f"{base_url}defecto.png"

        tarjeta_contenido = ft.Container(
            padding=ft.padding.only(top=7),
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



                    ft.Container(
                        content=ft.Text(
                            profesion,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        height=40,
                    ),

                    ft.Text("Descripción:", size=12, color=ft.Colors.BLACK54, text_align=ft.TextAlign.CENTER),

                    ft.Container(
                        content=ft.Text(
                            descripcion,
                            size=11,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            color=TEXT_COLOR,
                            text_align=ft.TextAlign.CENTER
                        ),
                        height=18,
                        alignment=ft.alignment.center
                    ),

                    # Botón Ver más más pegado a descripción
                    ft.Container(
                        content=ft.TextButton(
                            "Ver más" if mostrar_boton else "",
                            on_click=(lambda e: abrir_modal_detalle(
                                foto_perfil, nombre, profesion, descripcion, costo, calificacion
                            )) if mostrar_boton else None,
                            style=ft.ButtonStyle(
                                color=PRIMARY_COLOR if mostrar_boton else "transparent",
                                padding=0,
                                text_style=ft.TextStyle(size=11)
                            )
                        ),
                        margin=ft.margin.only(top=-6)
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3
            )
        )

        # Botón Contactar experto fijo abajo
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
                # ---------------------------------------------------------------------------------
                # ✅ NUEVA LÓGICA DE CONTACTO Y NAVEGACIÓN
                # ---------------------------------------------------------------------------------
                on_click=lambda e: contactar_experto_y_navegar(
                    page,
                    cambiar_pantalla,
                    sio,
                    user_id_global,
                    usuario_id,  # ID del experto (receptor_id)
                    nombre,  # Nombre del experto (receptor_nombre)
                    profesion  # Profesión/subcategoría (categoría)
                ) if token
                else mostrar_modal_acceso(page, cambiar_pantalla)
                # ---------------------------------------------------------------------------------
            ),
            bottom=8,
            left=10,
            right=10,
        )

        # Ajuste dinámico de ancho de tarjeta
        tarjeta_width = (
            page.width * 0.47 if page.width <= 480 else 179
        )

        return ft.Container(
            width=tarjeta_width,
            height=310,
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

    filas = []
    grid_column = ft.Column(
        filas,
        spacing=7,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    grid_column.controls.clear()
    publicaciones = publicaciones_filtradas
    for i in range(0, len(publicaciones), 2):
        fila = ft.Container(
            content=ft.Row(
                controls=[tarjeta_horizontal(**publicaciones[i])] +
                         ([tarjeta_horizontal(**publicaciones[i + 1])]
                          if i + 1 < len(publicaciones) else []),
                spacing=7,
                alignment=(
                    ft.MainAxisAlignment.CENTER if page.width <= 480
                    else ft.MainAxisAlignment.START
                ),
                wrap=True  # 🔹 Permite que salten de línea si no caben
            ),
            padding=ft.padding.symmetric(horizontal=5)
        )

        grid_column.controls.append(fila)

    back_action = lambda e: cambiar_pantalla("categorias") if origen == "categorias" else cambiar_pantalla("menu")

    layout = ft.Column(
        [
            nav_bar(
                page,
                page.width,
                show_back=True,
                show_explora=True,
                on_back_click=back_action
            ),
            ft.Column(
                [
                    header_resultados,
                    grid_column
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ],
        spacing=10,
        expand=True
    )

    selected_index = 4

    def on_bottom_nav_click(index):
        if index == 0:
            cambiar_pantalla("inicio")
        elif index == 1:
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
        elif index == 4:
            cambiar_pantalla("menu")

    menu = menu_inferior(selected_index, on_bottom_nav_click)
    page.bottom_appbar = ft.BottomAppBar(
        content=menu,
        bgcolor=ft.Colors.WHITE,
        elevation=0,
    )

    page.overlay.append(overlay)
    page.overlay.append(filtros_panel)

    saved_bottom = None

    page.add(layout)
    page.update()
