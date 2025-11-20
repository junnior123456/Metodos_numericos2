"""
Sistema de visión avanzada para detectar y extraer datos de tablas
Usa técnicas de IA y visión por computadora profesional
"""
import cv2
import numpy as np
import re
from PIL import Image

def analizar_imagen_completa(imagen):
    """
    Análisis completo de imagen con múltiples estrategias
    """
    if isinstance(imagen, Image.Image):
        img_array = np.array(imagen)
    else:
        img_array = imagen
    
    # Estrategia 1: Detección de tabla por líneas
    x1, y1 = detectar_tabla_por_lineas(img_array)
    if x1 and y1 and len(x1) >= 2:
        return x1, y1, "Detección por líneas"
    
    # Estrategia 2: Detección por regiones de texto
    x2, y2 = detectar_por_regiones_texto(img_array)
    if x2 and y2 and len(x2) >= 2:
        return x2, y2, "Detección por regiones"
    
    # Estrategia 3: OCR agresivo con múltiples configuraciones
    x3, y3 = ocr_agresivo_multiconfig(img_array)
    if x3 and y3 and len(x3) >= 2:
        return x3, y3, "OCR agresivo"
    
    # Estrategia 4: Análisis de patrones visuales
    x4, y4 = analizar_patrones_visuales(img_array)
    if x4 and y4 and len(x4) >= 2:
        return x4, y4, "Patrones visuales"
    
    return None, None, "No se detectaron datos"

