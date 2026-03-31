import streamlit as st
import hashlib
import re
import database


def inicio():
    st.title("🔍 CLUEDO")

    # Crear tabla usuarios si no existe
    _crear_tabla_usuarios()

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


def _crear_tabla_usuarios():
    conn = database.crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    genero VARCHAR(10)
                )
            """)
            conn.commit()
    except Exception as e:
        st.error(f"Error al crear la tabla usuarios: {e}")
    finally:
        conn.close()


# LOGIN
def _login():
    st.subheader("Inicio de sesión")

    usuario_o_email = st.text_input("Usuario o correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not usuario_o_email or not password:
            st.error("Rellena todos los campos")
            return

        hashed = hashlib.sha256(password.encode()).hexdigest()

        conn = database.crear_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT username, email, genero
                    FROM usuarios
                    WHERE (username = %s OR email = %s) AND password = %s
                    """,
                    (usuario_o_email, usuario_o_email, hashed)
                )
                user = cur.fetchone()

            if user:
                st.session_state.logueado = True
                st.session_state.usuario_actual = user[0]
                st.session_state.email_actual = user[1]
                st.session_state.genero_usuario = user[2]
                st.session_state.pantalla = "seleccion"
                st.rerun()
            else:
                st.error("Usuario/email o contraseña incorrectos")
        except Exception as e:
            st.error(f"Error al iniciar sesión: {e}")
        finally:
            conn.close()


# REGISTRO
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

        conn = database.crear_conexion()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM usuarios
                    WHERE username = %s OR email = %s
                    """,
                    (usuario, email)
                )

                if cur.fetchone():
                    st.error("El usuario o el correo ya existen")
                    return

                cur.execute(
                    """
                    INSERT INTO usuarios (username, email, password, genero)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (usuario, email, hashed, genero)
                )
                conn.commit()

            st.success("Usuario creado correctamente. Ya puedes iniciar sesión.")
        except Exception as e:
            st.error(f"Error al registrar el usuario: {e}")
        finally:
            conn.close()