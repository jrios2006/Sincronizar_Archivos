CREATE TABLE IF NOT EXISTS imagenes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único',
    nombre VARCHAR(255) NOT NULL COMMENT 'Nombre del archivo',
    ruta TEXT NOT NULL COMMENT 'Ruta absoluta en el sistema',
    hash_md5 CHAR(32) NOT NULL COMMENT 'Hash MD5 del contenido',
    tamano BIGINT NOT NULL COMMENT 'Tamaño en bytes',
    fecha_creacion DATETIME NOT NULL COMMENT 'Fecha de creación del fichero en el sistema',
    extension VARCHAR(20) COMMENT 'Extensión del archivo',
    mime_type VARCHAR(100) COMMENT 'Tipo MIME detectado',
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de la última actualización en la BD',
    UNIQUE KEY (ruta(255))
) COMMENT='Inventario de imagenes locales';
