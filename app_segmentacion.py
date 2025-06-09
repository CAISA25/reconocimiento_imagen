import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

import customtkinter as ctk
from customtkinter import CTkScrollableFrame, CTkLabel, CTkFrame

# -------------------------------------------------------------------
# 1) Función de segmentación con mejor precisión
# -------------------------------------------------------------------
def segmentar_colores_preciso(imagen_rgb):
    """
    Segmenta en tres colores (Azul, Verde y Rojo) usando:
      - Desenfoque gaussiano para reducir ruido
      - Conversión a HSV
      - Rangos varios de H para cubrir más matices
      - Operaciones morfológicas (OPEN/CLOSE) para limpiar máscaras
    Retorna:
      - img_segmentada_rgb: numpy array (H x W x 3, uint8) en RGB
      - porcentajes: dict con {"Azul (lago)", "Verde (lentejas)", "Rojo (resto)"}
    """

    # 1) Desenfozar ligeramente para atenuar ruido
    img_blur = cv2.GaussianBlur(imagen_rgb, (5, 5), 0)

    # 2) Convertir a HSV
    img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_RGB2HSV)
    alto, ancho = img_hsv.shape[:2]

    # 3) Máscara para TONOS AZULES (lago)
    #    Definimos DOS rangos de H para cubrir azules oscuros, claros y cianes:
    #    - Rango 1: H ∈ [90, 120]
    #    - Rango 2: H ∈ [120, 140]
    lower_blue1 = np.array([90,  60,  60])
    upper_blue1 = np.array([120, 255, 255])
    mascara_azul1 = cv2.inRange(img_hsv, lower_blue1, upper_blue1)

    lower_blue2 = np.array([120,  40,  40])
    upper_blue2 = np.array([140, 255, 255])
    mascara_azul2 = cv2.inRange(img_hsv, lower_blue2, upper_blue2)

    mascara_azul = cv2.bitwise_or(mascara_azul1, mascara_azul2)

    # 4) Máscara para TONOS VERDES (lentejas)
    #    De igual manera, usamos dos rangos amplios:
    #    - Rango 1: H ∈ [35, 75]
    #    - Rango 2: H ∈ [75, 95] (amarillo-verde muy claro)
    lower_green1 = np.array([35,  60,  60])
    upper_green1 = np.array([75, 255, 255])
    mascara_verde1 = cv2.inRange(img_hsv, lower_green1, upper_green1)

    lower_green2 = np.array([75,  30,  30])
    upper_green2 = np.array([95, 255, 255])
    mascara_verde2 = cv2.inRange(img_hsv, lower_green2, upper_green2)

    mascara_verde = cv2.bitwise_or(mascara_verde1, mascara_verde2)

    # 5) Operaciones morfológicas para LIMPIAR ruido
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    mascara_azul = cv2.morphologyEx(mascara_azul, cv2.MORPH_OPEN, kernel)
    mascara_azul = cv2.morphologyEx(mascara_azul, cv2.MORPH_CLOSE, kernel)

    mascara_verde = cv2.morphologyEx(mascara_verde, cv2.MORPH_OPEN, kernel)
    mascara_verde = cv2.morphologyEx(mascara_verde, cv2.MORPH_CLOSE, kernel)

    # 6) Máscara resto (rojo) = inversión de unión de azul+verde
    union_av = cv2.bitwise_or(mascara_azul, mascara_verde)
    mascara_rojo = cv2.bitwise_not(union_av)

    # 7) Construir imagen segmentada en RGB
    img_segmentada = np.zeros_like(imagen_rgb)

    # - Azul puro en RGB → (0, 0, 255)
    img_segmentada[mascara_azul == 255] = [0, 0, 255]
    # - Verde puro en RGB → (0, 255, 0)
    img_segmentada[mascara_verde == 255] = [0, 255, 0]
    # - Resto → Rojo puro en RGB → (255, 0, 0)
    img_segmentada[mascara_rojo == 255] = [255, 0, 0]

    # 8) Cálculo de porcentajes
    total_px = alto * ancho
    cnt_azul  = int(cv2.countNonZero(mascara_azul))
    cnt_verde = int(cv2.countNonZero(mascara_verde))
    cnt_rojo  = total_px - cnt_azul - cnt_verde

    pct_azul  = round((cnt_azul  / total_px) * 100, 2)
    pct_verde = round((cnt_verde / total_px) * 100, 2)
    pct_rojo  = round((cnt_rojo  / total_px) * 100, 2)

    porcentajes = {
        "Azul (lago)": pct_azul,
        "Verde (lentejas)": pct_verde,
        "Rojo (resto)": pct_rojo
    }

    return img_segmentada, porcentajes


