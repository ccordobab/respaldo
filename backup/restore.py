# backup/restore.py
import os
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

def desencriptar_archivo(archivo_encriptado, archivo_salida, clave_path):
    """Versión mejorada de desencriptación"""
    # Verificaciones iniciales
    if not os.path.exists(archivo_encriptado):
        raise FileNotFoundError(f"Archivo encriptado no encontrado: {archivo_encriptado}")
    if os.path.getsize(archivo_encriptado) == 0:
        raise ValueError("El archivo encriptado está vacío")
    if not os.path.exists(clave_path):
        raise FileNotFoundError(f"Archivo clave no encontrado: {clave_path}")

    # Leer clave
    with open(clave_path, 'rb') as f:
        clave = f.read()

    # Desencriptar en bloques
    fernet = Fernet(clave)
    try:
        with open(archivo_encriptado, 'rb') as f_in, open(archivo_salida, 'wb') as f_out:
            while True:
                chunk = f_in.read(64 * 1024 + 64)  # Tamaño ajustado para chunks encriptados
                if not chunk:
                    break
                f_out.write(fernet.decrypt(chunk))
        
        # Verificación final
        if os.path.getsize(archivo_salida) == 0:
            os.remove(archivo_salida)
            raise ValueError("El archivo desencriptado está vacío - verifique la clave")
    
    except Exception as e:
        if os.path.exists(archivo_salida):
            os.remove(archivo_salida)
        raise

def recombinar_fragmentos(carpeta_fragmentos: str, archivo_salida: str):
    """Combina fragmentos .bin en un archivo completo"""
    fragmentos = sorted(Path(carpeta_fragmentos).glob("*.bin"))
    if not fragmentos:
        raise ValueError("No se encontraron fragmentos .bin en la carpeta")
    
    # Validar tamaño de fragmentos
    for f in fragmentos:
        if f.stat().st_size == 0:
            raise ValueError(f"El fragmento {f.name} está vacío.")

    with open(archivo_salida, 'wb') as output:
        for fragmento in fragmentos:
            with open(fragmento, 'rb') as f:
                output.write(f.read())


def descomprimir_archivo(archivo_comprimido, carpeta_destino):
    """Extrae archivos ZIP verificando integridad"""
    if not zipfile.is_zipfile(archivo_comprimido):
        raise ValueError("El archivo no es un ZIP válido")
    
    with zipfile.ZipFile(archivo_comprimido, 'r') as zip_ref:
        # Verificar integridad
        if zip_ref.testzip() is not None:
            raise ValueError("Archivo ZIP corrupto")
        zip_ref.extractall(carpeta_destino)

def restaurar_respaldo(origen: str, destino: str, clave_path: str = None, es_fragmentado: bool = False):
    try:
        if es_fragmentado:
            archivo_temp = os.path.join(os.path.dirname(origen), "temp_restore.zip")
            print(f"Recombinando fragmentos en: {archivo_temp}")
            recombinar_fragmentos(origen, archivo_temp)
            print(f"Archivo recombinado tamaño: {os.path.getsize(archivo_temp)} bytes")
            origen = archivo_temp
        else:
            archivo_temp = None

        if clave_path:
            archivo_desencriptado = origen + ".decrypted"
            print(f"Desencriptando archivo {origen} a {archivo_desencriptado}")
            desencriptar_archivo(origen, archivo_desencriptado, clave_path)
            print(f"Archivo desencriptado tamaño: {os.path.getsize(archivo_desencriptado)} bytes")
            origen = archivo_desencriptado
        else:
            archivo_desencriptado = None

        print(f"Descomprimiendo archivo {origen} en {destino}")
        descomprimir_archivo(origen, destino)

    except Exception as e:
        print(f"[ERROR] {e}")  
        if 'archivo_temp' in locals() and archivo_temp and os.path.exists(archivo_temp):
            os.remove(archivo_temp)
        if 'archivo_desencriptado' in locals() and archivo_desencriptado and os.path.exists(archivo_desencriptado):
            os.remove(archivo_desencriptado)
        raise