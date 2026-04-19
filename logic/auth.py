import re
import bcrypt
from logic.database import crear_conexion

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_email(email):
    return bool(EMAIL_PATTERN.match(email.strip()))


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def crear_tabla_usuarios():
    with crear_conexion() as conn:
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


def autenticar_usuario(usuario_o_email, password):
    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT username, email, genero, password
                    FROM usuarios
                    WHERE username = %s OR email = %s
                """,
                (usuario_o_email, usuario_o_email)
            )
            user = cur.fetchone()

    if not user:
        return None

    username, email, genero, hashed_password = user
    if not check_password(password, hashed_password):
        return None

    return {
        "username": username,
        "email": email,
        "genero": genero,
    }


def registrar_usuario(username, email, password, genero):
    if not validar_email(email):
        raise ValueError("Correo electrónico inválido")

    hashed_password = hash_password(password)

    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT 1 FROM usuarios WHERE username = %s OR email = %s
                """,
                (username, email)
            )
            if cur.fetchone():
                raise ValueError("El usuario o el correo ya existen")

            cur.execute(
                """
                    INSERT INTO usuarios (username, email, password, genero)
                    VALUES (%s, %s, %s, %s)
                """,
                (username, email, hashed_password, genero)
            )
            conn.commit()


def eliminar_cuenta(username, email):
    with crear_conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    DELETE FROM usuarios WHERE username = %s AND email = %s
                """,
                (username, email)
            )
            conn.commit()
