import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def segmentar_colores(imagen_rgb):
    # Convertimos la imagen a HSV y Lab
    imagen_hsv = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2HSV)
    imagen_lab = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2Lab)

    # ----------------- Segmentación Azul (lago) -------------------
    imagen_gray = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2GRAY)
    _, mascara_azul = cv2.threshold(imagen_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # ----------------- Segmentación Verde (lentejas) extendido ----
    # Rango extendido de verde para incluir tonos apagados
    rango_bajo_verde = np.array([40, 40, 40])    # más tolerante
    rango_alto_verde = np.array([70, 255, 255])
    mascara_verde = cv2.inRange(imagen_hsv, rango_bajo_verde, rango_alto_verde)

    # ----------------- Resto (no azul, no verde) ------------------
    solo_azul_o_verde = cv2.bitwise_or(mascara_azul, mascara_verde)
    mascara_resto = cv2.bitwise_not(solo_azul_o_verde)

    # ----------------- Crear Imagen Segmentada --------------------
    imagen_segmentada = np.zeros_like(imagen_rgb)
    imagen_segmentada[mascara_azul == 255] = [0, 0, 255]     # Azul → rojo visualizado
    imagen_segmentada[mascara_verde == 255] = [0, 255, 0]    # Verde
    imagen_segmentada[mascara_resto == 255] = [255, 0, 0]    # Rojo

    # ----------------- Calcular Porcentajes -----------------------
    total_pixeles = imagen_rgb.shape[0] * imagen_rgb.shape[1]
    porcentaje_azul = np.sum(mascara_azul == 255) / total_pixeles * 100
    porcentaje_verde = np.sum(mascara_verde == 255) / total_pixeles * 100
    porcentaje_rojo = np.sum(mascara_resto == 255) / total_pixeles * 100

    return imagen_segmentada, porcentaje_azul, porcentaje_verde, porcentaje_rojo

def mostrar_vista_previa(imagen_original, imagen_segmentada, titulo="Vista previa"):
    concatenada = np.hstack((imagen_original, imagen_segmentada))
    plt.figure(figsize=(10, 5))
    plt.imshow(concatenada)
    plt.title(titulo)
    plt.axis('off')
    plt.show()

def procesar_imagenes_en_carpeta(carpeta):
    resultados = []

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
            ruta = os.path.join(carpeta, archivo)
            imagen_bgr = cv2.imread(ruta)
            if imagen_bgr is None:
                print(f"❌ No se pudo leer la imagen {archivo}")
                continue

            imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
            imagen_segmentada, p_azul, p_verde, p_rojo = segmentar_colores(imagen_rgb)

            resultados.append({
                "Imagen": archivo,
                "Porcentaje_Azul_lago": round(p_azul, 2),
                "Porcentaje_Verde_lentejas": round(p_verde, 2),
                "Porcentaje_Rojo_resto": round(p_rojo, 2)
            })

            mostrar_vista_previa(imagen_rgb, imagen_segmentada, titulo=f"{archivo}")

            os.makedirs("imagenes_procesadas2", exist_ok=True)
            salida = os.path.join("imagenes_procesadas2", f"procesada_{archivo}")
            cv2.imwrite(salida, cv2.cvtColor(imagen_segmentada, cv2.COLOR_RGB2BGR))
            print(f"✅ Imagen procesada guardada como {salida}\n")

    return resultados

# Ejecutar
carpeta_imagenes = "imagenes2"
resultados = procesar_imagenes_en_carpeta(carpeta_imagenes)

# Guardar CSV
df = pd.DataFrame(resultados)
df.to_csv("resultados_colores2.csv", index=False)
print("📄 Análisis completado. Resultados guardados en 'resultados_colores2.csv'")
