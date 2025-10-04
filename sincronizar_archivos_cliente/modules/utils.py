"""
Módulo `utils`
---------------

Proporciona funciones auxiliares para la carga de archivos JSON de configuración
y credenciales del proyecto. Permite centralizar la lectura de ficheros y
facilita la gestión de rutas y valores por defecto.

Funciones principales:
    - cargar_json(ruta): Carga cualquier fichero JSON y devuelve un diccionario.
    - cargar_config(ruta=None): Carga el fichero de configuración principal del proyecto.
    - cargar_credenciales(ruta=None): Carga el fichero de credenciales del proyecto.

Dependencias:
    - json: para la lectura de archivos JSON.
    - os: para gestión de rutas y construcción de paths.
"""
import json
import os

def cargar_json(ruta):
    """
    Carga un archivo JSON desde la ruta especificada y devuelve su contenido como diccionario.

    Args:
        ruta (str): Ruta completa del archivo JSON a cargar.

    Returns:
        dict: Contenido del JSON convertido a un diccionario de Python.

    Ejemplo:
        data = cargar_json("config/config.json")
    """
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_config(ruta=None):
    """
    Carga el fichero de configuración principal del proyecto.

    Si no se especifica `ruta`, por defecto carga `config/config.json`.

    Args:
        ruta (str, opcional): Ruta del archivo de configuración. Default: None.

    Returns:
        dict: Diccionario con los parámetros de configuración.

    Ejemplo:
        config = cargar_config()  # carga config/config.json por defecto
        config = cargar_config("config/config_cliente.json")
    """
    if ruta is None:
        ruta = os.path.join("config", "config.json")
    return cargar_json(ruta)


def cargar_credenciales(ruta=None):
    """
    Carga el fichero de credenciales del proyecto.

    Si no se especifica `ruta`, por defecto carga `config/credenciales.json`.

    Args:
        ruta (str, opcional): Ruta del archivo de credenciales. Default: None.

    Returns:
        dict: Diccionario con las credenciales (SFTP, correo, BBDD, etc.).

    Ejemplo:
        credenciales = cargar_credenciales()  # carga config/credenciales.json por defecto
        credenciales = cargar_credenciales("config/credenciales_cliente.json")
    """
    if ruta is None:
        ruta = os.path.join("config", "credenciales.json")
    return cargar_json(ruta)
