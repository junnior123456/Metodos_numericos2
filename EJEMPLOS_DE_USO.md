# 📚 Ejemplos de Uso - Interpolación de Newton

## Ejemplo 1: Función Lineal

### Datos
```
X: 0, 1, 2, 3
Y: 1, 3, 5, 7
```

### Resultado Esperado
- **Polinomio:** P(x) = 2x + 1
- **Grado:** 1 (lineal)
- **Error:** ~0 (función exacta)

### Interpretación
Los puntos forman una línea recta perfecta con pendiente 2 y ordenada al origen 1.

---

## Ejemplo 2: Función Cuadrática

### Datos
```
X: 0, 1, 2, 3, 4
Y: 1, 2, 5, 10, 17
```

### Resultado Esperado
- **Polinomio:** P(x) = x² + 1
- **Grado:** 2 (cuadrático)
- **Error:** ~0 (función exacta)

### Interpretación
Los puntos siguen una parábola con vértice en (0, 1).

---

## Ejemplo 3: Función Cúbica

### Datos
```
X: -2, -1, 0, 1, 2
Y: -8, -1, 0, 1, 8
```

### Resultado Esperado
- **Polinomio:** P(x) = x³
- **Grado:** 3 (cúbico)
- **Error:** ~0 (función exacta)

### Interpretación
Los puntos siguen la función cúbica clásica, simétrica respecto al origen.

---

## Ejemplo 4: Datos Experimentales (Exponencial)

### Datos
```
X: 0, 1, 2, 3
Y: 1, 2.7, 7.4, 20.1
```

### Resultado Esperado
- **Polinomio:** P(x) ≈ polinomio de grado 3
- **Aproxima:** e^x
- **Error:** Pequeño dentro del rango

### Interpretación
Interpolación de datos que siguen aproximadamente una función exponencial.

---

## Ejemplo 5: Función Trigonométrica (Seno)

### Datos
```
X: 0, 0.5, 1, 1.5, 2
Y: 0, 0.48, 0.84, 1.0, 0.91
```

### Resultado Esperado
- **Polinomio:** P(x) ≈ polinomio de grado 4
- **Aproxima:** sin(x)
- **Error:** Pequeño dentro del rango

### Interpretación
Interpolación de la función seno en el intervalo [0, 2].

---

## Ejemplo 6: Datos de Temperatura

### Contexto
Temperatura registrada cada hora durante 5 horas.

### Datos
```
X (horas): 0, 1, 2, 3, 4
Y (°C):    20, 22, 25, 23, 21
```

### Uso
- Estimar temperatura a las 2.5 horas
- Predecir temperatura a las 5 horas (extrapolación)

### Resultado
- P(2.5) ≈ 24.1°C (interpolación confiable)
- P(5) ≈ ? (extrapolación, menos confiable)

---

## Ejemplo 7: Crecimiento Poblacional

### Contexto
Población de una ciudad en diferentes años.

### Datos
```
X (año): 2000, 2005, 2010, 2015, 2020
Y (miles): 100, 120, 145, 175, 210
```

### Uso
- Estimar población en 2012
- Proyectar población en 2025

### Consideraciones
- Interpolación (2012): Confiable
- Extrapolación (2025): Usar con precaución

---

## Ejemplo 8: Velocidad vs Tiempo

### Contexto
Velocidad de un vehículo en diferentes instantes.

### Datos
```
X (segundos): 0, 2, 4, 6, 8
Y (m/s):      0, 10, 18, 24, 28
```

### Análisis
- Aceleración no constante
- Polinomio de grado 4
- Útil para calcular velocidad en instantes intermedios

---

## Ejemplo 9: Presión vs Altitud

### Contexto
Presión atmosférica a diferentes altitudes.

### Datos
```
X (km):    0, 1, 2, 3, 4
Y (kPa):   101, 90, 80, 70, 62
```

