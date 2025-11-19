import streamlit as st
st.markdown("""
    <style>
    /* Fondo oscuro elegante */
    .main {
        background-color: #0f172a;
        color: white;
        font-family: 'Segoe UI';
    }

    /* Encabezado */
    h1, h2, h3 {
        color: #facc15;
        text-shadow: 1px 1px 3px black;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
    }

    /* Botones y selectbox */
    div[data-baseweb="select"] {
        background-color: #334155;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
from utils.interpolacion_newton import diferencias_divididas, interpolacion_newton, evaluar_polinomio
from utils.image_processor import procesar_imagen, extraer_puntos_interpolacion, mostrar_imagen_procesada
from utils.interpolacion_mejorada import crear_interfaz_interpolacion

st.set_page_config(page_title="Métodos Numéricos - Junnior", layout="wide")

st.title("🧮 Metodos directos")
st.subheader("Exposición: Métodos Directos – Ingeniería de Sistemas")

# Menú lateral
opcion = st.sidebar.selectbox(
    "Selecciona el método:",
    [
        "Métodos Directos",
        "Descomposición LU",
        "Cholesky",
        "Eliminación Gaussiana",
        "Gauss – Jordan",
        "Interpolación de Newton"
    ]
)

st.sidebar.info("Creado por **Junnior Chinchay**, Alice Saboya y Jannpier García 👨‍💻")

# --- MÉTODOS DIRECTOS ---
if opcion == "Métodos Directos":
    st.header("📘 Introducción a los Métodos Directos")
    st.write("""
    Los métodos directos buscan resolver sistemas de ecuaciones lineales 
    **Ax = b** de forma exacta en un número finito de pasos, 
    a diferencia de los métodos iterativos.
    """)

    st.image("images/metodos_directos.jpg", caption="Esquema general de un método directo")


# --- DESCOMPOSICIÓN LU ---
elif opcion == "Descomposición LU":
    st.header("📗 Descomposición LU – Ingreso de Ejercicios")
    st.write("""
    Este método descompone una matriz **A** en el producto de una matriz **L (triangular inferior)** 
    y una **U (triangular superior)**, tal que **A = L·U**.
    Posteriormente se resuelve el sistema lineal **Ax = b**.
    """)

    # --- Entradas del usuario ---
    A_text = st.text_area("🧮 Matriz A (separa filas con ';' y columnas con ',')",
                          "2,1,1; 4,-6,0; -2,7,2")
    b_text = st.text_input("🎯 Vector b (separa los valores con comas)", "5,-2,9")

    if st.button("Calcular Descomposición LU"):
        try:
            # --- Conversión de texto a numpy ---
            A = np.array([[float(num) for num in row.split(',')] for row in A_text.split(';')])
            b = np.array([float(x) for x in b_text.split(',')])

            n = len(A)
            L = np.zeros((n, n))
            U = np.zeros((n, n))

            # --- Cálculo manual LU ---
            for i in range(n):
                # Calcular U
                for k in range(i, n):
                    suma = sum(L[i][j] * U[j][k] for j in range(i))
                    U[i][k] = A[i][k] - suma
                # Calcular L
                for k in range(i, n):
                    if i == k:
                        L[i][i] = 1
                    else:
                        suma = sum(L[k][j] * U[j][i] for j in range(i))
                        L[k][i] = (A[k][i] - suma) / U[i][i]

            # --- Sustitución hacia adelante (Ly = b) ---
            y = np.zeros(n)
            for i in range(n):
                y[i] = b[i] - np.dot(L[i, :i], y[:i])

            # --- Sustitución hacia atrás (Ux = y) ---
            x = np.zeros(n)
            for i in range(n-1, -1, -1):
                x[i] = (y[i] - np.dot(U[i, i+1:], x[i+1:])) / U[i][i]

            # --- Mostrar resultados ---
            st.subheader("📊 Resultados del Cálculo")
            st.write("**Matriz A:**")
            st.write(A)
            st.write("**Matriz L (Triangular Inferior):**")
            st.write(L)
            st.write("**Matriz U (Triangular Superior):**")
            st.write(U)
            st.write("**Vector Solución (x):**")
            st.success(x)

            # --- Visualización de las matrices ---
            fig, ax = plt.subplots(1, 3, figsize=(14, 4))
            ax[0].imshow(A, cmap='Purples', interpolation='nearest')
            ax[0].set_title("Matriz A")
            ax[1].imshow(L, cmap='Blues', interpolation='nearest')
            ax[1].set_title("Matriz L (Inferior)")
            ax[2].imshow(U, cmap='Oranges', interpolation='nearest')
            ax[2].set_title("Matriz U (Superior)")
            for a in ax:
                a.set_xticks(range(n))
                a.set_yticks(range(n))
            st.pyplot(fig)

        except Exception as e:
            st.error(f"⚠️ Error en el ingreso o cálculo: {e}")



# --- CHOLESKY ---
elif opcion == "Cholesky":
    st.header("📙 Descomposición de Cholesky")

    st.write("Este método se utiliza para matrices simétricas y definidas positivas. "
             "Permite expresar A como el producto A = L·Lᵀ, donde L es triangular inferior.")

    A_input = st.text_area("Ingrese una matriz simétrica (ejemplo: 25,15,-5;15,18,0;-5,0,11)", "")
    b_input = st.text_input("Ingrese el vector b (ejemplo: 7,3,4,8)", "")

    if st.button("Calcular Descomposición de Cholesky"):
        try:
            # Convertir texto a matriz y vector
            A = np.array([[float(num) for num in fila.split(',')] for fila in A_input.split(';')])
            b = np.array([float(num) for num in b_input.split(',')])

            # Verificar dimensiones
            if A.shape[0] != A.shape[1]:
                st.error("⚠️ La matriz A debe ser cuadrada.")
            elif b.size != A.shape[0]:
                st.error("⚠️ El vector b debe tener la misma cantidad de elementos que filas de A.")
            elif not np.allclose(A, A.T):
                st.error("⚠️ La matriz A no es simétrica. Cholesky requiere A simétrica y definida positiva.")
            else:
                # Descomposición de Cholesky
                L = np.linalg.cholesky(A)
                st.subheader("✅ Matriz L (Triangular inferior):")
                st.write(L)

                # Resolver el sistema A·x = b
                y = np.linalg.solve(L, b)
                x = np.linalg.solve(L.T, y)

                st.subheader("📊 Solución del sistema (valores de x):")
                for i, valor in enumerate(x, start=1):
                    st.write(f"x{i} = {valor:.4f}")

        except Exception as e:
            st.error(f"Error: {e}")

# --- eliminación gaussiana ---
elif opcion == "Eliminación Gaussiana":
    st.header("📒 Eliminación Gaussiana – Paso a Paso")
    st.write("""
    Este método transforma el sistema lineal **Ax = b** en una forma **triangular superior** 
    mediante operaciones elementales por fila, para luego aplicar **sustitución regresiva**.
    """)

    A_text = st.text_area("🧮 Matriz A (ejemplo: 2,1,-1; -3,-1,2; -2,1,2)", "2,1,-1; -3,-1,2; -2,1,2")
    b_text = st.text_input("🎯 Vector b (ejemplo: 8,-11,-3)", "8,-11,-3")

    if "paso" not in st.session_state:
        st.session_state.paso = 0

    if st.button("🔄 Reiniciar"):
        st.session_state.paso = 0

    if st.button("➡ Siguiente Paso"):
        st.session_state.paso += 1

    try:
        # Convertir texto a matrices NumPy
        A = np.array([[float(num) for num in row.split(',')] for row in A_text.split(';')])
        b = np.array([float(x) for x in b_text.split(',')])
        n = len(b)

        # Crear copia para no modificar original
        A_proc = A.copy().astype(float)
        b_proc = b.copy().astype(float)

        pasos = []

        # Generar lista de matrices paso a paso
        for i in range(n-1):
            for j in range(i+1, n):
                factor = A_proc[j][i] / A_proc[i][i]
                A_proc[j] = A_proc[j] - factor * A_proc[i]
                b_proc[j] = b_proc[j] - factor * b_proc[i]
                pasos.append((i, j, A_proc.copy(), b_proc.copy()))

        paso_actual = min(st.session_state.paso, len(pasos))
        st.write(f"**Paso {paso_actual} de {len(pasos)}:**")

        if paso_actual > 0:
            i, j, A_mostrar, b_mostrar = pasos[paso_actual-1]
            st.write(f"➡ Se eliminó el elemento A[{j+1},{i+1}] usando la fila {i+1}")
        else:
            A_mostrar, b_mostrar = A, b

        # Mostrar matriz aumentada
        Ab = np.hstack([A_mostrar, b_mostrar.reshape(-1,1)])
        st.write("**Matriz aumentada [A|b]:**")
        st.write(Ab)

        # Mostrar visualización
        fig, ax = plt.subplots(figsize=(5,4))
        im = ax.imshow(Ab, cmap='coolwarm', interpolation='nearest')
        ax.set_title(f"Transformación paso {paso_actual}")
        plt.colorbar(im)
        st.pyplot(fig)

        # Si ya terminó la eliminación → resolver por sustitución regresiva
        if paso_actual == len(pasos):
            x = np.zeros(n)
            for i in range(n-1, -1, -1):
                x[i] = (b_proc[i] - np.dot(A_proc[i, i+1:], x[i+1:])) / A_proc[i][i]
            st.subheader("✅ Resultado Final (Sustitución Regresiva)")
            for i, val in enumerate(x, start=1):
                st.success(f"x{i} = {val:.4f}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")


# --- INTERPOLACIÓN DE NEWTON ---
elif opcion == "Interpolación de Newton":
    crear_interfaz_interpolacion()


# --- GAUSS–JORDAN ---
elif opcion == "Gauss – Jordan":
    st.header("📕 Método de Gauss–Jordan – Reducción Completa")
    st.write("""
    Este método transforma el sistema **Ax = b** en su forma reducida **[I | x]** 
    mediante operaciones elementales por fila (pivoteo, normalización y eliminación completa).
    """)

    # Entrada del usuario
    A_text = st.text_area("🧮 Matriz A (ejemplo: 2,1,-1; -3,-1,2; -2,1,2)", "2,1,-1; -3,-1,2; -2,1,2")
    b_text = st.text_input("🎯 Vector b (ejemplo: 8,-11,-3)", "8,-11,-3")

    # Estado de pasos
    if "paso_gj" not in st.session_state:
        st.session_state.paso_gj = 0

    if st.button("🔄 Reiniciar"):
        st.session_state.paso_gj = 0

    if st.button("➡ Siguiente Paso"):
        st.session_state.paso_gj += 1

    try:
        # Convertir texto a matrices
        A = np.array([[float(num) for num in row.split(',')] for row in A_text.split(';')])
        b = np.array([float(x) for x in b_text.split(',')])
        n = len(b)

        # Matriz aumentada
        Ab = np.hstack([A, b.reshape(-1, 1)])
        pasos = []

        # Guardar pasos del proceso Gauss–Jordan
        for i in range(n):
            # Normalizar fila pivote
            Ab[i] = Ab[i] / Ab[i, i]
            pasos.append((i, f"Normalizamos fila {i+1}", Ab.copy()))

            # Eliminar en las demás filas
            for j in range(n):
                if i != j:
                    factor = Ab[j, i]
                    Ab[j] = Ab[j] - factor * Ab[i]
                    pasos.append((j, f"Eliminamos elemento ({j+1},{i+1})", Ab.copy()))

        # Mostrar paso actual
        paso_actual = min(st.session_state.paso_gj, len(pasos))
        st.write(f"**Paso {paso_actual} de {len(pasos)}:**")

        if paso_actual > 0:
            fila, accion, matriz = pasos[paso_actual - 1]
            st.write(f"➡ {accion}")
        else:
            matriz = np.hstack([A, b.reshape(-1, 1)])

        # Mostrar matriz aumentada actual
        st.write("**Matriz aumentada [A|b]:**")
        st.write(matriz)

        # Visualización gráfica
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(matriz, cmap='plasma', interpolation='nearest')
        ax.set_title(f"Transformación paso {paso_actual}")
        plt.colorbar(im)
        st.pyplot(fig)

        # Resultado final
        if paso_actual == len(pasos):
            x = matriz[:, -1]
            st.subheader("✅ Resultado Final (Matriz Identidad y solución):")
            st.write("**[I | x]:**")
            st.write(matriz)
            for i, val in enumerate(x, start=1):
                st.success(f"x{i} = {val:.4f}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

