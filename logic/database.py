import psycopg2
import streamlit as st
from psycopg2 import sql

TABLAS_CON_NOMBRE = {
    "armas",
    "personajes",
    "victimas",
    "habitaciones"
}


def crear_conexion():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        dbname=st.secrets["DB_NAME"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )


def obtener_datos(tabla):
    if tabla not in TABLAS_CON_NOMBRE:
        raise ValueError(f"Tabla no permitida: {tabla}")

    with crear_conexion() as conn:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT nombre FROM {} ORDER BY id").format(sql.Identifier(tabla))
            cur.execute(query)
            rows = cur.fetchall()
            return [row[0] for row in rows]


def obtener_hora():
    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT to_char(hora, 'HH24:MI') FROM horas ORDER BY id")
            rows = cur.fetchall()
            return [row[0] for row in rows]


def obtener_personalidad(nombre):
    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT personalidad, descripcion, forma_habla
                FROM personajes
                WHERE nombre = %s
                """,
                (nombre,)
            )
            row = cur.fetchone()

    if row:
        return {
            "personalidad": row[0],
            "descripcion": row[1],
            "forma_habla": row[2],
        }

    return {}


def obtener_relaciones_victima(victima, participantes):
    if not participantes:
        return []

    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.nombre AS personaje_nombre,
                    v.nombre AS victima_nombre,
                    r.tipo,
                    r.descripcion
                FROM relaciones r
                JOIN personajes p ON r.personaje_a = p.id
                JOIN victimas v ON r.victima_b = v.id
                WHERE v.nombre = %s
                ORDER BY p.nombre
                """,
                (victima,)
            )
            rows = cur.fetchall()

    participantes_set = set(participantes)
    relaciones = []

    for row in rows:
        personaje_nombre = row[0]
        victima_nombre = row[1]
        tipo = row[2]
        descripcion = row[3]

        if personaje_nombre in participantes_set:
            relaciones.append({
                "personaje": personaje_nombre,
                "victima": victima_nombre,
                "tipo": tipo,
                "descripcion": descripcion,
            })

    return relaciones


def obtener_personajes_detallados():
    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nombre, personalidad, descripcion, forma_habla
                FROM personajes
                ORDER BY id
                """
            )
            rows = cur.fetchall()

            personajes = []
            for row in rows:
                personajes.append({
                    "nombre": row[0],
                    "personalidad": row[1],
                    "descripcion": row[2],
                    "forma_habla": row[3]
                })

            return personajes