import streamlit as st
import random
from database import obtener_datos, obtener_secretos, obtener_hora, obtener_personalidad

def seleccion():
    st.title("🔍 Selecciona tus personajes")

    if st.session_state.get("usuario_actual"):
        st.sidebar.write(f"👤 {st.session_state.usuario_actual}")
        if st.sidebar.button("Cerrar sesión"):
            for key in ["logueado", "usuario_actual", "pantalla", "caso",
                        "personajes", "messages_por_personaje", "historial_detective"]:
                st.session_state.pop(key, None)
            st.rerun()

    personajes_lista = obtener_datos("personajes")
    victimas         = obtener_datos("victimas")
    armas            = obtener_datos("armas")
    lugares          = obtener_datos("lugares")
    motivos          = obtener_datos("motivos")
    secretos         = obtener_secretos()
    horas            = obtener_hora()

    seleccion_jugadores = st.multiselect("Elige tus personajes (mínimo 2)", personajes_lista)

    if st.button("Comenzar partida"):
        if len(seleccion_jugadores) < 2:
            st.error("Debes elegir al menos 2 personajes")
            return

        caso, personajes_data = _generar_misterio(
            seleccion_jugadores, victimas, armas, lugares, motivos, secretos, horas
        )
        caso["personajes"] = seleccion_jugadores
        st.session_state.caso             = caso
        st.session_state.personajes       = personajes_data
        st.session_state.messages_por_personaje = {}
        st.session_state.historial_detective    = []
        st.session_state.pantalla         = "juego"
        st.rerun()

def _generar_misterio(seleccion, victimas, armas, lugares, motivos, secretos, horas):

    asesino = random.choice(seleccion)
    victima = random.choice(victimas)
    lugar   = random.choice(lugares)
    hora    = random.choice(horas)
    arma    = random.choice(armas)
    motivo  = random.choice(motivos)

    # Lugar falso para coartada del asesino (distinto al real)
    lugares_falsos = [l for l in lugares if l != lugar]
    lugar_coartada = random.choice(lugares_falsos) if lugares_falsos else lugar

    solucion = {
        "victima": victima,
        "asesino": asesino,
        "arma":    arma,
        "lugar":   lugar,
        "hora":    hora,
        "motivo":  motivo
    }

    # Elegir a quién desvía el asesino (un inocente aleatorio)
    inocentes = [p for p in seleccion if p != asesino]
    chivo_expiatorio = random.choice(inocentes) if inocentes else None

    personajes_data = {}
    secretos_disponibles = secretos.copy()
    random.shuffle(secretos_disponibles)

    for i, personaje in enumerate(seleccion):
        secreto = secretos_disponibles[i % len(secretos_disponibles)]
        p_info  = obtener_personalidad(personaje)
        resistencia = p_info.get("nivel_resistencia", 2)

        if personaje == asesino:
            personajes_data[personaje] = {
                "rol":             "asesino",
                "resistencia":     resistencia,
                "coartada":        f"Estabas en {lugar_coartada} cuando ocurrió todo",
                "motivo_real":     motivo,
                "chivo":           chivo_expiatorio,
                "secreto":         secreto
            }
        else:
            # Acusación cruzada: este inocente sospecha de alguien
            # Con 40% de probabilidad sospecha del asesino real (sin certeza)
            # Con 60% sospecha de otro inocente (pista falsa)
            otros = [p for p in seleccion if p != personaje]
            if random.random() < 0.4 and asesino in otros:
                sospechoso = asesino
                certeza    = "baja"   # lo insinúa, no lo afirma
            else:
                candidatos = [p for p in otros if p != asesino]
                sospechoso = random.choice(candidatos) if candidatos else random.choice(otros)
                certeza    = "falsa"

            personajes_data[personaje] = {
                "rol":         "inocente",
                "resistencia": resistencia,
                "presiones":   0,          # contador de veces que el detective ha insistido
                "verdad_1":    _pista_nivel1(solucion),
                "verdad_2":    _pista_nivel2(solucion),
                "verdad_3":    _pista_nivel3(solucion),
                "confusion":   _pista_falsa(solucion, seleccion, personaje),
                "sospechoso":  sospechoso,
                "certeza":     certeza,    # 'baja' = podría ser, 'falsa' = está seguro pero se equivoca
                "secreto":     secreto
            }

    return solucion, personajes_data

def _pista_nivel1(solucion):
    """Información superficial — la suelta fácilmente."""
    opciones = [
        f"Esa noche estabas en una parte alejada de {solucion['lugar']}",
        f"Viste a {solucion['victima']} nervioso/a antes de la cena",
        f"Escuchaste pasos en el pasillo cerca de las {solucion['hora']}",
        f"Notaste que el ambiente en la mansión estaba muy tenso esa noche"
    ]
    return random.choice(opciones)

def _pista_nivel2(solucion):
    """Información relevante — necesita algo de presión."""
    opciones = [
        f"Viste a alguien cerca de {solucion['lugar']} alrededor de las {solucion['hora']}",
        f"Escuchaste un ruido extraño en {solucion['lugar']} esa noche",
        f"Crees haber visto {solucion['arma']} fuera de su sitio habitual",
        f"Alguien tenía un conflicto serio con {solucion['victima']} por {solucion['motivo']}"
    ]
    return random.choice(opciones)

def _pista_nivel3(solucion):
    """Información clave — solo bajo mucha presión."""
    opciones = [
        f"Estás casi seguro/a de haber visto {solucion['arma']} en {solucion['lugar']}",
        f"Escuchaste voces en {solucion['lugar']} justo a las {solucion['hora']}",
        f"Alguien salió de {solucion['lugar']} justo después de las {solucion['hora']} con aspecto alterado",
        f"Viste a alguien esconder algo que podría ser {solucion['arma']} esa noche"
    ]
    return random.choice(opciones)

def _pista_falsa(solucion, seleccion, personaje_actual):
    """Pista incorrecta para despistar."""
    lugares_falsos  = ["el salón", "la cocina", "el jardín", "la biblioteca", "el estudio"]
    lugares_falsos  = [l for l in lugares_falsos if l != solucion["lugar"]]
    horas_falsas    = ["las 21:00", "las 23:30", "la medianoche", "las 22:00"]
    horas_falsas    = [h for h in horas_falsas if h != solucion["hora"]]

    tipo = random.choice(["lugar", "hora"])
    if tipo == "lugar" and lugares_falsos:
        return f"Crees que el crimen ocurrió en {random.choice(lugares_falsos)}"
    elif horas_falsas:
        return f"Crees que el crimen ocurrió alrededor de {random.choice(horas_falsas)}"
    return "No recuerdas bien los detalles de esa noche"