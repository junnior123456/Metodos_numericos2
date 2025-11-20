"""
Lector directo de tablas - versión robusta
Lee la tabla de la imagen y extrae X e Y sin reventarse con errores
"""
import cv2
import numpy as np
from PIL import Image
import re

# ===================== HELPERS GENERALES ===================== #

def _to_gray(imagen):
    """Convierte lo que sea (PIL / np.array / BGR / RGB) a escala de grises."""
    if isinstance(imagen, Image.Image):
        img = np.array(imagen)
    else:
        img = imagen

    if img is None:
        return None

    # Si viene en BGR (típico de OpenCV) o RGB
    if len(img.shape) == 3:
        # Intento detectar si es BGR o RGB (no es crítico para gray)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.shape[2] == 3 else cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    else:
        gray = img.copy()

    return gray


def _normalizar_numero(txt):
    """
    De un texto, toma el primer número que encuentre (con coma o punto) y lo convierte a float.
    Devuelve None si no puede.
    """
    if not txt:
        return None

    # Aceptar números con signo, comas o puntos
    nums = re.findall(r'-?\d+[.,]?\d*', txt)
    if not nums:
        return None

    n = nums[0].replace(',', '.')  # coma decimal -> punto
    try:
        return float(n)
    except ValueError:
        return None


def _agrupar_en_filas(numeros_con_pos, altura_img):
    """
    numeros_con_pos: lista de (x, y, valor)
    Agrupa por filas usando Y y devuelve dos listas X, Y si puede.
    """
    if not numeros_con_pos:
        return None, None

    # Orden por Y luego X
    datos = sorted(numeros_con_pos, key=lambda d: (d[1], d[0]))

    filas = []
    fila_actual = []
    y_anterior = None

    # Tolerancia vertical según tamaño de imagen
    # (para fotos grandes permite más variación de píxeles)
    tolerancia_y = max(10, int(0.04 * altura_img))

    for x, y, v in datos:
        if y_anterior is None:
            fila_actual = [(x, y, v)]
            y_anterior = y
            continue

        if abs(y - y_anterior) > tolerancia_y:
            # Cierra fila anterior
            if fila_actual:
                fila_actual.sort(key=lambda t: t[0])  # ordenar por X
                filas.append([val[2] for val in fila_actual])
            fila_actual = [(x, y, v)]
            y_anterior = y
        else:
            fila_actual.append((x, y, v))

    # Última fila
    if fila_actual:
        fila_actual.sort(key=lambda t: t[0])
        filas.append([val[2] for val in fila_actual])

    if len(filas) == 0:
        return None, None

    # 1) Buscar dos filas con misma cantidad de elementos
    if len(filas) >= 2:
        for i in range(len(filas) - 1):
            if len(filas[i]) == len(filas[i+1]) and len(filas[i]) >= 2:
                return filas[i], filas[i+1]

    # 2) Si hay muchas filas, tomar las dos más largas
    if len(filas) >= 2:
        filas_ordenadas = sorted(filas, key=lambda f: len(f), reverse=True)
        if len(filas_ordenadas[0]) >= 2 and len(filas_ordenadas[1]) >= 2:
            n = min(len(filas_ordenadas[0]), len(filas_ordenadas[1]))
            return filas_ordenadas[0][:n], filas_ordenadas[1][:n]

    # 3) Si solo hay una fila y tiene cantidad par, partir a la mitad
    if len(filas) == 1 and len(filas[0]) >= 4 and len(filas[0]) % 2 == 0:
        mitad = len(filas[0]) // 2
        return filas[0][:mitad], filas[0][mitad:]

    return None, None

# ===================== OCR CON EASYOCR ===================== #

