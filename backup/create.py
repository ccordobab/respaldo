# backup/create.py
import os
import shutil
from pathlib import Path
from backup.cloud.google_drive import GoogleDriveProvider
from backup.encryptor import generar_clave, guardar_clave, encriptar_archivo

def crear_respaldo(
    carpeta_a_resguardar: str,
    carpeta_salida: str,
    encriptar: bool = True,
    fragmentar: bool = True,
    tamano_fragmento_mb: int = 100,
    clave_path: str = None,
    upload_to_cloud: bool = False,
):
    # 1. Inicialización de variables de resultado
    resultado = {
        'success': True,
        'archivo_principal': None,
        'clave_generada': None,
        'fragmentos': None,
        'drive_status': None,
        'warnings': []
    }

    try:
        # 2. Validación de rutas
        if not os.path.exists(carpeta_a_resguardar):
            raise FileNotFoundError(f"Carpeta a respaldar no existe: {carpeta_a_resguardar}")

        os.makedirs(carpeta_salida, exist_ok=True)
        if not os.access(carpeta_salida, os.W_OK):
            raise PermissionError(f"No hay permisos de escritura en: {carpeta_salida}")

        # 3. Creación del archivo ZIP
        nombre_zip = "respaldo.zip"
        ruta_zip = os.path.join(carpeta_salida, nombre_zip)
        shutil.make_archive(os.path.splitext(ruta_zip)[0], 'zip', carpeta_a_resguardar)
        archivo_para_subir = ruta_zip

        # 4. Encriptación (si aplica)
        clave = None
        if encriptar:
            if clave_path:
                # Leer clave existente SIN modificaciones
                with open(clave_path, 'rb') as f:
                    clave = f.read()
            else:
                # Generar clave nueva (usando encryptor.py)
                clave = generar_clave()
                ruta_clave = os.path.join(carpeta_salida, "clave.key")
                guardar_clave(clave, ruta_clave)
                resultado['clave_generada'] = ruta_clave
            
            # Encriptar (usando encryptor.py)
            ruta_encriptado = os.path.join(carpeta_salida, "respaldo_encriptado.zip")
            encriptar_archivo(ruta_zip, ruta_encriptado, clave)
            archivo_para_subir = ruta_encriptado
        
        resultado['archivo_principal'] = archivo_para_subir

        # 5. Fragmentación (si aplica)
        if fragmentar:
            carpeta_fragmentos = os.path.join(carpeta_salida, "fragmentos")
            try:
                os.makedirs(carpeta_fragmentos, exist_ok=True)
                if os.access(carpeta_fragmentos, os.W_OK):
                    # Lógica de fragmentación aquí
                    pass
                else:
                    msg = f"Sin permisos para fragmentos en: {carpeta_fragmentos}"
                    resultado['warnings'].append(msg)
            except Exception as e:
                resultado['warnings'].append(f"Error en fragmentación: {str(e)}")
            
            resultado['fragmentos'] = carpeta_fragmentos

        # 6. Subida a Google Drive
        if upload_to_cloud:
            try:
                archivo_path = Path(archivo_para_subir)
                if not archivo_path.exists():
                    raise FileNotFoundError(f"Archivo no encontrado: {archivo_path}")

                drive = GoogleDriveProvider()
                if not drive.authenticate():
                    raise ConnectionError("Falló la autenticación con Google Drive")
                
                drive.upload_file(str(archivo_path))
                resultado['drive_status'] = "Subida exitosa a Google Drive"
                
            except Exception as e:
                resultado['drive_status'] = f"Error en Google Drive: {str(e)}"
                resultado['warnings'].append(resultado['drive_status'])

        return resultado

    except Exception as e:
        resultado.update({
            'success': False,
            'error': str(e)
        })
        return resultado