"""
Módulo de Interpolación de Newton con Diferencias Divididas
"""
import numpy as np
import sympy as sp

def diferencias_divididas(x_datos, y_datos):
    """
    Calcula la tabla de diferencias divididas
    
    Returns:
        tabla: matriz con las diferencias divididas
        coeficientes: coeficientes del polinomio de Newton
    """
    n = len(x_datos)
    tabla = np.zeros((n, n))
    tabla[:, 0] = y_datos
    
    for j in range(1, n):
        for i in range(n - j):
            tabla[i][j] = (tabla[i+1][j-1] - tabla[i][j-1]) / (x_datos[i+j] - x_datos[i])
    
    coeficientes = tabla[0, :]
    return tabla, coeficientes

def interpolacion_newton(x_datos, y_datos):
    """
    Calcula el polinomio de interpolación de Newton
    
    Returns:
        polinomio: expresión simbólica del polinomio
        tabla: tabla de diferencias divididas
        detalles: información detallada del proceso
    """
    x = sp.Symbol('x')
    tabla, coeficientes = diferencias_divididas(x_datos, y_datos)
    
    polinomio = coeficientes[0]
    detalles = []
    
    for i in range(1, len(coeficientes)):
        termino = coeficientes[i]
        producto = 1
        
        for j in range(i):
            producto *= (x - x_datos[j])
        
        termino_completo = sp.expand(termino * producto)
        polinomio += termino_completo
        
        detalles.append({
            'orden': i,
            'coeficiente': coeficientes[i],
            'termino': termino_completo
        })
    
    polinomio = sp.expand(polinomio)
    return polinomio, tabla, detalles

def evaluar_polinomio(polinomio, valores_x):
    """
    Evalúa el polinomio en un conjunto de valores
    """
    x = sp.Symbol('x')
    f = sp.lambdify(x, polinomio, 'numpy')
    return f(valores_x)
