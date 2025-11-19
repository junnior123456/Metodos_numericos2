"""
Módulo de Interpolación con Splines Cúbicos
"""
import numpy as np
from scipy.interpolate import CubicSpline, interp1d

def spline_cubico(x_datos, y_datos):
    """
    Calcula la interpolación con splines cúbicos
    
    Returns:
        spline: objeto CubicSpline
        detalles: información sobre los segmentos
    """
    spline = CubicSpline(x_datos, y_datos)
    
    detalles = []
    for i in range(len(x_datos) - 1):
        coefs = spline.c[:, i]
        detalles.append({
            'segmento': i,
            'intervalo': (x_datos[i], x_datos[i+1]),
            'coeficientes': coefs,
            'ecuacion': f"S{i}(x) = {coefs[0]:.4f}(x-{x_datos[i]})³ + {coefs[1]:.4f}(x-{x_datos[i]})² + {coefs[2]:.4f}(x-{x_datos[i]}) + {coefs[3]:.4f}"
        })
    
    return spline, detalles

def spline_lineal(x_datos, y_datos):
    """
    Calcula la interpolación lineal por tramos
    """
    return interp1d(x_datos, y_datos, kind='linear')

def spline_cuadratico(x_datos, y_datos):
    """
    Calcula la interpolación cuadrática por tramos
    """
    return interp1d(x_datos, y_datos, kind='quadratic')
