"""
Módulo `sync`
---------------

Proporciona funciones para sincronizar los metadatos de archivos de un directorio
local con una tabla de base de datos MariaDB.

Funciones principales:
    - sincronizar(directorio, tabla):
        Escanea un directorio local, compara los archivos con los registros de la tabla
        y realiza inserciones, actualizaciones o eliminaciones según corresponda.

Dependencias:
    - modules.db: para ejecutar consultas en la base de datos.
    - modules.files: para escanear directorios y obtener metadatos de archivos.
    - logging: para registrar el progreso de la sincronización.
"""

from modules import db, files
import logging
logger = logging.getLogger(__name__)


def sincronizar(directorio, tabla):
    """
    Sincroniza los metadatos de los archivos de un directorio con una tabla de base de datos.

    Args:
        directorio (str): Ruta del directorio local a escanear.
        tabla (str): Nombre de la tabla en la base de datos donde se almacenan los metadatos.

    Comportamiento:
        1. Escanea el directorio y obtiene la lista de archivos.
        2. Obtiene las rutas de los registros existentes en la tabla.
        3. Inserta nuevos archivos que no existan en la base de datos.
        4. Actualiza los registros cuyo hash MD5 o tamaño haya cambiado.
        5. Elimina registros de la base de datos si ya no existen localmente.
        6. Registra el número total de archivos sincronizados al finalizar.

    Logging:
        - INFO para cada inserción, actualización y eliminación.
        - INFO con el número total de archivos al final.
    
    Ejemplo:
        sincronizar("/tmp/Images", "archivos")
    """
    # 1. Escanear ficheros reales
    ficheros = files.escanear_directorio(directorio)
    rutas_reales = set(ficheros)
    logger.info(f"Escaneados {len(ficheros)} ficheros en el directorio {directorio}")
    
    # 2. Obtener rutas de BD
    query_rutas = f"SELECT ruta FROM {tabla}"
    rutas_db = {r[0] for r in db.ejecutar_select(query_rutas)}

    # 3. Insertar o actualizar
    for fichero in ficheros:
        meta = files.obtener_metadatos(fichero)

        query_buscar = f"SELECT id, hash_md5, tamano FROM {tabla} WHERE ruta = ?"
        row = db.ejecutar_select(query_buscar, (meta["ruta"],))

        if not row:
            # INSERT
            query_insert = f"""
                INSERT INTO {tabla} (nombre, ruta, hash_md5, tamano, fecha_creacion, extension, mime_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            db.ejecutar_modificacion(query_insert, (
                meta["nombre"], meta["ruta"], meta["hash_md5"], meta["tamano"],
                meta["fecha_creacion"], meta["extension"], meta["mime_type"]
            ))
            logger.info(f"Insertado: {meta['ruta']}")

        else:
            # UPDATE si ha cambiado
            id_, hash_db, tamano_db = row[0]
            if hash_db != meta["hash_md5"] or tamano_db != meta["tamano"]:
                query_update = f"""
                    UPDATE {tabla}
                    SET nombre=?, hash_md5=?, tamano=?, fecha_creacion=?, extension=?, mime_type=?
                    WHERE id=?
                """
                db.ejecutar_modificacion(query_update, (
                    meta["nombre"], meta["hash_md5"], meta["tamano"], meta["fecha_creacion"],
                    meta["extension"], meta["mime_type"], id_
                ))
                logger.info(f"Actualizado: {meta['ruta']}")

    # 4. Eliminar registros que ya no existen
    faltan = rutas_db - rutas_reales
    for ruta in faltan:
        query_delete = f"DELETE FROM {tabla} WHERE ruta = ?"
        db.ejecutar_modificacion(query_delete, (ruta,))
        logger.info(f"Eliminado: {ruta}")

    # 5. Log final con número total de archivos sincronizados
    num_ficheros_final = len(rutas_reales)
    logger.info(f"Sincronización completada con {num_ficheros_final} archivos")