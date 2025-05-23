import argparse
from backup import file_collector, compressor, encryptor, fragmenter, restore
import os

def comando_respaldo():
    carpeta_base = os.path.dirname(__file__)
    ruta_carpeta = os.path.join(carpeta_base, "carpetaAComprimir")
    carpetas = [ruta_carpeta]

    print("Recolectando archivos...")
    archivos = file_collector.recolectar_archivos(carpetas)

    if not archivos:
        print("[ADVERTENCIA] No se encontraron archivos para respaldar.")
    else:
        print(f"Archivos encontrados para respaldar:\n{archivos}")

    print("Comprimiendo archivos...")
    os.makedirs("output", exist_ok=True)
    ruta_zip = "output/respaldo.zip"
    compressor.comprimir_archivos(archivos, ruta_zip, base_dir=os.path.commonpath(carpetas))

    print("Encriptando archivo...")
    clave = encryptor.generar_clave()
    encryptor.guardar_clave(clave, "output/clave.key")
    ruta_encriptado = "output/respaldo_encriptado.zip"  # Cambia extensión
    encryptor.encriptar_archivo(ruta_zip, ruta_encriptado, clave)
    
    # Verificar que el archivo encriptado no esté vacío
    if os.path.getsize(ruta_encriptado) == 0:
        raise ValueError("El archivo encriptado está vacío")
    
    os.remove(ruta_zip)  # Eliminar el ZIP original
    ruta_final = ruta_encriptado

    print("Fragmentando en partes de 100MB para USB...")
    fragmenter.fragmentar_archivo(ruta_final, tamaño_mb=100, carpeta_salida="output/fragmentos")

    print("¡Respaldo completado!")

def comando_restaurar(args):
    print("Iniciando proceso de restauración...")
    restore.restaurar_respaldo(
        origen=args.origen,
        destino=args.destino,
        clave_path=args.clave,
        es_fragmentado=args.fragmentado
    )
    print("¡Restauración completada!")

def main():
    parser = argparse.ArgumentParser(description="Sistema de respaldo y restauración")
    subparsers = parser.add_subparsers(dest='comando')

    subparser_respaldo = subparsers.add_parser('respaldar', help='Realizar respaldo')
    subparser_restaurar = subparsers.add_parser('restaurar', help='Restaurar respaldo')
    subparser_restaurar.add_argument('--origen', required=True)
    subparser_restaurar.add_argument('--destino', required=True)
    subparser_restaurar.add_argument('--clave')
    subparser_restaurar.add_argument('--fragmentado', action='store_true')

    args = parser.parse_args()

    if args.comando == 'respaldar':
        comando_respaldo()
    elif args.comando == 'restaurar':
        comando_restaurar(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
