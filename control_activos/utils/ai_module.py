# utils/ai_module.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

# Configurar la ruta para guardar modelos entrenados
MODEL_PATH = 'media/models/'
os.makedirs(MODEL_PATH, exist_ok=True)

def clasificar_criticidad_activos(datos):
    """
    Clasifica automáticamente la criticidad de los activos usando K-means
    
    Args:
        datos (list of dict): Lista de diccionarios con datos de activos
                            Debe contener claves: 'impacto_produccion', 
                            'disponibilidad_repuestos', 'probabilidad_falla'
    
    Returns:
        dict: Clasificación de criticidad para cada activo
    """
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Mapear valores categóricos a numéricos
    impacto_map = {'bajo': 1, 'medio': 2, 'alto': 3, 'critico': 4}
    disponibilidad_map = {'alta': 1, 'media': 2, 'baja': 3, 'nula': 4}
    probabilidad_map = {'baja': 1, 'media': 2, 'alta': 3}
    
    # Aplicar mapeo
    df['impacto_num'] = df['impacto_produccion'].map(impacto_map)
    df['disponibilidad_num'] = df['disponibilidad_repuestos'].map(disponibilidad_map)
    df['probabilidad_num'] = df['probabilidad_falla'].map(probabilidad_map)
    
    # Crear características para clustering
    X = df[['impacto_num', 'disponibilidad_num', 'probabilidad_num']].values
    
    # Escalar características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Aplicar K-means (4 clusters para 4 niveles de criticidad)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Calcular gravedad media de cada cluster para asignar etiquetas
    cluster_gravity = []
    for i in range(4):
        cluster_data = X[clusters == i]
        if len(cluster_data) > 0:
            # Calcular "gravedad" como suma ponderada de factores
            gravity = np.mean(cluster_data[:, 0] * 2 + cluster_data[:, 1] + cluster_data[:, 2])
            cluster_gravity.append((i, gravity))
    
    # Ordenar clusters por gravedad
    cluster_gravity.sort(key=lambda x: x[1])
    
    # Mapear clusters a niveles de criticidad
    criticidad_map = {
        cluster_gravity[0][0]: 'baja',
        cluster_gravity[1][0]: 'media',
        cluster_gravity[2][0]: 'alta',
        cluster_gravity[3][0]: 'extrema'
    }
    
    # Asignar criticidad a cada activo
    df['criticidad_calculada'] = [criticidad_map[c] for c in clusters]
    
    # Generar visualización
    plt.figure(figsize=(10, 8))
    
    # Gráfico 3D
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Colores para cada nivel de criticidad
    colors = {
        'baja': 'green',
        'media': 'blue',
        'alta': 'orange',
        'extrema': 'red'
    }
    
    # Graficar cada punto con color según su criticidad
    for i, row in df.iterrows():
        criticidad = row['criticidad_calculada']
        ax.scatter(
            row['impacto_num'],
            row['disponibilidad_num'],
            row['probabilidad_num'],
            color=colors[criticidad],
            s=50,
            alpha=0.7
        )
    
    # Etiquetas y título
    ax.set_xlabel('Impacto en Producción')
    ax.set_ylabel('Disponibilidad de Repuestos')
    ax.set_zlabel('Probabilidad de Falla')
    ax.set_title('Clasificación de Criticidad de Activos')
    
    # Guardar gráfico en memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Preparar resultados
    resultados = {
        'criticidad': df[['criticidad_calculada']].to_dict('records'),
        'grafico': f"data:image/png;base64,{imagen_base64}"
    }
    
    return resultados

