import customtkinter as ctk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from typing import Optional, Tuple, List


class ColorReplacerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Editor de colores RGB con cuentagotas (5 colores)")
        self.geometry("1000x850")
        self.minsize(900, 800)
        
        # Variables de estado
        self.img_original: Optional[Image.Image] = None
        self.img_procesada: Optional[Image.Image] = None
        self.tk_img: Optional[ImageTk.PhotoImage] = None
        self.tk_img_original: Optional[ImageTk.PhotoImage] = None
        self.current_color_index: Optional[int] = None
        self.mostrar_original = False
        self.num_colores = 5  # Aumentamos a 5 colores
        
        # Listas para colores
        self.colores_originales: List[Optional[Tuple[int, int, int]]] = [None] * self.num_colores
        self.colores_nuevos: List[Optional[Tuple[int, int, int]]] = [None] * self.num_colores
        
        # Configuración de UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura todos los elementos de la interfaz de usuario."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Panel de controles superiores
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.btn_cargar = ctk.CTkButton(
            control_frame, 
            text="Cargar Imagen", 
            command=self.cargar_imagen
        )
        self.btn_cargar.pack(side="left", padx=5)
        
        self.btn_procesar = ctk.CTkButton(
            control_frame, 
            text="Procesar Imagen", 
            command=self.procesar_imagen,
            state="disabled"
        )
        self.btn_procesar.pack(side="left", padx=5)
        
        self.btn_guardar = ctk.CTkButton(
            control_frame, 
            text="Guardar Imagen", 
            command=self.guardar_imagen,
            state="disabled"
        )
        self.btn_guardar.pack(side="left", padx=5)
        
        self.btn_toggle = ctk.CTkButton(
            control_frame,
            text="Mostrar Original",
            command=self.toggle_imagen,
            state="disabled"
        )
        self.btn_toggle.pack(side="right", padx=5)
        
        # Área de visualización de imagen
        self.img_frame = ctk.CTkFrame(main_frame)
        self.img_frame.grid(row=1, column=0, sticky="nsew")
        
        self.canvas = ctk.CTkCanvas(self.img_frame, bg="#2b2b2b", bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        
        # Panel de información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.lbl_info = ctk.CTkLabel(
            info_frame, 
            text="Haz clic en la imagen para seleccionar colores originales (cuentagotas)"
        )
        self.lbl_info.pack(pady=5)
        
        self.lbl_pixel_info = ctk.CTkLabel(
            info_frame,
            text="Posición: (0, 0) | Color: #FFFFFF",
            text_color="cyan"
        )
        self.lbl_pixel_info.pack(pady=5)
        
        # Frame para los selectores de color
        self.frame_colores = ctk.CTkScrollableFrame(main_frame, height=200)
        self.frame_colores.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        
        # Crear selectores de color (5 pares)
        self._crear_selectores_color()
    
    def _crear_selectores_color(self):
        """Crea los elementos de la interfaz para seleccionar colores."""
        self.color_original_btns = []
        self.color_nuevo_btns = []
        self.color_original_labels = []
        self.color_nuevo_labels = []
        
        for i in range(self.num_colores):
            frame = ctk.CTkFrame(self.frame_colores)
            frame.pack(fill="x", padx=5, pady=5)
            
            # Selector color original
            lbl_orig = ctk.CTkLabel(frame, text=f"Original #{i+1}:", width=100)
            lbl_orig.pack(side="left", padx=(5, 0))
            
            self.color_original_labels.append(ctk.CTkLabel(
                frame, 
                text="No seleccionado", 
                width=150,
                corner_radius=5
            ))
            self.color_original_labels[i].pack(side="left", padx=5)
            
            btn_orig = ctk.CTkButton(
                frame, 
                text="Seleccionar de imagen", 
                width=150,
                command=lambda idx=i: self.preparar_cuenta_gotas(idx)
            )
            btn_orig.pack(side="left", padx=5)
            self.color_original_btns.append(btn_orig)
            
            # Selector color nuevo
            lbl_new = ctk.CTkLabel(frame, text=f"Nuevo #{i+1}:", width=100)
            lbl_new.pack(side="left", padx=(10, 0))
            
            self.color_nuevo_labels.append(ctk.CTkLabel(
                frame, 
                text="No seleccionado", 
                width=150,
                corner_radius=5
            ))
            self.color_nuevo_labels[i].pack(side="left", padx=5)
            
            btn_new = ctk.CTkButton(
                frame, 
                text="Elegir Color", 
                width=100,
                command=lambda idx=i: self.seleccionar_color_nuevo(idx)
            )
            btn_new.pack(side="left", padx=5)
            self.color_nuevo_btns.append(btn_new)
    
    def cargar_imagen(self):
        """Carga una imagen desde el sistema de archivos."""
        filetypes = [
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp"),
            ("Todos los archivos", "*.*")
        ]
        
        ruta = filedialog.askopenfilename(filetypes=filetypes)
        if not ruta:
            return
            
        try:
            self.img_original = Image.open(ruta).convert("RGB")
            self.img_procesada = None
            self.mostrar_imagen(self.img_original)
            self.btn_procesar.configure(state="normal")
            self.btn_toggle.configure(state="normal")
            self._actualizar_estado_botones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
    
    def mostrar_imagen(self, pil_img: Image.Image):
        """Muestra la imagen en el canvas, redimensionándola si es necesario."""
        canvas_width = self.canvas.winfo_width() - 20
        canvas_height = self.canvas.winfo_height() - 20
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 500
        
        # Calcular relación de aspecto
        original_width, original_height = pil_img.size
        ratio = min(canvas_width/original_width, canvas_height/original_height)
        new_size = (int(original_width * ratio), int(original_height * ratio))
        
        img_copy = pil_img.resize(new_size, Image.Resampling.LANCZOS)
        
        if pil_img == self.img_original:
            self.tk_img_original = ImageTk.PhotoImage(img_copy)
            self.current_display_img = self.tk_img_original
        else:
            self.tk_img = ImageTk.PhotoImage(img_copy)
            self.current_display_img = self.tk_img
        
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2, 
            canvas_height//2, 
            anchor="center", 
            image=self.current_display_img
        )
        
        # Guardar referencia de la imagen mostrada para el cuentagotas
        self.displayed_img_size = new_size
        self.displayed_img = img_copy
        self.original_img_size = (original_width, original_height)
    
    def preparar_cuenta_gotas(self, idx: int):
        """Prepara la interfaz para seleccionar un color de la imagen."""
        if self.img_original is None:
            messagebox.showwarning("Atención", "Primero carga una imagen.")
            return
        
        self.current_color_index = idx
        self.lbl_info.configure(
            text=f"Click en la imagen para seleccionar el color original #{idx+1}",
            text_color="yellow"
        )
    
    def on_canvas_hover(self, event):
        """Muestra información del pixel bajo el cursor."""
        if not hasattr(self, 'displayed_img'):
            return
            
        # Obtener coordenadas relativas a la imagen mostrada
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_x = event.x - (canvas_width - self.displayed_img_size[0]) // 2
        img_y = event.y - (canvas_height - self.displayed_img_size[1]) // 2
        
        # Verificar que el cursor está dentro de la imagen
        if 0 <= img_x < self.displayed_img_size[0] and 0 <= img_y < self.displayed_img_size[1]:
            # Obtener color del pixel en la imagen mostrada
            pixel = self.displayed_img.getpixel((int(img_x), int(img_y)))
            self.lbl_pixel_info.configure(
                text=f"Posición: ({img_x:.0f}, {img_y:.0f}) | Color: RGB{pixel}",
                fg_color=self._rgb_to_hex(pixel),
                text_color="black" if sum(pixel) > 384 else "white"
            )
    
    def on_canvas_click(self, event):
        """Maneja el evento de clic en el canvas para el cuentagotas."""
        if self.current_color_index is None or self.img_original is None:
            return
        
        # Obtener coordenadas relativas a la imagen mostrada
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        img_x = event.x - (canvas_width - self.displayed_img_size[0]) // 2
        img_y = event.y - (canvas_height - self.displayed_img_size[1]) // 2
        
        # Verificar que el clic fue dentro de la imagen
        if 0 <= img_x < self.displayed_img_size[0] and 0 <= img_y < self.displayed_img_size[1]:
            # Obtener color del pixel en la imagen original (no en la mostrada)
            x_orig = int(img_x * self.original_img_size[0] / self.displayed_img_size[0])
            y_orig = int(img_y * self.original_img_size[1] / self.displayed_img_size[1])
            
            pixel = self.img_original.getpixel((x_orig, y_orig))
            self.colores_originales[self.current_color_index] = pixel
            
            # Actualizar UI
            self.color_original_labels[self.current_color_index].configure(
                text=f"RGB{pixel}",
                fg_color=self._rgb_to_hex(pixel),
                text_color="black" if sum(pixel) > 384 else "white"
            )
            
            # Dibujar marcador en la imagen
            self.dibujar_marcador(img_x, img_y, pixel)
            
            self._actualizar_estado_botones()
        
        self.current_color_index = None
        self.lbl_info.configure(
            text="Haz clic en la imagen para seleccionar colores originales (cuentagotas)",
            text_color="white"
        )
    
    def dibujar_marcador(self, x: int, y: int, color: Tuple[int, int, int]):
        """Dibuja un marcador en la posición seleccionada."""
        if not hasattr(self, 'displayed_img'):
            return
            
        img_with_marker = self.displayed_img.copy()
        draw = ImageDraw.Draw(img_with_marker)
        
        # Dibujar un círculo alrededor del punto seleccionado
        r = 10
        draw.ellipse([(x-r, y-r), (x+r, y+r)], outline="red", width=2)
        
        # Dibujar cruz para mayor precisión
        draw.line([(x-15, y), (x+15, y)], fill="red", width=2)
        draw.line([(x, y-15), (x, y+15)], fill="red", width=2)
        
        # Mostrar la imagen con el marcador
        self.tk_img_marked = ImageTk.PhotoImage(img_with_marker)
        self.canvas.create_image(
            self.canvas.winfo_width()//2, 
            self.canvas.winfo_height()//2, 
            anchor="center", 
            image=self.tk_img_marked
        )
        self.after(1000, self.remover_marcador)
    
    def remover_marcador(self):
        """Remueve el marcador del cuentagotas."""
        if self.mostrar_original:
            self.mostrar_imagen(self.img_original)
        else:
            if self.img_procesada:
                self.mostrar_imagen(self.img_procesada)
            else:
                self.mostrar_imagen(self.img_original)
    
    def seleccionar_color_nuevo(self, idx: int):
        """Permite al usuario seleccionar un nuevo color de reemplazo."""
        color = colorchooser.askcolor(title=f"Seleccionar Color Nuevo #{idx+1}")
        if color[0]:
            rgb = tuple(int(c) for c in color[0])
            self.colores_nuevos[idx] = rgb
            self.color_nuevo_labels[idx].configure(
                text=f"RGB{rgb}",
                fg_color=self._rgb_to_hex(rgb),
                text_color="black" if sum(rgb) > 384 else "white"
            )
            self._actualizar_estado_botones()
    
    def toggle_imagen(self):
        """Alterna entre mostrar la imagen original y la procesada."""
        if self.img_original is None:
            return
            
        self.mostrar_original = not self.mostrar_original
        self.btn_toggle.configure(
            text="Mostrar Original" if not self.mostrar_original else "Mostrar Procesada"
        )
        
        if self.mostrar_original:
            self.mostrar_imagen(self.img_original)
        else:
            if self.img_procesada:
                self.mostrar_imagen(self.img_procesada)
            else:
                self.mostrar_imagen(self.img_original)
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convierte un color RGB a formato hexadecimal."""
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    
    def _actualizar_estado_botones(self):
        """Actualiza el estado de los botones según las condiciones necesarias."""
        # Verificar si hay al menos un par de colores completo
        pares_completos = any(
            orig is not None and nuevo is not None
            for orig, nuevo in zip(self.colores_originales, self.colores_nuevos)
        )
        
        self.btn_procesar.configure(state="normal" if pares_completos and self.img_original else "disabled")
        self.btn_guardar.configure(state="normal" if self.img_procesada else "disabled")
    
    def procesar_imagen(self):
        """Procesa la imagen reemplazando los colores seleccionados."""
        if self.img_original is None:
            messagebox.showwarning("Atención", "Debes cargar primero una imagen.")
            return
        
        # Validar que al menos un par de colores esté completo
        pares_validos = [
            (orig, nuevo) 
            for orig, nuevo in zip(self.colores_originales, self.colores_nuevos)
            if orig is not None and nuevo is not None
        ]
        
        if not pares_validos:
            messagebox.showwarning("Atención", "Debes seleccionar al menos un par de colores (original y nuevo).")
            return
        
        try:
            # Crear copia para procesar
            img_proc = self.img_original.copy()
            
            # Convertir a array para procesamiento más rápido
            img_array = img_proc.load()
            ancho, alto = img_proc.size
            
            # Preprocesar los colores y tolerancias
            colores_procesar = []
            for orig, nuevo in pares_validos:
                # Crear rangos de tolerancia para cada canal
                rango_r = range(max(0, orig[0]-30), min(255, orig[0]+30)+1)
                rango_g = range(max(0, orig[1]-30), min(255, orig[1]+30)+1)
                rango_b = range(max(0, orig[2]-30), min(255, orig[2]+30)+1)
                colores_procesar.append((rango_r, rango_g, rango_b, nuevo))
            
            # Procesar la imagen
            for x in range(ancho):
                for y in range(alto):
                    pixel = img_array[x, y]
                    for rango_r, rango_g, rango_b, nuevo in colores_procesar:
                        if pixel[0] in rango_r and pixel[1] in rango_g and pixel[2] in rango_b:
                            img_array[x, y] = nuevo
                            break
            
            self.img_procesada = img_proc
            self.mostrar_imagen(self.img_procesada)
            self.btn_guardar.configure(state="normal")
            self.btn_toggle.configure(state="normal")
            messagebox.showinfo("Listo", "La imagen ha sido procesada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar la imagen:\n{str(e)}")
    
    def guardar_imagen(self):
        """Guarda la imagen procesada en el sistema de archivos."""
        if self.img_procesada is None:
            messagebox.showwarning("Atención", "No hay imagen procesada para guardar.")
            return
        
        filetypes = [
            ("PNG", "*.png"),
            ("JPEG", "*.jpg;*.jpeg"),
            ("BMP", "*.bmp"),
            ("WEBP", "*.webp"),
            ("Todos los archivos", "*.*")
        ]
        
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            title="Guardar imagen procesada"
        )
        
        if not ruta:
            return
            
        try:
            format_map = {
                ".png": "PNG",
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".bmp": "BMP",
                ".webp": "WEBP"
            }
            ext = ruta[ruta.rfind("."):].lower()
            formato = format_map.get(ext, "PNG")
            
            self.img_procesada.save(ruta, format=formato)
            messagebox.showinfo("Éxito", f"Imagen guardada correctamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la imagen:\n{str(e)}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ColorReplacerApp()
    app.mainloop()