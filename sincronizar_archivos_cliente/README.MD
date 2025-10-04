# Proyecto Reporte diferencias de archivos

Este proyecto descarga un fichero json con el resumen de los metadatos que deberían de tener el cliente en una carpeta.
Se analizan diferencias y estas generan un archivo html

* Se sube a un sitio remoto.
* Se envía por mail a un operador.
* Si no hay diferencias no se envía nada.

---

## Estructura del proyecto

```bash
sincronizar_archivos_cliente/
│
├── config/
│   ├── config.json           # Parámetros generales (directorio base, etc.)
│   └── credenciales.json     # Credenciales de acceso a sistemas externos que usamos o usaremos
│
├── templates/
│   └── diferencias.html.j2   # Plantilla para poder renderizar un archivo HTML
│
├── modules/
│   ├── __init__.py
│   ├── email_module.py       # Funciones genéricas para enviar un correo electrónico
│   ├── logging_config.py     # Funciones genéricas para tener un log del programa
│   ├── export.py             # Funciones genéricas para exportar información de BBDD a SFTP
│   ├── utils.py              # Funciones genéricas (cargar JSON)
│   ├── files.py              # Utilidades para leer metadatos de ficheros
│   ├── ssh.py                # Utilidades para usar un servidor ssh (sftp)
│   ├── verificar.py          # Utilidades para verificar diferencias y generar reportes
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
  "carpeta_local": "Ruta local a colocar",
  "fichero_json_origen": "inventario_imagenes.json",
  "ruta_html_salida": "diferencias_inventario_imagenes.html",
  "accion_salida": "TODOS",  
  "documentacion_accion_salida" : "SFTP, EMAIL, TODOS",
  "ruta_remota_fichero": "Ruta remota donde está el fichero origina",
  "ruta_remota_salida": "Ruta remota donde depositar el informe generado",
  "servidor_nombre" : "Nombre del Cliente",
  "email": {
    "para": "operador@dominio.com",
    "asunto": "Diferencias con el repositorio central de imágenes con el cliente"
  },
    "log": {
    "ruta_log": "logs/cliente.log",
    "max_megas": 5,
    "copias": 3
  }
}

```

`config/credenciales.json`

```json
{
    "SFTP": [
    "servidor sftp",
    2222,
    "user sftp",
    "password user sftp",
    "",
    ""
    ],
    "CORREO" : [
        "noreply@dominio.com",
        "smtp.serviciodecorreo.es",
        465,
        "noreply@dominio.com",
        "pass user email"
    ]
}
```

---


## Requerimientos

Instala las dependencias necesarias (Python 3.9+):

```bash
pip install paramiko jinja2
```

También se puede instalar mediante el comando

```bash
pip install -r requirements.txt
```

### Dependencias estándar de Python

* os, hashlib, mimetypes, datetime, json, smtp.

---

## ▶️ Ejecución

* Configura config/config.json y config/credenciales.json.

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
  "ruta_log": "logs/cliente.log",
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
2025-10-04 13:26:44 [INFO] root: === INICIO DEL SCRIPT ===
2025-10-04 13:26:45 [INFO] modules.verificar: No hay diferencias. No se enviará ningún HTML ni se subirá a SFTP.
2025-10-04 13:26:45 [INFO] root: === FIN DEL SCRIPT ===
```

---

## Archivos generados

El programa genera un archivo json que se baja del sitio SFTP y no lo borra, lo reemplaza al ejecutar el programa.

Si no hay conexión tendrá uno con el que comparar antiguo.

Se genera un archivo .html con el informe de diferencias. Tampoco se borra y se reemplaza en cada ejecución. Puede que se suba o no dependiendo de la configuración o de si hay o no diferencias encontradas

Si la ruta donde busca no existe para el programa generará un archivo con todas las diferencias posibles.