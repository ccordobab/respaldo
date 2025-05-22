# main.py
import os
from backup import file_collector, compressor, encryptor, fragmenter

# 1. Seleccionar carpetas
carpetas = [
    r"C:\Users\Camilo\Documents\Importante",
    r"D:\Universidad\Proyectos"
]

# 2. Recolectar archivos
print("Recolectando archivos...")
archivos = file_collector.recolectar_archivos(carpetas)

# 3. Comprimirlos con Dask
print("Comprimiendo archivos...")
os.makedirs("output", exist_ok=True)
ruta_zip = "output/respaldo.zip"
compressor.comprimir_archivos(archivos, ruta_zip, base_dir=os.path.commonpath(carpetas))

# 4. Encriptar (si se desea)
encriptar = True
if encriptar:
    clave = encryptor.generar_clave()
    encryptor.guardar_clave(clave, "output/clave.key")
    ruta_encriptado = "output/respaldo_encriptado.zip"
    encryptor.encriptar_archivo(ruta_zip, ruta_encriptado, clave)
    os.remove(ruta_zip)
    ruta_final = ruta_encriptado
else:
    ruta_final = ruta_zip

# 5. Fragmentar para USBs
print("Fragmentando en partes de 100MB para USB...")
fragmenter.fragmentar_archivo(ruta_final, tamaño_mb=100, carpeta_salida="output/fragmentos")

print("¡Respaldo completado!")
