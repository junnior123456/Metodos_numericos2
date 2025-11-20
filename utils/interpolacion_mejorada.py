"""
Módulo mejorado de interpolación con visualizaciones avanzadas
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sympy as sp
from utils.interpolacion_newton import diferencias_divididas, interpolacion_newton, evaluar_polinomio
from utils.generador_desarrollo import generar_desarrollo_completo, generar_tabla_html, generar_desarrollo_visual
from utils.ocr_profesional import extraer_numeros_profesional
from PIL import Image

def detectar_tabla_y_extraer_datos(imagen):
    """
    Detecta tabla y extrae datos - OCR PROFESIONAL
    Perfecciona imagen primero, luego extrae
    """
    x, y = extraer_numeros_profesional(imagen)
    if x and y:
        return x, y, True
    return None, None, False

def crear_interfaz_interpolacion():
    """
    Crea la interfaz completa de interpolación con carga de imágenes
    """
    st.header("📐 Interpolación de Newton - Versión Avanzada")
    
    # Tabs para diferentes métodos de entrada
    tab1, tab2, tab3 = st.tabs(["📝 Entrada Manual", "📷 Subir Imagen", "📊 Ejemplos"])
    
    x_datos = None
    y_datos = None
    
    # TAB 1: Entrada Manual
    with tab1:
        st.markdown("### 📊 Ingreso Manual de Datos")
        st.info("💡 Ingresa los puntos (x, y) separados por comas")
        
        col1, col2 = st.columns(2)
        with col1:
            x_text = st.text_input("🔢 Valores de X", "0,1,2,3,4", key="x_manual")
        with col2:
            y_text = st.text_input("📈 Valores de Y", "1,2,5,10,17", key="y_manual")
        
        if st.button("✅ Usar estos datos", key="btn_manual"):
            try:
                x_datos = np.array([float(x.strip()) for x in x_text.split(',')])
                y_datos = np.array([float(y.strip()) for y in y_text.split(',')])
                st.session_state['x_datos'] = x_datos
                st.session_state['y_datos'] = y_datos
                st.success(f"✓ {len(x_datos)} puntos cargados correctamente")
            except Exception as e:
                st.error(f"Error al procesar datos: {e}")
    
    # TAB 2: Subir Imagen
    with tab2:
        st.markdown("### 📷 Cargar Ejercicio desde Imagen")
        st.info("📸 Sube una imagen, tómala con la cámara o arrástrala aquí. El sistema intentará extraer los datos automáticamente.")
        
        # Opciones de carga
        col_upload1, col_upload2 = st.columns(2)
        
        with col_upload1:
            uploaded_file = st.file_uploader(
                "📁 Selecciona o arrastra una imagen",
                type=['jpg', 'jpeg', 'png'],
                key="image_upload",
                help="Arrastra y suelta una imagen aquí o haz clic para seleccionar"
            )
        
        with col_upload2:
            camera_photo = st.camera_input(
                "📸 O toma una foto",
                key="camera_input",
                help="Usa tu cámara para capturar el ejercicio"
            )
        
        # Usar la imagen de cámara si existe, sino la subida
        imagen_source = camera_photo if camera_photo is not None else uploaded_file
        
        if imagen_source is not None:
            uploaded_file = imagen_source
        
        if uploaded_file is not None:
            # Mostrar imagen original
            imagen = Image.open(uploaded_file)
            
            # Mostrar solo imagen original
            st.image(imagen, caption="📸 Imagen Cargada", use_column_width=True)
            
            # Análisis INTERNO (sin mostrar procesamiento)
            with st.spinner("🤖 Analizando imagen internamente..."):
                x_ext, y_ext, exito_tabla = detectar_tabla_y_extraer_datos(imagen)
                
                if x_ext and y_ext and len(x_ext) >= 2:
                    st.success(f"✓ Se detectaron {len(x_ext)} puntos automáticamente")
                    
                    # Mostrar puntos detectados en formato visual
                    col_det1, col_det2 = st.columns(2)
                    with col_det1:
                        st.markdown("**Valores de X detectados:**")
                        st.code(", ".join([str(x) for x in x_ext]))
                    with col_det2:
                        st.markdown("**Valores de Y detectados:**")
                        st.code(", ".join([str(y) for y in y_ext]))
                    
                    # Tabla de puntos
                    df_puntos = pd.DataFrame({'X': x_ext, 'Y': y_ext})
                    st.dataframe(df_puntos)
                    
                    # Botones en columnas
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("✅ Usar y Calcular Automáticamente", key="btn_auto_calc", type="primary"):
                            st.session_state['x_datos'] = np.array(x_ext)
                            st.session_state['y_datos'] = np.array(y_ext)
                            st.session_state['calcular_automatico'] = True
                            st.success("✓ Datos cargados y calculando...")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📝 Solo Cargar Datos", key="btn_image"):
                            st.session_state['x_datos'] = np.array(x_ext)
                            st.session_state['y_datos'] = np.array(y_ext)
                            st.session_state['calcular_automatico'] = False
                            st.success("✓ Datos cargados desde imagen")
                            st.rerun()
                else:
                    st.warning("⚠️ No se pudieron detectar puntos automáticamente.")
                    st.info("""
                    **💡 Consejos para mejorar la detección:**
                    - Asegúrate de que la imagen tenga buena iluminación
                    - El texto debe ser claro y legible
                    - Evita imágenes borrosas o con mucho ruido
                    - Los números deben estar bien separados
                    """)
            
            # Opción de entrada manual después de ver la imagen
            st.markdown("---")
            st.markdown("### ✏️ Ingreso Manual de Datos")
            st.info("👀 Observa la imagen arriba e ingresa los datos que veas")
            
            col_x, col_y = st.columns(2)
            with col_x:
                x_manual_img = st.text_input(
                    "🔢 Valores de X (separados por comas)", 
                    key="x_from_img",
                    placeholder="Ej: 0, 1, 2, 3, 4"
                )
            with col_y:
                y_manual_img = st.text_input(
                    "📈 Valores de Y (separados por comas)", 
                    key="y_from_img",
                    placeholder="Ej: 1, 2, 5, 10, 17"
                )
            
            if st.button("✅ Usar estos datos", key="btn_manual_img", type="primary"):
                try:
                    if not x_manual_img or not y_manual_img:
                        st.error("⚠️ Por favor ingresa valores para X e Y")
                    else:
                        x_datos = np.array([float(x.strip()) for x in x_manual_img.split(',')])
                        y_datos = np.array([float(y.strip()) for y in y_manual_img.split(',')])
                        
                        if len(x_datos) != len(y_datos):
                            st.error("⚠️ X e Y deben tener la misma cantidad de valores")
                        elif len(x_datos) < 2:
                            st.error("⚠️ Se necesitan al menos 2 puntos")
                        else:
                            st.session_state['x_datos'] = x_datos
                            st.session_state['y_datos'] = y_datos
                            st.success(f"✓ {len(x_datos)} puntos cargados correctamente")
                            st.rerun()
                except ValueError as e:
                    st.error(f"⚠️ Error: Asegúrate de ingresar solo números separados por comas")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
    
    # TAB 3: Ejemplos
    with tab3:
        st.markdown("### 📚 Ejemplos Predefinidos")
        
        ejemplos = {
            "Ejemplo 1: Lineal": ([0, 1, 2, 3], [1, 3, 5, 7]),
            "Ejemplo 2: Cuadrático": ([0, 1, 2, 3, 4], [1, 2, 5, 10, 17]),
            "Ejemplo 3: Cúbico": ([-2, -1, 0, 1, 2], [-8, -1, 0, 1, 8]),
            "Ejemplo 4: Exponencial": ([0, 1, 2, 3], [1, 2.7, 7.4, 20.1]),
            "Ejemplo 5: Seno": ([0, 0.5, 1, 1.5, 2], [0, 0.48, 0.84, 1.0, 0.91])
        }
        
        ejemplo_seleccionado = st.selectbox("Selecciona un ejemplo:", list(ejemplos.keys()))
        
        x_ej, y_ej = ejemplos[ejemplo_seleccionado]
        
        col_ej1, col_ej2 = st.columns(2)
        with col_ej1:
            st.write("**Valores de X:**", x_ej)
        with col_ej2:
            st.write("**Valores de Y:**", y_ej)
        
        if st.button("✅ Usar este ejemplo", key="btn_ejemplo"):
            st.session_state['x_datos'] = np.array(x_ej)
            st.session_state['y_datos'] = np.array(y_ej)
            st.success(f"✓ Ejemplo cargado: {ejemplo_seleccionado}")
    
    # Verificar si hay datos cargados
    if 'x_datos' in st.session_state and 'y_datos' in st.session_state:
        x_datos = st.session_state['x_datos']
        y_datos = st.session_state['y_datos']
        
        st.markdown("---")
        st.markdown("### 🎯 Datos Actuales")
        
        col_data1, col_data2 = st.columns(2)
        with col_data1:
            st.write("**X:**", x_datos)
        with col_data2:
            st.write("**Y:**", y_datos)
        
        # Opciones de cálculo
        st.markdown("### ⚙️ Opciones de Cálculo")
        
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        
        with col_opt1:
            mostrar_tabla = st.checkbox("📋 Tabla de diferencias", value=True)
            mostrar_pasos = st.checkbox("📝 Pasos detallados", value=True)
        
        with col_opt2:
            mostrar_graficas = st.checkbox("📊 Gráficas interactivas", value=True)
            mostrar_estadisticas = st.checkbox("📈 Estadísticas", value=True)
        
        with col_opt3:
            puntos_grafica = st.slider("Puntos en gráfica", 50, 500, 200)
            evaluar_punto = st.text_input("Evaluar en x =", "")
        
        # Verificar si debe calcular automáticamente
        calcular_auto = st.session_state.get('calcular_automatico', False)
        
        # Botón principal de cálculo
        if st.button("🚀 CALCULAR INTERPOLACIÓN", type="primary") or calcular_auto:
            # Resetear flag de cálculo automático
            if calcular_auto:
                st.session_state['calcular_automatico'] = False
                st.info("🤖 Calculando automáticamente con los datos detectados...")
            
            calcular_y_mostrar_resultados(
                x_datos, y_datos, 
                mostrar_tabla, mostrar_pasos, mostrar_graficas, 
                mostrar_estadisticas, puntos_grafica, evaluar_punto
            )
    else:
        st.info("👆 Selecciona un método de entrada de datos arriba para comenzar")

def calcular_y_mostrar_resultados(x_datos, y_datos, mostrar_tabla, mostrar_pasos, 
                                   mostrar_graficas, mostrar_estadisticas, 
                                   puntos_grafica, evaluar_punto):
    """
    Calcula y muestra todos los resultados de la interpolación
    """
    try:
        # Validaciones
        if len(x_datos) != len(y_datos):
            st.error("⚠️ X e Y deben tener la misma cantidad de elementos")
            return
        if len(x_datos) < 2:
            st.error("⚠️ Se necesitan al menos 2 puntos")
            return
        if len(x_datos) != len(set(x_datos)):
            st.error("⚠️ Los valores de X deben ser únicos")
            return
        
        # Calcular interpolación
        with st.spinner("🔄 Calculando interpolación..."):
            polinomio, tabla, detalles = interpolacion_newton(x_datos, y_datos)
        
        st.success("✅ ¡Interpolación calculada exitosamente!")
        
        # Crear contenedores expandibles para cada sección
        if mostrar_tabla:
            with st.expander("📋 TABLA DE DIFERENCIAS DIVIDIDAS", expanded=True):
                mostrar_tabla_diferencias(x_datos, y_datos, tabla)
        
        if mostrar_pasos:
            with st.expander("📝 CONSTRUCCIÓN PASO A PASO", expanded=True):
                mostrar_construccion_paso_a_paso(tabla, detalles, x_datos)
        
        # Polinomio final
        with st.expander("🎓 POLINOMIO DE INTERPOLACIÓN", expanded=True):
            mostrar_polinomio_final(polinomio)
        
        # Evaluación
        if evaluar_punto:
            with st.expander("🔍 EVALUACIÓN EN PUNTO ESPECÍFICO", expanded=True):
                evaluar_en_punto(polinomio, evaluar_punto, x_datos)
        
        # Gráficas
        if mostrar_graficas:
            with st.expander("📊 VISUALIZACIONES INTERACTIVAS", expanded=True):
                crear_graficas_interactivas(x_datos, y_datos, polinomio, puntos_grafica, evaluar_punto)
        
        # Estadísticas
        if mostrar_estadisticas:
            with st.expander("📈 ESTADÍSTICAS Y ANÁLISIS", expanded=True):
                mostrar_estadisticas_completas(x_datos, y_datos, polinomio, tabla)
        
        # Desarrollo completo tipo libro
        with st.expander("📚 DESARROLLO COMPLETO (Formato Libro de Texto)", expanded=False):
            mostrar_desarrollo_completo_libro(x_datos, y_datos, tabla, polinomio, detalles)
    
    except Exception as e:
        st.error(f"⚠️ Error en el cálculo: {e}")
        st.exception(e)

def mostrar_tabla_diferencias(x_datos, y_datos, tabla):
    """Muestra la tabla de diferencias divididas"""
    n = len(x_datos)
    columnas = ['x', 'f(x)'] + [f'DD{i}' for i in range(1, n)]
    
    tabla_mostrar = np.zeros((n, n+1))
    tabla_mostrar[:, 0] = x_datos
    tabla_mostrar[:, 1:] = tabla
    
    df_tabla = pd.DataFrame(tabla_mostrar, columns=columnas)
    
    st.dataframe(
        df_tabla.style.format("{:.8f}").background_gradient(cmap='RdYlGn', axis=None)
    )
    
    st.markdown("#### 🎯 Coeficientes del Polinomio")
    coeficientes = tabla[0, :]
    cols = st.columns(min(len(coeficientes), 5))
    for i, (col, coef) in enumerate(zip(cols, coeficientes)):
        with col:
            st.metric(f"a{i}", f"{coef:.6f}")

def mostrar_construccion_paso_a_paso(tabla, detalles, x_datos):
    """Muestra la construcción paso a paso del polinomio"""
    st.latex(r"P_n(x) = a_0 + a_1(x-x_0) + a_2(x-x_0)(x-x_1) + \cdots")
    
    st.markdown(f"**Paso 0:** Término constante")
    st.latex(f"P_0(x) = {tabla[0,0]:.8f}")
    
    for i, detalle in enumerate(detalles, 1):
        with st.container():
            st.markdown(f"**Paso {i}:** Agregar término de orden {i}")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"Coeficiente: `{detalle['coeficiente']:.8f}`")
            with col2:
                termino_str = sp.latex(detalle['termino'])
                st.latex(f"+ {termino_str}")

def mostrar_polinomio_final(polinomio):
    """Muestra el polinomio final en diferentes formatos"""
    polinomio_expandido = sp.expand(polinomio)
    polinomio_simplificado = sp.simplify(polinomio_expandido)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Forma Expandida:**")
        st.latex(sp.latex(polinomio_expandido))
    
    with col2:
        st.markdown("**Forma Simplificada:**")
        st.latex(sp.latex(polinomio_simplificado))
    
    st.markdown("**Formato de Texto (copiable):**")
    st.code(str(polinomio_simplificado), language="python")

def evaluar_en_punto(polinomio, punto_str, x_datos):
    """Evalúa el polinomio en un punto específico"""
    try:
        x_eval = float(punto_str)
        y_eval = evaluar_polinomio(polinomio, x_eval)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Punto X", f"{x_eval:.4f}")
        with col2:
            st.metric("Resultado P(x)", f"{y_eval:.8f}")
        with col3:
            if min(x_datos) <= x_eval <= max(x_datos):
                st.success("✓ Interpolación")
            else:
                st.warning("⚠️ Extrapolación")
    
    except ValueError:
        st.error("⚠️ Ingresa un número válido")

def crear_graficas_interactivas(x_datos, y_datos, polinomio, puntos_grafica, evaluar_punto):
    """Crea gráficas interactivas con Plotly"""
    # Generar puntos para la gráfica
    x_min, x_max = min(x_datos), max(x_datos)
    rango = x_max - x_min
    x_plot = np.linspace(x_min - 0.2*rango, x_max + 0.2*rango, puntos_grafica)
    y_plot = evaluar_polinomio(polinomio, x_plot)
    
    # Crear subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Interpolación de Newton', 'Error en Puntos', 
                       'Coeficientes', 'Vista Detallada'),
        specs=[[{'type': 'scatter'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'scatter'}]]
    )
    
    # Gráfica 1: Interpolación principal
    fig.add_trace(
        go.Scatter(x=x_plot, y=y_plot, mode='lines', name='Polinomio',
                  line=dict(color='blue', width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=x_datos, y=y_datos, mode='markers', name='Puntos',
                  marker=dict(size=12, color='red', symbol='circle')),
        row=1, col=1
    )
    
    # Punto de evaluación si existe
    if evaluar_punto:
        try:
            x_eval = float(evaluar_punto)
            y_eval = evaluar_polinomio(polinomio, x_eval)
            fig.add_trace(
                go.Scatter(x=[x_eval], y=[y_eval], mode='markers', name='Evaluación',
                          marker=dict(size=15, color='green', symbol='star')),
                row=1, col=1
            )
        except:
            pass
    
    # Gráfica 2: Errores
    y_interpolados = evaluar_polinomio(polinomio, x_datos)
    errores = np.abs(y_datos - y_interpolados)
    fig.add_trace(
        go.Bar(x=list(range(len(x_datos))), y=errores, name='Error',
              marker_color='coral'),
        row=1, col=2
    )
    
    # Gráfica 3: Coeficientes
    tabla, coeficientes = diferencias_divididas(x_datos, y_datos)
    fig.add_trace(
        go.Bar(x=[f'a{i}' for i in range(len(coeficientes))], 
               y=np.abs(coeficientes), name='Coeficientes',
               marker_color='lightblue'),
        row=2, col=1
    )
    
    # Gráfica 4: Vista detallada
    x_zoom = np.linspace(x_min, x_max, puntos_grafica)
    y_zoom = evaluar_polinomio(polinomio, x_zoom)
    fig.add_trace(
        go.Scatter(x=x_zoom, y=y_zoom, mode='lines', name='Detalle',
                  line=dict(color='purple', width=2), fill='tozeroy'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=x_datos, y=y_datos, mode='markers', name='Puntos',
                  marker=dict(size=10, color='red'), showlegend=False),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="Análisis Completo de Interpolación")
    st.plotly_chart(fig)

def mostrar_estadisticas_completas(x_datos, y_datos, polinomio, tabla):
    """Muestra estadísticas completas del análisis"""
    y_interpolados = evaluar_polinomio(polinomio, x_datos)
    errores = np.abs(y_datos - y_interpolados)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Grado del Polinomio", len(x_datos) - 1)
        st.metric("Número de Puntos", len(x_datos))
    
    with col2:
        st.metric("Error Máximo", f"{np.max(errores):.2e}")
        st.metric("Error Promedio", f"{np.mean(errores):.2e}")
    
    with col3:
        st.metric("Rango de X", f"{max(x_datos) - min(x_datos):.4f}")
        st.metric("Rango de Y", f"{max(y_datos) - min(y_datos):.4f}")
    
    with col4:
        st.metric("Min X", f"{min(x_datos):.4f}")
        st.metric("Max X", f"{max(x_datos):.4f}")
    
    # Tabla de valores interpolados
    st.markdown("### 📊 Tabla de Valores Interpolados")
    n_tabla = min(20, len(x_datos) * 3)
    x_tabla = np.linspace(min(x_datos), max(x_datos), n_tabla)
    y_tabla = evaluar_polinomio(polinomio, x_tabla)
    
    df_valores = pd.DataFrame({
        'X': x_tabla,
        'Y Interpolado': y_tabla
    })
    st.dataframe(df_valores.style.format("{:.6f}"))

def mostrar_desarrollo_completo_libro(x_datos, y_datos, tabla, polinomio, detalles):
    """
    Muestra el desarrollo completo en formato de libro de texto
    """
    st.markdown("### 📖 Desarrollo Completo del Ejercicio")
    st.info("Este es el desarrollo detallado como aparece en los libros de Métodos Numéricos")
    
    # Generar desarrollo en texto
    desarrollo_texto = generar_desarrollo_completo(x_datos, y_datos, tabla, polinomio, detalles)
    
    # Tabs para diferentes formatos
    tab1, tab2, tab3 = st.tabs(["📝 Texto Completo", "📊 Visualización", "🌐 Tabla HTML"])
    
    with tab1:
        st.markdown("#### Desarrollo Paso a Paso")
        st.text_area(
            "Desarrollo completo (puedes copiar todo el texto)",
            desarrollo_texto,
            height=600,
            key="desarrollo_completo"
        )
        
        # Botón para descargar
        st.download_button(
            label="📥 Descargar Desarrollo Completo (.txt)",
            data=desarrollo_texto,
            file_name="desarrollo_interpolacion_newton.txt",
            mime="text/plain"
        )
    
    with tab2:
        st.markdown("#### Visualización Gráfica del Desarrollo")
        
        try:
            fig_desarrollo = generar_desarrollo_visual(x_datos, y_datos, tabla, polinomio)
            st.pyplot(fig_desarrollo)
            
            # Guardar figura
            import io
            buf = io.BytesIO()
            fig_desarrollo.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="📥 Descargar Visualización (.png)",
                data=buf,
                file_name="desarrollo_visual_newton.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Error al generar visualización: {e}")
    
    with tab3:
        st.markdown("#### Tabla de Diferencias Divididas (HTML)")
        
        tabla_html = generar_tabla_html(x_datos, y_datos, tabla)
        st.markdown(tabla_html, unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Descargar Tabla HTML",
            data=tabla_html,
            file_name="tabla_diferencias_divididas.html",
            mime="text/html"
        )
    
    # Sección de ejemplo de evaluación
    st.markdown("---")
    st.markdown("### 🎯 Ejemplo de Evaluación Completa")
    
    col_eval1, col_eval2 = st.columns(2)
    
    with col_eval1:
        st.markdown("#### Evaluación en x = 2.1")
        st.markdown("**Usando diferentes grados del polinomio:**")
        
        from utils.interpolacion_newton import interpolacion_newton as interp_newton
        
        for grado in range(1, min(4, len(x_datos))):
            x_temp = x_datos[:grado+1]
            y_temp = y_datos[:grado+1]
            poli_temp, _, _ = interp_newton(x_temp, y_temp)
            resultado = evaluar_polinomio(poli_temp, 2.1)
            st.write(f"**P{grado}(2.1)** = {resultado:.10f}")
    
    with col_eval2:
        st.markdown("#### Resultado Final")
        resultado_final = evaluar_polinomio(polinomio, 2.1)
        st.success(f"**P{len(x_datos)-1}(2.1) = {resultado_final:.10f}**")
        
        st.markdown("**Interpretación:**")
        st.write(f"El valor interpolado en x = 2.1 es aproximadamente {resultado_final:.6f}")
        
        if min(x_datos) <= 2.1 <= max(x_datos):
            st.info("✓ Este valor está dentro del rango de interpolación (confiable)")
        else:
            st.warning("⚠️ Este valor está fuera del rango (extrapolación)")
    
    # Notas finales
    st.markdown("---")
    st.markdown("### 📌 Notas Importantes")
    
    col_nota1, col_nota2 = st.columns(2)
    
    with col_nota1:
        st.markdown("""
        **Ventajas del Método de Newton:**
        - Fácil de implementar
        - Permite agregar puntos sin recalcular todo
        - Útil para interpolación incremental
        - Buena estabilidad numérica
        """)
    
    with col_nota2:
        st.markdown("""
        **Consideraciones:**
        - El error es cero en los puntos dados
        - Mayor precisión dentro del rango
        - Polinomios de alto grado pueden oscilar
        - Usar con precaución fuera del rango
        """)
