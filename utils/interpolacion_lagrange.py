"""
Módulo de Interpolación de Lagrange
Permite interpolar puntos usando el método de Lagrange
"""
import numpy as np
import sympy as sp

def interpolacion_lagrange(x_datos, y_datos):
    """
    Calcula el polinomio de interpolación de Lagrange
    
    Args:
        x_datos: array de valores x conocidos
        y_datos: array de valores y conocidos
    
    Returns:
        polinomio: expresión simbólica del polinomio
        detalles: lista con los pasos del cálculo
    """
    n = len(x_datos)
    x = sp.Symbol('x')
    polinomio = 0
    detalles = []
    
    for i in range(n):
        # Calcular el término L_i(x)
        termino = y_datos[i]
        L_i = 1
        
        for j in range(n):
            if i != j:
                L_i *= (x - x_datos[j]) / (x_datos[i] - x_datos[j])
        
        termino_expandido = sp.expand(termino * L_i)
        polinomio += termino_expandido
        
        detalles.append({
            'i': i,
            'L_i': L_i,
            'termino': termino_expandido,
            'punto': (x_datos[i], y_datos[i])
        })
    
    polinomio = sp.expand(polinomio)
    return polinomio, detalles

def evaluar_polinomio(polinomio, valores_x):
    """
    Evalúa el polinomio en un conjunto de valores
    """
    x = sp.Symbol('x')
    f = sp.lambdify(x, polinomio, 'numpy')
    return f(valores_x)
