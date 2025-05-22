from cryptography.fernet import Fernet

def generar_clave():
    return Fernet.generate_key()

def guardar_clave(clave, ruta):
    with open(ruta, 'wb') as f:
        f.write(clave)

def encriptar_archivo(ruta_input, ruta_output, clave):
    fernet = Fernet(clave)
    with open(ruta_input, 'rb') as f:
        datos = f.read()
    datos_encriptados = fernet.encrypt(datos)
    with open(ruta_output, 'wb') as f:
        f.write(datos_encriptados)
