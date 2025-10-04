"""
Módulo `verificar`
------------------

Este módulo gestiona la comparación entre los archivos locales del cliente y el inventario
JSON proveniente del servidor. Permite identificar diferencias, generar un informe HTML 
con los resultados y, según la configuración, enviar dicho informe por correo electrónico 
o subirlo al servidor mediante SFTP.

Funciones principales:
    - comparar_carpetas(): Detecta archivos faltantes o extra en la carpeta local.
    - generar_html(): Crea un informe HTML con los resultados de la comparación.
    - procesar_diferencias(): Coordina el flujo completo de comparación, generación de 
      informe y envío según la acción configurada.

Dependencias:
    - modules.files: para el escaneo y metadatos de archivos locales.
    - modules.ssh: para la transferencia de archivos vía SFTP.
    - modules.email: para el envío del informe por correo electrónico.
    - Jinja2: para la generación de la plantilla HTML.
"""

import os
import json
import logging
from jinja2 import Environment, FileSystemLoader
from . import files, ssh, utils
from modules.email_module import EnviarCorreoSSL  # tu fichero de correo

logger = logging.getLogger(__name__)

def comparar_carpetas(json_servidor, carpeta_local):
    """
    Compara los ficheros de una carpeta local con los metadatos
    de referencia obtenidos del servidor.

    Esta función permite detectar **diferencias de sincronización**
    entre los archivos locales del cliente y el inventario central
    definido por el JSON descargado desde el servidor SFTP.

    Args:
        json_servidor (list[dict]): Lista de diccionarios que representan
            los metadatos de los archivos en el servidor. Cada elemento
            debe incluir al menos:
                - nombre
                - hash_md5
                - ruta
                - tamaño
                - fecha_creacion
        carpeta_local (str): Ruta local donde se buscarán los archivos
            del cliente para comparar.

    Returns:
        list[dict]: Lista de diferencias detectadas. Cada elemento tiene
        la siguiente estructura:

            {
                "tipo": "extra_local" | "falta_local",
                "local": { ... } | "servidor": { ... }
            }

        Donde:
            - "extra_local": el archivo existe localmente pero no en el JSON del servidor.
            - "falta_local": el archivo existe en el JSON del servidor pero no localmente.

    Ejemplo:
        diferencias = comparar_carpetas(json_servidor, "/tmp/Images")

    Notas:
        - La comparación se realiza por combinación de (nombre, hash_md5),
          ignorando la ruta del archivo, ya que puede diferir entre cliente
          y servidor.
        - Los archivos idénticos (mismo nombre y hash) se consideran sincronizados.
    """
    ficheros_locales = files.escanear_directorio(carpeta_local)
    metadatos_locales = [files.obtener_metadatos(f) for f in ficheros_locales]

    diferencias = []

    # Diccionario servidor por (nombre, hash)
    servidor_dict = {(f['nombre'], f['hash_md5']): f for f in json_servidor}

    # Extra en local
    for local in metadatos_locales:
        key = (local['nombre'], local['hash_md5'])
        if key not in servidor_dict:
            diferencias.append({"tipo": "extra_local", "local": local})

    # Falta en local
    for servidor in json_servidor:
        key = (servidor['nombre'], servidor['hash_md5'])
        if not any((local['nombre'], local['hash_md5']) == key for local in metadatos_locales):
            diferencias.append({"tipo": "falta_local", "servidor": servidor})

    return diferencias

def generar_html(diferencias, ruta_salida):
    """
    Renderiza un HTML de diferencias usando Jinja2.
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('diferencias.html.j2')

    html = template.render(diferencias=diferencias)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"HTML generado en {ruta_salida}")
    return ruta_salida

def procesar_diferencias(json_servidor, carpeta_local, ruta_html, accion, credenciales):
    diferencias = comparar_carpetas(json_servidor, carpeta_local)
    archivo_html = generar_html(diferencias, ruta_html)

    if accion.upper() == "SFTP":
        for ruta in credenciales["rutas_remotas_salida"]:
            ok = ssh.SubirFicheroSFTP(credenciales["SFTP"], ruta, archivo_html, os.path.basename(archivo_html))
            if ok:
                logger.info(f"HTML subido a {ruta} correctamente")
            else:
                logger.error(f"Error subiendo HTML a {ruta}")
    elif accion.upper() == "EMAIL":
        destinatario = credenciales["email"]["para"]
        asunto = credenciales["email"]["asunto"]
        mensaje = "Se adjunta el informe de diferencias entre el cliente y el servidor."
        ok, errores = EnviarCorreoSSL(
            credenciales["CORREO"],
            destinatario,
            asunto,
            mensaje,
            archivo_html,
            CopiaOculta=True
        )
        if ok:
            logger.info(f"Correo enviado correctamente a {destinatario}")
        else:
            logger.error(f"Error enviando correo: {errores}")