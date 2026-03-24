import streamlit as st
from database import cursor, conexion, verificar_conexion
import hashlib
import re

def inicio():
    st.title("🔍 CLUEDO")

    # Crear tabla solo una vez al inicio real de la app
    verificar_conexion()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    conexion.commit()

    st.session_state.setdefault("logueado", False)

    # Si ya está logueado, redirigir directamente
    if st.session_state.logueado:
        st.session_state.pantalla = "seleccion"
        st.rerun()

    opcion = st.sidebar.selectbox("Menú", ["Login", "Registro"])

    if opcion == "Login":
        _login()
    else:
        _registro()

def _login():
    st.subheader("Inicio de sesión")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not usuario or not password:
            st.error("Rellena todos los campos")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (usuario, hashed)
        )
        if cursor.fetchone():
            st.session_state.logueado = True
            st.session_state.usuario_actual = usuario
            st.session_state.pantalla = "seleccion"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

def _registro():
    st.subheader("Registro de usuario")
    nuevo_usuario = st.text_input("Nuevo usuario")
    nueva_password = st.text_input("Nueva contraseña", type="password")

    if st.button("Registrarse"):
        if not nuevo_usuario or not nueva_password:
            st.error("Rellena todos los campos")
            return
        if len(nueva_password) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres")
            return
        if not re.search(r"\d", nueva_password):
            st.error("La contraseña debe contener al menos un número")
            return

        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (nuevo_usuario,))
        if cursor.fetchone():
            st.error("El usuario ya existe")
            return

        hashed = hashlib.sha256(nueva_password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (nuevo_usuario, hashed)
        )
        conexion.commit()
        st.success("Usuario creado correctamente. Ya puedes iniciar sesión.")