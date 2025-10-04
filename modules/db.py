"""
Módulo `db`
------------

Proporciona funciones para conectar y manipular una base de datos MariaDB/MySQL
utilizando credenciales definidas en un fichero JSON de configuración.

Funciones principales:
    - conectar(): Conecta a la base de datos usando credenciales del JSON.
    - inicializar_tabla(tabla): Crea la tabla especificada usando SQL de creación.
    - ejecutar_select(query, params=None): Ejecuta un SELECT y devuelve resultados.
    - ejecutar_modificacion(query, params=None): Ejecuta INSERT/UPDATE/DELETE y confirma cambios.

Dependencias:
    - mariadb: cliente de MariaDB/MySQL.
    - utils: para cargar credenciales desde config/credenciales.json.
"""

import mariadb
from . import utils

def conectar():
    """
    Establece una conexión a la base de datos MariaDB usando credenciales.

    Carga las credenciales desde `config/credenciales.json` bajo la clave "BBDD".

    Returns:
        mariadb.connection: Conexión activa a la base de datos.

    Ejemplo:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT * FROM archivos")
    """
    creds = utils.cargar_credenciales()
    db_creds = creds["BBDD"]

    # Si no se especifica puerto, usar 3306 por defecto
    port = db_creds.get("port", 3306)

    return mariadb.connect(
        user=db_creds["user"],
        password=db_creds["password"],
        host=db_creds["host"],
        port=port,
        database=db_creds["database"]
    )

def inicializar_tabla(tabla):
    """
    Crea la tabla en la base de datos ejecutando el SQL definido en `sql/create_archivos.sql`.

    Reemplaza el nombre de la tabla genérica "archivos" por el nombre proporcionado.

    Args:
        tabla (str): Nombre de la tabla a crear.

    Ejemplo:
        inicializar_tabla("mis_archivos")
    """
    with open("sql/create_archivos.sql", "r", encoding="utf-8") as f:
        sql = f.read().replace("archivos", tabla)
    conn = conectar()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

# === Funciones utilitarias de ejecución ===

def ejecutar_select(query, params=None):
    """
    Ejecuta un SELECT en la base de datos y devuelve los resultados.

    Args:
        query (str): Consulta SQL a ejecutar.
        params (tuple, opcional): Parámetros de la consulta SQL.

    Returns:
        list[tuple]: Lista de tuplas con los resultados.

    Ejemplo:
        resultados = ejecutar_select("SELECT * FROM archivos WHERE nombre=?", ("file.txt",))
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute(query, params or ())
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    return resultados

def ejecutar_modificacion(query, params=None):
    """
    Ejecuta una modificación en la base de datos (INSERT, UPDATE, DELETE)
    y confirma los cambios con commit.

    Args:
        query (str): Consulta SQL a ejecutar.
        params (tuple, opcional): Parámetros de la consulta SQL.

    Ejemplo:
        ejecutar_modificacion("DELETE FROM archivos WHERE id=?", (123,))
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    cur.close()
    conn.close()
