"""
OCR REAL que funciona - Extrae números de tablas
"""
import cv2
import numpy as np
from PIL import Image
import re

def extraer_numeros_reales(imagen):
    """
    Extrae números de una imagen de tabla REALMENTE
    """
    print("\n" + "="*60)
    print("EXTRAYENDO NÚMEROS DE LA IMAGEN")
    print("="*60)
    
    # Convertir imagen
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
    if h < 400 or w < 400:
        scale = max(400/h, 400/w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        print(f"Imagen escalada: {w}x{h} -> {gray.shape[1]}x{gray.shape[0]}")
    
    # INTENTAR CON EASYOCR
    try:
        import easyocr
        print("Usando EasyOCR...")
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        # Leer
        results = reader.readtext(gray)
        
        # Extraer números con posición
        numeros = []
        for (bbox, text, conf) in results:
            if conf > 0.2:  # Confianza baja para capturar más
                # Normalizar texto
                text = text.replace(',', '.').replace('O', '0').replace('o', '0')
                # Buscar números
                nums = re.findall(r'-?\d+\.?\d*', text)
                for n in nums:
                    try:
                        val = float(n)
                        x = int((bbox[0][0] + bbox[2][0]) / 2)
                        y = int((bbox[0][1] + bbox[2][1]) / 2)
                        numeros.append({'val': val, 'x': x, 'y': y})
                        print(f"  Detectado: {val} en ({x}, {y})")
                    except:
                        pass
        
        if len(numeros) >= 4:
            print(f"✓ EasyOCR detectó {len(numeros)} números")
            return organizar_numeros(numeros)
    
    except Exception as e:
        print(f"EasyOCR falló: {e}")
    
    # INTENTAR CON PYTESSERACT
    try:
        import pytesseract
        print("Usando Pytesseract...")
        
        # Preprocesar
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extraer
        config = '--psm 6 -c tessedit_char_whitelist=0123456789.,-'
        text = pytesseract.image_to_string(binary, config=config)
        
        # Normalizar
        text = text.replace(',', '.').replace('O', '0').replace('o', '0')
        
        # Extraer números
        nums = re.findall(r'-?\d+\.?\d*', text)
        
        if len(nums) >= 4:
            valores = [float(n) for n in nums]
            print(f"✓ Pytesseract detectó {len(valores)} números")
            print(f"  Valores: {valores}")
            
            # Dividir en X e Y
            if len(valores) % 2 == 0:
                mitad = len(valores) // 2
                x_vals = valores[:mitad]
                y_vals = valores[mitad:]
                
                # Validar
                if len(set(x_vals)) == len(x_vals):  # X sin duplicados
                    print(f"✓ X = {x_vals}")
                    print(f"✓ Y = {y_vals}")
                    return x_vals, y_vals
    
    except Exception as e:
        print(f"Pytesseract falló: {e}")
    
    print("✗ No se pudieron extraer números")
    return None, None

def organizar_numeros(numeros):
    """
    Organiza números por posición en filas
    """
    print("\nOrganizando números por posición...")
    
    # Ordenar por Y
    numeros.sort(key=lambda n: n['y'])
    
    # Agrupar en filas
    filas = []
    fila = []
    y_ref = numeros[0]['y']
    
    for num in numeros:
        if abs(num['y'] - y_ref) < 30:  # Misma fila
            fila.append(num)
        else:
            if fila:
                fila.sort(key=lambda n: n['x'])  # Ordenar por X
                filas.append([n['val'] for n in fila])
            fila = [num]
            y_ref = num['y']
    
    if fila:
        fila.sort(key=lambda n: n['x'])
        filas.append([n['val'] for n in fila])
    
    print(f"Filas detectadas: {len(filas)}")
    for i, f in enumerate(filas):
        print(f"  Fila {i+1}: {f}")
    
    # Buscar dos filas iguales
    for i in range(len(filas)):
        for j in range(i+1, len(filas)):
            if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                x_vals = filas[i]
                y_vals = filas[j]
                if len(set(x_vals)) == len(x_vals):  # X sin duplicados
                    print(f"✓ X = {x_vals}")
                    print(f"✓ Y = {y_vals}")
                    return x_vals, y_vals
    
    # Dividir primera fila
    if filas and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
        mitad = len(filas[0]) // 2
        x_vals = filas[0][:mitad]
        y_vals = filas[0][mitad:]
        if len(set(x_vals)) == len(x_vals):
            print(f"✓ X = {x_vals}")
            print(f"✓ Y = {y_vals}")
            return x_vals, y_vals
    
    return None, None
