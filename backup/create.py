# backup/create.py
import os
from backup import file_collector, compressor, encryptor, fragmenter

def crear_respaldo(
    carpeta_a_resguardar: str,
    carpeta_salida: str,
    encriptar: bool = True,
    fragmentar: bool = True,
    tamano_fragmento_mb: int = 100,
    clave_path: str = None
):
    carpetas = [carpeta_a_resguardar]

    archivos = file_collector.recolectar_archivos(carpetas)
    if not archivos:
        raise ValueError("No se encontraron archivos para respaldar.")

    os.makedirs(carpeta_salida, exist_ok=True)
    ruta_zip = os.path.join(carpeta_salida, "respaldo.zip")
    compressor.comprimir_archivos(archivos, ruta_zip, base_dir=os.path.commonpath(carpetas))

    if encriptar:
        if clave_path:
            # Leer clave existente
            with open(clave_path, 'rb') as f:
                clave = f.read()
        else:
            # Generar clave nueva
            clave = encryptor.generar_clave()
            encryptor.guardar_clave(clave, os.path.join(carpeta_salida, "clave.key"))

        ruta_encriptado = os.path.join(carpeta_salida, "respaldo_encriptado.zip")
        encryptor.encriptar_archivo(ruta_zip, ruta_encriptado, clave)
        if os.path.getsize(ruta_encriptado) == 0:
            raise ValueError("El archivo encriptado está vacío")
        os.remove(ruta_zip)
        ruta_final = ruta_encriptado
    else:
        ruta_final = ruta_zip

    if fragmentar:
        carpeta_fragmentos = os.path.join(carpeta_salida, "fragmentos")
        os.makedirs(carpeta_fragmentos, exist_ok=True)
        fragmenter.fragmentar_archivo(ruta_final, tamaño_mb=tamano_fragmento_mb, carpeta_salida=carpeta_fragmentos)
        ruta_final = carpeta_fragmentos

    return ruta_final
