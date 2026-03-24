import mysql.connector

def crear_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="manserrubTFG",
        password="manserrub",
        database="cluedoTFG"
    )

conexion = crear_conexion()
cursor = conexion.cursor(buffered=True)

def verificar_conexion():
    global conexion, cursor
    if not conexion.is_connected():
        conexion = crear_conexion()
        cursor = conexion.cursor(buffered=True)

def obtener_datos(tabla):
    verificar_conexion()
    cursor.execute(f"SELECT nombre FROM {tabla}")
    return [row[0] for row in cursor.fetchall()]

def obtener_secretos():
    verificar_conexion()
    cursor.execute("SELECT descripcion FROM secretos")
    return [row[0] for row in cursor.fetchall()]

def obtener_hora():
    verificar_conexion()
    cursor.execute("SELECT hora FROM horas")
    return [row[0] for row in cursor.fetchall()]

def obtener_personalidad(nombre):
    verificar_conexion()
    cursor.execute(
        "SELECT personalidad, descripcion, forma_habla, secreto_caracter, nivel_resistencia "
        "FROM personajes WHERE nombre = %s",
        (nombre,)
    )
    row = cursor.fetchone()
    if row:
        return {
            "personalidad":      row[0],
            "descripcion":       row[1],
            "forma_habla":       row[2],
            "secreto_caracter":  row[3],
            "nivel_resistencia": row[4]
        }
    return {}

def obtener_relaciones(nombre, participantes):
    """Devuelve las relaciones de un personaje con los que están en la partida."""
    verificar_conexion()
    cursor.execute("""
        SELECT personaje_a, personaje_b, tipo, descripcion
        FROM relaciones
        WHERE personaje_a = %s OR personaje_b = %s
    """, (nombre, nombre))
    rows = cursor.fetchall()
    resultado = []
    for row in rows:
        otro = row[1] if row[0] == nombre else row[0]
        if otro in participantes:
            resultado.append({
                "con": otro,
                "tipo": row[2],
                "descripcion": row[3]
            })
    return resultado