def predecir_fallas(datos_historicos, sensor_data, dias_prediccion=30):
    """
    Predice posibles fallas en base a datos históricos y lecturas de sensores
    
    Args:
        datos_historicos (list of dict): Lista con datos históricos de fallas y mantenimientos
        sensor_data (list of dict): Lista con lecturas de sensores
        dias_prediccion (int): Número de días a futuro para la predicción
    
    Returns:
        dict: Predicciones de fallas con probabilidades
    """
    # Convertir a DataFrames
    df_hist = pd.DataFrame(datos_historicos)
    df_sensor = pd.DataFrame(sensor_data)
    
    # Verificar si hay suficientes datos para entrenar
    if len(df_hist) < 10:
        return {'error': 'Datos históricos insuficientes para generar predicciones confiables'}
    
    # Preparar datos para entrenamiento
    # Combinar datos históricos con datos de sensores
    df_combined = pd.merge(
        df_hist, 
        df_sensor, 
        on=['activo_id', 'fecha'],
        how='inner'
    )
    
    # Definir características y variable objetivo
    features = [col for col in df_combined.columns if col not in ['activo_id', 'fecha', 'falla']]
    X = df_combined[features]
    y = df_combined['falla']  # 1 si hubo falla, 0 si no
    
    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Identificar columnas numéricas y categóricas
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    # Definir preprocesadores
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combinar preprocesadores
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Crear y entrenar modelo
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Guardar modelo entrenado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = os.path.join(MODEL_PATH, f'fault_prediction_{timestamp}.joblib')
    joblib.dump(model, model_filename)
    
    # Generar predicciones para días futuros
    predicciones = []
    
    # Obtener últimos datos de sensores para cada activo
    activos_unicos = df_sensor['activo_id'].unique()
    
    for activo_id in activos_unicos:
        # Filtrar datos del activo
        df_activo = df_sensor[df_sensor['activo_id'] == activo_id].sort_values('fecha')
        
        if len(df_activo) == 0:
            continue
            
        # Obtener última lectura
        ultima_lectura = df_activo.iloc[-1]
        
        # Crear un dataframe para predicción
        df_pred = pd.DataFrame([ultima_lectura])
        
        # Eliminar columnas que no son características
        if 'fecha' in df_pred.columns:
            df_pred = df_pred.drop(columns=['fecha'])
            
        # Probabilidad de falla
        prob_falla = model.predict_proba(df_pred)[0][1]  # Probabilidad de la clase positiva (falla)
        
        # Determinar nivel de riesgo
        if prob_falla < 0.3:
            nivel_riesgo = 'bajo'
        elif prob_falla < 0.6:
            nivel_riesgo = 'medio'
        else:
            nivel_riesgo = 'alto'
            
        # Añadir a predicciones
        predicciones.append({
            'activo_id': activo_id,
            'probabilidad_falla': prob_falla,
            'nivel_riesgo': nivel_riesgo,
            'dias_prediccion': dias_prediccion,
            'fecha_prediccion': (datetime.now() + timedelta(days=dias_prediccion)).strftime('%Y-%m-%d')
        })
    
    # Generar visualización
    if predicciones:
        plt.figure(figsize=(10, 6))
        df_pred = pd.DataFrame(predicciones)
        
        # Ordenar por probabilidad de falla
        df_pred = df_pred.sort_values('probabilidad_falla', ascending=False)
        
        # Crear gráfico de barras
        bars = plt.bar(
            df_pred['activo_id'].astype(str), 
            df_pred['probabilidad_falla'],
            color=[
                'green' if r == 'bajo' else 'orange' if r == 'medio' else 'red' 
                for r in df_pred['nivel_riesgo']
            ]
        )
        
        # Añadir etiquetas
        plt.xlabel('ID de Activo')
        plt.ylabel('Probabilidad de Falla')
        plt.title(f'Predicción de Fallas - Próximos {dias_prediccion} días')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Añadir líneas de referencia
        plt.axhline(y=0.3, color='green', linestyle='--', alpha=0.5)
        plt.axhline(y=0.6, color='red', linestyle='--', alpha=0.5)
        
        # Guardar gráfico en memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        grafico = f"data:image/png;base64,{imagen_base64}"
    else:
        grafico = None
    
    return {
        'predicciones': predicciones,
        'precision_modelo': accuracy,
        'grafico': grafico
    }

