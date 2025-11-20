"""
Lector directo de tablas - Optimizado para Streamlit Cloud
Usa OpenCV + EasyOCR/Pytesseract con preprocesamiento robusto
"""
import cv2
import numpy as np
from PIL import Image
import re

# Flags de disponibilidad de librerías
EASYOCR_AVAILABLE = False
PYTESSERACT_AVAILABLE = False

# Intentar importar EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✓ EasyOCR está disponible")
except ImportError:
    print("⚠ EasyOCR no está disponible - usando Pytesseract como fallback")

# Intentar importar Pytesseract
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
    print("✓ Pytesseract está disponible")
except ImportError:
    print("⚠ Pytesseract no está disponible")

def preprocesar_imagen(img_array):
    """
    Preprocesamiento robusto de imagen con OpenCV
    
    Args:
        img_array: numpy array de la imagen
        
    Returns:
        list: Lista de versiones preprocesadas de la imagen
    """
    print("🔧 Iniciando preprocesamiento de imagen...")
    
    # Convertir a escala de grises si es necesario
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        print(f"  - Convertido a escala de grises: {gray.shape}")
    else:
        gray = img_array
        print(f"  - Ya está en escala de grises: {gray.shape}")
    
    # Escalar imagen si es muy pequeña (mejora OCR)
    height, width = gray.shape
    if height < 300 or width < 300:
        scale_factor = max(300 / height, 300 / width)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        print(f"  - Imagen escalada de {width}x{height} a {new_width}x{new_height}")
    
    versiones = []
    
    # Versión 1: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    versiones.append(("CLAHE", enhanced))
    print("  - Versión 1: CLAHE aplicado")
    
    # Versión 2: Denoise + CLAHE
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
    denoised_enhanced = clahe.apply(denoised)
    versiones.append(("Denoise+CLAHE", denoised_enhanced))
    print("  - Versión 2: Denoise + CLAHE aplicado")
    
    # Versión 3: Threshold Otsu
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    versiones.append(("Otsu", thresh_otsu))
    print("  - Versión 3: Threshold Otsu aplicado")
    
    # Versión 4: Threshold adaptativo
    thresh_adapt = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    versiones.append(("Adaptativo", thresh_adapt))
    print("  - Versión 4: Threshold adaptativo aplicado")
    
    # Versión 5: Morfología para limpiar ruido
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel)
    versiones.append(("Morfología", morph))
    print("  - Versión 5: Morfología aplicada")
    
    print(f"✓ Preprocesamiento completado: {len(versiones)} versiones generadas")
    return versiones

def extraer_con_easyocr(versiones_img):
    """
    Extrae números usando EasyOCR
    
    Args:
        versiones_img: Lista de tuplas (nombre, imagen)
        
    Returns:
        tuple: (numeros_con_posicion, mejor_version) o (None, None)
    """
    if not EASYOCR_AVAILABLE:
        print("⚠ EasyOCR no disponible, saltando...")
        return None, None
    
    print("\n🔍 Intentando extracción con EasyOCR...")
    
    try:
        # Inicializar reader (solo una vez)
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        print("  - Reader de EasyOCR inicializado")
        
        mejor_resultado = None
        max_numeros = 0
        mejor_version_nombre = None
        
        for nombre, img in versiones_img:
            try:
                print(f"  - Procesando versión: {nombre}")
                
                # Leer texto con EasyOCR
                detecciones = reader.readtext(img, detail=1, paragraph=False)
                
                # Extraer números con posición
                numeros_detectados = []
                for (bbox, text, confidence) in detecciones:
                    # Solo considerar detecciones con confianza > 0.3
                    if confidence > 0.3:
                        # Buscar números (positivos, negativos, decimales con punto o coma)
                        # Reemplazar comas por puntos para normalizar
                        text_normalizado = text.replace(',', '.')
                        nums = re.findall(r'-?\d+\.?\d*', text_normalizado)
                        
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
                            except ValueError:
                                continue
                
                num_detectados = len(numeros_detectados)
                print(f"    → Detectados {num_detectados} números")
                
                if num_detectados > max_numeros:
                    max_numeros = num_detectados
                    mejor_resultado = numeros_detectados
                    mejor_version_nombre = nombre
            
            except Exception as e:
                print(f"    ✗ Error en versión {nombre}: {e}")
                continue
        
        if mejor_resultado and len(mejor_resultado) >= 4:
            print(f"✓ EasyOCR: Mejor resultado con versión '{mejor_version_nombre}': {len(mejor_resultado)} números")
            return mejor_resultado, mejor_version_nombre
        else:
            print(f"✗ EasyOCR: No se detectaron suficientes números (mínimo 4)")
            return None, None
    
    except Exception as e:
        print(f"✗ Error general en EasyOCR: {e}")
        return None, None

