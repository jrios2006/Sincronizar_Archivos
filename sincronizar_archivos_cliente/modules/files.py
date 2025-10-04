"""
Módulo `files`
---------------

Proporciona funciones para el manejo de archivos locales, cálculo de hashes MD5,
obtención de metadatos y escaneo recursivo de directorios.

Funciones principales:
    - calcular_md5(fichero, bloque=65536):
        Calcula el hash MD5 de un fichero.
    - obtener_metadatos(ruta):
        Obtiene metadatos de un archivo como nombre, ruta, tamaño, hash, fecha de creación,
        extensión y tipo MIME.
    - escanear_directorio(base):
        Escanea un directorio de manera recursiva y devuelve la lista de ficheros encontrados.

Dependencias:
    - os: para manejo de archivos y rutas.
    - hashlib: para cálculo de hashes MD5.
    - mimetypes: para obtener tipo MIME de archivos.
    - datetime: para manejo de fechas.
"""

import os
import hashlib
import mimetypes
import datetime

def calcular_md5(fichero, bloque=65536):
    """
    Calcula el hash MD5 de un fichero.

    Args:
        fichero (str): Ruta al archivo cuyo hash se desea calcular.
        bloque (int, opcional): Tamaño de bloque en bytes para leer el archivo. Default: 65536.

    Returns:
        str: Cadena hexadecimal del hash MD5 del archivo.

    Ejemplo:
        hash_archivo = calcular_md5("/tmp/imagen.png")
    """
    md5 = hashlib.md5()
    with open(fichero, "rb") as f:
        while chunk := f.read(bloque):
            md5.update(chunk)
    return md5.hexdigest()

def obtener_metadatos(ruta):
    """
    Obtiene metadatos de un archivo.

    Args:
        ruta (str): Ruta al archivo.

    Returns:
        dict: Diccionario con la siguiente información:
            - nombre (str): Nombre del archivo.
            - ruta (str): Ruta completa.
            - hash_md5 (str): Hash MD5 del archivo.
            - tamano (int): Tamaño en bytes.
            - fecha_creacion (datetime): Fecha de creación del archivo.
            - extension (str): Extensión del archivo (con punto).
            - mime_type (str): Tipo MIME estimado (puede ser None).

    Ejemplo:
        meta = obtener_metadatos("/tmp/imagen.png")
    """
    stat = os.stat(ruta)
    nombre = os.path.basename(ruta)
    tamano = stat.st_size
    fecha_creacion = datetime.datetime.fromtimestamp(stat.st_ctime)
    extension = os.path.splitext(nombre)[1].lower()
    mime_type, _ = mimetypes.guess_type(ruta)
    hash_md5 = calcular_md5(ruta)
    return {
        "nombre": nombre,
        "ruta": ruta,
        "hash_md5": hash_md5,
        "tamano": tamano,
        "fecha_creacion": fecha_creacion,
        "extension": extension,
        "mime_type": mime_type
    }

def escanear_directorio(base):
    """
    Escanea recursivamente un directorio y devuelve la lista de archivos encontrados.

    Args:
        base (str): Ruta del directorio a escanear.

    Returns:
        list[str]: Lista de rutas completas de los archivos encontrados.

    Ejemplo:
        archivos = escanear_directorio("/tmp/Images")
    """
    archivos = []
    for root, _, files in os.walk(base):
        for f in files:
            archivos.append(os.path.join(root, f))
    return archivos
