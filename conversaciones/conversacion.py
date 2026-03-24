import streamlit as st
from openai import OpenAI
from conversaciones.generarPrompt import generar_prompt

def conversacion_personaje(personaje, datos, caso):

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    st.session_state.setdefault("messages_por_personaje", {})
    st.session_state.setdefault("historial_detective", [])

    prompt_sistema = generar_prompt(
        personaje, datos, caso, st.session_state.historial_detective
    )

    if personaje not in st.session_state.messages_por_personaje:
        st.session_state.messages_por_personaje[personaje] = [
            {"role": "system",    "content": prompt_sistema},
            {"role": "assistant", "content": "🔍 Buenas, señor detective. ¿Qué necesita saber?"}
        ]

    messages = st.session_state.messages_por_personaje[personaje]

    for msg in messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"Interroga a {personaje}..."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Actualizar system prompt con historial más reciente
        messages[0]["content"] = generar_prompt(
            personaje, datos, caso, st.session_state.historial_detective
        )

        with st.spinner(f"{personaje} está pensando..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=400,
                temperature=0.85
            )
        reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.historial_detective.append({
            "personaje": personaje,
            "pregunta":  prompt,
            "respuesta": reply
        })

        st.session_state.messages_por_personaje[personaje] = messages