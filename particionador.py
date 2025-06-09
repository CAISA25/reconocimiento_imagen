import os
from PIL import Image

def fraccionar_imagen(ruta_imagen, filas, columnas, carpeta_salida):
    # Crear carpeta de salida si no existe
    os.makedirs(carpeta_salida, exist_ok=True)

    # Abrir la imagen
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size

    # Tamaño de cada fragmento
    ancho_corte = ancho // columnas
    alto_corte = alto // filas

    contador = 0
    for fila in range(filas):
        for col in range(columnas):
            # Coordenadas de la región a recortar
            izquierda = col * ancho_corte
            superior = fila * alto_corte
            derecha = izquierda + ancho_corte
            inferior = superior + alto_corte

            # Recortar y guardar la imagen
            fragmento = imagen.crop((izquierda, superior, derecha, inferior))
            nombre_fragmento = f"fragmento_{fila}_{col}.png"
            ruta_fragmento = os.path.join(carpeta_salida, nombre_fragmento)
            fragmento.save(ruta_fragmento)
            contador += 1

    print(f"{contador} fragmentos guardados en '{carpeta_salida}'")

# Parámetros de ejemplo
ruta_imagen = "imgs2.png"              # Cambia esto por la ruta de tu imagen
filas = 5                               # Número de divisiones verticales
columnas = 5                           # Número de divisiones horizontales
carpeta_salida = "fragmentos_imagen"    # Carpeta donde se guardarán

# Ejecutar
fraccionar_imagen(ruta_imagen, filas, columnas, carpeta_salida)