def extraer_con_pytesseract(versiones_img):
    """
    Extrae números usando Pytesseract
    
    Args:
        versiones_img: Lista de tuplas (nombre, imagen)
        
    Returns:
        list: Lista de números detectados o None
    """
    if not PYTESSERACT_AVAILABLE:
        print("⚠ Pytesseract no disponible, saltando...")
        return None
    
    print("\n🔍 Intentando extracción con Pytesseract...")
    
    try:
        mejor_resultado = None
        max_numeros = 0
        mejor_version_nombre = None
        
        # Configuración específica para números
        config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.,-'
        
        for nombre, img in versiones_img:
            try:
                print(f"  - Procesando versión: {nombre}")
                
                # Extraer texto
                texto = pytesseract.image_to_string(img, config=config)
                
                # Normalizar comas a puntos
                texto_normalizado = texto.replace(',', '.')
                
                # Extraer números
                numeros = re.findall(r'-?\d+\.?\d*', texto_normalizado)
                
                num_detectados = len(numeros)
                print(f"    → Detectados {num_detectados} números")
                
                if num_detectados > max_numeros:
                    max_numeros = num_detectados
                    mejor_resultado = numeros
                    mejor_version_nombre = nombre
            
            except Exception as e:
                print(f"    ✗ Error en versión {nombre}: {e}")
                continue
        
        if mejor_resultado and len(mejor_resultado) >= 4:
            print(f"✓ Pytesseract: Mejor resultado con versión '{mejor_version_nombre}': {len(mejor_resultado)} números")
            return [float(n) for n in mejor_resultado]
        else:
            print(f"✗ Pytesseract: No se detectaron suficientes números (mínimo 4)")
            return None
    
    except Exception as e:
        print(f"✗ Error general en Pytesseract: {e}")
        return None

def organizar_por_posicion(numeros_con_pos):
    """
    Organiza números por su posición en filas y columnas
    
    Args:
        numeros_con_pos: Lista de diccionarios con 'valor', 'x', 'y'
        
    Returns:
        tuple: (x_vals, y_vals) o (None, None)
    """
    print("\n📊 Organizando números por posición...")
    
    if not numeros_con_pos or len(numeros_con_pos) < 4:
        print("✗ No hay suficientes números para organizar")
        return None, None
    
    # Ordenar por Y (fila) primero
    numeros_ordenados = sorted(numeros_con_pos, key=lambda n: n['y'])
    print(f"  - Números ordenados por Y: {len(numeros_ordenados)}")
    
    # Agrupar en filas (Y similar)
    filas = []
    fila_actual = []
    y_ref = numeros_ordenados[0]['y']
    tolerancia_y = 40  # píxeles
    
    for num in numeros_ordenados:
        if abs(num['y'] - y_ref) <= tolerancia_y:
            fila_actual.append(num)
        else:
            if fila_actual:
                # Ordenar fila por X (columna)
                fila_actual.sort(key=lambda n: n['x'])
                valores_fila = [n['valor'] for n in fila_actual]
                filas.append(valores_fila)
                print(f"  - Fila {len(filas)}: {len(valores_fila)} números → {valores_fila}")
            fila_actual = [num]
            y_ref = num['y']
    
    # Última fila
    if fila_actual:
        fila_actual.sort(key=lambda n: n['x'])
        valores_fila = [n['valor'] for n in fila_actual]
        filas.append(valores_fila)
        print(f"  - Fila {len(filas)}: {len(valores_fila)} números → {valores_fila}")
    
    print(f"✓ Total de filas detectadas: {len(filas)}")
    
    # Buscar dos filas con la misma cantidad de elementos
    for i in range(len(filas)):
        for j in range(i + 1, len(filas)):
            if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                x_vals = filas[i]
                y_vals = filas[j]
                
                # Validar que X no tenga duplicados
                if len(set(x_vals)) == len(x_vals):
                    print(f"✓ Encontradas filas {i+1} y {j+1} con {len(x_vals)} elementos cada una")
                    print(f"  X = {x_vals}")
                    print(f"  Y = {y_vals}")
                    return x_vals, y_vals
    
    # Si no encontramos dos filas iguales, intentar dividir una fila con números pares
    for idx, fila in enumerate(filas):
        if len(fila) >= 4 and len(fila) % 2 == 0:
            mitad = len(fila) // 2
            x_vals = fila[:mitad]
            y_vals = fila[mitad:]
            
            # Validar que X no tenga duplicados
            if len(set(x_vals)) == len(x_vals):
                print(f"✓ Dividiendo fila {idx+1} en dos mitades de {mitad} elementos")
                print(f"  X = {x_vals}")
                print(f"  Y = {y_vals}")
                return x_vals, y_vals
    
    print("✗ No se pudo organizar en X e Y válidos")
    return None, None

