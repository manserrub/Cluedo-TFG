import streamlit as st
import random
from database import obtener_datos
from conversaciones.conversacion import conversacion_personaje

def juego():
    caso       = st.session_state.caso
    personajes = st.session_state.personajes

    if "todas_armas" not in st.session_state:
        armas = obtener_datos("armas")
        random.shuffle(armas)
        st.session_state.todas_armas = armas

    if "todos_lugares" not in st.session_state:
        lugares = obtener_datos("lugares")
        random.shuffle(lugares)
        st.session_state.todos_lugares = lugares

    st.session_state.setdefault("cuaderno_notas", "")
    st.session_state.setdefault("intentos_acusacion", 3)
    st.session_state.setdefault("partida_terminada", False)

    todas_armas   = st.session_state.todas_armas
    todos_lugares = st.session_state.todos_lugares

    with st.sidebar:
        st.markdown("### 🔍 El caso")
        st.write(f"**Víctima:** {caso['victima']}")
        st.write(f"**Hora:** {caso['hora']}")
        st.write(f"**Sospechosos:** {', '.join(caso['personajes'])}")
        st.divider()

        st.markdown("### 📓 Cuaderno del detective")
        st.text_area(
            "Notas del caso",
            key="cuaderno_notas",
            height=220,
            placeholder="Escribe aquí tus deducciones, contradicciones y pistas importantes..."
        )

        if st.button("🧹 Limpiar notas"):
            st.session_state.cuaderno_notas = ""
            st.rerun()

        st.divider()

        st.markdown("### 🎯 Realizar acusación")

        acusado   = st.selectbox("Asesino", caso["personajes"], key="ac_asesino")
        arma_sel  = st.selectbox("Arma",    todas_armas,        key="ac_arma")
        lugar_sel = st.selectbox("Lugar",   todos_lugares,      key="ac_lugar")

        if st.session_state.partida_terminada:
            st.warning("La partida ha terminado. Ya no puedes realizar más acusaciones.")
        else:
            if st.button("⚖️ Acusar", type="primary"):
                _resolver_acusacion(acusado, arma_sel, lugar_sel, caso)

        st.divider()
        if st.button("🔄 Nueva partida"):
            for key in [
                "caso", "personajes", "messages_por_personaje",
                "historial_detective", "todas_armas", "todos_lugares",
                "cuaderno_notas", "intentos_acusacion", "partida_terminada"
            ]:
                st.session_state.pop(key, None)
            st.session_state.pantalla = "seleccion"
            st.rerun()

    st.title("🔍 El caso comienza")
    st.caption(f"Investiga la muerte de **{caso['victima']}**. Interroga a los sospechosos y resuelve el caso.")

    if st.session_state.partida_terminada:
        st.info("La investigación ha concluido. Puedes revisar las conversaciones, pero no continuar los interrogatorios.")
        st.error(
            f"La solución era: {caso['asesino']} mató a {caso['victima']} "
            f"con {caso['arma']} en {caso['lugar']}. "
            f"El motivo era: {caso['motivo']}"
        )

    nombres = list(personajes.keys())
    choice = st.selectbox("¿Con quién quieres hablar?", nombres)
    st.divider()
    conversacion_personaje(choice, personajes[choice], caso)


def _resolver_acusacion(acusado, arma, lugar, caso):
    acierto_asesino = acusado == caso["asesino"]
    acierto_arma    = arma.lower()  in caso["arma"].lower()  or caso["arma"].lower()  in arma.lower()
    acierto_lugar   = lugar.lower() in caso["lugar"].lower() or caso["lugar"].lower() in lugar.lower()

    if acierto_asesino and acierto_arma and acierto_lugar:
        st.session_state.partida_terminada = True
        st.balloons()
        st.success(
            f"🎉 ¡Correcto! {caso['asesino']} mató a {caso['victima']} "
            f"con {caso['arma']} en {caso['lugar']}."
        )
        st.info(f"El motivo era: {caso['motivo']}")
        return

    st.session_state.intentos_acusacion -= 1

    errores = []
    if not acierto_asesino:
        errores.append("el asesino")
    if not acierto_arma:
        errores.append("el arma")
    if not acierto_lugar:
        errores.append("el lugar")

    if st.session_state.intentos_acusacion > 0:
        st.error(
            f"❌ Acusación incorrecta. Te has equivocado en: {', '.join(errores)}. "
            f"Te quedan {st.session_state.intentos_acusacion} oportunidades."
        )
    else:
        st.session_state.partida_terminada = True
        st.error("❌ Has agotado tus 3 oportunidades.")
