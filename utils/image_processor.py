"""
Módulo para procesar imágenes y extraer datos matemáticos
"""
import cv2
import numpy as np
from PIL import Image
import re
import streamlit as st

def procesar_imagen(imagen):
    """
    Procesa una imagen y extrae texto matemático con múltiples técnicas
    
    Args:
        imagen: PIL Image o numpy array
        
    Returns:
        dict con datos extraídos
    """
    try:
        # Convertir PIL a numpy si es necesario
        if isinstance(imagen, Image.Image):
            img_array = np.array(imagen)
        else:
            img_array = imagen
        
        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Aplicar múltiples técnicas de preprocesamiento
        procesadas = []
        textos = []
        
        # Técnica 1: Threshold adaptativo
        thresh1 = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        procesadas.append(thresh1)
        
        # Técnica 2: Threshold de Otsu
        _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        procesadas.append(thresh2)
        
        # Técnica 3: Mejorar contraste con CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        _, thresh3 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        procesadas.append(thresh3)
        
        # Técnica 4: Invertir colores (útil para texto claro en fondo oscuro)
        inverted = cv2.bitwise_not(gray)
        _, thresh4 = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        procesadas.append(thresh4)
        
        # Técnica 5: Denoise + threshold
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        _, thresh5 = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        procesadas.append(thresh5)
        
        # Intentar OCR con pytesseract en cada versión procesada
        mejor_texto = ""
        mejor_imagen = thresh1
        max_numeros = 0
        
        try:
            import pytesseract
            
            # Configuraciones de OCR para probar
            configs = [
                '--psm 6',  # Asume un bloque uniforme de texto
                '--psm 4',  # Asume una sola columna de texto
                '--psm 11', # Texto disperso
                '--psm 12', # Texto disperso con OSD
            ]
            
            for img_proc in procesadas:
                for config in configs:
                    try:
                        texto = pytesseract.image_to_string(img_proc, config=config)
                        textos.append(texto)
                        
                        # Contar cuántos números detectó
                        numeros = re.findall(r'-?\d+\.?\d*', texto)
                        if len(numeros) > max_numeros:
                            max_numeros = len(numeros)
                            mejor_texto = texto
                            mejor_imagen = img_proc
                    except:
                        continue
            
            # Si no se detectó nada, intentar con EasyOCR como fallback
            if max_numeros < 4:
                try:
                    import easyocr
                    reader = easyocr.Reader(['es', 'en'])
                    for img_proc in procesadas[:3]:  # Solo las 3 mejores
                        results = reader.readtext(img_proc)
                        texto_easy = ' '.join([text for (bbox, text, prob) in results])
                        numeros = re.findall(r'-?\d+\.?\d*', texto_easy)
                        if len(numeros) > max_numeros:
                            max_numeros = len(numeros)
                            mejor_texto = texto_easy
                except:
                    pass
        except:
            # Si pytesseract no está disponible, usar el texto vacío
            mejor_texto = ""
        
        # Si aún no hay texto, combinar todos los intentos
        if not mejor_texto and textos:
            mejor_texto = "\n".join(textos)
        
        return {
            'texto': mejor_texto,
            'imagen_procesada': mejor_imagen,
            'exito': True,
            'num_numeros_detectados': max_numeros
        }
    
    except Exception as e:
        return {
            'texto': '',
            'imagen_procesada': None,
            'exito': False,
            'error': str(e),
            'num_numeros_detectados': 0
        }

def extraer_matriz_de_texto(texto):
    """
    Extrae matrices del texto OCR
    """
    # Buscar patrones de números
    numeros = re.findall(r'-?\d+\.?\d*', texto)
    
    if not numeros:
        return None, None
    
    # Convertir a floats
    valores = [float(n) for n in numeros]
    
    return valores, texto

