"""
Módulo para generar desarrollo completo de ejercicios de interpolación
Similar al formato de libros de texto
"""
import numpy as np
import pandas as pd
import sympy as sp
import matplotlib.pyplot as plt

def generar_desarrollo_completo(x_datos, y_datos, tabla_dd, polinomio, detalles):
    """
    Genera un desarrollo completo del ejercicio en formato texto
    """
    desarrollo = []
    
    # Encabezado
    desarrollo.append("=" * 80)
    desarrollo.append("POLINOMIO INTERPOLANTE DE NEWTON")
    desarrollo.append("Desarrollo Completo del Ejercicio")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    # Datos del problema
    desarrollo.append("📊 DATOS DEL PROBLEMA")
    desarrollo.append("-" * 80)
    desarrollo.append("")
    desarrollo.append(f"Número de puntos: {len(x_datos)}")
    desarrollo.append(f"Grado del polinomio: {len(x_datos) - 1}")
    desarrollo.append("")
    
    # Tabla de datos
    desarrollo.append("Tabla de datos:")
    desarrollo.append("")
    for i, (x, y) in enumerate(zip(x_datos, y_datos)):
        desarrollo.append(f"  x{i} = {x:>10.6f}    f(x{i}) = {y:>10.6f}")
    desarrollo.append("")
    
    # Objetivo
    desarrollo.append("Objetivo: Obtener una aproximación de f(2.1) usando los datos dados.")
    desarrollo.append("Usar polinomios interpolantes de Newton de grado uno, dos y tres más.")
    desarrollo.append("")
    
    # Tabla de diferencias divididas
    desarrollo.append("=" * 80)
    desarrollo.append("📋 TABLA DE DIFERENCIAS DIVIDIDAS")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    n = len(x_datos)
    
    # Encabezados
    header = "i    xi         f(xi)      "
    for j in range(1, n):
        header += f"f[x{j-1}...x{j}]".ljust(15)
    desarrollo.append(header)
    desarrollo.append("-" * len(header))
    
    # Filas de la tabla
    for i in range(n):
        fila = f"{i}    {x_datos[i]:<10.6f} {tabla_dd[i, 0]:<10.6f} "
        for j in range(1, n):
            if i + j < n:
                valor = tabla_dd[i, j]
                fila += f"{valor:<15.6f}"
            else:
                fila += " " * 15
        desarrollo.append(fila)
    desarrollo.append("")
    
    # Coeficientes
    desarrollo.append("Coeficientes del polinomio de Newton:")
    coeficientes = tabla_dd[0, :]
    for i, coef in enumerate(coeficientes):
        desarrollo.append(f"  a{i} = {coef:.10f}")
    desarrollo.append("")
    
    # Fórmula general
    desarrollo.append("=" * 80)
    desarrollo.append("📐 FÓRMULA GENERAL DEL POLINOMIO DE NEWTON")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    desarrollo.append("Pn(x) = f[x0] + f[x0,x1](x-x0) + f[x0,x1,x2](x-x0)(x-x1) + ...")
    desarrollo.append("        + f[x0,x1,...,xn](x-x0)(x-x1)...(x-xn-1)")
    desarrollo.append("")
    
    # Construcción paso a paso
    desarrollo.append("=" * 80)
    desarrollo.append("🔨 CONSTRUCCIÓN PASO A PASO")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    # P0(x)
    desarrollo.append(f"Paso 0: Polinomio de grado 0")
    desarrollo.append(f"  P0(x) = {coeficientes[0]:.10f}")
    desarrollo.append("")
    
    # Construcción incremental
    polinomio_actual = f"{coeficientes[0]:.6f}"
    
    for i in range(1, min(len(coeficientes), len(x_datos))):
        desarrollo.append(f"Paso {i}: Polinomio de grado {i}")
        
        # Construir el término
        termino_producto = ""
        for j in range(i):
            if j == 0:
                termino_producto = f"(x - {x_datos[j]:.6f})"
            else:
                termino_producto += f"(x - {x_datos[j]:.6f})"
        
        desarrollo.append(f"  Término a agregar: {coeficientes[i]:.10f} × {termino_producto}")
        
        # Expandir el término
        x = sp.Symbol('x')
        termino_sym = coeficientes[i]
        for j in range(i):
            termino_sym *= (x - x_datos[j])
        termino_expandido = sp.expand(termino_sym)
        
        desarrollo.append(f"  Expandido: {termino_expandido}")
        desarrollo.append(f"  P{i}(x) = P{i-1}(x) + {termino_expandido}")
        desarrollo.append("")
    
    # Polinomio final
    desarrollo.append("=" * 80)
    desarrollo.append("🎯 POLINOMIO FINAL")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    polinomio_expandido = sp.expand(polinomio)
    desarrollo.append("Forma expandida:")
    desarrollo.append(f"  P(x) = {polinomio_expandido}")
    desarrollo.append("")
    
    polinomio_simplificado = sp.simplify(polinomio_expandido)
    desarrollo.append("Forma simplificada:")
    desarrollo.append(f"  P(x) = {polinomio_simplificado}")
    desarrollo.append("")
    
    # Evaluaciones
    desarrollo.append("=" * 80)
    desarrollo.append("🔍 EVALUACIONES Y RESULTADOS")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    # Evaluar en diferentes grados
    from utils.interpolacion_newton import evaluar_polinomio
    
    desarrollo.append("Evaluación en x = 2.1 con diferentes grados:")
    desarrollo.append("")
    
    for grado in range(1, min(4, len(x_datos))):
        # Construir polinomio de ese grado
        x_temp = x_datos[:grado+1]
        y_temp = y_datos[:grado+1]
        
        from utils.interpolacion_newton import interpolacion_newton
        poli_temp, _, _ = interpolacion_newton(x_temp, y_temp)
        
        resultado = evaluar_polinomio(poli_temp, 2.1)
        desarrollo.append(f"  P{grado}(2.1) = {resultado:.10f}")
    
    desarrollo.append("")
    
    # Evaluación final
    resultado_final = evaluar_polinomio(polinomio, 2.1)
    desarrollo.append(f"Resultado final con polinomio completo:")
    desarrollo.append(f"  P{len(x_datos)-1}(2.1) = {resultado_final:.10f}")
    desarrollo.append("")
    
    # Verificación en puntos originales
    desarrollo.append("=" * 80)
    desarrollo.append("✅ VERIFICACIÓN EN PUNTOS ORIGINALES")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    
    desarrollo.append("El polinomio debe pasar exactamente por todos los puntos dados:")
    desarrollo.append("")
    
    for i, (x, y) in enumerate(zip(x_datos, y_datos)):
        y_calc = evaluar_polinomio(polinomio, x)
        error = abs(y - y_calc)
        desarrollo.append(f"  P({x:.6f}) = {y_calc:.10f}  (esperado: {y:.6f}, error: {error:.2e})")
    
    desarrollo.append("")
    
    # Conclusión
    desarrollo.append("=" * 80)
    desarrollo.append("📝 CONCLUSIÓN")
    desarrollo.append("=" * 80)
    desarrollo.append("")
    desarrollo.append(f"Se ha construido exitosamente el polinomio interpolante de Newton")
    desarrollo.append(f"de grado {len(x_datos)-1} que pasa por los {len(x_datos)} puntos dados.")
    desarrollo.append("")
    desarrollo.append(f"El polinomio puede usarse para:")
    desarrollo.append(f"  • Interpolar valores dentro del rango [{min(x_datos):.2f}, {max(x_datos):.2f}]")
    desarrollo.append(f"  • Aproximar la función original en puntos intermedios")
    desarrollo.append(f"  • Estimar derivadas e integrales numéricamente")
    desarrollo.append("")
    desarrollo.append("=" * 80)
    
    return "\n".join(desarrollo)

