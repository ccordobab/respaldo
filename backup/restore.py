# backup/restore.py
import os
import zipfile
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

def verificar_archivo_encriptado(ruta):
    """Verifica integridad básica del archivo encriptado"""
    size = os.path.getsize(ruta)
    if size < 16:
        raise ValueError(f"Archivo encriptado corrupto (tamaño: {size} bytes)")
    with open(ruta, 'rb') as f:
        header = f.read(5)
        if header != b'gAAAA':
            raise ValueError("Encabezado encriptado inválido (¿archivo corrupto?)")

def normalizar_clave(clave_bytes):
    """Normaliza la clave eliminando caracteres problemáticos"""
    # Primero intentamos decodificar a UTF-8
    try:
        clave_str = clave_bytes.decode('utf-8').strip()
        # Eliminamos todos los whitespaces (incluyendo \r, \n, etc.)
        clave_str = ''.join(clave_str.split())
        return clave_str.encode('utf-8')
    except UnicodeDecodeError:
        # Si no es UTF-8 válido, devolvemos los bytes originales limpios
        return clave_bytes.strip()
    
def desencriptar_archivo(archivo_encriptado, archivo_salida, clave_path):
    """Versión corregida que coincide con el método de encriptación original"""
    try:
        # Verificaciones iniciales
        if not os.path.exists(archivo_encriptado):
            raise FileNotFoundError(f"Archivo encriptado no encontrado: {archivo_encriptado}")
        
        if os.path.getsize(archivo_encriptado) == 0:
            raise ValueError("El archivo encriptado está vacío")

        # Leer clave SIN normalización (para mantener compatibilidad)
        with open(clave_path, 'rb') as f:
            clave = f.read().strip()  # Solo strip() básico
            
            # Verificación mínima de clave
            if len(clave) != 44:
                raise ValueError("La clave debe tener exactamente 44 caracteres (formato Fernet)")

        fernet = Fernet(clave)
        
        # Desencriptar en bloques (mismo tamaño que en encryptor.py)
        with open(archivo_encriptado, 'rb') as f_in, open(archivo_salida, 'wb') as f_out:
            while True:
                chunk = f_in.read(64 * 1024)  # 64KB chunks (igual que en encriptación)
                if not chunk:
                    break
                try:
                    f_out.write(fernet.decrypt(chunk))
                except InvalidToken:
                    raise ValueError("Clave incorrecta o archivo corrupto - no se pudo desencriptar")

        # Verificación final
        if os.path.getsize(archivo_salida) == 0:
            os.remove(archivo_salida)
            raise ValueError("El archivo desencriptado está vacío")

    except Exception as e:
        if os.path.exists(archivo_salida):
            os.remove(archivo_salida)
        raise

def recombinar_fragmentos(carpeta_fragmentos: str, archivo_salida: str):
    """Combina fragmentos .bin en un archivo completo"""
    fragmentos = sorted(Path(carpeta_fragmentos).glob("parte_*.bin"))  # Cambiado para coincidir con tu formato
    
    if not fragmentos:
        raise ValueError("No se encontraron fragmentos .bin en la carpeta")
    
    with open(archivo_salida, 'wb') as output:
        for fragmento in fragmentos:
            with open(fragmento, 'rb') as f:
                output.write(f.read())

def descomprimir_archivo(archivo_comprimido, carpeta_destino):
    """Extrae archivos ZIP con verificación de integridad"""
    if not zipfile.is_zipfile(archivo_comprimido):
        raise ValueError("El archivo no es un ZIP válido")
    
    with zipfile.ZipFile(archivo_comprimido, 'r') as zip_ref:
        # Verificación de integridad
        archivo_corrupto = zip_ref.testzip()
        if archivo_corrupto is not None:
            raise ValueError(f"Archivo ZIP corrupto (archivo afectado: {archivo_corrupto})")
        
        # Extracción con manejo de rutas seguras
        for file in zip_ref.namelist():
            zip_ref.extract(file, carpeta_destino)

def restaurar_respaldo(origen: str, destino: str, clave_path: str = None, es_fragmentado: bool = False):
    archivo_temp = None
    archivo_desencriptado = None
    
    try:
        # 1. Validación inicial
        if not os.path.exists(origen):
            raise FileNotFoundError(f"Ruta de origen no existe: {origen}")
        
        if not os.path.exists(destino):
            os.makedirs(destino, exist_ok=True)
        
        # 2. Manejo de fragmentos
        if es_fragmentado:
            if not os.path.isdir(origen):
                raise ValueError("Para restauración fragmentada, el origen debe ser una carpeta")
            
            archivo_temp = os.path.join(os.path.dirname(origen), "temp_restore.zip")
            print(f"\n[1/3] Recombinando {len(list(Path(origen).glob('*.bin')))} fragmentos...")
            recombinar_fragmentos(origen, archivo_temp)
            origen = archivo_temp

        # 3. Desencriptación
        if clave_path:
            archivo_desencriptado = origen + ".decrypted"
            print(f"\n[2/3] Desencriptando archivo...")
            desencriptar_archivo(origen, archivo_desencriptado, clave_path)
            origen = archivo_desencriptado

        # 4. Descompresión
        print(f"\n[3/3] Descomprimiendo en {destino}...")
        descomprimir_archivo(origen, destino)
        print("\n✅ Restauración completada con éxito")

    except Exception as e:
        # Manejo detallado de errores
        error_msg = f"""
        ERROR EN RESTAURACIÓN:
        Tipo: {type(e).__name__}
        Mensaje: {str(e)}
        Origen: {origen}
        Destino: {destino}
        Clave: {'Sí' if clave_path else 'No'}
        Fragmentado: {'Sí' if es_fragmentado else 'No'}
        """
        raise RuntimeError(error_msg) from e

    finally:
        # Limpieza de archivos temporales
        for temp_file in [archivo_temp, archivo_desencriptado]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"Archivo temporal eliminado: {temp_file}")
                except Exception as e:
                    print(f"Advertencia: No se pudo eliminar {temp_file}: {str(e)}")