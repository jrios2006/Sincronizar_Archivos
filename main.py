"""
Script principal de sincronización de archivos y exportación a JSON.

Este programa realiza las siguientes operaciones:

1. Carga la configuración y las credenciales desde los ficheros JSON.
2. Configura el sistema de logging con rotación de ficheros.
3. Asegura que la tabla de metadatos exista en la base de datos, creando la tabla si es necesario.
4. Escanea la carpeta local configurada y sincroniza los metadatos de los archivos en la base de datos.
5. Exporta el contenido de la tabla a un fichero JSON local.
6. Sube el fichero JSON a una o varias rutas remotas mediante SFTP.
7. Registra en el log todas las acciones y errores ocurridos durante el proceso.

Variables de configuración utilizadas:
- directorio_base: ruta de la carpeta local a sincronizar
- tabla: nombre de la tabla de la base de datos
- fichero_a_exportar: nombre del fichero JSON de salida
- rutas_remotas_a_exportar: lista de rutas remotas SFTP donde subir el JSON

Uso:
    $ python main.py

Requisitos:
- Python 3.10+ (u otra versión compatible)
- Módulos externos: mariadb, paramiko, jinja2, etc.
- Ficheros de configuración: config/config.json y config/credenciales.json
"""

from modules import utils, db, sync, export, logging_config

if __name__ == "__main__":
    config = utils.cargar_config()
    logger = logging_config.configurar_logger(config)

    logger.info("=== Inicio de sincronización de archivos ===")    
    try:
    
        directorio = config["directorio_base"]
        tabla = config["tabla"]
        fichero_exportar = config["fichero_a_exportar"]
        rutas_remotas = config["rutas_remotas_a_exportar"]

        # 1. Asegurar tabla
        db.inicializar_tabla(tabla)

        # 2. Sincronizar metadatos locales
        sync.sincronizar(directorio, tabla)

        # 3. Exportar tabla a JSON
        exportar = export.exportar_tabla_a_json(tabla, fichero_exportar)

        # 4. Subir el JSON a rutas remotas vía SFTP
        export.subir_json_por_sftp(exportar, rutas_remotas)

        logger.info("✅ Sincronización y exportación completadas correctamente.")
        
    except Exception as e:
        logger.exception(f"❌ Error durante la ejecución: {e}")
    finally:
        logger.info("=== Fin del proceso ===\n")