def detectar_tabla_por_lineas(img_array):
    """
    Detecta tabla buscando líneas horizontales y verticales
    """
    try:
        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Threshold adaptativo
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Detectar líneas con HoughLines
        lines = cv2.HoughLinesP(binary, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        
        if lines is None:
            return None, None
        
        # Separar líneas horizontales y verticales
        h_lines = []
        v_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            if angle < 10 or angle > 170:  # Horizontal
                h_lines.append((y1 + y2) // 2)
            elif 80 < angle < 100:  # Vertical
                v_lines.append((x1 + x2) // 2)
        
        if len(h_lines) >= 2 and len(v_lines) >= 2:
            # Hay una tabla, extraer celdas
            h_lines = sorted(set(h_lines))
            v_lines = sorted(set(v_lines))
            
            # Extraer números de cada celda
            numeros_por_fila = []
            
            for i in range(len(h_lines) - 1):
                fila_numeros = []
                for j in range(len(v_lines) - 1):
                    # Extraer región de celda
                    y1, y2 = h_lines[i], h_lines[i+1]
                    x1, x2 = v_lines[j], v_lines[j+1]
                    
                    celda = gray[y1:y2, x1:x2]
                    numero = extraer_numero_celda(celda)
                    if numero is not None:
                        fila_numeros.append(numero)
                
                if fila_numeros:
                    numeros_por_fila.append(fila_numeros)
            
            # Organizar en X e Y
            if len(numeros_por_fila) >= 2:
                # Buscar dos filas con la misma cantidad de números
                for i in range(len(numeros_por_fila) - 1):
                    if len(numeros_por_fila[i]) == len(numeros_por_fila[i+1]):
                        return numeros_por_fila[i], numeros_por_fila[i+1]
        
        return None, None
    
    except:
        return None, None

def detectar_por_regiones_texto(img_array):
    """
    Detecta números buscando regiones con texto
    """
    try:
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Aplicar MSER (Maximally Stable Extremal Regions)
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Filtrar regiones que parezcan texto/números
        regiones_texto = []
        
        for region in regions:
            x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
            aspect_ratio = w / float(h) if h > 0 else 0
            
            # Filtrar por tamaño y proporción
            if 10 < w < 200 and 10 < h < 100 and 0.1 < aspect_ratio < 5:
                roi = gray[y:y+h, x:x+w]
                numero = extraer_numero_celda(roi)
                if numero is not None:
                    regiones_texto.append((x, y, numero))
        
        if len(regiones_texto) >= 4:
            return organizar_por_posicion(regiones_texto)
        
        return None, None
    
    except:
        return None, None

def ocr_agresivo_multiconfig(img_array):
    """
    OCR con múltiples configuraciones y técnicas
    """
    try:
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Múltiples preprocesamientos
        versiones = []
        
        # Versión 1: Original
        versiones.append(gray)
        
        # Versión 2: CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        versiones.append(clahe.apply(gray))
        
        # Versión 3: Denoise
        versiones.append(cv2.fastNlMeansDenoising(gray, None, 10, 7, 21))
        
        # Versión 4: Threshold Otsu
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        versiones.append(otsu)
        
        # Versión 5: Invertido
        versiones.append(cv2.bitwise_not(gray))
        
        # Intentar OCR en cada versión
        mejor_resultado = None
        max_numeros = 0
        
        # Intentar con EasyOCR primero (más robusto)
        try:
            import easyocr
            reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
            
            for version in versiones[:3]:  # Solo las 3 mejores
                try:
                    results = reader.readtext(version)
                    numeros_detectados = []
                    
                    for (bbox, text, prob) in results:
                        nums = re.findall(r'-?\d+\.?\d*', text)
                        for num in nums:
                            try:
                                valor = float(num)
                                x_pos = int(bbox[0][0])
                                y_pos = int(bbox[0][1])
                                numeros_detectados.append((x_pos, y_pos, valor))
                            except:
                                continue
                    
                    if len(numeros_detectados) > max_numeros:
                        max_numeros = len(numeros_detectados)
                        mejor_resultado = numeros_detectados
                
                except:
                    continue
        
        except:
            pass
        
        # Si EasyOCR encontró suficientes números
        if mejor_resultado and len(mejor_resultado) >= 4:
            return organizar_por_posicion(mejor_resultado)
        
        # Fallback: Pytesseract
        try:
            import pytesseract
            
            configs = [
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,-',
                r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789.,-',
                r'--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789.,-',
            ]
            
            for version in versiones:
                for config in configs:
                    try:
                        texto = pytesseract.image_to_string(version, config=config)
                        numeros = re.findall(r'-?\d+\.?\d*', texto)
                        
                        if len(numeros) > max_numeros:
                            max_numeros = len(numeros)
                            valores = [float(n) for n in numeros]
                            
                            # Dividir en X e Y
                            if len(valores) >= 4 and len(valores) % 2 == 0:
                                mitad = len(valores) // 2
                                mejor_resultado = (valores[:mitad], valores[mitad:])
                    
                    except:
                        continue
            
            if mejor_resultado and isinstance(mejor_resultado, tuple):
                return mejor_resultado[0], mejor_resultado[1]
        
        except:
            pass
        
        return None, None
    
    except:
        return None, None

def analizar_patrones_visuales(img_array):
    """
    Analiza patrones visuales para encontrar números
    """
    try:
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        height, width = gray.shape
        
        # Dividir imagen en cuadrantes
        cuadrantes = [
            gray[0:height//2, 0:width//2],  # Superior izquierdo
            gray[0:height//2, width//2:],   # Superior derecho
            gray[height//2:, 0:width//2],   # Inferior izquierdo
            gray[height//2:, width//2:],    # Inferior derecho
        ]
        
        numeros_por_cuadrante = []
        
        for cuadrante in cuadrantes:
            nums = extraer_numeros_region(cuadrante)
            if nums:
                numeros_por_cuadrante.append(nums)
        
        # Si encontramos números en al menos 2 cuadrantes
        if len(numeros_por_cuadrante) >= 2:
            # Combinar y organizar
            todos_numeros = []
            for nums in numeros_por_cuadrante:
                todos_numeros.extend(nums)
            
            if len(todos_numeros) >= 4 and len(todos_numeros) % 2 == 0:
                mitad = len(todos_numeros) // 2
                return todos_numeros[:mitad], todos_numeros[mitad:]
        
        return None, None
    
    except:
        return None, None

def extraer_numero_celda(celda):
    """
    Extrae un número de una celda/región
    """
    try:
        # Preprocesar
        if len(celda.shape) == 3:
            celda = cv2.cvtColor(celda, cv2.COLOR_RGB2GRAY)
        
        # Redimensionar si es muy pequeña
        if celda.shape[0] < 20 or celda.shape[1] < 20:
            celda = cv2.resize(celda, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Threshold
        _, binary = cv2.threshold(celda, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Intentar OCR
        try:
            import pytesseract
            config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,-'
            texto = pytesseract.image_to_string(binary, config=config).strip()
            
            # Buscar número
            numeros = re.findall(r'-?\d+\.?\d*', texto)
            if numeros:
                return float(numeros[0])
        except:
            pass
        
        return None
    
    except:
        return None

def extraer_numeros_region(region):
    """
    Extrae todos los números de una región
    """
    try:
        if len(region.shape) == 3:
            region = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        
        # Preprocesar
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(region)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR
        try:
            import pytesseract
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,-'
            texto = pytesseract.image_to_string(binary, config=config)
            
            numeros = re.findall(r'-?\d+\.?\d*', texto)
            if numeros:
                return [float(n) for n in numeros]
        except:
            pass
        
        return None
    
    except:
        return None

def organizar_por_posicion(datos_con_posicion):
    """
    Organiza números por su posición en la imagen
    """
    try:
        # Ordenar por Y (fila) y luego por X (columna)
        datos_ordenados = sorted(datos_con_posicion, key=lambda d: (d[1], d[0]))
        
        # Agrupar por filas (Y similar)
        filas = []
        fila_actual = []
        y_anterior = datos_ordenados[0][1]
        tolerancia_y = 30  # píxeles
        
        for dato in datos_ordenados:
            x, y, valor = dato
            
            if abs(y - y_anterior) > tolerancia_y:
                if fila_actual:
                    filas.append(fila_actual)
                fila_actual = [valor]
                y_anterior = y
            else:
                fila_actual.append(valor)
        
        if fila_actual:
            filas.append(fila_actual)
        
        # Buscar dos filas con la misma cantidad de elementos
        if len(filas) >= 2:
            for i in range(len(filas) - 1):
                if len(filas[i]) == len(filas[i+1]) and len(filas[i]) >= 2:
                    return filas[i], filas[i+1]
        
        # Si solo hay una fila con números pares, dividir
        if len(filas) == 1 and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
            mitad = len(filas[0]) // 2
            return filas[0][:mitad], filas[0][mitad:]
        
        return None, None
    
    except:
        return None, None
