import streamlit as st
from logic.database import (
    obtener_datos,
    obtener_hora,
    obtener_personajes_detallados,
)
from logic.game_logic import generar_misterio
from screens.inicio import mostrar_confirmacion_borrado

IMAGENES_PERSONAJES = {
    "Miss Scarlet": "assets/personajes/miss_scarlet.png",
    "Coronel Mustard": "assets/personajes/coronel_mustard.png",
    "Señora Peacock": "assets/personajes/senora_peacock.png",
    "Señora White": "assets/personajes/senora_white.png",
    "Señor Green": "assets/personajes/senor_green.png",
    "Profesor Plum": "assets/personajes/profesor_plum.png",
}


def seleccion():
    st.title("Selecciona a los sospechosos")

    st.session_state.setdefault("mostrar_confirmacion_borrado", False)
    _mostrar_sidebar_usuario()

    if "datos_partida" not in st.session_state:
        st.session_state.datos_partida = _cargar_datos_partida()

    datos = st.session_state.datos_partida
    st.write("Selecciona al menos 2 personajes para comenzar.")

    seleccion_jugadores = _mostrar_selector_personajes(datos["personajes_detallados"])

    st.divider()

    if st.button("Comenzar partida", type="primary", width='stretch'):
        if len(seleccion_jugadores) < 2:
            st.error("Debes elegir al menos 2 personajes")
            return

        caso, personajes_data = generar_misterio(seleccion_jugadores, datos)

        caso["personajes"] = seleccion_jugadores
        st.session_state.caso = caso
        st.session_state.personajes = personajes_data
        st.session_state.messages_por_personaje = {}
        st.session_state.historial_detective = []
        st.session_state.pantalla = "juego"
        st.session_state.personajes_seleccionados = seleccion_jugadores

        st.session_state.pop("datos_partida", None)
        st.rerun()


def _mostrar_sidebar_usuario():
    with st.sidebar:
        st.markdown("### ⚠️ Cuenta")
        st.write(f"👤 {st.session_state.usuario_actual}")
        if st.session_state.get("email_actual"):
            st.write(f"📧 {st.session_state.email_actual}")

        if st.button("Cerrar sesión", width='stretch'):
            for key in [
                "logueado", "usuario_actual", "email_actual", "genero_usuario",
                "pantalla", "caso", "personajes",
                "messages_por_personaje", "historial_detective",
                "cuaderno_notas", "intentos_acusacion", "partida_terminada",
                "datos_partida", "mostrar_confirmacion_borrado",
                "personajes_seleccionados"
            ]:
                st.session_state.pop(key, None)
            st.rerun()

        st.divider()

        if st.sidebar.button("🗑️ Borrar cuenta", width='stretch'):
            st.session_state.mostrar_confirmacion_borrado = True
            st.rerun()
        mostrar_confirmacion_borrado()


@st.cache_data(show_spinner=False)
def _cargar_datos_partida():
    return {
        "personajes_detallados": obtener_personajes_detallados(),
        "victimas": obtener_datos("victimas"),
        "armas": obtener_datos("armas"),
        "habitaciones": obtener_datos("habitaciones"),
        "horas": obtener_hora(),
    }


def _mostrar_selector_personajes(personajes_detallados):
    cols_por_fila = 3

    for i in range(0, len(personajes_detallados), cols_por_fila):
        fila = personajes_detallados[i:i + cols_por_fila]
        cols = st.columns(cols_por_fila)

        for j, personaje in enumerate(fila):
            nombre = personaje["nombre"]
            personalidad = personaje.get("personalidad", "Sin personalidad definida")
            descripcion = personaje.get("descripcion", "")

            with cols[j]:
                with st.container(border=True):
                    ruta_imagen = IMAGENES_PERSONAJES.get(nombre)
                    if ruta_imagen:
                        st.image(ruta_imagen, width='stretch')
                    else:
                        st.markdown("### 👤")

                    st.markdown(f"### {nombre}")

                    if descripcion:
                        st.caption(descripcion)

                    st.markdown(f"**Personalidad:** {personalidad}")

                    st.checkbox(
                        f"Seleccionar a {nombre}",
                        key=f"check_{nombre}",
                    )

    return [
        personaje["nombre"]
        for personaje in personajes_detallados
        if st.session_state.get(f"check_{personaje['nombre']}", False)
    ]




