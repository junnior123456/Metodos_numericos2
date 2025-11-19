# 🧮 Sistema de Métodos Numéricos - Interpolación de Newton

## 🎯 Descripción

Sistema completo de métodos numéricos con énfasis en **Interpolación de Newton**, que incluye carga de imágenes, procesamiento automático, visualizaciones interactivas y resultados detallados.

## ✨ Características Principales

### 📷 Carga de Datos Múltiple
- **Arrastrar y soltar** imágenes
- **Seleccionar archivo** desde explorador
- **Tomar foto** con cámara del dispositivo
- **Entrada manual** tradicional
- **Ejemplos predefinidos** listos para usar

### 🤖 Procesamiento Inteligente
- Mejora automática de imágenes
- Extracción de datos con múltiples patrones
- Validaciones robustas
- Sugerencias cuando falla la detección

### 📊 Visualizaciones Avanzadas
- **4 gráficas interactivas** con Plotly
- Zoom, pan y hover
- Tablas con gradientes de color
- Fórmulas matemáticas en LaTeX

### 📝 Resultados Detallados
- Tabla de diferencias divididas
- Construcción paso a paso
- Polinomio en múltiples formatos
- Evaluación en puntos específicos
- Estadísticas completas

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar Aplicación
```bash
streamlit run app.py
```

### 3. Abrir en Navegador
```
http://localhost:8501
```

## 📖 Documentación

- **[INSTRUCCIONES_USO.md](INSTRUCCIONES_USO.md)** - Guía completa de usuario
- **[EJEMPLOS_DE_USO.md](EJEMPLOS_DE_USO.md)** - 10 ejemplos prácticos
- **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)** - Documentación técnica
- **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** - Resumen ejecutivo

## 🎓 Métodos Disponibles

1. **Interpolación de Newton** ⭐ (Versión Avanzada)
   - Carga de imágenes
   - Procesamiento automático
   - Visualizaciones interactivas

2. **Descomposición LU**
   - Resolución de sistemas lineales
   - Visualización de matrices

3. **Cholesky**
   - Matrices simétricas definidas positivas
   - Verificación automática

4. **Eliminación Gaussiana**
   - Paso a paso interactivo
   - Visualización de transformaciones

5. **Gauss-Jordan**
   - Reducción completa
   - Forma escalonada reducida

## 💻 Tecnologías

- **Python 3.11**
- **Streamlit** - Framework web
- **Plotly** - Gráficas interactivas
- **OpenCV** - Procesamiento de imágenes
- **NumPy** - Cálculos numéricos
- **SymPy** - Matemática simbólica
- **Pandas** - Manejo de datos

## 📦 Dependencias

```
streamlit==1.50.0
numpy==2.2.6
matplotlib==3.10.7
sympy==1.14.0
pillow==11.3.0
pytesseract==0.3.13
opencv-python==4.10.0.84
pandas==2.3.3
plotly==5.24.1
scipy==1.15.2
```

## 🎯 Casos de Uso

### Estudiantes
- Resolver tareas de métodos numéricos
- Verificar resultados de ejercicios
- Aprender paso a paso

### Profesores
- Demostrar conceptos en clase
- Generar ejemplos visuales
- Evaluar comprensión

### Profesionales
- Análisis de datos experimentales
- Interpolación de mediciones
- Modelado matemático

## 📱 Compatibilidad

- ✅ Windows, Mac, Linux
- ✅ Navegadores modernos
- ✅ Dispositivos móviles
- ✅ Tablets

## 🎨 Capturas de Pantalla

### Interfaz Principal
- Diseño oscuro elegante
- Menú lateral organizado
- Pestañas intuitivas

### Carga de Imágenes
- Arrastrar y soltar
- Botón de cámara
- Visualización comparativa

### Resultados
- Gráficas interactivas
- Tablas coloreadas
- Métricas destacadas

## 🔧 Estructura del Proyecto

```
metodos_numericos/
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias
├── utils/
│   ├── interpolacion_newton.py     # Cálculos de Newton
│   ├── interpolacion_mejorada.py   # Interfaz mejorada
│   └── image_processor.py          # Procesamiento de imágenes
├── images/                         # Imágenes de la interfaz
├── INSTRUCCIONES_USO.md           # Guía de usuario
├── EJEMPLOS_DE_USO.md             # Ejemplos prácticos
├── MEJORAS_IMPLEMENTADAS.md       # Documentación técnica
├── RESUMEN_FINAL.md               # Resumen ejecutivo
└── README.md                       # Este archivo
```

## 🎓 Ejemplos Rápidos

### Ejemplo 1: Función Cuadrática
```
X: 0, 1, 2, 3, 4
Y: 1, 2, 5, 10, 17
Resultado: P(x) = x² + 1
```

### Ejemplo 2: Función Lineal
```
X: 0, 1, 2, 3
Y: 1, 3, 5, 7
Resultado: P(x) = 2x + 1
```

### Ejemplo 3: Función Cúbica
```
X: -2, -1, 0, 1, 2
Y: -8, -1, 0, 1, 8
Resultado: P(x) = x³
```

## 🤝 Contribuciones

Este proyecto fue desarrollado como parte del curso de Métodos Numéricos.

**Equipo de Desarrollo:**
- Junnior Chinchay
- Alice Saboya
- Jannpier García

## 📄 Licencia

Proyecto educativo - Universidad [Nombre]
Curso: Métodos Numéricos
Ciclo: VI - 2025-II

## 🆘 Soporte

### Problemas Comunes

**P: No se detectan datos de la imagen**
- R: Ingresa los datos manualmente en los campos disponibles

**P: Error al calcular**
- R: Verifica que X e Y tengan la misma cantidad de valores

**P: Valores de X repetidos**
- R: Los valores de X deben ser únicos

### Contacto

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

## 🎉 Agradecimientos

- Profesor del curso de Métodos Numéricos
- Comunidad de Streamlit
- Documentación de NumPy y SymPy

---

## 🚀 ¡Comienza Ahora!

```bash
# 1. Clonar o descargar el proyecto
# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
streamlit run app.py

# 4. Abrir navegador en http://localhost:8501
```

---

**Versión:** 2.0 - Edición Avanzada con Reconocimiento de Imágenes
**Última actualización:** Noviembre 19, 2025
**Estado:** ✅ Producción - Totalmente Funcional
