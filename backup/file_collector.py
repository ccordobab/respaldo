import os

def recolectar_archivos(rutas_carpeta):
    archivos = []
    for carpeta in rutas_carpeta:
        for raiz, _, nombres in os.walk(carpeta):
            for nombre in nombres:
                archivos.append(os.path.join(raiz, nombre))
    return archivos
