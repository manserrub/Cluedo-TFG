import random
from logic.database import obtener_datos


def generar_misterio(seleccion_jugadores, datos):
    caso = {
        "asesino": random.choice(seleccion_jugadores),
        "victima": random.choice(datos["victimas"]),
        "arma": random.choice(datos["armas"]),
        "habitacion": random.choice(datos["habitaciones"]),
        "hora": random.choice(datos["horas"]),
    }

    personajes_data = _crear_roles_partida(
        seleccion_jugadores=seleccion_jugadores,
        caso=caso,
        habitaciones=datos["habitaciones"],
    )

    return caso, personajes_data


def _crear_roles_partida(seleccion_jugadores, caso, habitaciones):
    personajes_data = {}
    asesino = caso["asesino"]

    inocentes = [p for p in seleccion_jugadores if p != asesino]
    chivo_expiatorio = random.choice(inocentes) if inocentes else None

    habitaciones_falsas = [h for h in habitaciones if h != caso["habitacion"]]
    habitacion_coartada = random.choice(habitaciones_falsas) if habitaciones_falsas else caso["habitacion"]

    focos_base = ["habitacion", "arma", "comportamiento"]
    focos_asignados = []
    while len(focos_asignados) < len(inocentes):
        random.shuffle(focos_base)
        focos_asignados.extend(focos_base)

    mapa_focos = {inocente: focos_asignados[i] for i, inocente in enumerate(inocentes)}
    inocentes_con_sospecha_real = set(random.sample(inocentes, k=min(2, len(inocentes)))) if inocentes else set()

    for personaje in seleccion_jugadores:

        if personaje == asesino:
            personajes_data[personaje] = _crear_datos_asesino(
                caso=caso,
                habitacion_coartada=habitacion_coartada,
                chivo_expiatorio=chivo_expiatorio,
            )
        else:
            foco = mapa_focos[personaje]
            sospecha_real = personaje in inocentes_con_sospecha_real
            personajes_data[personaje] = _crear_datos_inocente(
                personaje=personaje,
                seleccion_jugadores=seleccion_jugadores,
                caso=caso,
                asesino=asesino,
                foco=foco,
                sospecha_real=sospecha_real,
            )

    return personajes_data


def _crear_datos_asesino(caso, habitacion_coartada, chivo_expiatorio):
    tema_sensible = random.choice(["arma", "habitacion", "hora", "victima"])
    return {
        "rol": "asesino",
        "coartada": f"Estabas en {habitacion_coartada} cuando ocurrió todo.",
        "chivo": chivo_expiatorio,
        "tema_sensible": tema_sensible,
    }


def _crear_datos_inocente(personaje, seleccion_jugadores, caso, asesino, foco, sospecha_real):
    sospechoso, certeza = _generar_sospecha_inocente(
        personaje=personaje,
        seleccion_jugadores=seleccion_jugadores,
        asesino=asesino,
        sospecha_real=sospecha_real,
    )

    verdad_1, verdad_2 = _generar_pistas_por_foco(caso, foco, sospechoso)
    confusion = _pista_falsa(caso)

    return {
        "rol": "inocente",
        "foco": foco,
        "verdad_1": verdad_1,
        "verdad_2": verdad_2,
        "confusion": confusion,
        "sospechoso": sospechoso,
        "certeza": certeza,
    }


def _generar_sospecha_inocente(personaje, seleccion_jugadores, asesino, sospecha_real=False):
    otros = [p for p in seleccion_jugadores if p != personaje]
    if sospecha_real and asesino in otros:
        return asesino, random.choice(["baja", "media"])

    candidatos = [p for p in otros if p != asesino]
    sospechoso = random.choice(candidatos) if candidatos else random.choice(otros)
    return sospechoso, "falsa"


def _generar_pistas_por_foco(caso, foco, sospechoso):
    if foco == "habitacion":
        return (
            f"Esa noche había una tensión extraña alrededor de {caso['habitacion']}",
            f"Notaste a {sospechoso} rondando cerca de {caso['habitacion']} en un momento inquietante",
        )

    if foco == "arma":
        return (
            f"Te llamó la atención que {caso['arma']} no estaba donde debía estar",
            f"Tienes la impresión de que {caso['arma']} pudo haber sido usada en lo sucedido",
        )

    return (
        f"Viste a alguien actuar con nerviosismo cerca de {caso['habitacion']} esa noche",
        f"La actitud de {sospechoso} te pareció extraña justo después de las {caso['hora']}",
    )


def _pista_falsa(caso):
    habitaciones = obtener_datos("habitaciones")
    armas = obtener_datos("armas")
    habitaciones_falsas = [
        lugar for lugar in habitaciones
        if lugar != caso["habitacion"]
    ]
    armas_falsas = [
        arma for arma in armas
        if arma != caso["arma"]
    ]
    if not habitaciones_falsas and not armas_falsas:
        return "No recuerdas bien los detalles de esa noche."

    if habitaciones_falsas and (not armas_falsas or random.choice([True, False])):
        return f"Crees que el crimen ocurrió en {random.choice(habitaciones_falsas)}"

    return f"Crees que el crimen se produjo con {random.choice(armas_falsas)}"


def resolver_acusacion(acusado, arma, habitacion, caso, intentos_restantes):
    acierto_asesino = acusado == caso["asesino"]
    acierto_arma = arma.lower() in caso["arma"].lower() or caso["arma"].lower() in arma.lower()
    acierto_habitacion = (
        habitacion.lower() in caso["habitacion"].lower()
        or caso["habitacion"].lower() in habitacion.lower()
    )

    if acierto_asesino and acierto_arma and acierto_habitacion:
        return {
            "resultado": "victoria",
            "intentos": intentos_restantes,
            "mensaje": (
                f"🎉 ¡Correcto! {caso['asesino']} mató a {caso['victima']} "
                f"con {caso['arma']} en {caso['habitacion']}.")
        }

    intentos_restantes -= 1
    errores = []
    if not acierto_asesino:
        errores.append("el asesino")
    if not acierto_arma:
        errores.append("el arma")
    if not acierto_habitacion:
        errores.append("la habitación")

    if intentos_restantes > 0:
        return {
            "resultado": "fallo",
            "intentos": intentos_restantes,
            "mensaje": (
                f"❌ Acusación incorrecta. Te has equivocado en: {', '.join(errores)}. "
                f"Te quedan {intentos_restantes} oportunidades.")
        }

    return {
        "resultado": "derrota",
        "intentos": 0,
        "mensaje": (
            f"❌ Has agotado tus 3 oportunidades. La solución era: {caso['asesino']} "
            f"mató a {caso['victima']} con {caso['arma']} en {caso['habitacion']}.")
    }
