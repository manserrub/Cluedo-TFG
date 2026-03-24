import streamlit as st
import random
from database import obtener_datos, obtener_secretos, obtener_hora, obtener_personalidad


def seleccion():
    st.title("🔍 Selecciona tus personajes")
    _mostrar_sidebar_usuario()

    datos = _cargar_datos_partida()

    seleccion_jugadores = st.multiselect(
        "Elige tus personajes (mínimo 2)",
        datos["personajes"]
    )

    if st.button("Comenzar partida"):
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
            "cuaderno_notas", "intentos_acusacion", "partida_terminada"
        ]:
            st.session_state.pop(key, None)
        st.rerun()


def _cargar_datos_partida():
    return {
        "personajes": obtener_datos("personajes"),
        "victimas": obtener_datos("victimas"),
        "armas": obtener_datos("armas"),
        "lugares": obtener_datos("lugares"),
        "motivos": obtener_datos("motivos"),
        "secretos": obtener_secretos(),
        "horas": obtener_hora()
    }


def _generar_misterio(seleccion_jugadores, datos):
    asesino = random.choice(seleccion_jugadores)
    victima = random.choice(datos["victimas"])
    lugar = random.choice(datos["lugares"])
    hora = random.choice(datos["horas"])
    arma = random.choice(datos["armas"])
    motivo = random.choice(datos["motivos"])

    caso = {
        "victima": victima,
        "asesino": asesino,
        "arma": arma,
        "lugar": lugar,
        "hora": hora,
        "motivo": motivo
    }

    personajes_data = _crear_roles_partida(
        seleccion_jugadores=seleccion_jugadores,
        caso=caso,
        lugares=datos["lugares"],
        secretos=datos["secretos"]
    )

    return caso, personajes_data


def _crear_roles_partida(seleccion_jugadores, caso, lugares, secretos):
    personajes_data = {}
    asesino = caso["asesino"]

    inocentes = [p for p in seleccion_jugadores if p != asesino]
    chivo_expiatorio = random.choice(inocentes) if inocentes else None

    lugares_falsos = [l for l in lugares if l != caso["lugar"]]
    lugar_coartada = random.choice(lugares_falsos) if lugares_falsos else caso["lugar"]

    secretos_disponibles = secretos.copy()
    random.shuffle(secretos_disponibles)

    focos = ["hora", "lugar", "arma", "motivo", "comportamiento"]
    random.shuffle(focos)

    for i, personaje in enumerate(seleccion_jugadores):
        secreto = secretos_disponibles[i % len(secretos_disponibles)]
        p_info = obtener_personalidad(personaje)
        resistencia = p_info.get("nivel_resistencia", 2)

        if personaje == asesino:
            personajes_data[personaje] = _crear_datos_asesino(
                caso=caso,
                resistencia=resistencia,
                lugar_coartada=lugar_coartada,
                chivo_expiatorio=chivo_expiatorio,
                secreto=secreto
            )
        else:
            foco = focos[i % len(focos)]
            personajes_data[personaje] = _crear_datos_inocente(
                personaje=personaje,
                seleccion_jugadores=seleccion_jugadores,
                caso=caso,
                asesino=asesino,
                resistencia=resistencia,
                secreto=secreto,
                foco=foco
            )

    return personajes_data


def _crear_datos_asesino(caso, resistencia, lugar_coartada, chivo_expiatorio, secreto):
    tema_sensible = random.choice(["arma", "lugar", "hora", "motivo", "victima"])

    return {
        "rol": "asesino",
        "resistencia": resistencia,
        "coartada": f"Estabas en {lugar_coartada} cuando ocurrió todo",
        "motivo_real": caso["motivo"],
        "chivo": chivo_expiatorio,
        "secreto": secreto,
        "tema_sensible": tema_sensible
    }


def _crear_datos_inocente(personaje, seleccion_jugadores, caso, asesino, resistencia, secreto, foco):
    sospechoso, certeza = _generar_sospecha_inocente(
        personaje=personaje,
        seleccion_jugadores=seleccion_jugadores,
        asesino=asesino
    )

    verdad_1, verdad_2, verdad_3 = _generar_pistas_por_foco(caso, foco)
    confusion = _pista_falsa(caso)

    return {
        "rol": "inocente",
        "resistencia": resistencia,
        "presiones": 0,
        "foco": foco,
        "verdad_1": verdad_1,
        "verdad_2": verdad_2,
        "verdad_3": verdad_3,
        "confusion": confusion,
        "sospechoso": sospechoso,
        "certeza": certeza,
        "secreto": secreto
    }


def _generar_sospecha_inocente(personaje, seleccion_jugadores, asesino):
    otros = [p for p in seleccion_jugadores if p != personaje]

    if random.random() < 0.4 and asesino in otros:
        return asesino, "baja"

    candidatos = [p for p in otros if p != asesino]
    sospechoso = random.choice(candidatos) if candidatos else random.choice(otros)
    return sospechoso, "falsa"


def _generar_pistas_por_foco(caso, foco):
    if foco == "hora":
        return (
            f"No recuerdas con exactitud todo, pero sabes que algo raro ocurrió cerca de las {caso['hora']}.",
            f"Escuchaste movimiento o pasos poco antes o poco después de las {caso['hora']}.",
            f"Estás casi seguro/a de que el momento clave del crimen fue exactamente alrededor de las {caso['hora']}."
        )

    if foco == "lugar":
        return (
            f"Esa noche te fijaste en que había tensión alrededor de {caso['lugar']}.",
            f"Viste a alguien merodeando cerca de {caso['lugar']} cuando no parecía tener motivo para estar allí.",
            f"Estás casi seguro/a de que todo ocurrió en o junto a {caso['lugar']}."
        )

    if foco == "arma":
        return (
            f"Algo te llamó la atención porque un objeto no estaba donde solía estar.",
            f"Crees haber visto {caso['arma']} fuera de su sitio habitual esa noche.",
            f"Estás casi seguro/a de que el objeto implicado en el crimen fue {caso['arma']}."
        )

    if foco == "motivo":
        return (
            f"Sabías que la víctima arrastraba tensiones con alguien de la casa.",
            f"Te consta que había un conflicto serio con {caso['victima']} relacionado con {caso['motivo']}.",
            f"Estás convencido/a de que el motivo real del crimen fue {caso['motivo']}."
        )

    return (
        f"Notaste a alguien especialmente alterado/a antes de que todo ocurriera.",
        f"Viste a una persona salir nerviosa del entorno de {caso['lugar']} tras lo sucedido.",
        f"Recuerdas a alguien con expresión extraña, como si intentara ocultar algo, justo después de las {caso['hora']}."
    )


def _pista_falsa(caso):
    lugares_falsos = ["el salón", "la cocina", "el jardín", "la biblioteca", "el estudio"]
    lugares_falsos = [l for l in lugares_falsos if l != caso["lugar"]]

    horas_falsas = ["las 21:00", "las 23:30", "la medianoche", "las 22:00"]
    horas_falsas = [h for h in horas_falsas if h != caso["hora"]]

    tipos = []
    if lugares_falsos:
        tipos.append("lugar")
    if horas_falsas:
        tipos.append("hora")

    if not tipos:
        return "No recuerdas bien los detalles de esa noche."

    tipo = random.choice(tipos)

    if tipo == "lugar":
        return f"Crees que el crimen ocurrió en {random.choice(lugares_falsos)}"
    return f"Crees que el crimen ocurrió alrededor de {random.choice(horas_falsas)}"