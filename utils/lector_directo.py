"""
Lector directo de tablas - Sin tonterías, directo al grano
Lee la tabla de la imagen y extrae X e Y
"""
import cv2
import numpy as np
from PIL import Image
import re

def leer_tabla_directamente(imagen):
    """
    Lee la tabla directamente de la imagen
    Retorna X, Y o None, None
    """
    # Convertir imagen
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen
    
    # A escala de grises
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Intentar con EasyOCR (el mejor)
    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        # Leer toda la imagen
        results = reader.readtext(gray)
        
        # Extraer TODOS los números con su posición
        numeros_con_pos = []
        for (bbox, text, prob) in results:
            # Buscar números en el texto
            nums = re.findall(r'-?\d+\.?\d*', text)
            for num in nums:
                try:
                    valor = float(num)
                    # Posición Y del texto
                    y_pos = int(bbox[0][1])
                    # Posición X del texto
                    x_pos = int(bbox[0][0])
                    numeros_con_pos.append((x_pos, y_pos, valor))
                except:
                    continue
        
        # Organizar por filas (Y similar)
        if len(numeros_con_pos) >= 4:
            # Ordenar por Y
            numeros_con_pos.sort(key=lambda x: x[1])
            
            # Agrupar por filas
            filas = []
            fila_actual = []
            y_anterior = numeros_con_pos[0][1]
            
            for x_pos, y_pos, valor in numeros_con_pos:
                # Si Y es muy diferente, nueva fila
                if abs(y_pos - y_anterior) > 30:
                    if fila_actual:
                        # Ordenar por X dentro de la fila
                        fila_actual.sort(key=lambda x: x[0])
                        filas.append([v[2] for v in fila_actual])
                    fila_actual = [(x_pos, y_pos, valor)]
                    y_anterior = y_pos
                else:
                    fila_actual.append((x_pos, y_pos, valor))
            
            # Última fila
            if fila_actual:
                fila_actual.sort(key=lambda x: x[0])
                filas.append([v[2] for v in fila_actual])
            
            # Buscar dos filas con la misma cantidad
            for i in range(len(filas)):
                for j in range(i+1, len(filas)):
                    if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                        return filas[i], filas[j]
            
            # Si no, dividir la primera fila con números pares
            for fila in filas:
                if len(fila) >= 4 and len(fila) % 2 == 0:
                    mitad = len(fila) // 2
                    return fila[:mitad], fila[mitad:]
    
    except Exception as e:
        print(f"EasyOCR falló: {e}")
    
    # Plan B: Pytesseract
    try:
        import pytesseract
        
        # Preprocesar
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Leer
        texto = pytesseract.image_to_string(binary, config='--psm 6')
        
        # Extraer números
        numeros = re.findall(r'-?\d+\.?\d*', texto)
        
        if len(numeros) >= 4:
            valores = [float(n) for n in numeros]
            
            # Dividir en X e Y
            if len(valores) % 2 == 0:
                mitad = len(valores) // 2
                return valores[:mitad], valores[mitad:]
    
    except Exception as e:
        print(f"Pytesseract falló: {e}")
    
    return None, None

def extraer_de_imagen_rapido(imagen):
    """
    Extracción rápida y directa
    """
    x, y = leer_tabla_directamente(imagen)
    
    if x and y:
        return x, y, True
    
    return None, None, False
