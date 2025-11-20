"""
Analizador inteligente de imágenes - Análisis interno profundo
Extrae datos EXACTOS de tablas sin mostrar procesamiento
"""
import cv2
import numpy as np
from PIL import Image
import re

def analizar_imagen_internamente(imagen):
    """
    Análisis INTERNO completo de la imagen
    Retorna X, Y directamente sin mostrar procesamiento
    """
    # Convertir imagen
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen
    
    # Convertir a escala de grises
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # ANÁLISIS PROFUNDO INTERNO
    resultados = []
    
    # Método 1: EasyOCR con análisis de posición
    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        # Leer con alta precisión
        detecciones = reader.readtext(gray, detail=1, paragraph=False)
        
        # Extraer números con posición EXACTA
        numeros_detectados = []
        for (bbox, text, confidence) in detecciones:
            # Solo considerar detecciones con buena confianza
            if confidence > 0.3:
                # Buscar números (incluyendo negativos y decimales)
                nums = re.findall(r'-?\d+\.?\d*', text)
                for num_str in nums:
                    try:
                        valor = float(num_str)
                        # Posición del centro del bbox
                        x_centro = int((bbox[0][0] + bbox[2][0]) / 2)
                        y_centro = int((bbox[0][1] + bbox[2][1]) / 2)
                        numeros_detectados.append({
                            'valor': valor,
                            'x': x_centro,
                            'y': y_centro,
                            'confianza': confidence
                        })
                    except:
                        continue
        
        # Organizar por filas (Y similar)
        if len(numeros_detectados) >= 4:
            # Ordenar por Y primero
            numeros_detectados.sort(key=lambda n: n['y'])
            
            # Agrupar en filas
            filas = []
            fila_actual = []
            y_ref = numeros_detectados[0]['y']
            tolerancia_y = 40  # píxeles
            
            for num in numeros_detectados:
                if abs(num['y'] - y_ref) <= tolerancia_y:
                    fila_actual.append(num)
                else:
                    if fila_actual:
                        # Ordenar fila por X
                        fila_actual.sort(key=lambda n: n['x'])
                        filas.append([n['valor'] for n in fila_actual])
                    fila_actual = [num]
                    y_ref = num['y']
            
            # Última fila
            if fila_actual:
                fila_actual.sort(key=lambda n: n['x'])
                filas.append([n['valor'] for n in fila_actual])
            
            # Buscar dos filas con la misma cantidad de elementos
            for i in range(len(filas)):
                for j in range(i+1, len(filas)):
                    if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                        # Verificar que sean valores razonables
                        if validar_valores(filas[i], filas[j]):
                            return filas[i], filas[j], "EasyOCR - Análisis de posición"
            
            # Si no encontramos dos filas iguales, buscar patrón alternativo
            # A veces los números están en una sola fila alternados
            for fila in filas:
                if len(fila) >= 4 and len(fila) % 2 == 0:
                    mitad = len(fila) // 2
                    x_vals = fila[:mitad]
                    y_vals = fila[mitad:]
                    if validar_valores(x_vals, y_vals):
                        return x_vals, y_vals, "EasyOCR - Fila única"
    
    except Exception as e:
        print(f"EasyOCR interno falló: {e}")
    
    # Método 2: Preprocesamiento múltiple + Pytesseract
    try:
        import pytesseract
        
        # Aplicar múltiples preprocesamientos
        versiones = []
        
        # Versión 1: CLAHE + Denoise
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        versiones.append(denoised)
        
        # Versión 2: Threshold adaptativo
        thresh_adapt = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        versiones.append(thresh_adapt)
        
        # Versión 3: Otsu
        _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        versiones.append(thresh_otsu)
        
        # Versión 4: Morfología para limpiar
        kernel = np.ones((2,2), np.uint8)
        morph = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel)
        versiones.append(morph)
        
        mejor_resultado = None
        max_numeros = 0
        
        for version in versiones:
            # Configuración específica para números
            config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.,-'
            texto = pytesseract.image_to_string(version, config=config)
            
            # Extraer números
            numeros = re.findall(r'-?\d+\.?\d*', texto)
            
            if len(numeros) > max_numeros:
                max_numeros = len(numeros)
                mejor_resultado = numeros
        
        if mejor_resultado and len(mejor_resultado) >= 4:
            valores = [float(n) for n in mejor_resultado]
            
            # Intentar dividir en X e Y
            if len(valores) % 2 == 0:
                mitad = len(valores) // 2
                x_vals = valores[:mitad]
                y_vals = valores[mitad:]
                if validar_valores(x_vals, y_vals):
                    return x_vals, y_vals, "Pytesseract - Multiprocesamiento"
    
    except Exception as e:
        print(f"Pytesseract interno falló: {e}")
    
    # Método 3: Análisis de regiones específicas
    try:
        # Dividir imagen en regiones horizontales
        height, width = gray.shape
        
        # Región superior (donde suele estar X)
        region_superior = gray[int(height*0.4):int(height*0.6), :]
        
        # Región inferior (donde suele estar Y)
        region_inferior = gray[int(height*0.6):int(height*0.85), :]
        
        x_vals = extraer_numeros_de_region(region_superior)
        y_vals = extraer_numeros_de_region(region_inferior)
        
        if x_vals and y_vals and len(x_vals) == len(y_vals) and len(x_vals) >= 2:
            if validar_valores(x_vals, y_vals):
                return x_vals, y_vals, "Análisis por regiones"
    
    except Exception as e:
        print(f"Análisis por regiones falló: {e}")
    
    return None, None, "No se pudo extraer"

def extraer_numeros_de_region(region):
    """
    Extrae números de una región específica
    """
    try:
        import pytesseract
        
        # Preprocesar región
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(region)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR
        config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.,-'
        texto = pytesseract.image_to_string(binary, config=config)
        
        # Extraer números
        numeros = re.findall(r'-?\d+\.?\d*', texto)
        
        if numeros:
            return [float(n) for n in numeros]
    
    except:
        pass
    
    return None

def validar_valores(x_vals, y_vals):
    """
    Valida que los valores sean razonables para interpolación
    """
    try:
        # Verificar que tengan la misma longitud
        if len(x_vals) != len(y_vals):
            return False
        
        # Verificar que haya al menos 2 puntos
        if len(x_vals) < 2:
            return False
        
        # Verificar que X no tenga duplicados
        if len(set(x_vals)) != len(x_vals):
            return False
        
        # Verificar que los valores sean números válidos
        for val in x_vals + y_vals:
            if not isinstance(val, (int, float)):
                return False
            if np.isnan(val) or np.isinf(val):
                return False
        
        return True
    
    except:
        return False

def extraer_con_analisis_interno(imagen):
    """
    Función principal de extracción con análisis interno
    NO muestra procesamiento, solo retorna resultados
    """
    x, y, metodo = analizar_imagen_internamente(imagen)
    
    if x and y:
        return x, y, True, metodo
    
    return None, None, False, "Falló la extracción"