# -------------------------------------------------------------------
# 2) Función para procesar lote en carpeta
# -------------------------------------------------------------------
def procesar_lote(carpeta_in, carpeta_out):
    """
    Recorre 'carpeta_in' buscando .jpg/.jpeg/.png, los segmenta con segmentar_colores_preciso,
    guarda cada salida en 'carpeta_out' y retorna lista de diccionarios para el CSV.
    """
    os.makedirs(carpeta_out, exist_ok=True)
    resultados = []

    for nombre in sorted(os.listdir(carpeta_in)):
        if not nombre.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        ruta_in = os.path.join(carpeta_in, nombre)
        img_bgr = cv2.imread(ruta_in)
        if img_bgr is None:
            print(f"⚠️ No se pudo leer '{nombre}'. Se omite.")
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        seg_rgb, porcentajes = segmentar_colores_preciso(img_rgb)

        # Guardar segmentada ← convertimos RGB → BGR para imwrite
        seg_bgr = cv2.cvtColor(seg_rgb, cv2.COLOR_RGB2BGR)
        nombre_salida = f"procesada_{nombre}"
        ruta_out = os.path.join(carpeta_out, nombre_salida)
        cv2.imwrite(ruta_out, seg_bgr)

        resultados.append({
            "Imagen": nombre,
            "Porcentaje_Azul_lago": porcentajes["Azul (lago)"],
            "Porcentaje_Verde_lentejas": porcentajes["Verde (lentejas)"],
            "Porcentaje_Rojo_resto": porcentajes["Rojo (resto)"]
        })

        print(f"✅ Procesada '{nombre}' → '{nombre_salida}'")

    return resultados


# -------------------------------------------------------------------
# 3) Conversión NumPy → PhotoImage para Tkinter
# -------------------------------------------------------------------
def numpy_a_photoimage(img_rgb):
    """
    Convierte un array numpy (H x W x 3) en RGB a un PhotoImage de PIL (compatible con Tkinter).
    """
    img_pil = Image.fromarray(img_rgb)
    return ImageTk.PhotoImage(img_pil)


# -------------------------------------------------------------------
# 4) Interfaz con CustomTkinter
# -------------------------------------------------------------------
class AppVisor(ctk.CTk):
    def __init__(self, carpeta_orig, carpeta_proc, resultados):
        super().__init__()
        self.title("Visor de Imágenes: Original vs Segmentada")
        self.geometry("1024x768")
        self.minsize(800, 600)

        # Estilo de tema
        ctk.set_appearance_mode("System")   # "Dark" o "Light" o "System"
        ctk.set_default_color_theme("blue")  # tema de acentos

        # Contenedor principal con scroll
        self.scroll_frame = CTkScrollableFrame(self, width=900, height=700)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Por cada resultado, agregamos un bloque con info + dos imágenes
        for idx, fila in enumerate(resultados):
            nombre = fila["Imagen"]
            ruta_orig = os.path.join(carpeta_orig, nombre)
            ruta_seg  = os.path.join(carpeta_proc,  f"procesada_{nombre}")

            # Cargar y convertir a PhotoImage
            img_orig_bgr = cv2.imread(ruta_orig)
            img_seg_bgr  = cv2.imread(ruta_seg)
            if img_orig_bgr is None or img_seg_bgr is None:
                continue

            img_orig_rgb = cv2.cvtColor(img_orig_bgr, cv2.COLOR_BGR2RGB)
            img_seg_rgb  = cv2.cvtColor(img_seg_bgr,  cv2.COLOR_BGR2RGB)

            photo_orig = numpy_a_photoimage(img_orig_rgb)
            photo_seg  = numpy_a_photoimage(img_seg_rgb)

            # Etiqueta con info (nombre + porcentajes)
            texto = (
                f"{nombre}   |   "
                f"Azul: {fila['Porcentaje_Azul_lago']}%   –   "
                f"Verde: {fila['Porcentaje_Verde_lentejas']}%   –   "
                f"Rojo: {fila['Porcentaje_Rojo_resto']}%"
            )
            label_info = CTkLabel(self.scroll_frame, text=texto, font=("Arial", 14, "bold"))
            label_info.grid(row=3*idx, column=0, columnspan=2, pady=(10, 5), sticky="w")

            # Labels para mostrar las imágenes (original y segmentada)
            label_o = CTkLabel(self.scroll_frame, image=photo_orig, text="")
            label_o.image = photo_orig  # evitar garbage collection
            label_s = CTkLabel(self.scroll_frame, image=photo_seg, text="")
            label_s.image = photo_seg

            # Ubicamos lado a lado: columna 0 → original; columna 1 → segmentada
            label_o.grid(row=3*idx + 1, column=0, padx=5, pady=5)
            label_s.grid(row=3*idx + 1, column=1, padx=5, pady=5)

            # Línea divisoria (un espacio en blanco) antes del siguiente bloque
            divider = CTkFrame(self.scroll_frame, height=1, fg_color=("gray75", "gray25"))
            divider.grid(row=3*idx + 2, column=0, columnspan=2, sticky="we", padx=5, pady=(5, 0))

        # Ajustes de columnas para que no se achiquen las imágenes
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)


# -------------------------------------------------------------------
# 5) Función main
# -------------------------------------------------------------------
if __name__ == "__main__":
    carpeta_imagenes = "imagenes"
    carpeta_segmentadas = "imagenes_procesadas"

    if not os.path.isdir(carpeta_imagenes):
        print(f"❌ La carpeta '{carpeta_imagenes}' no existe. Crea 'imagenes/' con tus fotos.")
        exit(1)

    # Procesar lote y generar CSV
    print("🔄 Procesando imágenes con segmentación precisa...")
    resultados = procesar_lote(carpeta_imagenes, carpeta_segmentadas)

    if not resultados:
        print("⚠️ No se procesó ninguna imagen. Verifica la carpeta.")
        exit(0)

    # Guardar CSV
    df = pd.DataFrame(resultados)
    df.to_csv("resultados_colores.csv", index=False, encoding="utf-8-sig")
    print("📄 Guardado 'resultados_colores.csv' con porcentajes.")

    # Iniciar interfaz gráfica
    app = AppVisor(carpeta_imagenes, carpeta_segmentadas, resultados)
    app.mainloop()