def generar_tabla_html(x_datos, y_datos, tabla_dd):
    """
    Genera una tabla HTML con el formato del libro
    """
    n = len(x_datos)
    
    html = '<div style="font-family: monospace; background: white; padding: 20px; color: black;">'
    html += '<h3 style="text-align: center;">TABLA DE DIFERENCIAS DIVIDIDAS</h3>'
    html += '<table style="border-collapse: collapse; margin: 20px auto; border: 2px solid black;">'
    
    # Encabezado
    html += '<tr style="background: #4CAF50; color: white;">'
    html += '<th style="border: 1px solid black; padding: 8px;">i</th>'
    html += '<th style="border: 1px solid black; padding: 8px;">xi</th>'
    html += '<th style="border: 1px solid black; padding: 8px;">f(xi)</th>'
    
    for j in range(1, n):
        html += f'<th style="border: 1px solid black; padding: 8px;">f[x<sub>i</sub>,...,x<sub>i+{j}</sub>]</th>'
    
    html += '</tr>'
    
    # Filas
    for i in range(n):
        html += '<tr>'
        html += f'<td style="border: 1px solid black; padding: 8px; text-align: center;">{i}</td>'
        html += f'<td style="border: 1px solid black; padding: 8px; text-align: right;">{x_datos[i]:.6f}</td>'
        html += f'<td style="border: 1px solid black; padding: 8px; text-align: right;">{tabla_dd[i, 0]:.6f}</td>'
        
        for j in range(1, n):
            if i + j < n:
                valor = tabla_dd[i, j]
                html += f'<td style="border: 1px solid black; padding: 8px; text-align: right;">{valor:.6f}</td>'
            else:
                html += '<td style="border: 1px solid black; padding: 8px;"></td>'
        
        html += '</tr>'
    
    html += '</table>'
    html += '</div>'
    
    return html

