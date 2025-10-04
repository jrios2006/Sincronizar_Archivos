#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================
Sincronizador Cliente de Metadatos de Archivos
=========================================================

Este script se ejecuta en el CLIENTE y tiene como objetivo:
    - Descargar desde un servidor SFTP un fichero JSON con la información
      de los archivos esperados (metadatos).
    - Comparar esa información con la carpeta local del cliente.
    - Generar un informe HTML de diferencias.
    - Enviar el informe por correo electrónico y/o subirlo por SFTP.

El comportamiento se define mediante:
    - config/config.json          → Parámetros de ejecución
    - config/credenciales.json    → Credenciales de conexión (SFTP, correo)
    - modules/                    → Módulos de funciones reutilizables

Dependencias externas:
    pip install paramiko

Versión: 1.0
Fecha: 2025-10-04
"""

from modules import ssh, utils, verificar
from modules.logging_config import configurar_logger
import json
import os

if __name__ == "__main__":
    # Cargar configuración y credenciales
    config = utils.cargar_config("config/config.json")
    credenciales = utils.cargar_credenciales("config/credenciales.json")

    # Configurar logger usando tu módulo
    logger = configurar_logger(config)

    logger.info("=== INICIO DEL SCRIPT ===")

    # Descargar JSON maestro
    exito, json_local = ssh.DescargarArchivoSFTP(
        credenciales["SFTP"],
        config["fichero_json_origen"],
        config["ruta_remota_fichero"]
    )
    if not exito:
        logger.error("No se pudo descargar el JSON del servidor")
        exit(1)

    # Leer JSON
    with open(json_local, "r", encoding="utf-8") as f:
        json_servidor = json.load(f)

    # Procesar diferencias y generar HTML + enviar
    verificar.procesar_diferencias(
        json_servidor,
        config["carpeta_local"],
        config["ruta_html_salida"],
        config["accion_salida"],
        {
            **credenciales,
            "ruta_remota_salida": config["ruta_remota_salida"],
            "email": config["email"]
        },
        nombre_servidor=config.get("servidor_nombre", "ServidorDesconocido")
    )

    logger.info("=== FIN DEL SCRIPT ===")
