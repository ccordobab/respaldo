import math

def fragmentar_archivo(ruta_archivo, tamaño_mb, carpeta_salida):
    tamaño_bytes = tamaño_mb * 1024 * 1024
    with open(ruta_archivo, 'rb') as f:
        i = 0
        while True:
            chunk = f.read(tamaño_bytes)
            if not chunk:
                break
            with open(f"{carpeta_salida}/parte_{i:03}.bin", 'wb') as out:
                out.write(chunk)
            i += 1
