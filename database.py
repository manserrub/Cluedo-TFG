import psycopg2
import streamlit as st

TABLAS_CON_NOMBRE = {
    "armas",
    "personajes",
    "victimas",
    "motivos",
    "lugares",
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

    conn = crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT nombre FROM {tabla} ORDER BY id")
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()

def obtener_hora():
    conn = crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_char(hora, 'HH24:MI') FROM horas ORDER BY id")
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()


def obtener_personalidad(nombre):
    conn = crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT personalidad, descripcion, forma_habla, nivel_resistencia
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
                    "nivel_resistencia": row[3]
                }

            return {}
    finally:
        conn.close()


def obtener_relaciones(nombre, participantes):
    conn = crear_conexion()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p1.nombre AS personaje_a_nombre,
                    p2.nombre AS personaje_b_nombre,
                    r.tipo,
                    r.descripcion
                FROM relaciones r
                JOIN personajes p1 ON r.personaje_a = p1.id
                JOIN personajes p2 ON r.personaje_b = p2.id
                WHERE p1.nombre = %s OR p2.nombre = %s
                ORDER BY r.id
                """,
                (nombre, nombre)
            )
            rows = cur.fetchall()

        resultado = []

        for row in rows:
            personaje_a = row[0]
            personaje_b = row[1]
            tipo = row[2]
            descripcion = row[3]

            otro = personaje_b if personaje_a == nombre else personaje_a

            if otro in participantes:
                resultado.append({
                    "con": otro,
                    "tipo": tipo,
                    "descripcion": descripcion
                })

        return resultado
    finally:
        conn.close()


def obtener_personajes_detallados():
    conn = crear_conexion()
    try:
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
    finally:
        conn.close()