# Proyecto Inventario de Archivos

Este proyecto permite sincronizar metadatos de ficheros locales en una base de datos MariaDB.
Se registran nombre, ruta, hash MD5, tamaño, fechas, extensión y tipo MIME, manteniendo la tabla siempre sincronizada:

* Inserta archivos nuevos.
* Actualiza archivos modificados.
* Elimina registros de archivos que ya no existen.
* Sube el contenido actual de esa carpeta en un fichero json a varios sitios de un servidor remoto de ficheros

---

## Estructura del proyecto

```bash
proyecto_inventario/
│
├── config/
│   ├── config.json           # Parámetros generales (directorio base, tabla, etc.)
│   └── credenciales.json     # Credenciales de base de datos y otros servicios
│
├── sql/
│   └── create_archivos.sql   # Script SQL para crear la tabla con comentarios
│
├── modules/
│   ├── __init__.py
│   ├── logging_config.py     # Funciones genéricas para tener un log del programa
│   ├── export.py             # Funciones genéricas para exportar información de BBDD a SFTP
│   ├── utils.py              # Funciones genéricas (cargar JSON)
│   ├── db.py                 # Funciones de conexión y consultas a la base de datos
│   ├── files.py              # Utilidades para leer metadatos de ficheros
│   ├── ssh.py                # Utilidades para usar un servidor ssh (sftp)
│   └── sync.py               # Algoritmo de sincronización
│
├── main.py                   # Punto de entrada principal
└── README.md                 # Documentación del proyecto

```

---

## ⚙️ Configuración

`config/config.json`

```json
{
  "directorio_base": "/ruta/a/tu/carpeta",
  "tabla": "archivos",
  "fichero_a_exportar": "listado_archivos.json",
  "rutas_remotas_a_exportar": [
    "/ruta1"
  ],
  "log": {
    "ruta_log": "logs/sincronizar_archivos.log",
    "max_megas": 5,
    "copias": 5
  }
}

```

`config/credenciales.json`

```json
{
  "BBDD": {
    "user": "inventario_user",
    "password": "inventario_pass",
    "host": "localhost",
    "port": 3306,
    "database": "inventario_db"
  },
  "SFTP": [
    "server_SFTP",
    2222,
    "USER_SFTP",
    "PASS_SFTP",
    "",
    ""
  ]
}
```

---

## 🗄️ Base de datos

El script sql/create_archivos.sql crea la tabla para almacenar los metadatos con comentarios

Verifica que la tabla que se crea está correctamente puesta en `config.json`

---

## Requerimientos

Instala las dependencias necesarias (Python 3.9+):

```bash
pip install mariadb paramiko
```

También se puede instalar mediante el comando

```bash
pip install -r requirements.txt
```

### Dependencias estándar de Python

* os, hashlib, mimetypes, datetime, json.

---

## ▶️ Ejecución

* Configura config/config.json y config/credenciales.json.
* Crea la base de datos y la tabla (ejecutando sql/create_archivos.sql o dejando que el programa lo haga en el primer arranque).

Ejecuta el programa:
```bash
python main.py
```

---

## Logging del programa

El proyecto utiliza el módulo logging de Python para registrar la actividad del script. Esto es especialmente útil cuando se ejecuta desde cron, ya que no hay consola visible.

### ⚙️ Configuración del log

Los parámetros del log se configuran en `config/config.json`:

```json
"log": {
  "ruta_log": "logs/sincronizar_archivos.log",
  "max_megas": 5,
  "copias": 5
}
```

* ruta_log: ruta del fichero donde se almacenan los logs.
* max_megas: tamaño máximo del fichero de log en MB antes de rotar.
* copias: número de ficheros de log antiguos que se mantienen (rotación).
* El programa crea automáticamente la carpeta logs/ si no existe.

### 📄 Comportamiento del log

* Se registra información relevante del programa (INFO, WARNING, ERROR).
* Se silencian los mensajes INFO internos de paramiko, para no llenar el log con información de SFTP.
* Cuando el fichero de log supera el tamaño máximo (max_megas), se rota automáticamente, creando copias numeradas:

```bash
sincronizar_archivos.log        <-- log actual
sincronizar_archivos.log.1      <-- copia más reciente
sincronizar_archivos.log.2      <-- copia anterior
...
```

### 📝 Ejemplo de entradas en el log

```bash
2025-10-04 17:23:58 [INFO] root: === Inicio de sincronización de archivos ===
2025-10-04 17:23:59 [INFO] modules.sync: Sincronización completada con 321 archivos
2025-10-04 17:24:00 [INFO] modules.export: Fichero JSON exportado: listado_archivos.json
2025-10-04 17:24:02 [INFO] root: ✅ Sincronización y exportación completadas correctamente.
2025-10-04 17:24:03 [ERROR] modules.ssh: ❌ Error al subir fichero a /ruta1

```

---

## Archivos generados

El programa genera un archivo json que se pone en la tabla SQL para comparar y lo sube a varias carpetas SFTP

Este archivo no lo borra, lo reemplaza al ejecutar el programa.

