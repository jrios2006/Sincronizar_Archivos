"""
Módulo `correo`
----------------

Proporciona funciones para validar direcciones de correo electrónico y enviar correos
usando SMTP/SSL, con soporte para adjuntar archivos y copia oculta al remitente.

Funciones principales:
    - ValidarSintaxisEmail(email): Valida sintácticamente la dirección de correo.
    - EnviarCorreoSSL(credenciales, destinatario, asunto, mensaje, archivo, CopiaOculta=True):
        Envía un correo electrónico con mensaje HTML y opcionalmente un archivo adjunto.

Dependencias:
    - logging: para registrar errores e información sobre el envío.
    - smtplib, ssl, email.mime: para construir y enviar el correo.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging # para guardar un log
logger = logging.getLogger(__name__)

def ValidarSintaxisEmail(email):
    """
    Valida sintácticamente una dirección de correo electrónico.

    Args:
        email (str): Dirección de correo a validar.

    Returns:
        bool: True si la dirección tiene un formato válido, False en caso contrario.

    Ejemplo:
        >>> ValidarSintaxisEmail("usuario@dominio.com")
        True
        >>> ValidarSintaxisEmail("usuario@@dominio")
        False
    """
    import re
    Aux = False
    addressToVerify ='info@emailhippo.com'
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', \
                     email)
    if match == None:
	    #print('Bad Syntax: ' + email )
        A = 0
    else:
        Aux = True
    return Aux

def EnviarCorreoSSL(credenciales, destinatario, asunto, mensaje, archivo, CopiaOculta=True):
    """
    Envía un correo electrónico mediante un servidor SMTP con SSL.

    Args:
        credenciales (list): Lista con credenciales y datos del servidor:
            [remitente, smtp_server, smtp_port, smtp_user, smtp_pass]
        destinatario (str): Dirección de correo del receptor.
        asunto (str): Asunto del correo.
        mensaje (str): Cuerpo del mensaje en HTML.
        archivo (str): Ruta del archivo a adjuntar (opcional).
        CopiaOculta (bool, opcional): Si True, envía copia oculta al remitente.

    Returns:
        tuple:
            - bool: True si el correo se envió correctamente, False en caso de error.
            - dict: Contiene el mensaje de éxito o el detalle del error.

    Comportamiento:
        - Adjunta el archivo especificado si existe.
        - Registra errores de conexión, autenticación, remitente o destinatario.
        - Usa formato HTML para el mensaje.

    Ejemplo:
        credenciales = ["noreply@dominio.com", "smtp.servidor.es", 465, "noreply@dominio.com", "password"]
        EnviarCorreoSSL(credenciales, "usuario@dominio.com", "Asunto", "<p>Mensaje HTML</p>", "archivo.pdf")
    """
    import smtplib
    import ssl
    import os

    # importamos librerias  para construir el mensaje
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    #importamos librerias para adjuntar
    #from email.MIMEBase import MIMEBase
    from email.mime.base import MIMEBase
    from email import encoders 
    from email.encoders import encode_base64    

    Aux = False # Variable que contiene el estado del enví­o
    Errores = {}
    # Obtenemos las credenciales de envío del correo
    # [remitente, smtp_server, smtp_port, smtp_user, smtp_pass]
    remitente = credenciales[0]
    smtp_server = credenciales[1]
    smtp_port = credenciales[2]
    smtp_user = credenciales[3]
    smtp_pass = credenciales[4]
    
    context = ssl.create_default_context()
    Conectado = False
    Cadena = ''
    #Generamos el objeto del mensaje
    header = MIMEMultipart()
    header['Subject'] = asunto
    header['From'] = remitente
    header['To'] = destinatario
    if CopiaOculta:
        header['Bcc'] = remitente
    # Componemos el mensaje
    mensaje = MIMEText(mensaje, 'html') #Content-type:text/html
    header.attach(mensaje)
    if (os.path.isfile(archivo)):
        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(open(archivo, "rb").read())
        encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(archivo))
        header.attach(adjunto)    
    #Intentamos hacer la conexión con el servidor de correo
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as servidor_correo:
            servidor_correo.login(smtp_user, smtp_pass)
            #servidor_correo.set_debuglevel(2)  # Habilitar el nivel de depuración  
            servidor_correo.sendmail(remitente, destinatario, header.as_string())
        Aux = True
    except smtplib.SMTPAuthenticationError:
        Cadena = 'La contraseña del usuario de correo ' + smtp_user + ' no es correcta en el servidor ' + smtp_server
    except smtplib.SMTPException as e:
        Cadena = 'Ha ocurrido una exepción con el usuario de correo ' + smtp_user + ' y el servidor ' + smtp_server
        logger.error(e)
    except smtplib.SMTPSenderRefused:
        Cadena = 'El remitente de correo ' + remitente + ' no puede enviar un mail con el usuario ' + smtp_user + ' y el servidor ' + smtp_server
    except smtplib.SMTPDataError:
        Cadena = 'Se ha producido un error con el usuario ' + smtp_user + ' y el servidor ' + smtp_server + '. No se puede enviar el mail'
    except smtplib.SMTPRecipientsRefused:
        Cadena = 'No es posible enviar un correo al destinatario del correo ' + destinatario + ' a través del servidor ' + smtp_server + ' con el usuario ' + smtp_user
    if (Cadena != ''):
        Errores['Error'] = Cadena
        logger.error(Cadena)
        Cadena = ''
    else:
        Cadena = 'Correo enviado a ' + destinatario + ' a través del servidor ' + smtp_server + ' con asunto ' + asunto
        logger.info(Cadena)
        Errores['Mensaje'] = Cadena          
    return Aux, Errores