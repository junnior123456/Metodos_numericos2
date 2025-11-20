"""
OCR ULTRA ROBUSTO - Funciona con CUALQUIER imagen
Múltiples técnicas de perfeccionamiento y extracción
"""
import cv2
import numpy as np
from PIL import Image
import re

def perfeccionar_ultra(img):
    """
    Perfeccionamiento ULTRA agresivo
    """
    print("\n🔧 PERFECCIONAMIENTO ULTRA...")
    
    # Escala de grises
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # ESCALAR GRANDE (800px mínimo)
    h, w = gray.shape
    if h < 800 or w < 800:
        scale = max(800/h, 800/w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        print(f"  ✓ Escalado: {w}x{h} → {gray.shape[1]}x{gray.shape[0]}")
    
    versiones = []
    
    # VERSIÓN 1: Denoise + CLAHE + Sharpen
    denoised = cv2.fastNlMeansDenoising(gray, None, h=20, templateWindowSize=7, searchWindowSize=21)
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    kernel_sharpen = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
    v1 = cv2.filter2D(enhanced, -1, kernel_sharpen)
    versiones.append(("Ultra Enhanced", v1))
    
    # VERSIÓN 2: Threshold Otsu
    _, v2 = cv2.threshold(v1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    versiones.append(("Otsu", v2))
    
    # VERSIÓN 3: Threshold Adaptativo
    v3 = cv2.adaptiveThreshold(v1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5)
    versiones.append(("Adaptativo", v3))
    
    # VERSIÓN 4: Invertido
    v4 = cv2.bitwise_not(v3)
    versiones.append(("Invertido", v4))
    
    # VERSIÓN 5: Morfología agresiva
    kernel = np.ones((3,3), np.uint8)
    v5 = cv2.morphologyEx(v2, cv2.MORPH_CLOSE, kernel, iterations=2)
    v5 = cv2.morphologyEx(v5, cv2.MORPH_OPEN, kernel, iterations=1)
    versiones.append(("Morfología", v5))
    
    # VERSIÓN 6: Bilateral Filter + Threshold
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    _, v6 = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    versiones.append(("Bilateral", v6))
    
    # VERSIÓN 7: Erosión + Dilatación
    v7 = cv2.erode(v2, kernel, iterations=1)
    v7 = cv2.dilate(v7, kernel, iterations=1)
    versiones.append(("Erosión-Dilatación", v7))
    
    # VERSIÓN 8: Original mejorado
    versiones.append(("Original Mejorado", enhanced))
    
    print(f"  ✓ {len(versiones)} versiones generadas")
    return versiones

def limpiar_texto_agresivo(text):
    """
    Limpieza AGRESIVA de texto OCR
    """
    # Reemplazos comunes
    replacements = {
        ',': '.', 'O': '0', 'o': '0', 'l': '1', 'I': '1', 
        'S': '5', 's': '5', 'Z': '2', 'z': '2', 'B': '8',
        'G': '6', 'T': '7', '|': '1', 'i': '1', 'D': '0'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def extraer_con_easyocr_ultra(versiones):
    """
    EasyOCR ULTRA con todas las versiones
    """
    try:
        import easyocr
        print("\n🔍 EASYOCR ULTRA...")
        
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        todos = []
        
        for nombre, img in versiones:
            print(f"  Procesando: {nombre}")
            
            # Múltiples configuraciones
            configs = [
                {'detail': 1, 'paragraph': False, 'min_size': 5, 'text_threshold': 0.2},
                {'detail': 1, 'paragraph': False, 'min_size': 10, 'text_threshold': 0.3},
                {'detail': 1, 'paragraph': True, 'min_size': 5, 'text_threshold': 0.2},
            ]
            
            for config in configs:
                try:
                    results = reader.readtext(img, **config)
                    
                    for (bbox, text, conf) in results:
                        text = limpiar_texto_agresivo(text.strip())
                        nums = re.findall(r'-?\d+\.?\d*', text)
                        
                        for n in nums:
                            try:
                                val = float(n)
                                x = int((bbox[0][0] + bbox[2][0]) / 2)
                                y = int((bbox[0][1] + bbox[2][1]) / 2)
                                
                                # Evitar duplicados
                                es_dup = False
                                for t in todos:
                                    if abs(t['val'] - val) < 0.01 and abs(t['x'] - x) < 30 and abs(t['y'] - y) < 30:
                                        es_dup = True
                                        break
                                
                                if not es_dup:
                                    todos.append({'val': val, 'x': x, 'y': y, 'conf': conf})
                                    print(f"    → {val}")
                            except:
                                pass
                except:
                    pass
        
        print(f"  ✓ Total: {len(todos)} números")
        return todos
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def extraer_con_pytesseract_ultra(versiones):
    """
    Pytesseract ULTRA con todas las versiones
    """
    try:
        import pytesseract
        print("\n🔍 PYTESSERACT ULTRA...")
        
        todos = []
        
        configs = [
            '--psm 6 --oem 3',
            '--psm 4 --oem 3',
            '--psm 11 --oem 3',
            '--psm 12 --oem 3',
            '--psm 3 --oem 3',
        ]
        
        for nombre, img in versiones:
            for config in configs:
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    text = limpiar_texto_agresivo(text)
                    nums = re.findall(r'-?\d+\.?\d*', text)
                    
                    for n in nums:
                        try:
                            val = float(n)
                            if not any(abs(t['val'] - val) < 0.01 for t in todos):
                                todos.append({'val': val, 'x': 0, 'y': 0, 'conf': 0.5})
                        except:
                            pass
                except:
                    pass
        
        print(f"  ✓ Total: {len(todos)} números")
        return todos
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

def organizar_ultra(numeros):
    """
    Organización ULTRA inteligente
    """
    print("\n📊 ORGANIZACIÓN ULTRA...")
    
    if len(numeros) < 4:
        print("  ✗ Muy pocos números")
        return None, None
    
    # Eliminar duplicados exactos
    unicos = []
    for num in numeros:
        if not any(abs(u['val'] - num['val']) < 0.001 for u in unicos):
            unicos.append(num)
    
    print(f"  Números únicos: {len(unicos)}")
    
    # Si tienen posición válida
    if unicos[0]['x'] > 0:
        # Ordenar por Y
        unicos.sort(key=lambda n: n['y'])
        
        # Agrupar en filas
        filas = []
        fila = []
        y_ref = unicos[0]['y']
        
        for num in unicos:
            if abs(num['y'] - y_ref) < 50:
                fila.append(num)
            else:
                if fila:
                    fila.sort(key=lambda n: n['x'])
                    filas.append([n['val'] for n in fila])
                    print(f"  Fila {len(filas)}: {filas[-1]}")
                fila = [num]
                y_ref = num['y']
        
        if fila:
            fila.sort(key=lambda n: n['x'])
            filas.append([n['val'] for n in fila])
            print(f"  Fila {len(filas)}: {filas[-1]}")
        
        # Buscar dos filas iguales
        for i in range(len(filas)):
            for j in range(i+1, len(filas)):
                if len(filas[i]) == len(filas[j]) and len(filas[i]) >= 2:
                    x_vals = filas[i]
                    y_vals = filas[j]
                    if len(set(x_vals)) == len(x_vals):
                        print(f"\n✓ X = {x_vals}")
                        print(f"✓ Y = {y_vals}")
                        return x_vals, y_vals
        
        # Dividir fila con números pares
        for fila in filas:
            if len(fila) >= 4 and len(fila) % 2 == 0:
                mitad = len(fila) // 2
                x_vals = fila[:mitad]
                y_vals = fila[mitad:]
                if len(set(x_vals)) == len(x_vals):
                    print(f"\n✓ X = {x_vals}")
                    print(f"✓ Y = {y_vals}")
                    return x_vals, y_vals
    
    # Sin posición, dividir lista
    valores = [n['val'] for n in unicos]
    if len(valores) >= 4 and len(valores) % 2 == 0:
        mitad = len(valores) // 2
        x_vals = valores[:mitad]
        y_vals = valores[mitad:]
        if len(set(x_vals)) == len(x_vals):
            print(f"\n✓ X = {x_vals}")
            print(f"✓ Y = {y_vals}")
            return x_vals, y_vals
    
    print("  ✗ No se pudo organizar")
    return None, None

def extraer_numeros_ultra(imagen):
    """
    EXTRACCIÓN ULTRA - Funciona con CUALQUIER imagen
    """
    print("\n" + "="*70)
    print("🚀 EXTRACCIÓN ULTRA ROBUSTA")
    print("="*70)
    
    # Convertir
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen
    
    # PERFECCIONAR
    versiones = perfeccionar_ultra(img)
    
    # EXTRAER con EasyOCR
    numeros = extraer_con_easyocr_ultra(versiones)
    
    # Si no hay suficientes, Pytesseract
    if len(numeros) < 4:
        print("\n⚠️ Complementando con Pytesseract...")
        numeros_pyt = extraer_con_pytesseract_ultra(versiones)
        numeros.extend(numeros_pyt)
    
    # ORGANIZAR
    x, y = organizar_ultra(numeros)
    
    if x and y:
        print("\n" + "="*70)
        print("✅ ÉXITO")
        print("="*70)
        return x, y
    else:
        print("\n" + "="*70)
        print("❌ FALLO")
        print("="*70)
        return None, None
