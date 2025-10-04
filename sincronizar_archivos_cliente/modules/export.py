"""
Módulo `export`
----------------

Proporciona funciones para exportar el contenido de la base de datos a archivos JSON
y subirlos a servidores remotos mediante SFTP.

Funciones principales:
    - exportar_tabla_a_json(tabla, fichero_salida):
        Exporta los registros de una tabla de la base de datos a un fichero JSON.
    - subir_json_por_sftp(fichero_local, rutas_remotas):
        Sube un fichero JSON a una o varias rutas en un servidor SFTP usando credenciales
        configuradas en `config/credenciales.json`.

Dependencias:
    - modules.db: para ejecutar consultas en la base de datos MariaDB.
    - modules.utils: para cargar credenciales.
    - modules.ssh: para subir ficheros por SFTP.
    - json, os, logging, datetime
"""

import json
import os
import logging

from modules import db, utils, ssh
from datetime import datetime, date

logger = logging.getLogger(__name__)

def exportar_tabla_a_json(tabla, fichero_salida):
    """
    Exporta todos los registros de una tabla de la base de datos a un fichero JSON.

    Args:
        tabla (str): Nombre de la tabla de la base de datos a exportar.
        fichero_salida (str): Ruta local donde se guardará el fichero JSON.

    Returns:
        str: Ruta del fichero JSON generado.

    Notas:
        - Convierte automáticamente objetos `datetime` y `date` a formato ISO 8601.
        - Registra en el logger el éxito de la operación.
    
    Ejemplo:
        archivo = exportar_tabla_a_json("archivos", "inventario.json")
    """
    query = f"SELECT * FROM {tabla}"
    registros = db.ejecutar_select(query)

    # Obtener nombres de columnas
    conn = db.conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {tabla} LIMIT 0")
    columnas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    # Convertir registros a lista de diccionarios
    datos = [dict(zip(columnas, fila)) for fila in registros]

    # Función para convertir tipos especiales
    def convertir(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return str(o)

    with open(fichero_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4, default=convertir)

    logger.info(f"✅ Fichero JSON exportado: {fichero_salida}")
    return fichero_salida


def subir_json_por_sftp(fichero_local, rutas_remotas):
    """
    Sube un fichero JSON a una o varias rutas en un servidor SFTP.

    Args:
        fichero_local (str): Ruta local del fichero JSON a subir.
        rutas_remotas (list[str]): Lista de rutas remotas donde se debe subir el archivo.

    Returns:
        None

    Notas:
        - Utiliza las credenciales SFTP definidas en `config/credenciales.json`.
        - Registra en el logger el progreso de la subida y posibles errores.
    
    Ejemplo:
        subir_json_por_sftp("inventario.json", ["/remote/path1", "/remote/path2"])
    """
    creds = utils.cargar_credenciales()
    credenciales_sftp = creds["SFTP"]

    for ruta in rutas_remotas:
        nombre_fichero = os.path.basename(fichero_local)
        logger.info(f"📤 Subiendo {nombre_fichero} a {ruta}...")
        ok = ssh.SubirFicheroSFTP(credenciales_sftp, ruta, fichero_local, nombre_fichero)
        if ok:
            logger.info(f"✅ Subida completada en {ruta}")
        else:
            logger.error(f"❌ Error al subir a {ruta}")
