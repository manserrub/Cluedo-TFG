import streamlit as st
import logic.auth as auth


def inicio():
    st.title("CLUEDO")
    auth.crear_tabla_usuarios()

    st.session_state.setdefault("logueado", False)

    if st.session_state.logueado:
        st.session_state.pantalla = "seleccion"
        st.rerun()

    opcion = st.sidebar.selectbox("Menú", ["Login", "Registro"])

    if opcion == "Login":
        _login()
    else:
        _registro()


# LOGIN
def _login():
    st.subheader("Inicio de sesión")

    usuario_o_email = st.text_input("Usuario o correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if not usuario_o_email or not password:
            st.error("Rellena todos los campos")
            return

        try:
            user = auth.autenticar_usuario(usuario_o_email, password)
            if not user:
                st.error("Usuario/email o contraseña incorrectos")
                return

            st.session_state.logueado = True
            st.session_state.usuario_actual = user["username"]
            st.session_state.email_actual = user["email"]
            st.session_state.genero_usuario = user["genero"]
            st.session_state.pantalla = "seleccion"
            st.rerun()
        except Exception as e:
            st.error(f"Error al iniciar sesión: {e}")


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

        if not any(char.isdigit() for char in password):
            st.error("La contraseña debe contener al menos un número")
            return

        try:
            auth.registrar_usuario(usuario, email, password, genero)
            st.success("Usuario creado correctamente. Ya puedes iniciar sesión.")
        except ValueError as error:
            st.error(str(error))
        except Exception as e:
            st.error(f"Error al registrar el usuario: {e}")

def eliminar_cuenta_actual():
    usuario = st.session_state.get("usuario_actual")
    email = st.session_state.get("email_actual")

    if not usuario or not email:
        st.error("No hay ninguna sesión activa.")
        return

    try:
        auth.eliminar_cuenta(usuario, email)

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