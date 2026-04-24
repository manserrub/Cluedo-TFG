import streamlit as st
import logic.auth as auth


def inicio():
    auth.crear_tabla_usuarios()

    st.session_state.setdefault("logueado", False)

    if st.session_state.logueado:
        st.session_state.pantalla = "seleccion"
        st.rerun()

    st.title("CLUEDO")

    # Tabs para Login y Registro
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registro"])

    with tab1:
        _login()
    
    with tab2:
        _registro()


# LOGIN
def _login():
    st.subheader("Accede a tu cuenta")

    usuario_o_email = st.text_input("Usuario o correo", placeholder="usuario123 o ejemplo@gmail.com", key="login_user")
    password = st.text_input("Contraseña", type="password", placeholder="Tu contraseña", key="login_pass")

    if st.button("🔓 Iniciar sesión", use_container_width=True):
        if not usuario_o_email:
            st.error("⚠️ Por favor, ingresa tu usuario o correo")
            return
        
        if not password:
            st.error("⚠️ Por favor, ingresa tu contraseña")
            return

        try:
            user = auth.autenticar_usuario(usuario_o_email, password)
            if not user:
                st.error("❌ Usuario/email o contraseña incorrectos")
                return

            st.session_state.logueado = True
            st.session_state.usuario_actual = user["username"]
            st.session_state.email_actual = user["email"]
            st.session_state.genero_usuario = user["genero"]
            st.session_state.pantalla = "seleccion"
            st.success("✅ ¡Bienvenido! Redirigiendo...")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al iniciar sesión: {e}")

    st.caption("¿No tienes cuenta? Regístrate en la pestaña de Registro")


# REGISTRO
def _registro():
    st.subheader("Crea una nueva cuenta")

    usuario = st.text_input("Nombre de usuario", placeholder="usuario123", key="reg_user")
    email = st.text_input("Correo electrónico", placeholder="ejemplo@gmail.com", key="reg_email")
    password = st.text_input("Contraseña", type="password", placeholder="Mínimo 8 caracteres y 1 número", key="reg_pass")
    password_confirm = st.text_input("Confirmar contraseña", type="password", placeholder="Repite tu contraseña", key="reg_pass_confirm")
    genero = st.selectbox("Género", ["Hombre", "Mujer", "Prefiero no decirlo"], key="reg_gender")

    if st.button("📝 Registrarse", use_container_width=True):
        # Validaciones específicas
        if not usuario:
            st.error("⚠️ Por favor, ingresa un nombre de usuario")
            return
        
        if not email:
            st.error("⚠️ Por favor, ingresa un correo electrónico")
            return
        
        if not password:
            st.error("⚠️ Por favor, ingresa una contraseña")
            return
        
        if not password_confirm:
            st.error("⚠️ Por favor, confirma tu contraseña")
            return

        if password != password_confirm:
            st.error("❌ Las contraseñas no coinciden. Intenta de nuevo.")
            return

        if len(password) < 8:
            st.error("❌ La contraseña debe tener al menos 8 caracteres")
            return

        if not any(char.isdigit() for char in password):
            st.error("❌ La contraseña debe contener al menos un número")
            return

        try:
            auth.registrar_usuario(usuario, email, password, genero)
            st.success("✅ ¡Cuenta creada correctamente! Ya puedes iniciar sesión en la pestaña de Inicio de Sesión.")
        except ValueError as error:
            st.error(f"❌ {str(error)}")
        except Exception as e:
            st.error(f"❌ Error al registrar el usuario: {e}")

    st.caption("¿Ya tienes cuenta? Inicia sesión en la pestaña de Inicio de Sesión")

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