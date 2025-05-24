import tkinter as tk
from tkinter import filedialog, messagebox
from backup.restore import restaurar_respaldo
from tkinter import ttk
import os
from pathlib import Path 
from gui.cloud_auth_window import CloudAuthWindow
from backup.cloud.google_drive import GoogleDriveProvider
from backup.create import crear_respaldo as crear_respaldo_backend
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import sys
from io import StringIO

class BackupApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Crear Respaldo")
        self.geometry("600x450")  # Aumentado para mejor visualización
        self.transient(parent)
        self.grab_set()

        # Variables de control
        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.clave_var = tk.StringVar()
        self.encriptar_var = tk.BooleanVar(value=True)
        self.fragmentar_var = tk.BooleanVar(value=True)
        self.tamano_fragmento_var = tk.IntVar(value=100)
        self.cloud_upload_var = tk.BooleanVar(value=False)
        self.origenes = []
        # Frame principal para mejor organización
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configuración del grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.columnconfigure(2, weight=1)

        # Origen carpeta
        tk.Label(main_frame, text="Carpeta a respaldar:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.origen_var, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_origen).grid(row=0, column=2, padx=5)

        # Destino carpeta
        tk.Label(main_frame, text="Carpeta destino:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.destino_var, width=50).grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_destino).grid(row=1, column=2, padx=5)

        # Clave (opcional)
        tk.Label(main_frame, text="Archivo de clave:").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.clave_var, width=50).grid(row=2, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_clave).grid(row=2, column=2, padx=5)

        # Opciones de respaldo
        options_frame = tk.LabelFrame(main_frame, text="Opciones de Respaldo")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        
        tk.Checkbutton(options_frame, text="Encriptar respaldo", variable=self.encriptar_var).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Fragmentar archivo", variable=self.fragmentar_var).pack(anchor="w")
        
        tk.Label(options_frame, text="Tamaño fragmentos (MB):").pack(anchor="w")
        tk.Entry(options_frame, textvariable=self.tamano_fragmento_var, width=10).pack(anchor="w")

        # Opciones de nube
        cloud_frame = tk.LabelFrame(main_frame, text="Opciones de Nube")
        cloud_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        
        tk.Button(
            cloud_frame,
            text="Configurar Google Drive",
            command=self.open_cloud_auth,
            bg="#4285F4",
            fg="white"
        ).pack(pady=5, fill=tk.X)
        
        tk.Checkbutton(
            cloud_frame,
            text="Subir a Google Drive después de crear",
            variable=self.cloud_upload_var
        ).pack(anchor="w")

        # Botón principal
        tk.Button(
            main_frame,
            text="Crear Respaldo",
            command=self.crear_respaldo,
            bg="green",
            fg="white",
            height=2
        ).grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

    def elegir_origen(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta a respaldar")
        if carpeta:
            if carpeta not in self.origenes:
                self.origenes.append(carpeta)
                # Mostrar todas las carpetas seleccionadas, separadas por ;
                self.origen_var.set("; ".join(self.origenes))


    def elegir_destino(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if carpeta:
            self.destino_var.set(carpeta)

    def elegir_clave(self):
        clave = filedialog.askopenfilename(
            title="Seleccionar archivo de clave",
            filetypes=[("Key files", "*.key"), ("Todos los archivos", "*.*")]
        )
        if clave:
            self.clave_var.set(clave)

    def open_cloud_auth(self):
        CloudAuthWindow(self)

    def crear_respaldo(self):  # Este es el método de la clase
        origen = self.origen_var.get()
        origenes = self.origenes
        destino = self.destino_var.get()
        clave = self.clave_var.get() or None
        encriptar = self.encriptar_var.get()
        fragmentar = self.fragmentar_var.get()
        tamano = self.tamano_fragmento_var.get()
        subir_a_cloud = self.cloud_upload_var.get()

        if not origenes or not destino:
            messagebox.showerror("Error", "Debes seleccionar carpeta origen y destino.")
            return

        try:
            # Llamamos a la función del backend con el nombre renombrado
            mensajes = []
            for origen in origenes:
                resultado = crear_respaldo_backend(
                    origen,  # Primer parámetro posicional (carpeta_a_resguardar)
                    destino, # Segundo parámetro posicional (carpeta_salida)
                    encriptar=encriptar,
                    fragmentar=fragmentar,
                    tamano_fragmento_mb=tamano,
                    clave_path=clave,
                    upload_to_cloud=False
                )
                mensaje = ""
                if isinstance(resultado, dict):
                    if resultado.get('success', False):
                        #mensaje = f"¡Respaldo creado con éxito!\n\nArchivo principal:\n{resultado.get('archivo_principal', '')}"
                        mensajes.append(f"Respaldo de {origen} creado con éxito:\n{resultado.get('archivo_principal', '')}")
                        # Subida manual a Google Drive
                        if subir_a_cloud and resultado.get('archivo_principal'):
                            try:
                                drive = GoogleDriveProvider()
                                if drive.authenticate():
                                    archivo_path = Path(resultado['archivo_principal'])
                                    
                                    media = MediaFileUpload(
                                        str(archivo_path),
                                        mimetype='application/zip',
                                        resumable=True
                                    )
                                    
                                    file_metadata = {
                                        'name': archivo_path.name,
                                        'mimeType': 'application/zip'
                                    }
                                    drive.service.files().create(
                                        body=file_metadata,
                                        media_body=media,
                                        fields='id'
                                    ).execute()
                                    
                                    mensaje += "\n\nGoogle Drive: Subida exitosa"
                                else:
                                    mensaje += "\n\nGoogle Drive: Error de autenticación"
                            except Exception as e:
                                mensaje += f"\n\nGoogle Drive: Error al subir - {str(e)}"
                        
                       # messagebox.showinfo("Éxito", mensaje)
                    else:
                        #messagebox.showerror("Error", resultado.get('error', 'Error desconocido'))
                        mensajes.append(f"Error al crear respaldo de {origen}:\n{resultado.get('error', 'Error desconocido')}")
                else:
                    messagebox.showinfo("Éxito", f"¡Respaldo creado con éxito en:\n{resultado}")
            
            messagebox.showinfo("Resultado", "\n\n".join(mensajes))
        except Exception as e:
            messagebox.showerror("Error", f"Falló la creación del respaldo:\n{str(e)}")

class RestoreApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Restaurar Respaldo")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        # Variables de control
        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.clave_var = tk.StringVar()
        self.es_fragmentado = tk.BooleanVar()

        # Frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Origen
        tk.Label(main_frame, text="Origen del respaldo:").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.origen_var, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_origen).grid(row=0, column=2, padx=5)

        # Destino
        tk.Label(main_frame, text="Carpeta destino:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.destino_var, width=50).grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_destino).grid(row=1, column=2, padx=5)

        # Clave
        tk.Label(main_frame, text="Archivo de clave:").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(main_frame, textvariable=self.clave_var, width=50).grid(row=2, column=1, sticky="ew", padx=5)
        tk.Button(main_frame, text="Seleccionar...", command=self.elegir_clave).grid(row=2, column=2, padx=5)

        # Opciones
        options_frame = tk.LabelFrame(main_frame, text="Opciones de Restauración")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        
        tk.Checkbutton(
            options_frame, 
            text="Respaldo fragmentado", 
            variable=self.es_fragmentado
        ).pack(anchor="w")

        # Botón principal
        tk.Button(
            main_frame,
            text="Restaurar Respaldo",
            command=self.restaurar,
            bg="blue",
            fg="white",
            height=2
        ).grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

    def elegir_origen(self):
        # Primero intentamos seleccionar un archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de respaldo", 
            filetypes=[("Archivos de respaldo", "*.zip *.zip.enc *.bin"), ("Todos", "*.*")]
        )
        
        # Si no se seleccionó archivo, intentamos seleccionar carpeta
        if not archivo:
            archivo = filedialog.askdirectory(title="Seleccionar carpeta con fragmentos")
        
        if archivo:
            self.origen_var.set(archivo)
            # Auto-detectamos si es fragmentado
            es_fragmentado = False
            if archivo.endswith('.bin'):
                es_fragmentado = True
            elif os.path.isdir(archivo):
                try:
                    for f in os.listdir(archivo):
                        if f.endswith('.bin'):
                            es_fragmentado = True
                            break
                except PermissionError:
                    messagebox.showwarning("Advertencia", "No se pudo leer el contenido del directorio")
            self.es_fragmentado.set(es_fragmentado)

    def elegir_destino(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if carpeta:
            self.destino_var.set(carpeta)

    def elegir_clave(self):
        clave = filedialog.askopenfilename(
            title="Seleccionar archivo de clave",
            filetypes=[("Archivos de clave", "*.key"), ("Todos", "*.*")]
        )
        if clave:
            self.clave_var.set(clave)

    def restaurar(self):
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        clave = self.clave_var.get() or None
        fragmentado = self.es_fragmentado.get()

        if not origen or not destino:
            messagebox.showerror("Error", "Debes seleccionar origen y destino.")
            return

        try:
            # Mostrar ventana de progreso
            progress = tk.Toplevel(self)
            progress.title("Progreso de Restauración")
            progress.geometry("400x200")
            
            tk.Label(progress, text="Restaurando respaldo...", font=('Arial', 12)).pack(pady=10)
            progress_text = tk.Text(progress, height=8, wrap=tk.WORD)
            progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            progress.update()
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            # Ejecutar restauración
            restaurar_respaldo(origen, destino, clave_path=clave, es_fragmentado=fragmentado)
            
            # Obtener output y restaurar stdout
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # Mostrar output en la ventana
            progress_text.insert(tk.END, output)
            progress_text.see(tk.END)
            
            # Botón para cerrar
            tk.Button(progress, text="Cerrar", command=progress.destroy).pack(pady=5)
            
            messagebox.showinfo("Éxito", "¡Restauración completada con éxito!")
            
        except Exception as e:
            # Mostrar error detallado
            error_msg = f"""
            Error durante la restauración:
            
            {str(e)}
            
            Posibles causas:
            - La clave de encriptación no es correcta
            - Los archivos están corruptos
            - No hay permisos suficientes
            - Espacio insuficiente en disco
            """
            messagebox.showerror("Error en Restauración", error_msg)

def ejecutar_gui():
    root = tk.Tk()
    root.title("Sistema de Respaldo")
    root.geometry("300x200")
    root.resizable(False, False)

    # Estilo
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10), padding=10)

    # Frame principal
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Botones principales
    ttk.Button(
        main_frame,
        text="Crear Respaldo",
        command=lambda: BackupApp(root),
        style='TButton'
    ).pack(fill=tk.X, pady=10)

    ttk.Button(
        main_frame,
        text="Restaurar Respaldo",
        command=lambda: RestoreApp(root),
        style='TButton'
    ).pack(fill=tk.X, pady=10)

    root.mainloop()


if __name__ == "__main__":
    ejecutar_gui()