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

    todas_armas   = st.session_state.todas_armas
    todos_lugares = st.session_state.todos_lugares

    with st.sidebar:
        st.markdown("### 🔍 El caso")
        st.write(f"**Víctima:** {caso['victima']}")
        st.write(f"**Hora:** {caso['hora']}")
        st.divider()
        st.write(f"**Sospechosos:** {', '.join(caso['personajes'])}")
        st.divider()

        st.markdown("### 🎯 Realizar acusación")
        acusado   = st.selectbox("Asesino", caso["personajes"], key="ac_asesino")
        arma_sel  = st.selectbox("Arma",    todas_armas,        key="ac_arma")
        lugar_sel = st.selectbox("Lugar",   todos_lugares,      key="ac_lugar")

        if st.button("⚖️ Acusar", type="primary"):
            _resolver_acusacion(acusado, arma_sel, lugar_sel, caso)

        st.divider()
        if st.button("🔄 Nueva partida"):
            for key in ["caso", "personajes", "messages_por_personaje",
                        "historial_detective", "todas_armas", "todos_lugares"]:
                st.session_state.pop(key, None)
            st.session_state.pantalla = "seleccion"
            st.rerun()

    st.title("🔍 El caso comienza")
    st.caption(f"Investiga la muerte de **{caso['victima']}**. Interroga a los sospechosos y resuelve el caso.")

    nombres = list(personajes.keys())
    choice  = st.selectbox("¿Con quién quieres hablar?", nombres)
    st.divider()
    conversacion_personaje(choice, personajes[choice], caso)


def _resolver_acusacion(acusado, arma, lugar, caso):
    acierto_asesino = acusado == caso["asesino"]
    acierto_arma    = arma.lower()  in caso["arma"].lower()  or caso["arma"].lower()  in arma.lower()
    acierto_lugar   = lugar.lower() in caso["lugar"].lower() or caso["lugar"].lower() in lugar.lower()

    if acierto_asesino and acierto_arma and acierto_lugar:
        st.balloons()
        st.success(f"🎉 ¡Correcto! {caso['asesino']} mató a {caso['victima']} "
                   f"con {caso['arma']} en {caso['lugar']}.")
        st.info(f"El motivo era: {caso['motivo']}")
    else:
        errores = []
        if not acierto_asesino: errores.append("el asesino")
        if not acierto_arma:    errores.append("el arma")
        if not acierto_lugar:   errores.append("el lugar")
        st.error(f"❌ Acusación incorrecta. Te has equivocado en: {', '.join(errores)}. Sigue investigando.")