### Aplicación
- Estimar presión a 2.5 km
- Modelo para sistemas de aviación

---

## Ejemplo 10: Concentración Química

### Contexto
Concentración de un reactivo en el tiempo.

### Datos
```
X (minutos): 0, 5, 10, 15, 20
Y (mol/L):   1.0, 0.8, 0.6, 0.5, 0.4
```

### Análisis
- Decaimiento no lineal
- Interpolación para tiempos intermedios
- Útil en cinética química

---

## 💡 Consejos para Cada Tipo de Datos

### Datos Exactos (Funciones Matemáticas)
- Error esperado: ~0
- Polinomio reproduce la función exactamente
- Ejemplos: 1, 2, 3

### Datos Experimentales
- Error esperado: Pequeño
- Polinomio aproxima la tendencia
- Ejemplos: 4, 5, 6, 7, 8, 9, 10

### Interpolación vs Extrapolación
- **Interpolación** (dentro del rango): Confiable
- **Extrapolación** (fuera del rango): Usar con precaución

### Número de Puntos
- **2-3 puntos:** Polinomio simple (lineal/cuadrático)
- **4-6 puntos:** Polinomio moderado (cúbico/cuártico)
- **7+ puntos:** Polinomio complejo (puede oscilar)

---

## 🎯 Cómo Probar Estos Ejemplos

### Método 1: Entrada Manual
1. Copia los valores de X
2. Copia los valores de Y
3. Pega en la interfaz
4. Calcula

### Método 2: Ejemplos Predefinidos
1. Ve a la pestaña "Ejemplos"
2. Selecciona el ejemplo
3. Usa el ejemplo
4. Calcula

### Método 3: Crear Imagen
1. Escribe los datos en papel
2. Toma una foto
3. Sube la imagen
4. Ingresa manualmente si es necesario

---

## 📊 Interpretación de Resultados

### Tabla de Diferencias Divididas
- **Primera columna:** Valores de Y
- **Columnas siguientes:** Diferencias de orden superior
- **Primera fila:** Coeficientes del polinomio

### Gráfica de Interpolación
- **Línea azul:** Polinomio interpolador
- **Puntos rojos:** Datos originales
- **Estrella verde:** Punto evaluado (si existe)

### Gráfica de Errores
- **Barras:** Error en cada punto
- **Altura:** Magnitud del error
- **Ideal:** Todas las barras cerca de cero

### Gráfica de Coeficientes
- **Escala logarítmica:** Para ver magnitudes relativas
- **Coeficientes grandes:** Mayor influencia
- **Coeficientes pequeños:** Menor influencia

---

## 🔍 Casos Especiales

### Caso 1: Puntos Colineales
```
X: 0, 1, 2
Y: 1, 2, 3
```
**Resultado:** Línea recta (grado 1)

### Caso 2: Puntos en Parábola
```
X: -1, 0, 1
Y: 1, 0, 1
```
**Resultado:** Parábola x² (grado 2)

### Caso 3: Datos Constantes
```
X: 0, 1, 2, 3
Y: 5, 5, 5, 5
```
**Resultado:** Línea horizontal P(x) = 5

### Caso 4: Oscilación
```
X: 0, 1, 2, 3, 4
Y: 0, 1, 0, 1, 0
```
**Resultado:** Polinomio oscilante (grado 4)

---

## ✅ Verificación de Resultados

Para verificar que el polinomio es correcto:

1. **Evalúa en los puntos originales**
   - P(x₀) debe ser ≈ y₀
   - P(x₁) debe ser ≈ y₁
   - etc.

2. **Revisa el grado**
   - Grado = n - 1 (donde n = número de puntos)

3. **Observa la gráfica**
   - El polinomio debe pasar por todos los puntos

4. **Verifica los errores**
   - Deben ser prácticamente cero (~10⁻¹⁵)

---

**¡Experimenta con tus propios datos y descubre el poder de la interpolación de Newton!**
