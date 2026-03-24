import streamlit as st
from database import cursor, conexion, verificar_conexion
import hashlib
import re

def inicio():
    st.title("🔍 CLUEDO")

    verificar_conexion()
    _preparar_tabla_usuarios()

    st.session_state.setdefault("logueado", False)

    if st.session_state.logueado:
        st.session_state.pantalla = "seleccion"
        st.rerun()

    opcion = st.sidebar.selectbox("Menú", ["Login", "Registro"])

    if opcion == "Login":
        _login()
    else:
        _registro()


def _preparar_tabla_usuarios():
    # Crear tabla base si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            genero VARCHAR(10)
        )
    """)
    conexion.commit()

    # Revisar columnas existentes por si la tabla ya venía de antes
    cursor.execute("SHOW COLUMNS FROM usuarios")
    columnas = [row[0] for row in cursor.fetchall()]

    if "email" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN email VARCHAR(100) UNIQUE")
    if "genero" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN genero VARCHAR(10)")

    conexion.commit()


def _login():
    st.subheader("Inicio de sesión")

    identificador = st.text_input("Usuario o correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not identificador or not password:
            st.error("Rellena todos los campos")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        if _es_email(identificador):
            query = """
                SELECT username, email, genero 
                FROM usuarios 
                WHERE email=%s AND password=%s
            """
        else:
            query = """
                SELECT username, email, genero 
                FROM usuarios 
                WHERE username=%s AND password=%s
            """

        cursor.execute(query, (identificador, hashed))
        row = cursor.fetchone()

        if row:
            st.session_state.logueado = True
            st.session_state.usuario_actual = row[0]
            st.session_state.email_actual = row[1]
            st.session_state.genero_usuario = row[2] if row[2] else "chico"
            st.session_state.pantalla = "seleccion"
            st.rerun()
        else:
            st.error("Usuario/correo o contraseña incorrectos")


def _es_email(texto):
    return "@" in texto and "." in texto


def _registro():
    st.subheader("Registro de usuario")

    correo = st.text_input("Correo electrónico")
    nuevo_usuario = st.text_input("Nombre de usuario")
    nueva_password = st.text_input("Nueva contraseña", type="password")
    genero = st.radio("¿Eres chico o chica?", ["chico", "chica"], horizontal=True)

    if st.button("Registrarse"):
        if not correo or not nuevo_usuario or not nueva_password or not genero:
            st.error("Rellena todos los campos")
            return

        if not _email_valido(correo):
            st.error("Introduce un correo válido")
            return

        if len(nueva_password) < 8:
            st.error("La contraseña debe tener al menos 8 caracteres")
            return

        if not re.search(r"\d", nueva_password):
            st.error("La contraseña debe contener al menos un número")
            return

        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (nuevo_usuario,))
        if cursor.fetchone():
            st.error("El nombre de usuario ya existe")
            return

        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (correo,))
        if cursor.fetchone():
            st.error("El correo ya está registrado")
            return

        hashed = hashlib.sha256(nueva_password.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO usuarios (email, username, password, genero) VALUES (%s, %s, %s, %s)",
            (correo, nuevo_usuario, hashed, genero)
        )
        conexion.commit()

        st.success("Usuario creado correctamente. Ya puedes iniciar sesión.")


def _email_valido(email):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None