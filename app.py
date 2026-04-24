import streamlit as st
from pantallas.inicio import inicio
from pantallas.juego import juego
from pantallas.seleccion import seleccion
from logic.estilos import aplicar_estilos

st.set_page_config(
    page_title="CLUEDO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

aplicar_estilos()

st.session_state.setdefault("pantalla", "inicio")
st.session_state.setdefault("caso", {})
st.session_state.setdefault("personajes", {})

if st.session_state.pantalla == "inicio":
    inicio()
elif st.session_state.pantalla == "seleccion":
    seleccion()
elif st.session_state.pantalla == "juego":
    juego()