def extraer_puntos_interpolacion(texto):
    """
    Extrae puntos (x,y) para interpolación del texto
    Soporta múltiples formatos y es más inteligente
    """
    if not texto or len(texto.strip()) < 3:
        return None, None
    
    # Limpiar texto
    texto = texto.replace('|', ' ').replace(':', ' ').replace(';', ' ')
    texto = texto.replace('=', ' ')
    
    # Patrón 1: Buscar patrones como (x,y) o x,y
    patron_puntos = r'\(?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)?'
    puntos = re.findall(patron_puntos, texto)
    
    if puntos and len(puntos) >= 2:
        x_vals = [float(p[0]) for p in puntos]
        y_vals = [float(p[1]) for p in puntos]
        return x_vals, y_vals
    
    # Patrón 2: Buscar tablas con x e y (más flexible)
    lineas = texto.split('\n')
    x_vals = []
    y_vals = []
    
    for i, linea in enumerate(lineas):
        linea_lower = linea.lower()
        nums = re.findall(r'-?\d+\.?\d*', linea)
        
        # Buscar líneas que contengan 'x' seguida de números
        if ('x' in linea_lower or 'X' in linea) and nums and not y_vals:
            # Filtrar números que no sean parte de 'x1', 'x2', etc.
            x_vals = [float(n) for n in nums if len(n) > 0]
        
        # Buscar líneas que contengan 'y' o 'f' seguida de números
        elif (('y' in linea_lower or 'f' in linea_lower or 'Y' in linea or 'F' in linea) 
              and nums and x_vals and not y_vals):
            y_vals = [float(n) for n in nums if len(n) > 0]
    
    if x_vals and y_vals and len(x_vals) == len(y_vals) and len(x_vals) >= 2:
        return x_vals, y_vals
    
    # Patrón 3: Buscar dos listas de números en líneas consecutivas
    numeros_por_linea = []
    for linea in lineas:
        nums = re.findall(r'-?\d+\.?\d*', linea)
        if len(nums) >= 2:  # Al menos 2 números
            numeros_por_linea.append([float(n) for n in nums])
    
    if len(numeros_por_linea) >= 2:
        # Verificar que tengan la misma longitud
        if len(numeros_por_linea[0]) == len(numeros_por_linea[1]):
            return numeros_por_linea[0], numeros_por_linea[1]
        
        # Si no, buscar las dos líneas con más números iguales
        for i in range(len(numeros_por_linea)):
            for j in range(i+1, len(numeros_por_linea)):
                if len(numeros_por_linea[i]) == len(numeros_por_linea[j]) and len(numeros_por_linea[i]) >= 2:
                    return numeros_por_linea[i], numeros_por_linea[j]
    
    # Patrón 4: Todos los números en una sola línea, dividir por la mitad
    todos_nums = re.findall(r'-?\d+\.?\d*', texto)
    if len(todos_nums) >= 4 and len(todos_nums) % 2 == 0:
        mitad = len(todos_nums) // 2
        x_vals = [float(n) for n in todos_nums[:mitad]]
        y_vals = [float(n) for n in todos_nums[mitad:]]
        return x_vals, y_vals
    
    # Patrón 5: Buscar formato de tabla (números en columnas)
    # Ejemplo: "0  1" en una línea, "1  2" en otra
    if len(numeros_por_linea) >= 2:
        # Intentar transponer (asumir que cada línea es un par x,y)
        if all(len(linea) == 2 for linea in numeros_por_linea):
            x_vals = [linea[0] for linea in numeros_por_linea]
            y_vals = [linea[1] for linea in numeros_por_linea]
            if len(x_vals) >= 2:
                return x_vals, y_vals
    
    return None, None

def mostrar_imagen_procesada(imagen_original, imagen_procesada):
    """
    Muestra comparación de imagen original vs procesada
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    axes[0].imshow(imagen_original)
    axes[0].set_title('Imagen Original', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    if imagen_procesada is not None:
        axes[1].imshow(imagen_procesada, cmap='gray')
        axes[1].set_title('Imagen Procesada', fontsize=14, fontweight='bold')
        axes[1].axis('off')
    
    plt.tight_layout()
    return fig
