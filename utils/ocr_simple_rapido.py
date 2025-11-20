"""
OCR SIMPLE Y RÁPIDO - Solo lo necesario
Extrae números de tablas de forma eficiente
"""
import cv2
import numpy as np
from PIL import Image
import re

def extraer_rapido(imagen):
    """
    Extracción RÁPIDA y SIMPLE
    """
    print("\n🚀 EXTRACCIÓN RÁPIDA...")
    
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
    if h < 500 or w < 500:
        scale = max(500/h, 500/w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Preprocesar SIMPLE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # INTENTAR EASYOCR (más preciso)
    try:
        import easyocr
        print("  Usando EasyOCR...")
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        # UNA SOLA lectura
        results = reader.readtext(enhanced, detail=1)
        
        numeros = []
        for (bbox, text, conf) in results:
            if conf > 0.3:  # Solo confianza razonable
                # Limpiar
                text = text.replace(',', '.').replace('O', '0').replace('o', '0')
                nums = re.findall(r'-?\d+\.?\d*', text)
                
                for n in nums:
                    try:
                        val = float(n)
                        x = int((bbox[0][0] + bbox[2][0]) / 2)
                        y = int((bbox[0][1] + bbox[2][1]) / 2)
                        numeros.append({'val': val, 'x': x, 'y': y})
                        print(f"    {val}")
                    except:
                        pass
        
        if len(numeros) >= 4:
            print(f"  ✓ Detectados: {len(numeros)}")
            return organizar_simple(numeros)
    
    except Exception as e:
        print(f"  EasyOCR no disponible: {e}")
    
    # FALLBACK: PYTESSERACT
    try:
        import pytesseract
        print("  Usando Pytesseract...")
        
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text = pytesseract.image_to_string(binary, config='--psm 6')
        
        # Limpiar
        text = text.replace(',', '.').replace('O', '0').replace('o', '0')
        nums = re.findall(r'-?\d+\.?\d*', text)
        
        if len(nums) >= 4:
            valores = [float(n) for n in nums]
            print(f"  ✓ Detectados: {len(valores)}")
            
            # Dividir en X e Y
            if len(valores) % 2 == 0:
                mitad = len(valores) // 2
                x_vals = valores[:mitad]
                y_vals = valores[mitad:]
                
                if len(set(x_vals)) == len(x_vals):
                    print(f"  X = {x_vals}")
                    print(f"  Y = {y_vals}")
                    return x_vals, y_vals
    
    except Exception as e:
        print(f"  Pytesseract falló: {e}")
    
    print("  ✗ No se pudieron extraer")
    return None, None

def organizar_simple(numeros):
    """
    Organización SIMPLE por posición
    """
    # Ordenar por Y
    numeros.sort(key=lambda n: n['y'])
    
    # Agrupar en filas
    filas = []
    fila = []
    y_ref = numeros[0]['y']
    
    for num in numeros:
        if abs(num['y'] - y_ref) < 40:
            fila.append(num)
        else:
            if fila:
                fila.sort(key=lambda n: n['x'])
                filas.append([n['val'] for n in fila])
            fila = [num]
            y_ref = num['y']
    
    if fila:
        fila.sort(key=lambda n: n['x'])
        filas.append([n['val'] for n in fila])
    
    # Buscar dos filas iguales
    for i in range(len(filas)):
        for j in range(i+1, len(filas)):
            if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                x_vals = filas[i]
                y_vals = filas[j]
                if len(set(x_vals)) == len(x_vals):
                    print(f"  X = {x_vals}")
                    print(f"  Y = {y_vals}")
                    return x_vals, y_vals
    
    # Dividir primera fila
    if filas and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
        mitad = len(filas[0]) // 2
        x_vals = filas[0][:mitad]
        y_vals = filas[0][mitad:]
        if len(set(x_vals)) == len(x_vals):
            print(f"  X = {x_vals}")
            print(f"  Y = {y_vals}")
            return x_vals, y_vals
    
    return None, None
