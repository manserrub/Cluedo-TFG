import random
import streamlit as st
from database import (
    obtener_datos,
    obtener_hora,
    obtener_personalidad,
    obtener_personajes_detallados
)

IMAGENES_PERSONAJES = {
    "Miss Scarlet": "assets/personajes/miss_scarlet.png",
    "Coronel Mustard": "assets/personajes/coronel_mustard.png",
    "Señora Peacock": "assets/personajes/senora_peacock.png",
    "Señora White": "assets/personajes/senora_white.png",
    "Señor Green": "assets/personajes/senor_green.png",
    "Profesor Plum": "assets/personajes/profesor_plum.png"
}


def seleccion():
    st.title("🔍 Selecciona a los sospechosos")
    _mostrar_sidebar_usuario()

    if "datos_partida" not in st.session_state:
        st.session_state.datos_partida = _cargar_datos_partida()

    datos = st.session_state.datos_partida
    st.write("Selecciona al menos 2 personajes para comenzar.")

    seleccion_jugadores = _mostrar_selector_personajes(datos["personajes_detallados"])

    st.markdown("---")

    if st.button("Comenzar partida", type="primary"):
        if len(seleccion_jugadores) < 2:
            st.error("Debes elegir al menos 2 personajes")
            return

        caso, personajes_data = _generar_misterio(seleccion_jugadores, datos)

        caso["personajes"] = seleccion_jugadores
        st.session_state.caso = caso
        st.session_state.personajes = personajes_data
        st.session_state.messages_por_personaje = {}
        st.session_state.historial_detective = []
        st.session_state.pantalla = "juego"

        st.session_state.pop("datos_partida", None)
        st.rerun()


def _mostrar_sidebar_usuario():
    if not st.session_state.get("usuario_actual"):
        return

    st.sidebar.write(f"👤 {st.session_state.usuario_actual}")
    if st.session_state.get("email_actual"):
        st.sidebar.write(f"📧 {st.session_state.email_actual}")

    if st.sidebar.button("Cerrar sesión"):
        for key in [
            "logueado", "usuario_actual", "email_actual", "genero_usuario",
            "pantalla", "caso", "personajes",
            "messages_por_personaje", "historial_detective",
            "cuaderno_notas", "intentos_acusacion", "partida_terminada",
            "datos_partida"
        ]:
            st.session_state.pop(key, None)
        st.rerun()


@st.cache_data(show_spinner=False)
def _cargar_datos_partida():
    return {
        "personajes_detallados": obtener_personajes_detallados(),
        "victimas": obtener_datos("victimas"),
        "armas": obtener_datos("armas"),
        "habitaciones": obtener_datos("habitaciones"),
        "motivos": obtener_datos("motivos"),
        "horas": obtener_hora()
    }


def _mostrar_selector_personajes(personajes_detallados):
    seleccionados = []
    cols_por_fila = 3

    for i in range(0, len(personajes_detallados), cols_por_fila):
        fila = personajes_detallados[i:i + cols_por_fila]
        cols = st.columns(cols_por_fila)

        for j, personaje in enumerate(fila):
            nombre = personaje["nombre"]
            personalidad = personaje.get("personalidad", "Sin personalidad definida")
            forma_habla = personaje.get("forma_habla", "Sin forma de hablar definida")
            descripcion = personaje.get("descripcion", "")

            with cols[j]:
                with st.container(border=True):
                    ruta_imagen = IMAGENES_PERSONAJES.get(nombre)
                    if ruta_imagen:
                        st.image(ruta_imagen, use_container_width=True)
                    else:
                        st.markdown("### 👤")

                    st.markdown(f"### {nombre}")

                    if descripcion:
                        st.caption(descripcion)

                    st.markdown(f"**Personalidad:** {personalidad}")
                    st.markdown(f"**Forma de hablar:** {forma_habla}")

                    marcado = st.checkbox(
                        f"Seleccionar a {nombre}",
                        key=f"check_{nombre}"
                    )

                    if marcado:
                        seleccionados.append(nombre)

    return seleccionados


def _generar_misterio(seleccion_jugadores, datos):
    caso = {
        "asesino": random.choice(seleccion_jugadores),
        "victima": random.choice(datos["victimas"]),
        "arma": random.choice(datos["armas"]),
        "habitacion": random.choice(datos["habitaciones"]),
        "hora": random.choice(datos["horas"]),
        "motivo": random.choice(datos["motivos"])
    }

    personajes_data = _crear_roles_partida(
        seleccion_jugadores=seleccion_jugadores,
        caso=caso,
        habitaciones=datos["habitaciones"]
    )

    return caso, personajes_data


