"""
OCR PROFESIONAL - Perfecciona imagen y extrae números
Funciona con imágenes borrosas, mal iluminadas, etc.
"""
import cv2
import numpy as np
from PIL import Image
import re

def perfeccionar_imagen(img):
    """
    Perfecciona la imagen para OCR óptimo
    """
    print("\n🔧 PERFECCIONANDO IMAGEN...")
    
    # Escala de grises
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # 1. ESCALAR si es pequeña
    h, w = gray.shape
    if h < 600 or w < 600:
        scale = max(600/h, 600/w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        print(f"  ✓ Escalado: {w}x{h} → {gray.shape[1]}x{gray.shape[0]}")
    
    # 2. DENOISE agresivo
    denoised = cv2.fastNlMeansDenoising(gray, None, h=15, templateWindowSize=7, searchWindowSize=21)
    print("  ✓ Ruido eliminado")
    
    # 3. CLAHE (contraste adaptativo)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    print("  ✓ Contraste mejorado")
    
    # 4. SHARPEN (nitidez)
    kernel_sharpen = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
    print("  ✓ Nitidez aumentada")
    
    # 5. THRESHOLD adaptativo
    binary = cv2.adaptiveThreshold(
        sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 3
    )
    print("  ✓ Binarización aplicada")
    
    # 6. MORFOLOGÍA para limpiar
    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    print("  ✓ Morfología aplicada")
    
    return [
        ("Original mejorado", enhanced),
        ("Binarizado", binary),
        ("Limpio", cleaned),
        ("Sharpened", sharpened)
    ]

def extraer_con_easyocr(versiones):
    """
    Extrae con EasyOCR de múltiples versiones
    """
    try:
        import easyocr
        print("\n🔍 EXTRAYENDO CON EASYOCR...")
        
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        
        todos_numeros = []
        
        for nombre, img in versiones:
            print(f"  Procesando: {nombre}")
            
            # Leer con confianza MUY baja para capturar todo
            results = reader.readtext(img, detail=1, paragraph=False, 
                                     min_size=10, text_threshold=0.3)
            
            for (bbox, text, conf) in results:
                # Limpiar texto
                text = text.strip()
                text = text.replace(',', '.')
                text = text.replace('O', '0').replace('o', '0')
                text = text.replace('l', '1').replace('I', '1')
                text = text.replace('S', '5').replace('s', '5')
                
                # Buscar números
                nums = re.findall(r'-?\d+\.?\d*', text)
                
                for n in nums:
                    try:
                        val = float(n)
                        # Posición
                        x = int((bbox[0][0] + bbox[2][0]) / 2)
                        y = int((bbox[0][1] + bbox[2][1]) / 2)
                        
                        # Evitar duplicados cercanos
                        es_duplicado = False
                        for num_existente in todos_numeros:
                            if abs(num_existente['val'] - val) < 0.01 and \
                               abs(num_existente['x'] - x) < 20 and \
                               abs(num_existente['y'] - y) < 20:
                                es_duplicado = True
                                break
                        
                        if not es_duplicado:
                            todos_numeros.append({'val': val, 'x': x, 'y': y, 'conf': conf})
                            print(f"    → {val} en ({x},{y}) conf={conf:.2f}")
                    except:
                        pass
        
        print(f"\n  ✓ Total detectados: {len(todos_numeros)} números")
        return todos_numeros
    
    except Exception as e:
        print(f"  ✗ EasyOCR falló: {e}")
        return []

def extraer_con_pytesseract(versiones):
    """
    Extrae con Pytesseract de múltiples versiones
    """
    try:
        import pytesseract
        print("\n🔍 EXTRAYENDO CON PYTESSERACT...")
        
        todos_numeros = []
        
        configs = [
            '--psm 6 --oem 3',
            '--psm 4 --oem 3',
            '--psm 11 --oem 3'
        ]
        
        for nombre, img in versiones:
            for config in configs:
                try:
                    text = pytesseract.image_to_string(img, config=config)
                    
                    # Limpiar
                    text = text.replace(',', '.')
                    text = text.replace('O', '0').replace('o', '0')
                    text = text.replace('l', '1').replace('I', '1')
                    
                    # Extraer
                    nums = re.findall(r'-?\d+\.?\d*', text)
                    
                    for n in nums:
                        try:
                            val = float(n)
                            if val not in [num['val'] for num in todos_numeros]:
                                todos_numeros.append({'val': val, 'x': 0, 'y': 0, 'conf': 0.5})
                        except:
                            pass
                except:
                    pass
        
        print(f"  ✓ Total detectados: {len(todos_numeros)} números")
        return todos_numeros
    
    except Exception as e:
        print(f"  ✗ Pytesseract falló: {e}")
        return []

def organizar_inteligente(numeros):
    """
    Organiza números de forma inteligente
    """
    print("\n📊 ORGANIZANDO NÚMEROS...")
    
    if len(numeros) < 4:
        print("  ✗ Muy pocos números")
        return None, None
    
    # Si tienen posición, organizar por posición
    if numeros[0]['x'] > 0:
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
                        print(f"\n✓ ENCONTRADO:")
                        print(f"  X = {x_vals}")
                        print(f"  Y = {y_vals}")
                        return x_vals, y_vals
        
        # Dividir primera fila
        if filas and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
            mitad = len(filas[0]) // 2
            x_vals = filas[0][:mitad]
            y_vals = filas[0][mitad:]
            if len(set(x_vals)) == len(x_vals):
                print(f"\n✓ ENCONTRADO (dividiendo fila):")
                print(f"  X = {x_vals}")
                print(f"  Y = {y_vals}")
                return x_vals, y_vals
    
    # Sin posición, dividir lista
    valores = [n['val'] for n in numeros]
    if len(valores) >= 4 and len(valores) % 2 == 0:
        mitad = len(valores) // 2
        x_vals = valores[:mitad]
        y_vals = valores[mitad:]
        if len(set(x_vals)) == len(x_vals):
            print(f"\n✓ ENCONTRADO (lista simple):")
            print(f"  X = {x_vals}")
            print(f"  Y = {y_vals}")
            return x_vals, y_vals
    
    print("  ✗ No se pudo organizar")
    return None, None

def extraer_numeros_profesional(imagen):
    """
    EXTRACCIÓN PROFESIONAL - Funciona con cualquier imagen
    """
    print("\n" + "="*70)
    print("🚀 EXTRACCIÓN PROFESIONAL DE NÚMEROS")
    print("="*70)
    
    # Convertir
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen
    
    # PERFECCIONAR
    versiones = perfeccionar_imagen(img)
    
    # EXTRAER con EasyOCR
    numeros = extraer_con_easyocr(versiones)
    
    # Si no hay suficientes, intentar Pytesseract
    if len(numeros) < 4:
        print("\n⚠️ Pocos números con EasyOCR, intentando Pytesseract...")
        numeros_pyt = extraer_con_pytesseract(versiones)
        numeros.extend(numeros_pyt)
    
    # ORGANIZAR
    x, y = organizar_inteligente(numeros)
    
    if x and y:
        print("\n" + "="*70)
        print("✅ ÉXITO - NÚMEROS EXTRAÍDOS")
        print("="*70)
        return x, y
    else:
        print("\n" + "="*70)
        print("❌ NO SE PUDIERON EXTRAER NÚMEROS")
        print("="*70)
        return None, None
