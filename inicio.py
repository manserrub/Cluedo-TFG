import streamlit as st
import hashlib
import re
import database
from database import verificar_conexion


def inicio():
    st.title("🔍 CLUEDO")

    # Asegurar conexión a la BD
    verificar_conexion()

    # Crear tabla usuarios si no existe (PostgreSQL)
    database.cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            genero VARCHAR(10)
        )
    """)
    database.conexion.commit()

    st.session_state.setdefault("logueado", False)

    # Si ya está logueado → ir a selección
    if st.session_state.logueado:
        st.session_state.pantalla = "seleccion"
        st.rerun()

    opcion = st.sidebar.selectbox("Menú", ["Login", "Registro"])

    if opcion == "Login":
        _login()
    else:
        _registro()


# 🔐 LOGIN
def _login():
    st.subheader("Inicio de sesión")

    usuario_o_email = st.text_input("Usuario o correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not usuario_o_email or not password:
            st.error("Rellena todos los campos")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        verificar_conexion()
        database.cursor.execute(
            """
            SELECT username, email, genero
            FROM usuarios
            WHERE (username = %s OR email = %s) AND password = %s
            """,
            (usuario_o_email, usuario_o_email, hashed)
        )

        user = database.cursor.fetchone()

        if user:
            st.session_state.logueado = True
            st.session_state.usuario_actual = user[0]
            st.session_state.email_actual = user[1]
            st.session_state.genero_usuario = user[2]
            st.session_state.pantalla = "seleccion"
            st.rerun()
        else:
            st.error("Usuario/email o contraseña incorrectos")


# 📝 REGISTRO
def _registro():
    st.subheader("Registro de usuario")

    usuario = st.text_input("Nombre de usuario")
    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")
    genero = st.selectbox("Género", ["chico", "chica"])

    if st.button("Registrarse"):
        if not usuario or not email or not password:
            st.error("Rellena todos los campos")
            return

        if len(password) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres")
            return

        if not re.search(r"\d", password):
            st.error("La contraseña debe contener al menos un número")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        verificar_conexion()

        # comprobar si existe usuario o email
        database.cursor.execute(
            """
            SELECT * FROM usuarios
            WHERE username = %s OR email = %s
            """,
            (usuario, email)
        )

        if database.cursor.fetchone():
            st.error("El usuario o el correo ya existen")
            return

        # insertar usuario
        database.cursor.execute(
            """
            INSERT INTO usuarios (username, email, password, genero)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario, email, hashed, genero)
        )

        database.conexion.commit()

        st.success("Usuario creado correctamente. Ya puedes iniciar sesión.")