def _crear_roles_partida(seleccion_jugadores, caso, habitaciones):
    personajes_data = {}
    asesino = caso["asesino"]

    inocentes = [p for p in seleccion_jugadores if p != asesino]
    chivo_expiatorio = random.choice(inocentes) if inocentes else None

    habitaciones_falsas = [l for l in habitaciones if l != caso["habitacion"]]
    habitacion_coartada = random.choice(habitaciones_falsas) if habitaciones_falsas else caso["habitacion"]

    focos_base = ["habitacion", "arma", "motivo", "comportamiento"]
    focos_asignados = []

    while len(focos_asignados) < len(inocentes):
        random.shuffle(focos_base)
        focos_asignados.extend(focos_base)

    mapa_focos = {
        inocente: focos_asignados[i]
        for i, inocente in enumerate(inocentes)
    }

    inocentes_con_sospecha_real = set(
        random.sample(inocentes, k=min(2, len(inocentes)))
    ) if inocentes else set()

    for personaje in seleccion_jugadores:
        p_info = obtener_personalidad(personaje)

        if personaje == asesino:
            personajes_data[personaje] = _crear_datos_asesino(
                caso=caso,
                habitacion_coartada=habitacion_coartada,
                chivo_expiatorio=chivo_expiatorio,
            )
        else:
            foco = mapa_focos[personaje]
            sospecha_real = personaje in inocentes_con_sospecha_real

            personajes_data[personaje] = _crear_datos_inocente(
                personaje=personaje,
                seleccion_jugadores=seleccion_jugadores,
                caso=caso,
                asesino=asesino,
                foco=foco,
                sospecha_real=sospecha_real
            )

    return personajes_data


def _crear_datos_asesino(caso, habitacion_coartada, chivo_expiatorio):
    tema_sensible = random.choice(["arma", "habitacion", "hora", "motivo", "victima"])

    return {
        "rol": "asesino",
        "coartada": f"Estabas en {habitacion_coartada} cuando ocurrió todo",
        "motivo_real": caso["motivo"],
        "chivo": chivo_expiatorio,
        "tema_sensible": tema_sensible
    }


def _crear_datos_inocente(personaje, seleccion_jugadores, caso, asesino, foco, sospecha_real):
    sospechoso, certeza = _generar_sospecha_inocente(
        personaje=personaje,
        seleccion_jugadores=seleccion_jugadores,
        asesino=asesino,
        sospecha_real=sospecha_real
    )

    verdad_1, verdad_2 = _generar_pistas_por_foco(caso, foco, sospechoso)
    confusion = _pista_falsa(caso)

    return {
        "rol": "inocente",
        "foco": foco,
        "verdad_1": verdad_1,
        "verdad_2": verdad_2,
        "confusion": confusion,
        "sospechoso": sospechoso,
        "certeza": certeza,
    }


def _generar_sospecha_inocente(personaje, seleccion_jugadores, asesino, sospecha_real=False):
    otros = [p for p in seleccion_jugadores if p != personaje]

    if sospecha_real and asesino in otros:
        return asesino, random.choice(["baja", "media"])

    candidatos = [p for p in otros if p != asesino]
    sospechoso = random.choice(candidatos) if candidatos else random.choice(otros)
    return sospechoso, "falsa"


def _generar_pistas_por_foco(caso, foco, sospechoso):
    if foco == "habitacion":
        return (
            f"Esa noche te fijaste en que había una tensión extraña alrededor de {caso['habitacion']}.",
            f"No te sorprendió ver a {sospechoso} rondando cerca de {caso['habitacion']} en un momento extraño."
        )

    if foco == "arma":
        return (
            f"Te llamó la atención que {caso['arma']} no estaba donde normalmente debería estar.",
            f"Tienes la impresión de que {caso['arma']} pudo haber sido utilizada en lo ocurrido."
        )

    if foco == "motivo":
        return (
            f"Sabías que existía un conflicto serio relacionado con {caso['motivo']}.",
            f"Crees que {caso['motivo']} pudo ser la causa real de lo sucedido."
        )

    return (
        f"Viste a una persona actuar con nerviosismo cerca de {caso['habitacion']} después de lo sucedido.",
        f"La actitud de {sospechoso} te pareció especialmente extraña justo después de las {caso['hora']}."
    )


def _pista_falsa(caso):
    habitaciones_falsas = [l for l in ["el salón", "la cocina", "el jardín", "la biblioteca", "el estudio"] if l != caso["habitacion"]]
    armas_falsas = [a for a in ["cuchillo", "cuerda", "pistola", "veneno", "candelabro"] if a != caso["arma"]]

    tipos = []
    if habitaciones_falsas:
        tipos.append("habitacion")
    if armas_falsas:
        tipos.append("arma")

    if not tipos:
        return "No recuerdas bien los detalles de esa noche."

    tipo = random.choice(tipos)

    if tipo == "habitacion":
        return f"Crees que el crimen ocurrió en {random.choice(habitaciones_falsas)}"

    return f"Crees que el crimen se produjo con {random.choice(armas_falsas)}"