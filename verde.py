import cv2
import numpy as np
import matplotlib.pyplot as plt

def calibrar_verde(imagen_path):
    imagen_bgr = cv2.imread(imagen_path)
    if imagen_bgr is None:
        print(f"❌ No se pudo cargar la imagen: {imagen_path}")
        return

    imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
    imagen_hsv = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2HSV)

    print("👆 Haz clic sobre los verdes que quieras capturar (cierra la ventana para terminar).")

    coords = []

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            hsv_valor = imagen_hsv[y, x]
            print(f"🟢 HSV en ({x}, {y}): H={hsv_valor[0]}, S={hsv_valor[1]}, V={hsv_valor[2]}")
            coords.append((x, y, hsv_valor))

    fig, ax = plt.subplots()
    ax.imshow(imagen_rgb)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.title("Haz clic sobre zonas verdes. Cierra la ventana para salir.")
    plt.axis('off')
    plt.show()

# Cambia por tu imagen real
calibrar_verde("imagenes/fragmento_4_4.png")
