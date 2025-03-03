# Sistema de Control de Activos - Planta de Carbonato de Litio

Sistema completo para la gestión y control de activos industriales, con módulos para inventario, stock, criticidad, obsolescencia y mantenimiento. Incluye funcionalidades avanzadas de IA y machine learning para predicción de fallas y optimización de mantenimiento.

## Características principales

- **Gestión completa de activos**: Registro, seguimiento y administración de todos los activos de la planta.
- **Control de stock**: Gestión del inventario, movimientos de entrada/salida y niveles de stock.
- **Activos críticos**: Evaluación y clasificación de criticidad con análisis automático mediante IA.
- **Activos obsoletos**: Gestión de equipos en fin de vida útil, planificación de renovación.
- **Mantenimiento integral**: Preventivo, correctivo y predictivo, con seguimiento y análisis.
- **Inteligencia Artificial**: Predicción de fallas, detección de anomalías, optimización de mantenimiento.
- **Interfaz moderna y responsiva**: Diseño intuitivo adaptado a diferentes dispositivos.
- **Escalable y modular**: Arquitectura diseñada para ampliarse según necesidades futuras.

## Tecnologías utilizadas

- **Backend**: Python 3.8+ con Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de datos**: SQLite (configurable para PostgreSQL/MySQL)
- **Machine Learning**: scikit-learn, pandas, numpy
- **Visualización**: Matplotlib, Chart.js
- **Procesamiento de datos**: pandas, openpyxl

## Requisitos del sistema

- Python 3.6 o superior
- Pip (gestor de paquetes de Python)
- 2GB de RAM o superior
- 500MB de espacio en disco
- Sistema operativo: Windows 10/11, macOS, Linux

## Instalación rápida

### Método automático

Ejecute el script de instalación que configurará todo automáticamente:

```bash
python install.py
```

### Instalación manual

1. Clone el repositorio:
```bash
git clone https://github.com/su-usuario/control-activos-litio.git
cd control-activos-litio
```

2. Cree y active un entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Instale las dependencias:
```bash
pip install -r requirements.txt
```

4. Configure la base de datos:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Cree un superusuario:
```bash
python manage.py createsuperuser
```

6. Inicie el servidor:
```bash
python manage.py runserver
```

7. Acceda a la aplicación en su navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Estructura del proyecto

```
control_activos/
│
├── activos/             # Aplicación de gestión de activos
├── stock/               # Aplicación de control de stock
├── criticos/            # Aplicación de activos críticos
├── obsoletos/           # Aplicación de activos obsoletos
├── mantenimiento/       # Aplicación de mantenimiento
│
├── static/              # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/               # Archivos subidos por usuarios
│   ├── activos/         # Imágenes de activos
│   └── models/          # Modelos de ML entrenados
│
├── templates/           # Plantillas HTML
│   ├── base.html        # Plantilla base
│   ├── home.html        # Página de inicio
│   ├── activos/         # Plantillas específicas de activos
│   ├── stock/           # Plantillas específicas de stock
│   ├── criticos/        # Plantillas específicas de activos críticos
│   ├── obsoletos/       # Plantillas específicas de activos obsoletos
│   ├── mantenimiento/   # Plantillas específicas de mantenimiento
│   └── ai/              # Plantillas para funcionalidades de IA
│
├── utils/               # Utilidades y funciones auxiliares
│   └── ai_module.py     # Módulo de IA y machine learning
│
├── control_activos/     # Configuración del proyecto Django
│   ├── settings.py      # Configuración general
│   ├── urls.py          # URLs principales
│   └── wsgi.py          # Configuración WSGI
│
├── manage.py            # Script de gestión de Django
├── install.py           # Script de instalación automática
└── requirements.txt     # Dependencias del proyecto
```

## Módulos del sistema

### 1. Gestión de Activos

- Registro completo de activos con información técnica
- Organización por áreas y subáreas
- Filtrado y búsqueda avanzada
- Carga masiva desde archivos Excel
- Gestión de fabricantes y ubicaciones

### 2. Control de Stock

- Seguimiento de activos en inventario
- Registro de movimientos (entradas/salidas)
- Alertas de stock mínimo
- Sincronización con el módulo de activos
- Informes de inventario

### 3. Activos Críticos

- Evaluación de criticidad basada en múltiples factores
- Cálculo automático mediante IA (K-means clustering)
- Estrategias recomendadas según nivel de criticidad
- Visualización gráfica de distribución de criticidad
- Exportación a Excel para informes

### 4. Activos Obsoletos

- Registro de activos en fin de vida útil
- Planificación de renovación
- Análisis de impacto
- Presupuestos estimados
- Estrategias de mitigación

### 5. Mantenimiento

- Gestión integral de mantenimientos (preventivo, correctivo, predictivo)
- Programación y seguimiento de actividades
- Asignación de responsables
- Registro de costos y tiempos
- Análisis de eficiencia
- Plan de mantenimiento predictivo con umbrales configurables

### 6. Inteligencia Artificial y Machine Learning

- **Análisis de criticidad**: Clasificación automática mediante clustering
- **Predicción de fallas**: Algoritmos de Random Forest para predecir posibles fallos
- **Optimización de mantenimiento**: Determinación de intervalos óptimos de mantenimiento
- **Detección de anomalías**: Identificación de lecturas anómalas mediante análisis estadístico

## Funcionalidades de IA y Machine Learning

El sistema incorpora avanzados algoritmos de inteligencia artificial y machine learning:

### Algoritmos implementados:

1. **K-means clustering** para clasificación automática de criticidad
2. **Random Forest Classifier** para predicción de fallas
3. **Random Forest Regressor** para optimización de intervalos de mantenimiento
4. **Análisis estadístico (Z-score)** para detección de anomalías en lecturas

### Beneficios:

- **Objetividad**: Evaluaciones basadas en datos, no en percepciones subjetivas
- **Anticipación**: Detección temprana de posibles problemas
- **Optimización**: Mantenimiento en el momento justo, ni antes ni después
- **Reducción de costos**: Menos paradas no programadas, mejor uso de recursos

## Ejemplos de uso

### Flujo típico de trabajo:

1. Registro de activos en el sistema (manual o mediante carga masiva)
2. Evaluación automática de criticidad mediante IA
3. Configuración de planes de mantenimiento predictivo
4. Registro de lecturas y parámetros de operación
5. El sistema predice posibles fallas y recomienda mantenimientos preventivos
6. Registro y seguimiento de las actividades de mantenimiento
7. Análisis de eficiencia y ajuste de estrategias

## Contribuir al proyecto

Las contribuciones son bienvenidas. Para contribuir:

1. Haga un fork del repositorio
2. Cree una rama para su funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haga commit de sus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Empuje a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abra un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para preguntas, soporte o sugerencias, por favor contacte a:
- Correo: soporte@control-activos.com
- Sitio web: https://www.control-activos.com

---

Desarrollado para la gestión eficiente de activos en plantas de procesamiento de litio y adaptable a diversos entornos industriales.