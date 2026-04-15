import streamlit as st
import hashlib
import re
import database


def inicio():
    st.title("CLUEDO")

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

def eliminar_cuenta_actual():
    usuario = st.session_state.get("usuario_actual")
    email = st.session_state.get("email_actual")

    if not usuario or not email:
        st.error("No hay ninguna sesión activa.")
        return

    conn = database.crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM usuarios
                WHERE username = %s AND email = %s
                """,
                (usuario, email)
            )
            conn.commit()

        for key in [
            "logueado", "usuario_actual", "email_actual", "genero_usuario",
            "pantalla", "caso", "personajes", "messages_por_personaje",
            "historial_detective", "cuaderno_notas", "intentos_acusacion",
            "partida_terminada", "datos_partida", "todas_armas",
            "todos_habitaciones", "ac_asesino", "ac_arma", "ac_habitacion",
            "mostrar_confirmacion_borrado"
        ]:
            st.session_state.pop(key, None)

        st.session_state.pantalla = "inicio"
        st.rerun()

    except Exception as e:
        st.error(f"Error al eliminar la cuenta: {e}")
    finally:
        conn.close()

def mostrar_confirmacion_borrado():
    if not st.session_state.get("mostrar_confirmacion_borrado", False):
        return

    with st.container(border=True):
        st.error("⚠️ ¿Seguro que quieres borrar tu cuenta?")
        st.write("Esta acción eliminará tu usuario y no se podrá deshacer.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirmar borrado", use_container_width=True):
                eliminar_cuenta_actual()

        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.mostrar_confirmacion_borrado = False
                st.rerun()