def organizar_lista_simple(numeros):
    """
    Organiza una lista simple de números en X e Y
    
    Args:
        numeros: Lista de números
        
    Returns:
        tuple: (x_vals, y_vals) o (None, None)
    """
    print("\n📊 Organizando lista simple de números...")
    print(f"  - Total de números: {len(numeros)}")
    
    if len(numeros) >= 4 and len(numeros) % 2 == 0:
        mitad = len(numeros) // 2
        x_vals = numeros[:mitad]
        y_vals = numeros[mitad:]
        
        # Validar que X no tenga duplicados
        if len(set(x_vals)) == len(x_vals):
            print(f"✓ Dividido en dos mitades de {mitad} elementos")
            print(f"  X = {x_vals}")
            print(f"  Y = {y_vals}")
            return x_vals, y_vals
        else:
            print("✗ X tiene valores duplicados")
    else:
        print("✗ No se puede dividir en dos partes iguales")
    
    return None, None

def leer_tabla_directamente(imagen):
    """
    Lee la tabla directamente de la imagen usando OCR robusto
    
    Args:
        imagen: PIL Image o numpy array
        
    Returns:
        tuple: (x_vals, y_vals) o (None, None)
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO LECTURA DE TABLA")
    print("="*60)
    
    # Verificar disponibilidad de OCR
    if not EASYOCR_AVAILABLE and not PYTESSERACT_AVAILABLE:
        print("✗ ERROR: Ni EasyOCR ni Pytesseract están disponibles")
        print("  Instala al menos uno de ellos:")
        print("  - pip install easyocr")
        print("  - pip install pytesseract")
        return None, None
    
    try:
        # Convertir imagen a numpy array
        if isinstance(imagen, Image.Image):
            img_array = np.array(imagen)
            print(f"✓ Imagen PIL convertida a numpy: {img_array.shape}")
        else:
            img_array = imagen
            print(f"✓ Imagen numpy recibida: {img_array.shape}")
        
        # Preprocesar imagen
        versiones = preprocesar_imagen(img_array)
        
        # Intentar con EasyOCR primero (más robusto)
        numeros_con_pos, version_usada = extraer_con_easyocr(versiones)
        
        if numeros_con_pos:
            # Organizar por posición
            x_vals, y_vals = organizar_por_posicion(numeros_con_pos)
            if x_vals and y_vals:
                print("\n" + "="*60)
                print("✓ ÉXITO: Tabla leída con EasyOCR")
                print(f"  Método: EasyOCR + {version_usada}")
                print(f"  Puntos detectados: {len(x_vals)}")
                print("="*60)
                return x_vals, y_vals
        
        # Fallback: Pytesseract
        numeros_lista = extraer_con_pytesseract(versiones)
        
        if numeros_lista:
            # Organizar lista simple
            x_vals, y_vals = organizar_lista_simple(numeros_lista)
            if x_vals and y_vals:
                print("\n" + "="*60)
                print("✓ ÉXITO: Tabla leída con Pytesseract")
                print(f"  Puntos detectados: {len(x_vals)}")
                print("="*60)
                return x_vals, y_vals
        
        # No se pudo extraer
        print("\n" + "="*60)
        print("✗ FALLO: No se pudo extraer la tabla")
        print("  Sugerencias:")
        print("  - Verifica que la imagen tenga buena calidad")
        print("  - Asegúrate de que los números sean legibles")
        print("  - Intenta con mejor iluminación")
        print("="*60)
        return None, None
    
    except Exception as e:
        print(f"\n✗ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def extraer_de_imagen_rapido(imagen):
    """
    Extracción rápida y directa (wrapper para compatibilidad)
    
    Args:
        imagen: PIL Image o numpy array
        
    Returns:
        tuple: (x_vals, y_vals, exito)
    """
    x, y = leer_tabla_directamente(imagen)
    
    if x and y:
        return x, y, True
    
    return None, None, False
