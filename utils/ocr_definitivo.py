"""
OCR DEFINITIVO - Solución final que funciona
Rápido, preciso y robusto
"""
import cv2
import numpy as np
from PIL import Image
import re

def extraer_tabla(imagen):
    """
    Extrae tabla de imagen - DEFINITIVO
    """
    # Convertir
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen
    
    # Escala de grises
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Escalar si es pequeña
    h, w = gray.shape
    if h < 600:
        scale = 600 / h
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Preprocesar
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # EASYOCR
    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        results = reader.readtext(enhanced, detail=1)
        
        numeros = []
        for (bbox, text, conf) in results:
            if conf > 0.3:
                text = text.replace(',', '.').replace('O', '0').replace('o', '0').replace('l', '1')
                nums = re.findall(r'-?\d+\.?\d*', text)
                for n in nums:
                    try:
                        val = float(n)
                        x = int((bbox[0][0] + bbox[2][0]) / 2)
                        y = int((bbox[0][1] + bbox[2][1]) / 2)
                        numeros.append({'v': val, 'x': x, 'y': y})
                    except:
                        pass
        
        if len(numeros) >= 4:
            return organizar(numeros)
    except:
        pass
    
    # PYTESSERACT
    try:
        import pytesseract
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(binary, config='--psm 6')
        text = text.replace(',', '.').replace('O', '0').replace('o', '0')
        nums = re.findall(r'-?\d+\.?\d*', text)
        
        if len(nums) >= 4:
            vals = [float(n) for n in nums]
            if len(vals) % 2 == 0:
                m = len(vals) // 2
                x = vals[:m]
                y = vals[m:]
                if len(set(x)) == len(x):
                    return x, y
    except:
        pass
    
    return None, None

def organizar(nums):
    """
    Organiza números por posición
    """
    # Ordenar por Y
    nums.sort(key=lambda n: n['y'])
    
    # Agrupar filas
    filas = []
    fila = []
    y_ref = nums[0]['y']
    
    for n in nums:
        if abs(n['y'] - y_ref) < 40:
            fila.append(n)
        else:
            if fila:
                fila.sort(key=lambda n: n['x'])
                filas.append([n['v'] for n in fila])
            fila = [n]
            y_ref = n['y']
    
    if fila:
        fila.sort(key=lambda n: n['x'])
        filas.append([n['v'] for n in fila])
    
    # Buscar dos filas iguales
    for i in range(len(filas)):
        for j in range(i+1, len(filas)):
            if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                if len(set(filas[i])) == len(filas[i]):
                    return filas[i], filas[j]
    
    # Dividir fila
    for f in filas:
        if len(f) >= 4 and len(f) % 2 == 0:
            m = len(f) // 2
            if len(set(f[:m])) == len(f[:m]):
                return f[:m], f[m:]
    
    return None, None