def _extraer_con_easyocr(gray):
    """
    Intenta leer números con EasyOCR, devolviendo lista (x, y, valor).
    """
    try:
        import easyocr
    except ImportError:
        return []

    try:
        reader = easyocr.Reader(['es', 'en'], gpu=False, verbose=False)
        # Para mejorar: agrandamos un poco la imagen si es muy pequeña
        h, w = gray.shape
        escala = 2 if max(h, w) < 600 else 1
        if escala > 1:
            gray_proc = cv2.resize(gray, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
        else:
            gray_proc = gray

        results = reader.readtext(gray_proc)

        numeros = []
        for (bbox, text, prob) in results:
            valor = _normalizar_numero(text)
            if valor is None:
                continue

            # bbox: [ [x0,y0], [x1,y1], ... ]
            x_pos = int(bbox[0][0] / escala)
            y_pos = int(bbox[0][1] / escala)
            numeros.append((x_pos, y_pos, valor))

        return numeros
    except Exception as e:
        # Si EasyOCR falla, no reventamos
        # print(f"EasyOCR error: {e}")
        return []

# ===================== OCR CON TESSERACT ===================== #

def _extraer_con_tesseract(gray):
    """
    Intenta leer números con Tesseract, devolviendo lista (x, y, valor).
    No usa posiciones exactas de cada número (más débil),
    así que devolvemos solo lista lineal y luego partimos.
    """
    try:
        import pytesseract
    except ImportError:
        return []

    try:
        # Varias versiones preprocesadas
        versiones = []

        # Original
        versiones.append(gray)

        # Otsu
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        versiones.append(otsu)

        # Invertido
        versiones.append(cv2.bitwise_not(otsu))

        configs = [
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,-',
            r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789.,-',
        ]

        mejor = []
        for v in versiones:
            for c in configs:
                txt = pytesseract.image_to_string(v, config=c)
                nums = re.findall(r'-?\d+[.,]?\d*', txt)
                valores = []
                for n in nums:
                    n = n.replace(',', '.')
                    try:
                        valores.append(float(n))
                    except ValueError:
                        continue

                if len(valores) > len(mejor):
                    mejor = valores

        # Convertimos lista lineal en "pseudo posiciones" lineales
        # (sin X,Y reales, pero al menos no generamos error)
        numeros_con_pos = []
        for i, v in enumerate(mejor):
            numeros_con_pos.append((i * 10, 0, v))  # X artificial, Y mismo

        return numeros_con_pos
    except Exception as e:
        # print(f"Tesseract error: {e}")
        return []

# ===================== API PRINCIPAL ===================== #

def leer_tabla_directamente(imagen):
    """
    Lee la tabla directamente de la imagen.
    Retorna listas X, Y o (None, None) si no se pudo.
    """
    gray = _to_gray(imagen)
    if gray is None:
        return None, None

    h, w = gray.shape

    # 1) EasyOCR con posiciones reales
    numeros_con_pos = _extraer_con_easyocr(gray)

    # 2) Si EasyOCR no devuelve suficientes números, usar Tesseract como refuerzo
    if len(numeros_con_pos) < 4:
        numeros_tess = _extraer_con_tesseract(gray)
        # Si EasyOCR devolvió algo, mezclamos
        if numeros_con_pos and numeros_tess:
            # Nos quedamos con los valores de ambos (prioridad EasyOCR)
            # Solo añadimos de Tesseract si son "nuevos"
            valores_existentes = {round(v, 6) for _, _, v in numeros_con_pos}
            offset_y = h // 2  # poner los de Tesseract en otra "fila"
            for i, (_, _, v) in enumerate(numeros_tess):
                if round(v, 6) not in valores_existentes:
                    numeros_con_pos.append((i * 10, offset_y, v))
        elif numeros_tess:
            numeros_con_pos = numeros_tess

    if len(numeros_con_pos) < 4:
        # No hay suficientes números para formar X e Y
        return None, None

    X, Y = _agrupar_en_filas(numeros_con_pos, altura_img=h)
    return X, Y


def extraer_de_imagen_rapido(imagen):
    """
    Wrapper rápido: intenta extraer, y siempre devuelve algo manejable.
    """
    x, y = leer_tabla_directamente(imagen)

    if x is not None and y is not None and len(x) >= 2 and len(y) >= 2:
        return x, y, True

    return None, None, False
