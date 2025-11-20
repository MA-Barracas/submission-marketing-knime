
# 🏆 Classroom ML Leaderboard

Bienvenido al sistema de evaluación automatizada para el ejercicio de Machine Learning. Esta aplicación gestiona las entregas de los equipos, valida los resultados contra la solución real ("Ground Truth") y actualiza el ranking en tiempo real.

---

## 🧑‍🎓 Parte 1: Instrucciones para los Alumnos

### 🎯 El Objetivo
Vuestro objetivo es entrenar el mejor modelo de Machine Learning posible para el dataset proporcionado en clase. Una vez tengáis vuestras predicciones, debéis subirlas a esta plataforma para ver qué tal rendís frente al resto de equipos.

### 📂 Formato de Entrega (Submission)
El archivo que subáis **debe ser obligatoriamente un CSV** (`.csv`) y cumplir estrictamente con el siguiente formato:

1.  **Separador:** Coma (`,`).
2.  **Cabeceras:** Debe tener dos columnas llamadas exactamente `ID` y `PRED`.
3.  **Contenido:**
    *   `ID`: El identificador de la fila (correspondiente al dataset de test).
    *   `PRED`: La clase predicha por vuestro modelo (ej. 0 o 1).

**Ejemplo de archivo `submission.csv` válido:**

```csv
ID,PRED
1,0
2,1
3,0
4,1
...
```

> ⚠️ **Importante:** Si los nombres de las columnas no son exactos o los IDs no coinciden con los esperados, la plataforma rechazará la entrega.

### 📏 Métrica de Evaluación
La clasificación se basa en **Accuracy** (Exactitud).
$$ Accuracy = \frac{\text{Predicciones Correctas}}{\text{Total de Muestras}} $$

### 🚀 Cómo enviar tu solución
1.  Entra en la aplicación.
2.  Haz clic en el botón **"🚀 Submit Predictions"**.
3.  Selecciona tu **Nombre de Equipo** en el desplegable (Equipo 1 - Equipo 10).
4.  Selecciona tu archivo `.csv`.
5.  Pulsa **"Evaluar Modelo"**.

Si todo ha ido bien, el sistema te devolverá tu puntuación y actualizará el Leaderboard si has entrado en el TOP 3.

---

## 🛠️ Parte 2: Documentación Técnica (Backend)

Esta sección explica cómo desplegar, configurar y ejecutar el proyecto.

### 🏗️ Estructura del Proyecto

```text
/
├── app.py                # Lógica del servidor (Flask + Pandas + SQLAlchemy)
├── requirements.txt      # Dependencias de Python
├── solution.csv          # ⚠️ CRÍTICO: Archivo con las respuestas correctas
├── templates/            # Vistas HTML (Jinja2)
│   ├── index.html        # Ranking Top 3
│   ├── details.html      # Tabla completa histórica
│   └── submit.html       # Formulario de carga
└── static/
    └── style.css         # Estilos visuales (Dark Theme)
```

### ⚙️ Requisitos Previos

*   **Python 3.9+**
*   **PostgreSQL** (Local o en la nube, ej. Render/Neon/Supabase).
*   **Archivo `solution.csv`**: Debes tener este archivo en la raíz del proyecto para que el sistema pueda corregir. Debe tener columnas `ID` y `TRUE` (o el target real).

### 🔧 Instalación Local

1.  **Clonar el repositorio:**
    ```bash
    git clone <tu-repo>
    cd <tu-repo>
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Base de Datos:**
    El sistema busca la variable de entorno `DATABASE_URL`. Si no la encuentra, intenta conectar a localhost.
    
    *Linux/Mac:*
    ```bash
    export DATABASE_URL="postgresql://usuario:password@localhost:5432/nombre_db"
    ```
    *Windows (Powershell):*
    ```powershell
    $env:DATABASE_URL="postgresql://usuario:password@localhost:5432/nombre_db"
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```
    Visita `http://127.0.0.1:5000` en tu navegador.

### ☁️ Despliegue en Render.com

Esta app está optimizada para desplegarse en Render con **cero configuración extra**:

1.  Crea un nuevo **Web Service** conectado a tu repositorio GitHub.
2.  En la configuración de Render:
    *   **Runtime:** Python 3
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app`
3.  Añade una **PostgreSQL database** en Render y vinculala (o pega la `Internal Database URL` en las variables de entorno como `DATABASE_URL`).
4.  **IMPORTANTE:** Asegúrate de que el archivo `solution.csv` está subido al repositorio de GitHub, ya que Render lo necesitará para leer las respuestas correctas.

### 🧠 Lógica de Base de Datos

La app utiliza `pandas` y `SQLAlchemy` para una gestión simplificada (sin modelos ORM complejos):
*   **Escritura:** `df.to_sql('submissions', ...)` guarda cada entrega.
*   **Lectura:** `pd.read_sql(...)` recupera los datos para generar los rankings.
*   La tabla `submissions` se crea automáticamente la primera vez que alguien envía un archivo.

