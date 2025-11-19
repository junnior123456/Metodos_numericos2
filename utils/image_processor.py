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
    Procesa una imagen y extrae texto matemático
    
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
        
        # Mejorar contraste
        gray = cv2.equalizeHist(gray)
        
        # Aplicar threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Intentar OCR con pytesseract si está disponible
        try:
            import pytesseract
            texto = pytesseract.image_to_string(thresh, config='--psm 6')
        except:
            texto = ""
        
        return {
            'texto': texto,
            'imagen_procesada': thresh,
            'exito': True
        }
    
    except Exception as e:
        return {
            'texto': '',
            'imagen_procesada': None,
            'exito': False,
            'error': str(e)
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
    Soporta múltiples formatos
    """
    if not texto or len(texto.strip()) < 3:
        return None, None
    
    # Limpiar texto
    texto = texto.replace('|', ' ').replace(':', ' ')
    
    # Patrón 1: Buscar patrones como (x,y) o x,y
    patron_puntos = r'\(?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\)?'
    puntos = re.findall(patron_puntos, texto)
    
    if puntos and len(puntos) >= 2:
        x_vals = [float(p[0]) for p in puntos]
        y_vals = [float(p[1]) for p in puntos]
        return x_vals, y_vals
    
    # Patrón 2: Buscar tablas con x e y
    lineas = texto.split('\n')
    x_vals = []
    y_vals = []
    
    for linea in lineas:
        linea_lower = linea.lower()
        # Buscar líneas que contengan 'x' o 'y'
        if 'x' in linea_lower and not 'y' in linea_lower:
            nums = re.findall(r'-?\d+\.?\d*', linea)
            if nums:
                x_vals = [float(n) for n in nums]
        elif 'y' in linea_lower and not 'x' in linea_lower:
            nums = re.findall(r'-?\d+\.?\d*', linea)
            if nums:
                y_vals = [float(n) for n in nums]
    
    if x_vals and y_vals and len(x_vals) == len(y_vals):
        return x_vals, y_vals
    
    # Patrón 3: Buscar dos listas de números en líneas consecutivas
    numeros_por_linea = []
    for linea in lineas:
        nums = re.findall(r'-?\d+\.?\d*', linea)
        if len(nums) >= 2:  # Al menos 2 números
            numeros_por_linea.append([float(n) for n in nums])
    
    if len(numeros_por_linea) >= 2:
        # Tomar las dos primeras líneas con números
        return numeros_por_linea[0], numeros_por_linea[1]
    
    # Patrón 4: Todos los números en una sola línea, dividir por la mitad
    todos_nums = re.findall(r'-?\d+\.?\d*', texto)
    if len(todos_nums) >= 4 and len(todos_nums) % 2 == 0:
        mitad = len(todos_nums) // 2
        x_vals = [float(n) for n in todos_nums[:mitad]]
        y_vals = [float(n) for n in todos_nums[mitad:]]
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
