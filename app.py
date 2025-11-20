import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'

# --- CONFIGURACIÓN BBDD ---
# En Render, la variable de entorno suele ser DATABASE_URL.
# Si lo corres en local, cambia el string por defecto.

db_url = os.getenv("DATABASE_URL", "postgresql://usuario:password@localhost:5432/mi_base_de_datos")

# Fix para SQLAlchemy en Render (postgres:// -> postgresql://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

# --- CARGAR SOLUCIÓN (GROUND TRUTH) ---
# Se carga al inicio para no leer disco en cada petición.
# El archivo debe tener columnas: "ID" y "TRUE" (o el nombre que tenga tu target real)
try:
    solution_df = pd.read_csv('solution.csv')
    # Aseguramos que ID sea índice para facilitar comparación
    solution_df['ID'] = solution_df['ID'].astype(str)
    solution_df.set_index('ID', inplace=True)
    print("✅ Solución cargada correctamente.")
except Exception as e:
    print(f"⚠️ Error cargando solution.csv: {e}")
    solution_df = pd.DataFrame() # Empty para evitar crashes si no existe el fichero

# --- RUTAS ---

@app.route('/')
def index():
    """Muestra el Top 3"""
    try:
        # Leemos todas las entregas
        query = "SELECT team_name, score FROM submissions"
        df = pd.read_sql(query, engine)
        
        if not df.empty:
            # Agrupamos por equipo y nos quedamos con el MAX score
            ranking = df.groupby('team_name')['score'].max().reset_index()
            # Ordenamos descendente
            ranking = ranking.sort_values(by='score', ascending=False)
            # Top 3
            top_3 = ranking.head(3).to_dict(orient='records')
        else:
            top_3 = []
            
    except Exception as e:
        print(f"Error DB: {e}")
        top_3 = []
        # Si la tabla no existe, no pasa nada, se creará en el primer submit

    return render_template('index.html', ranking=top_3)

@app.route('/details')
def details():
    """Muestra el ranking completo"""
    try:
        query = "SELECT team_name, score, timestamp FROM submissions"
        df = pd.read_sql(query, engine)
        
        if not df.empty:
            # Mejor score por equipo
            ranking = df.groupby('team_name')[['score']].max().reset_index()
            ranking = ranking.sort_values(by='score', ascending=False)
            # Añadimos ranking (posición 1, 2, 3...)
            ranking['rank'] = range(1, len(ranking) + 1)
            full_ranking = ranking.to_dict(orient='records')
        else:
            full_ranking = []
    except:
        full_ranking = []

    return render_template('details.html', ranking=full_ranking)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        team = request.form.get('team')
        file = request.files.get('file')

        if not team or not file:
            flash('Falta equipo o archivo', 'error')
            return redirect(request.url)

        try:
            # 1. Leer CSV subido
            pred_df = pd.read_csv(file)
            
            # 2. Validaciones básicas
            if 'ID' not in pred_df.columns or 'PRED' not in pred_df.columns:
                flash('El CSV debe tener columnas "ID" y "PRED"', 'error')
                return redirect(request.url)
            
            # 3. Preprocesar para comparar
            pred_df['ID'] = pred_df['ID'].astype(str)
            pred_df.set_index('ID', inplace=True)
            
            # 4. Calcular Accuracy (Intersección de IDs)
            # Unimos con la solución usando el índice (ID)
            merged = pred_df.join(solution_df, how='inner', lsuffix='_pred', rsuffix='_true')
            
            if merged.empty:
                flash('Los IDs no coinciden con la solución.', 'error')
                return redirect(request.url)

            # Suponemos que la columna en solution.csv se llama "TRUE" (o ajusta aquí)
            # Si en solution.csv la columna target se llama diferente, cámbialo abajo.
            # Aquí asumimos que solution.csv tiene 'ID' y 'TRUE' (o 'PRED' real).
            # Para hacerlo genérico, usaremos la columna que no sea ID del solution_df original.
            target_col = solution_df.columns[0] # Asumimos que solo hay una columna de target
            
            # Calculamos accuracy
            score = (merged['PRED'] == merged[target_col]).mean()
            
            # 5. Guardar en BBDD usando to_sql
            submission_data = {
                'team_name': [team],
                'score': [score],
                'timestamp': [datetime.now()]
            }
            submission_df = pd.DataFrame(submission_data)
            
            # 'append' añade filas, si la tabla no existe la crea.
            submission_df.to_sql('submissions', engine, if_exists='append', index=False)
            
            flash(f'Entrega exitosa! Accuracy: {score:.4f}', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error procesando el archivo: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('submit.html')

if __name__ == '__main__':
    app.run(debug=True)