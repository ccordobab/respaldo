# backup/encryptor.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

def generar_clave():
    return Fernet.generate_key()

def guardar_clave(clave, ruta):
    with open(ruta, 'wb') as f:
        f.write(clave)

def encriptar_archivo(ruta_input, ruta_output, clave):
    # Verificar archivo de entrada
    if not os.path.exists(ruta_input):
        raise FileNotFoundError(f"Archivo a encriptar no encontrado: {ruta_input}")
    if os.path.getsize(ruta_input) == 0:
        raise ValueError("El archivo a encriptar está vacío")

    fernet = Fernet(clave)
    
    # Encriptar en bloques
    with open(ruta_input, 'rb') as f_in, open(ruta_output, 'wb') as f_out:
        while True:
            chunk = f_in.read(64 * 1024)  # 64KB chunks
            if not chunk:
                break
            f_out.write(fernet.encrypt(chunk))