def optimizar_mantenimiento(datos_mantenimientos, lecturas_sensores, activos_info):
    """
    Optimiza la programación de mantenimientos preventivos
    
    Args:
        datos_mantenimientos (list of dict): Datos históricos de mantenimientos
        lecturas_sensores (list of dict): Lecturas de sensores de los activos
        activos_info (list of dict): Información de los activos
    
    Returns:
        dict: Recomendaciones de mantenimiento optimizadas
    """
    # Convertir a DataFrames
    df_mant = pd.DataFrame(datos_mantenimientos)
    df_sensor = pd.DataFrame(lecturas_sensores)
    df_activos = pd.DataFrame(activos_info)
    
    # Verificar si hay suficientes datos
    if len(df_mant) < 10:
        return {'error': 'Datos históricos de mantenimiento insuficientes para optimización'}
    
    # Preparar características para el modelo
    # Crear características relevantes
    df_combined = pd.merge(
        df_mant, 
        df_activos, 
        on='activo_id',
        how='inner'
    )
    
    # Características para predecir intervalo óptimo
    features = [
        'tipo', 'duracion_real', 'costo_real', 'requiere_parada',
        'edad_activo', 'criticidad', 'horas_operacion'
    ]
    
    # Filtrar solo mantenimientos completados con datos completos
    df_train = df_combined[df_combined['estado'] == 'completado'].dropna(subset=features + ['dias_entre_mantenimientos'])
    
    # Si quedan muy pocos registros, no continuar
    if len(df_train) < 10:
        return {'error': 'Datos completos insuficientes para entrenar modelo de optimización'}
    
    # Variable objetivo: días entre mantenimientos
    X = df_train[features]
    y = df_train['dias_entre_mantenimientos']
    
    # Identificar columnas numéricas y categóricas
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    # Definir preprocesadores
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combinar preprocesadores
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Crear y entrenar modelo
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Dividir en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    # Guardar modelo entrenado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_filename = os.path.join(MODEL_PATH, f'maintenance_optimization_{timestamp}.joblib')
    joblib.dump(model, model_filename)
    
    # Generar recomendaciones para cada activo
    recomendaciones = []
    
    for _, activo in df_activos.iterrows():
        # Crear registro para predicción
        activo_features = {
            'activo_id': activo['activo_id'],
            'nombre': activo['nombre'],
            'tipo': 'preventivo',  # Asumimos mantenimiento preventivo
            'duracion_real': df_mant[df_mant['activo_id'] == activo['activo_id']]['duracion_real'].mean(),
            'costo_real': df_mant[df_mant['activo_id'] == activo['activo_id']]['costo_real'].mean(),
            'requiere_parada': True,  # Valor por defecto
            'edad_activo': activo['edad_activo'],
            'criticidad': activo['criticidad'],
            'horas_operacion': activo['horas_operacion']
        }
        
        # Si faltan datos, usar promedio o valor predeterminado
        for key, value in activo_features.items():
            if pd.isna(value):
                if key == 'duracion_real':
                    activo_features[key] = df_mant['duracion_real'].mean()
                elif key == 'costo_real':
                    activo_features[key] = df_mant['costo_real'].mean()
                elif key == 'requiere_parada':
                    activo_features[key] = True
        
        # Crear DataFrame para predicción
        df_pred = pd.DataFrame([activo_features])
        
        # Obtener solo las características necesarias
        X_pred = df_pred[features]
        
        # Predecir intervalo óptimo
        try:
            dias_recomendados = model.predict(X_pred)[0]
            
            # Redondear a un número entero razonable
            dias_recomendados = max(1, int(round(dias_recomendados)))
            
            # Calcular fecha recomendada
            ultimo_mantenimiento = df_mant[
                (df_mant['activo_id'] == activo['activo_id']) & 
                (df_mant['estado'] == 'completado')
            ]['fecha_realizada'].max()
            
            if pd.isna(ultimo_mantenimiento):
                fecha_recomendada = (datetime.now() + timedelta(days=dias_recomendados)).strftime('%Y-%m-%d')
            else:
                fecha_recomendada = (pd.to_datetime(ultimo_mantenimiento) + timedelta(days=dias_recomendados)).strftime('%Y-%m-%d')
            
            # Añadir a recomendaciones
            recomendaciones.append({
                'activo_id': activo['activo_id'],
                'nombre': activo['nombre'],
                'dias_recomendados': dias_recomendados,
                'fecha_recomendada': fecha_recomendada,
                'ultimo_mantenimiento': ultimo_mantenimiento.strftime('%Y-%m-%d') if not pd.isna(ultimo_mantenimiento) else None,
                'criticidad': activo['criticidad']
            })
        except Exception as e:
            continue
    
    # Visualización
    if recomendaciones:
        plt.figure(figsize=(12, 6))
        
        df_rec = pd.DataFrame(recomendaciones)
        df_rec = df_rec.sort_values('dias_recomendados')
        
        # Colores según criticidad
        colors = {
            'baja': 'green',
            'media': 'blue',
            'alta': 'orange',
            'extrema': 'red'
        }
        
        # Crear gráfico de barras horizontales
        bars = plt.barh(
            df_rec['nombre'], 
            df_rec['dias_recomendados'],
            color=[colors.get(c, 'blue') for c in df_rec['criticidad']]
        )
        
        # Añadir etiquetas
        plt.xlabel('Días Recomendados Entre Mantenimientos')
        plt.ylabel('Activo')
        plt.title('Intervalo Óptimo de Mantenimiento por Activo')
        plt.tight_layout()
        
        # Guardar gráfico en memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        grafico = f"data:image/png;base64,{imagen_base64}"
    else:
        grafico = None
    
    return {
        'recomendaciones': recomendaciones,
        'precision_modelo': {
            'r2': r2,
            'rmse': rmse
        },
        'grafico': grafico
    }

