import tkinter as tk
from tkinter import filedialog, messagebox
from backup.restore import restaurar_respaldo
import os
from backup.create import crear_respaldo

class BackupApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Crear Respaldo")
        self.geometry("600x400")
        self.transient(parent)  # Establece relación con la ventana principal
        self.grab_set()  # Hace que la ventana sea modal

        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.clave_var = tk.StringVar()
        self.encriptar_var = tk.BooleanVar(value=True)
        self.fragmentar_var = tk.BooleanVar(value=True)
        self.tamano_fragmento_var = tk.IntVar(value=100)

        # Origen carpeta
        tk.Label(self, text="📂 Carpeta a respaldar").pack(pady=5)
        tk.Entry(self, textvariable=self.origen_var, width=60).pack()
        tk.Button(self, text="Seleccionar carpeta...", command=self.elegir_origen).pack()

        # Destino carpeta
        tk.Label(self, text="📁 Carpeta destino para guardar respaldo").pack(pady=5)
        tk.Entry(self, textvariable=self.destino_var, width=60).pack()
        tk.Button(self, text="Seleccionar carpeta destino...", command=self.elegir_destino).pack()

        # Clave (opcional)
        tk.Label(self, text="🔐 Archivo de clave (opcional)").pack(pady=5)
        tk.Entry(self, textvariable=self.clave_var, width=60).pack()
        tk.Button(self, text="Seleccionar clave...", command=self.elegir_clave).pack()

        # Encriptar checkbox
        tk.Checkbutton(self, text="Encriptar respaldo", variable=self.encriptar_var).pack(pady=5)

        # Fragmentar checkbox y tamaño
        tk.Checkbutton(self, text="Fragmentar archivo", variable=self.fragmentar_var).pack()
        tk.Label(self, text="Tamaño fragmentos (MB):").pack()
        tk.Entry(self, textvariable=self.tamano_fragmento_var, width=10).pack()

        # Botón principal
        tk.Button(self, text="💾 Crear respaldo", command=self.crear_respaldo, bg="green", fg="white").pack(pady=20)

    def elegir_origen(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta a respaldar")
        if carpeta:
            self.origen_var.set(carpeta)

    def elegir_destino(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if carpeta:
            self.destino_var.set(carpeta)

    def elegir_clave(self):
        clave = filedialog.askopenfilename(filetypes=[("Key files", "*.key"), ("Todos", "*.*")])
        if clave:
            self.clave_var.set(clave)

    def crear_respaldo(self):
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        clave = self.clave_var.get() or None
        encriptar = self.encriptar_var.get()
        fragmentar = self.fragmentar_var.get()
        tamano = self.tamano_fragmento_var.get()

        if not origen or not destino:
            messagebox.showerror("Error", "Debes seleccionar carpeta origen y destino.")
            return

        try:
            ruta_final = crear_respaldo(
                carpeta_a_resguardar=origen,
                carpeta_salida=destino,
                encriptar=encriptar,
                fragmentar=fragmentar,
                tamano_fragmento_mb=tamano,
                clave_path=clave
            )
            messagebox.showinfo("Éxito", f"¡Respaldo creado con éxito en:\n{ruta_final}")
        except Exception as e:
            messagebox.showerror("Error", f"Falló la creación del respaldo:\n{str(e)}")


class RestoreApp(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Restaurar Respaldo")
        self.geometry("600x350")
        self.transient(parent)  # Establece relación con la ventana principal
        self.grab_set()  # Hace que la ventana sea modal

        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.clave_var = tk.StringVar()
        self.es_fragmentado = tk.BooleanVar()

        # Origen
        tk.Label(self, text="📂 Carpeta de fragmentos o archivo .zip/.zip.enc").pack(pady=5)
        tk.Entry(self, textvariable=self.origen_var, width=60).pack()
        
        # Usar solo un botón para seleccionar tanto archivo como carpeta
        tk.Button(self, text="Seleccionar origen...", command=self.elegir_origen).pack(pady=5)

        # Destino
        tk.Label(self, text="📁 Carpeta de destino para restauración").pack(pady=5)
        tk.Entry(self, textvariable=self.destino_var, width=60).pack()
        tk.Button(self, text="Seleccionar...", command=self.elegir_destino).pack()

        # Clave (opcional)
        tk.Label(self, text="🔐 Archivo de clave (opcional)").pack(pady=5)
        tk.Entry(self, textvariable=self.clave_var, width=60).pack()
        tk.Button(self, text="Seleccionar clave...", command=self.elegir_clave).pack()

        # Fragmentado
        tk.Checkbutton(self, text="¿Respaldo fragmentado (.bin)?", variable=self.es_fragmentado).pack(pady=10)

        # Botón principal
        tk.Button(self, text="🛠 Restaurar Respaldo", command=self.restaurar, bg="blue", fg="white").pack(pady=20)

    def elegir_origen(self):
        # Primero intentamos seleccionar un archivo
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de respaldo", 
            filetypes=[("ZIP files", "*.zip *.zip.enc"), ("Todos", "*.*")]
        )
        
        # Si no se seleccionó archivo, intentamos seleccionar carpeta
        if not archivo:
            archivo = filedialog.askdirectory(
                title="Seleccionar carpeta con fragmentos"
            )
        
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
            filetypes=[("Key files", "*.key"), ("Todos", "*.*")]
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
            restaurar_respaldo(origen, destino, clave_path=clave, es_fragmentado=fragmentado)
            messagebox.showinfo("Éxito", "¡Restauración completada con éxito!")
        except Exception as e:
            messagebox.showerror("Error", f"Falló la restauración:\n{str(e)}")


def ejecutar_gui():
    root = tk.Tk()
    root.title("Sistema de respaldo y restauración")
    root.geometry("300x150")

    def abrir_backup():
        backup_window = BackupApp(root)
        backup_window.wait_window()  # Espera hasta que se cierre la ventana

    def abrir_restore():
        restore_window = RestoreApp(root)
        restore_window.wait_window()  # Espera hasta que se cierre la ventana

    tk.Button(root, text="Crear Respaldo", command=abrir_backup, bg="green", fg="white", width=20).pack(pady=10)
    tk.Button(root, text="Restaurar Respaldo", command=abrir_restore, bg="blue", fg="white", width=20).pack(pady=10)

    root.mainloop()