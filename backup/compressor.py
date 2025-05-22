import pyzipper
from dask import delayed, compute
import os

@delayed
def agregar_a_zip(zip_path, archivo, base_dir):
    arcname = os.path.relpath(archivo, base_dir)
    with pyzipper.AESZipFile(zip_path, 'a', compression=pyzipper.ZIP_LZMA) as zf:
        with open(archivo, 'rb') as f:
            zf.writestr(arcname, f.read())

def comprimir_archivos(archivos, salida_zip, base_dir):
    tareas = [agregar_a_zip(salida_zip, f, base_dir) for f in archivos]
    compute(*tareas)