def generar_desarrollo_visual(x_datos, y_datos, tabla_dd, polinomio):
    """
    Genera visualización del desarrollo completo
    """
    from utils.interpolacion_newton import evaluar_polinomio
    
    fig = plt.figure(figsize=(16, 20))
    
    # 1. Tabla de datos
    ax1 = plt.subplot(5, 2, 1)
    ax1.axis('tight')
    ax1.axis('off')
    
    datos_tabla = []
    datos_tabla.append(['i', 'xi', 'f(xi)'])
    for i, (x, y) in enumerate(zip(x_datos, y_datos)):
        datos_tabla.append([str(i), f'{x:.6f}', f'{y:.6f}'])
    
    tabla1 = ax1.table(cellText=datos_tabla, cellLoc='center', loc='center',
                       colWidths=[0.2, 0.4, 0.4])
    tabla1.auto_set_font_size(False)
    tabla1.set_fontsize(10)
    tabla1.scale(1, 2)
    
    # Colorear encabezado
    for i in range(3):
        tabla1[(0, i)].set_facecolor('#4CAF50')
        tabla1[(0, i)].set_text_props(weight='bold', color='white')
    
    ax1.set_title('Datos del Problema', fontsize=14, fontweight='bold', pad=20)
    
    # 2. Gráfica de puntos
    ax2 = plt.subplot(5, 2, 2)
    ax2.plot(x_datos, y_datos, 'ro', markersize=10, label='Puntos dados')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('X', fontweight='bold')
    ax2.set_ylabel('Y', fontweight='bold')
    ax2.set_title('Puntos de Interpolación', fontsize=14, fontweight='bold')
    ax2.legend()
    
    # 3. Tabla de diferencias divididas (simplificada)
    ax3 = plt.subplot(5, 2, (3, 4))
    ax3.axis('tight')
    ax3.axis('off')
    
    n = len(x_datos)
    dd_tabla = []
    header = ['i', 'xi', 'f[xi]']
    for j in range(1, min(4, n)):
        header.append(f'DD{j}')
    dd_tabla.append(header)
    
    for i in range(n):
        fila = [str(i), f'{x_datos[i]:.4f}', f'{tabla_dd[i, 0]:.6f}']
        for j in range(1, min(4, n)):
            if i + j < n:
                fila.append(f'{tabla_dd[i, j]:.6f}')
            else:
                fila.append('')
        dd_tabla.append(fila)
    
    tabla3 = ax3.table(cellText=dd_tabla, cellLoc='center', loc='center')
    tabla3.auto_set_font_size(False)
    tabla3.set_fontsize(9)
    tabla3.scale(1, 2)
    
    # Colorear
    for i in range(len(header)):
        tabla3[(0, i)].set_facecolor('#2196F3')
        tabla3[(0, i)].set_text_props(weight='bold', color='white')
    
    ax3.set_title('Tabla de Diferencias Divididas', fontsize=14, fontweight='bold', pad=20)
    
    # 4. Polinomio interpolador
    ax4 = plt.subplot(5, 2, (5, 6))
    x_plot = np.linspace(min(x_datos) - 0.5, max(x_datos) + 0.5, 200)
    y_plot = evaluar_polinomio(polinomio, x_plot)
    
    ax4.plot(x_plot, y_plot, 'b-', linewidth=2, label='Polinomio de Newton')
    ax4.plot(x_datos, y_datos, 'ro', markersize=10, label='Puntos dados', zorder=5)
    
    # Evaluar en 2.1
    y_21 = evaluar_polinomio(polinomio, 2.1)
    ax4.plot(2.1, y_21, 'g*', markersize=15, label=f'P(2.1) = {y_21:.6f}', zorder=6)
    
    ax4.grid(True, alpha=0.3)
    ax4.set_xlabel('X', fontweight='bold')
    ax4.set_ylabel('Y', fontweight='bold')
    ax4.set_title('Polinomio Interpolante Completo', fontsize=14, fontweight='bold')
    ax4.legend()
    
    # 5. Evaluaciones por grado
    ax5 = plt.subplot(5, 2, 7)
    ax5.axis('tight')
    ax5.axis('off')
    
    eval_tabla = [['Grado', 'P(2.1)']]
    
    from utils.interpolacion_newton import interpolacion_newton
    for grado in range(1, min(4, len(x_datos))):
        x_temp = x_datos[:grado+1]
        y_temp = y_datos[:grado+1]
        poli_temp, _, _ = interpolacion_newton(x_temp, y_temp)
        resultado = evaluar_polinomio(poli_temp, 2.1)
        eval_tabla.append([f'P{grado}', f'{resultado:.8f}'])
    
    tabla5 = ax5.table(cellText=eval_tabla, cellLoc='center', loc='center',
                       colWidths=[0.3, 0.7])
    tabla5.auto_set_font_size(False)
    tabla5.set_fontsize(10)
    tabla5.scale(1, 2)
    
    tabla5[(0, 0)].set_facecolor('#FF9800')
    tabla5[(0, 1)].set_facecolor('#FF9800')
    tabla5[(0, 0)].set_text_props(weight='bold', color='white')
    tabla5[(0, 1)].set_text_props(weight='bold', color='white')
    
    ax5.set_title('Evaluaciones por Grado', fontsize=14, fontweight='bold', pad=20)
    
    # 6. Coeficientes
    ax6 = plt.subplot(5, 2, 8)
    coeficientes = tabla_dd[0, :]
    ax6.bar(range(len(coeficientes)), np.abs(coeficientes), color='skyblue', edgecolor='navy')
    ax6.set_xlabel('Coeficiente', fontweight='bold')
    ax6.set_ylabel('Valor Absoluto', fontweight='bold')
    ax6.set_title('Coeficientes del Polinomio', fontsize=14, fontweight='bold')
    ax6.set_xticks(range(len(coeficientes)))
    ax6.set_xticklabels([f'a{i}' for i in range(len(coeficientes))])
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. Verificación
    ax7 = plt.subplot(5, 2, (9, 10))
    ax7.axis('tight')
    ax7.axis('off')
    
    verif_tabla = [['xi', 'f(xi) real', 'P(xi) calculado', 'Error']]
    for x, y in zip(x_datos, y_datos):
        y_calc = evaluar_polinomio(polinomio, x)
        error = abs(y - y_calc)
        verif_tabla.append([f'{x:.4f}', f'{y:.6f}', f'{y_calc:.6f}', f'{error:.2e}'])
    
    tabla7 = ax7.table(cellText=verif_tabla, cellLoc='center', loc='center')
    tabla7.auto_set_font_size(False)
    tabla7.set_fontsize(9)
    tabla7.scale(1, 2)
    
    for i in range(4):
        tabla7[(0, i)].set_facecolor('#9C27B0')
        tabla7[(0, i)].set_text_props(weight='bold', color='white')
    
    ax7.set_title('Verificación en Puntos Originales', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig
