"""
Módulo para detectar y extraer datos de tablas en imágenes
Usa detección de contornos y análisis de estructura
"""
import cv2
import numpy as np
import re

def detectar_tabla_y_extraer_datos(imagen):
    """
    Detecta tablas en la imagen y extrae los datos numéricos
    usando análisis de estructura en lugar de solo OCR
    """
    try:
        # Convertir a numpy array si es necesario
        if hasattr(imagen, 'convert'):
            img_array = np.array(imagen.convert('RGB'))
        else:
            img_array = imagen
        
        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Aplicar múltiples técnicas de detección
        resultados = []
        
        # Técnica 1: Detección de líneas horizontales y verticales
        x_datos, y_datos = detectar_por_lineas(gray)
        if x_datos and y_datos:
            resultados.append((x_datos, y_datos, len(x_datos)))
        
        # Técnica 2: Detección por contornos de celdas
        x_datos, y_datos = detectar_por_contornos(gray)
        if x_datos and y_datos:
            resultados.append((x_datos, y_datos, len(x_datos)))
        
        # Técnica 3: OCR mejorado con preprocesamiento agresivo
        x_datos, y_datos = ocr_mejorado_tabla(img_array)
        if x_datos and y_datos:
            resultados.append((x_datos, y_datos, len(x_datos)))
        
        # Técnica 4: Análisis de regiones de interés
        x_datos, y_datos = analizar_regiones_numericas(gray)
        if x_datos and y_datos:
            resultados.append((x_datos, y_datos, len(x_datos)))
        
        # Seleccionar el mejor resultado (el que tenga más puntos válidos)
        if resultados:
            mejor = max(resultados, key=lambda x: x[2])
            return mejor[0], mejor[1], True
        
        return None, None, False
    
    except Exception as e:
        print(f"Error en detección de tabla: {e}")
        return None, None, False

def detectar_por_lineas(gray):
    """
    Detecta tabla usando líneas horizontales y verticales
    """
    try:
        # Binarizar
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Detectar líneas horizontales
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Detectar líneas verticales
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combinar líneas
        table_structure = cv2.add(horizontal_lines, vertical_lines)
        
        # Encontrar contornos de celdas
        contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extraer regiones de celdas y aplicar OCR
        celdas_datos = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 20:  # Filtrar celdas muy pequeñas
                celda = gray[y:y+h, x:x+w]
                texto = extraer_numero_de_celda(celda)
                if texto:
                    celdas_datos.append((x, y, texto))
        
        # Organizar celdas en filas
        if len(celdas_datos) >= 4:
            return organizar_celdas_en_xy(celdas_datos)
        
        return None, None
    
    except:
        return None, None

def detectar_por_contornos(gray):
    """
    Detecta números usando contornos de regiones
    """
    try:
        # Aplicar threshold adaptativo
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY_INV, 11, 2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos que parezcan números
        regiones_numeros = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            
            # Filtrar por tamaño y proporción
            if 10 < w < 100 and 10 < h < 100 and 0.1 < aspect_ratio < 3:
                region = gray[y:y+h, x:x+w]
                numero = extraer_numero_de_celda(region)
                if numero:
                    regiones_numeros.append((x, y, numero))
        
        if len(regiones_numeros) >= 4:
            return organizar_celdas_en_xy(regiones_numeros)
        
        return None, None
    
    except:
        return None, None

def ocr_mejorado_tabla(img_array):
    """
    OCR mejorado específicamente para tablas
    """
    try:
        # Convertir a escala de grises
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Preprocesamiento agresivo
        # 1. Aumentar contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # 3. Threshold
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 4. Dilatar para conectar números
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Intentar con EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['es', 'en'], gpu=False)
            results = reader.readtext(dilated)
            
            # Extraer todos los números
            numeros_detectados = []
            for (bbox, text, prob) in results:
                # Buscar números en el texto
                nums = re.findall(r'-?\d+\.?\d*', text)
                for num in nums:
                    try:
                        valor = float(num)
                        # Obtener posición
                        x_pos = int(bbox[0][0])
                        y_pos = int(bbox[0][1])
                        numeros_detectados.append((x_pos, y_pos, valor))
                    except:
                        continue
            
            if len(numeros_detectados) >= 4:
                return organizar_celdas_en_xy(numeros_detectados)
        
        except:
            pass
        
        # Fallback: Pytesseract
        try:
            import pytesseract
            
            # Configuración específica para números
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,-'
            texto = pytesseract.image_to_string(dilated, config=custom_config)
            
            # Extraer números
            numeros = re.findall(r'-?\d+\.?\d*', texto)
            if len(numeros) >= 4:
                valores = [float(n) for n in numeros]
                # Dividir en X e Y
                if len(valores) % 2 == 0:
                    mitad = len(valores) // 2
                    return valores[:mitad], valores[mitad:], True
        
        except:
            pass
        
        return None, None
    
    except:
        return None, None

def analizar_regiones_numericas(gray):
    """
    Analiza regiones específicas donde suelen estar los números en tablas
    """
    try:
        height, width = gray.shape
        
        # Dividir imagen en regiones
        # Típicamente las tablas tienen encabezados arriba y datos abajo
        region_superior = gray[int(height*0.3):int(height*0.6), :]
        region_inferior = gray[int(height*0.6):, :]
        
        numeros_superior = extraer_numeros_de_region(region_superior)
        numeros_inferior = extraer_numeros_de_region(region_inferior)
        
        # Si encontramos números en ambas regiones, asumir que son X e Y
        if numeros_superior and numeros_inferior:
            if len(numeros_superior) == len(numeros_inferior):
                return numeros_superior, numeros_inferior
        
        return None, None
    
    except:
        return None, None

def extraer_numero_de_celda(celda):
    """
    Extrae un número de una celda individual
    """
    try:
        # Preprocesar celda
        _, binary = cv2.threshold(celda, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Intentar con pytesseract
        try:
            import pytesseract
            config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,-'
            texto = pytesseract.image_to_string(binary, config=config)
            
            # Buscar número
            numeros = re.findall(r'-?\d+\.?\d*', texto)
            if numeros:
                return float(numeros[0])
        except:
            pass
        
        return None
    
    except:
        return None

def extraer_numeros_de_region(region):
    """
    Extrae todos los números de una región
    """
    try:
        # Preprocesar
        _, binary = cv2.threshold(region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
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

def organizar_celdas_en_xy(celdas_datos):
    """
    Organiza celdas detectadas en listas X e Y
    basándose en su posición
    """
    try:
        # Ordenar por posición Y (fila) y luego X (columna)
        celdas_ordenadas = sorted(celdas_datos, key=lambda c: (c[1], c[0]))
        
        # Agrupar por filas (Y similar)
        filas = []
        fila_actual = []
        y_anterior = celdas_ordenadas[0][1]
        
        for celda in celdas_ordenadas:
            x, y, valor = celda
            
            # Si Y es muy diferente, es una nueva fila
            if abs(y - y_anterior) > 20:
                if fila_actual:
                    filas.append(fila_actual)
                fila_actual = [valor]
                y_anterior = y
            else:
                fila_actual.append(valor)
        
        if fila_actual:
            filas.append(fila_actual)
        
        # Si tenemos 2 filas con la misma cantidad de elementos, son X e Y
        if len(filas) >= 2:
            for i in range(len(filas) - 1):
                if len(filas[i]) == len(filas[i+1]) and len(filas[i]) >= 2:
                    return filas[i], filas[i+1]
        
        # Si tenemos una sola fila con números pares, dividir
        if len(filas) == 1 and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
            mitad = len(filas[0]) // 2
            return filas[0][:mitad], filas[0][mitad:]
        
        return None, None
    
    except:
        return None, None