def detectar_anomalias(lecturas_sensores, umbral_zscore=3.0):
    """
    Detecta anomalías en las lecturas de sensores utilizando Z-score
    
    Args:
        lecturas_sensores (list of dict): Lista con lecturas de sensores
        umbral_zscore (float): Umbral de Z-score para considerar una lectura como anómala
        
    Returns:
        dict: Lecturas anómalas detectadas y visualización
    """
    # Convertir a DataFrame
    df = pd.DataFrame(lecturas_sensores)
    
    # Verificar que haya datos
    if len(df) < 10:
        return {'error': 'Datos insuficientes para detectar anomalías'}
    
    # Agrupar por activo y sensor
    grupos = df.groupby(['activo_id', 'sensor_id'])
    
    anomalias = []
    
    for (activo_id, sensor_id), grupo in grupos:
        # Ordenar por fecha
        grupo = grupo.sort_values('fecha')
        
        # Calcular estadísticas
        valores = grupo['valor']
        media = valores.mean()
        std = valores.std()
        
        if std == 0:
            # Si desviación estándar es 0, no podemos calcular Z-score
            continue
            
        # Calcular Z-score
        z_scores = (valores - media) / std
        
        # Identificar anomalías
        anomalias_indices = (z_scores.abs() > umbral_zscore)
        
        if anomalias_indices.any():
            # Obtener registros anómalos
            anomalias_grupo = grupo[anomalias_indices]
            
            for _, row in anomalias_grupo.iterrows():
                anomalias.append({
                    'activo_id': activo_id,
                    'sensor_id': sensor_id,
                    'valor': row['valor'],
                    'fecha': row['fecha'],
                    'z_score': z_scores[row.name],
                    'media': media,
                    'desviacion': std
                })
    
    # Visualización
    if anomalias:
        # Agrupar anomalías por activo para visualización
        df_anomalias = pd.DataFrame(anomalias)
        activos_unicos = df_anomalias['activo_id'].unique()
        
        # Crear subplots para cada activo (máximo 6)
        max_activos = min(6, len(activos_unicos))
        fig, axes = plt.subplots(max_activos, 1, figsize=(12, 3*max_activos))
        
        if max_activos == 1:
            axes = [axes]
        
        for i, activo_id in enumerate(activos_unicos[:max_activos]):
            ax = axes[i]
            
            # Filtrar datos del activo
            df_activo = df[df['activo_id'] == activo_id]
            df_anomalias_activo = df_anomalias[df_anomalias['activo_id'] == activo_id]
            
            # Agrupar por sensor
            sensores = df_activo['sensor_id'].unique()
            
            for sensor_id in sensores:
                # Datos normales
                sensor_data = df_activo[df_activo['sensor_id'] == sensor_id]
                ax.plot(
                    pd.to_datetime(sensor_data['fecha']), 
                    sensor_data['valor'],
                    'o-',
                    label=f'Sensor {sensor_id}',
                    alpha=0.5,
                    markersize=4
                )
                
                # Anomalías
                anomalias_sensor = df_anomalias_activo[df_anomalias_activo['sensor_id'] == sensor_id]
                if not anomalias_sensor.empty:
                    ax.scatter(
                        pd.to_datetime(anomalias_sensor['fecha']),
                        anomalias_sensor['valor'],
                        color='red',
                        s=80,
                        marker='*',
                        label=f'Anomalías Sensor {sensor_id}'
                    )
            
            ax.set_title(f'Activo ID: {activo_id}')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Valor')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar gráfico en memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        grafico = f"data:image/png;base64,{imagen_base64}"
    else:
        grafico = None
    
    return {
        'anomalias': anomalias,
        'total_anomalias': len(anomalias),
        'grafico': grafico
    }