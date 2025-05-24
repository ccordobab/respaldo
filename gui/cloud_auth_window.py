import tkinter as tk
from tkinter import ttk, messagebox
from backup.cloud.google_drive import GoogleDriveProvider


class CloudAuthWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Autenticación en Google Drive")
        self.geometry("450x250")
        self.cloud_provider = GoogleDriveProvider()
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        ttk.Label(main_frame, 
                text="Configuración de Google Drive",
                font=('Helvetica', 12, 'bold')).pack(pady=10)
        
        ttk.Label(main_frame, 
                text="Debes autenticarte para subir respaldos a la nube",
                wraplength=400).pack()
        
        self.auth_button = ttk.Button(
            main_frame,
            text="🔓 Autenticar con Google",
            command=self.authenticate,
            style='Accent.TButton'
        )
        self.auth_button.pack(pady=20)
        
        self.status_label = ttk.Label(main_frame, text="Estado: No autenticado", foreground='red')
        self.status_label.pack()
    
    def authenticate(self):
        try:
            if self.cloud_provider.authenticate():
                self.status_label.config(text="Autenticación exitosa!", foreground="green")
                self.auth_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Falló la autenticación: {str(e)}")