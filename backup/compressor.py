# backup/compressor.py
import zipfile
from dask import delayed, compute
import os

@delayed
def agregar_archivo(zip_path, archivo, arcname):
    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(archivo, arcname)

def comprimir_archivos(archivos, salida_zip, base_dir=None):
    """
    Crea un archivo ZIP estándar usando compresión DEFLATE en paralelo con Dask
    """
    # Crear archivo vacío primero
    with zipfile.ZipFile(salida_zip, 'w', zipfile.ZIP_DEFLATED):
        pass

    tareas = []
    for archivo in archivos:
        arcname = os.path.relpath(archivo, base_dir) if base_dir else os.path.basename(archivo)
        tareas.append(agregar_archivo(salida_zip, archivo, arcname))

    compute(*tareas)
