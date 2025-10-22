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
        "Gauss – Jordan"
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

    st.image("images/metodos_directos.JPG", caption="Esquema general de un método directo")


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
    st.write("""
    Este método se utiliza para **matrices simétricas y definidas positivas**.
    Permite expresar A como el producto **A = L·Lᵀ**, donde L es una matriz triangular inferior.
    """)

    A_text = st.text_area("🧮 Ingrese una matriz simétrica (ejemplo: 25,15,-5;15,18,0;-5,0,11)",
                          "25,15,-5;15,18,0;-5,0,11")

    if st.button("Calcular Descomposición de Cholesky"):
        try:
            A = np.array([[float(num) for num in row.split(',')] for row in A_text.split(';')])

            # --- Validaciones ---
            if not np.allclose(A, A.T):
                st.warning("⚠️ La matriz no es simétrica. El método de Cholesky requiere una matriz simétrica.")
            else:
                # --- Descomposición ---
                L = np.linalg.cholesky(A)
                st.write("**Matriz A:**")
                st.write(A)
                st.write("**Factor L:**")
                st.write(L)
                st.write("**Verificación A ≈ L·Lᵀ:**")
                st.write(np.dot(L, L.T))
                st.success("✅ ¡Descomposición de Cholesky realizada correctamente!")

                # --- Visualización ---
                fig, ax = plt.subplots(1, 2, figsize=(8, 4))
                ax[0].imshow(A, cmap='Purples')
                ax[0].set_title("Matriz A")
                ax[1].imshow(L, cmap='Greens')
                ax[1].set_title("Matriz L (Triangular Inferior)")
                st.pyplot(fig)

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

