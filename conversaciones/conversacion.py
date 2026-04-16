import streamlit as st
from openai import OpenAI
from conversaciones.generarPrompt import generar_prompt


def obtener_avatar(personaje):
    avatares = {
        "Miss Scarlet": "🌹",
        "Coronel Mustard": "🎖️",
        "Señora Peacock": "🦚",
        "Señora White": "🤍",
        "Señor Green": "💚",
        "Profesor Plum": "🎓"
    }
    return avatares.get(personaje, "🔍")


def obtener_avatar_detective():
    genero = st.session_state.get("genero_usuario", "chico")
    return "🕵️‍♂️" if genero == "chico" else "🕵️‍♀️"


def conversacion_personaje(personaje, datos, caso):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    st.session_state.setdefault("messages_por_personaje", {})
    st.session_state.setdefault("historial_detective", [])

    genero_usuario = st.session_state.get("genero_usuario", "chico")
    tratamiento = "señor detective" if genero_usuario == "chico" else "señorita detective"

    avatar_personaje = obtener_avatar(personaje)
    avatar_detective = obtener_avatar_detective()

    prompt_sistema = generar_prompt(
        personaje,
        datos,
        caso,
        st.session_state.historial_detective,
        genero_usuario
    )

    if personaje not in st.session_state.messages_por_personaje:
        st.session_state.messages_por_personaje[personaje] = [
            {"role": "system", "content": prompt_sistema},
            {"role": "assistant", "content": f"Buenas, {tratamiento}. ¿Qué necesita saber?"}
        ]

    messages = st.session_state.messages_por_personaje[personaje]

    for msg in messages[1:]:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar=avatar_personaje):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=avatar_detective):
                st.markdown(msg["content"])

    if st.session_state.get("partida_terminada", False):
        return

    if prompt := st.chat_input(f"Interroga a {personaje}..."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=avatar_detective):
            st.markdown(prompt)

        messages[0]["content"] = generar_prompt(
            personaje,
            datos,
            caso,
            st.session_state.historial_detective,
            genero_usuario
        )

        with st.spinner(f"{personaje} está escribiendo..."):
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages
            )

        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant", avatar=avatar_personaje):
            st.markdown(reply)

        st.session_state.historial_detective.append({
            "personaje": personaje,
            "pregunta": prompt,
            "respuesta": reply
        })

        st.session_state.messages_por_personaje[personaje] = messages