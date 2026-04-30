import streamlit as st
import random
from logic.database import obtener_datos
from logic.conversations.conversacion import conversacion_personaje
from pantallas.inicio import mostrar_confirmacion_borrado
from logic.game_logic import resolver_acusacion

def limpiar_cuaderno():
    st.session_state.cuaderno_notas = ""

def juego():
    caso = st.session_state.caso
    personajes = st.session_state.personajes

    if "todas_armas" not in st.session_state:
        armas = obtener_datos("armas")
        random.shuffle(armas)
        st.session_state.todas_armas = armas

    if "todos_habitaciones" not in st.session_state:
        habitaciones = obtener_datos("habitaciones")
        random.shuffle(habitaciones)
        st.session_state.todos_habitaciones = habitaciones

    st.session_state.setdefault("cuaderno_notas", "")
    st.session_state.setdefault("intentos_acusacion", 3)
    st.session_state.setdefault("partida_terminada", False)
    st.session_state.setdefault("mostrar_confirmacion_borrado", False)

    todas_armas = st.session_state.todas_armas
    todos_habitaciones = st.session_state.todos_habitaciones

    with st.sidebar:
        st.markdown("### 🔍 El caso")
        st.write(f"**Víctima:** {caso['victima']}")
        st.write(f"**Hora:** {caso['hora']}")
        st.write(f"**Sospechosos:** {', '.join(caso['personajes'])}")
        st.divider()

        st.markdown("### 📓 Cuaderno del detective")

        st.button("🧹 Limpiar notas", on_click=limpiar_cuaderno,width='stretch')

        st.text_area(
            "Notas del caso",
            key="cuaderno_notas",
            height=220,
            placeholder="Escribe aquí tus deducciones, contradicciones y pistas importantes..."
        )

        st.divider()
        st.markdown("### 🎯 Realizar acusación")

        acusado = st.selectbox("Asesino", ["---"] + caso["personajes"], key="ac_asesino")
        arma_sel = st.selectbox("Arma", ["---"] + list(todas_armas), key="ac_arma")
        habitacion_sel = st.selectbox("Habitación", ["---"] + list(todos_habitaciones), key="ac_habitacion")

        if st.session_state.partida_terminada:
            st.warning("La partida ha terminado. Ya no puedes realizar más acusaciones.")
        else:
            if st.button("⚖️ Acusar", type="primary", width='stretch'):
                resultado = resolver_acusacion(
                    acusado,
                    arma_sel,
                    habitacion_sel,
                    caso,
                    st.session_state.intentos_acusacion,
                )
                st.session_state.intentos_acusacion = resultado["intentos"]

                if resultado["resultado"] == "victoria":
                    st.session_state.partida_terminada = True
                    st.balloons()
                    st.success(resultado["mensaje"])
                elif resultado["resultado"] == "derrota":
                    st.session_state.partida_terminada = True
                    st.error(resultado["mensaje"])
                else:
                    st.error(resultado["mensaje"])

        st.divider()
        st.markdown("### ⚠️ Cuenta")

        st.sidebar.write(f"👤 {st.session_state.usuario_actual}")
        if st.session_state.get("email_actual"):
            st.sidebar.write(f"📧 {st.session_state.email_actual}")

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

        if st.button("🗑️ Borrar cuenta", width='stretch'):
            st.session_state.mostrar_confirmacion_borrado = True
            st.rerun()
        mostrar_confirmacion_borrado()

        st.divider()

        if st.button("🔄 Nueva partida", width='stretch'):
            for key in [
                "caso", "personajes", "messages_por_personaje",
                "historial_detective", "todas_armas", "todos_habitaciones",
                "cuaderno_notas", "intentos_acusacion", "partida_terminada",
                "mostrar_confirmacion_borrado"
            ]:
                st.session_state.pop(key, None)
            st.session_state.pantalla = "seleccion"
            st.rerun()


    if st.session_state.partida_terminada:
        st.info("La investigación ha concluido. Puedes revisar las conversaciones, pero no continuar los interrogatorios.")

    nombres = list(personajes.keys())
    choice = st.selectbox("¿Con quién quieres hablar?", nombres)
    st.divider()
    conversacion_personaje(choice, personajes[choice], caso)
