import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json

# Cargar los datos
region = pd.read_csv('C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data/region.csv', encoding='ISO-8859-1')
infra_data = pd.read_csv('C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data/infraestructura_2021.csv')
tarifas_data = pd.read_csv('C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data/tarifas_2021.csv')

merged_data = pd.merge(tarifas_data, infra_data, on='id_region', how='inner')
merged_data = pd.merge(merged_data, region, on='id_region', how='inner')

# Datos para boxplots e histogramas
datos_base = merged_data['base']
datos_intermedia = merged_data['intermedia']
datos_punta = merged_data['punta']
datos_capacidad = merged_data['capacidad']
datos_distribucion = merged_data['distribucion']

# Agrupar los datos por división y mes
data_grouped = merged_data.groupby(['division', 'mes_x']).agg({
    'base': 'mean',
    'intermedia': 'mean',
    'punta': 'mean',
    'distribucion': 'mean',
    'capacidad': 'mean'
}).reset_index()

# Datos agrupados por estado y mes:

data_grouped_estado = merged_data.groupby(['estado', 'mes_x']).agg({
    'base': ['mean', 'max', 'min'],
    'intermedia': ['mean', 'max', 'min'],
    'punta': ['mean', 'max', 'min'],
    'distribucion': ['mean', 'max', 'min'],
    'capacidad': ['mean', 'max', 'min']
}).reset_index()

# Aplanamos la df

data_grouped_estado.columns = ['estado', 'mes_x',
                               'base_mean', 'base_max', 'base_min',
                               'intermedia_mean', 'intermedia_max', 'intermedia_min',
                               'punta_mean', 'punta_max', 'punta_min',
                               'distribucion_mean', 'distribucion_max', 'distribucion_min',
                               'capacidad_mean', 'capacidad_max', 'capacidad_min']

# Definir el orden correcto de los meses
orden_meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
data_grouped['mes_x'] = pd.Categorical(data_grouped['mes_x'], categories=orden_meses, ordered=True)
data_grouped = data_grouped.sort_values(by=['division', 'mes_x'])
data_grouped_estado['mes_x'] = pd.Categorical(data_grouped_estado['mes_x'], categories=orden_meses, ordered=True)
data_grouped_estado = data_grouped_estado.sort_values(by=['estado', 'mes_x'])

# Para el mapa

with open('C:/Users/Francisco Valerio/Desktop/Work work/Atco/GDMTH-Project/data/mexicov2.geojson', encoding = 'utf-8') as f:

     geojson_data = json.load(f)

for feature in geojson_data['features']:

    if isinstance(feature['properties']['sta_name'], list):

        feature['properties']['sta_name'][0] = feature['properties']['sta_name'][0].upper()

# Diccionario de mapeo para normalizar los nombres de estados
mapeo_estados = {
    'AGUASCALIENTES': 'AGUASCALIENTES',
    'BAJA CALIFORNIA': 'BAJA CALIFORNIA',
    'BAJA CALIFORNIA SUR': 'BAJA CALIFORNIA SUR',
    'CAMPECHE': 'CAMPECHE',
    'CHIAPAS': 'CHIAPAS',
    'CHIHUAHUA': 'CHIHUAHUA',
    'CIUDAD DE MÉXICO': 'CIUDAD DE MÉXICO',
    'COAHUILA DE ZARAGOZA': 'COAHUILA',
    'COLIMA': 'COLIMA',
    'DURANGO': 'DURANGO',
    'MÉXICO': 'ESTADO DE MÉXICO',  # Normalizar a 'ESTADO DE MÉXICO'
    'GUANAJUATO': 'GUANAJUATO',
    'GUERRERO': 'GUERRERO',
    'HIDALGO': 'HIDALGO',
    'JALISCO': 'JALISCO',
    'MICHOACÁN DE OCAMPO': 'MICHOACÁN',
    'MORELOS': 'MORELOS',
    'NAYARIT': 'NAYARIT',
    'NUEVO LEÓN': 'NUEVO LEÓN',
    'OAXACA': 'OAXACA',
    'PUEBLA': 'PUEBLA',
    'QUERÉTARO': 'QUERÉTARO',
    'QUINTANA ROO': 'QUINTANA ROO',
    'SAN LUIS POTOSÍ': 'SAN LUIS POTOSÍ',
    'SINALOA': 'SINALOA',
    'SONORA': 'SONORA',
    'TABASCO': 'TABASCO',
    'TAMAULIPAS': 'TAMAULIPAS',
    'TLAXCALA': 'TLAXCALA',
    'VERACRUZ DE IGNACIO DE LA LLAVE': 'VERACRUZ',
    'YUCATÁN': 'YUCATÁN',
    'ZACATECAS': 'ZACATECAS'
}

# Convertir los nombres en el GeoJSON según el mapeo
for feature in geojson_data['features']:
    nombre_estado = feature['properties']['sta_name'][0].upper()
    if nombre_estado in mapeo_estados:
        feature['properties']['sta_name'][0] = mapeo_estados[nombre_estado]


# Inicializamos la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Crear los gráficos

# Crear los boxplots de tarifas
boxplots_tarifas = go.Figure()
boxplots_tarifas.add_trace(go.Box(x=datos_base, name='Base', marker_color='blue'))
boxplots_tarifas.add_trace(go.Box(x=datos_intermedia, name='Intermedia', marker_color='green'))
boxplots_tarifas.add_trace(go.Box(x=datos_punta, name='Punta', marker_color='red'))
boxplots_tarifas.update_layout(
    title_text='Boxplots de los datos de Base, Intermedia y Punta del año 2021',
    yaxis_title_text='$/kWh',
    boxmode='group'
)

# Crear los boxplots de infraestructura
boxplots_infraestructura = go.Figure()
boxplots_infraestructura.add_trace(go.Box(x=datos_capacidad, name='Capacidad', marker_color='purple'))
boxplots_infraestructura.add_trace(go.Box(x=datos_distribucion, name='Distribución', marker_color='orange'))
boxplots_infraestructura.update_layout(
    title_text='Boxplots de los datos de Distribución y Capacidad del año 2021',
    yaxis_title_text='$/kW',
    boxmode='group'
)

# Gráfico de barras
division_means = data_grouped.groupby('division')['base'].mean().reset_index()
bar_chart = px.bar(division_means, 
                   x='division', 
                   y='base', 
                   title='Tarifa Base Promedio por División',
                   labels={'base': 'Tarifa Base Promedio', 'division': 'División'})

# Gráfico de dispersión
scatter_plot = px.scatter(data_grouped, 
                          x='mes_x', 
                          y='base', 
                          color='division',
                          title='Tarifa Base por Mes y División',
                          labels={'base': 'Base', 'mes_x': 'Mes', 'division': 'División'})

# Histograma de capacidad y distribución
datos_capacidad = merged_data['capacidad']
datos_distribucion = merged_data['distribucion']

histograma_infraestructura = go.Figure()

histograma_infraestructura.add_trace(go.Histogram(x=datos_capacidad, name='Capacidad', marker_color='purple'))
histograma_infraestructura.add_trace(go.Histogram(x=datos_distribucion, name='Distribución', marker_color='orange'))

histograma_infraestructura.update_layout(
    title_text='Distribución de los datos de Capacidad y Distribución del año 2021',
    barmode='overlay',
    xaxis_title_text='$/kW',
    yaxis_title_text='Frecuencia',
    bargap=0.2,
    bargroupgap=0.1,
    xaxis_tickfont = dict(size=12),
    yaxis_tickfont=dict(size=12)
)

histograma_infraestructura.update_traces(opacity=0.75)

# Layout de la aplicación
app.layout = html.Div([
    dcc.Tabs(id="tabs-example", value = 'tab-1', children=[
        dcc.Tab(label='Análisis exploratorio', value = 'tab-1'),
        dcc.Tab(label='Análisis de correlación',value='tab-2'),
        dcc.Tab(label='Análisis de tendencias', value='tab-3'),
        dcc.Tab(label='Análisis de Tarifas', value='tab-4'),
        dcc.Tab(label='Análisis por ubicación', value='tab-5')
    ]),
    html.Div(id='tabs-content')
])

# Callback para actualizar el contenido de las pestañas

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs-example', 'value')]
)

def render_content(tab):
    if tab == 'tab-1':
        # Contenido para análisis exploratorio
        return html.Div([
            html.H1("Análisis exploratorio de datos"),
            # Dropdown para seleccionar el tipo de gráfico
            html.Div(className='dropdown-container', children=[
                html.Label('Selecciona el gráfico que deseas ver:'),
                dcc.Dropdown(
                    id='graph-selector',
                    options=[
                        {'label': 'Histograma de Tarifas', 'value': 'histogram'},
                        {'label': 'Histograma de Infraestructura', 'value': 'infra_histogram'},
                        {'label': 'Boxplot de Tarifas', 'value': 'boxplot_tarifas'},
                        {'label': 'Boxplot de Infraestructura', 'value': 'boxplot_infraestructura'}
                    ],
                    value='histogram',
                    className='dropdown'
                )
            ]),

            # Tarjetas estilo PowerBI
            html.Div(id='cards-container', children=[
                # Tarjetas para 'base'
                html.Div(className='card', children=[
                    html.Div("Base [$/kWh]", className="card-title"),
                    html.Div(id='card-mean-base', className='card-value'),
                    html.Div(id='card-std-base', className='card-value'),
                    html.Div(id='card-max-base', className='card-value'),
                    html.Div(id='card-min-base', className='card-value')
                ], style={'margin': '10px'}),

                # Tarjetas para 'intermedia'
                html.Div(className='card', children=[
                    html.Div("Intermedia [$/kWh]", className="card-title"),
                    html.Div(id='card-mean-intermedia', className='card-value'),
                    html.Div(id='card-std-intermedia', className='card-value'),
                    html.Div(id='card-max-intermedia', className='card-value'),
                    html.Div(id='card-min-intermedia', className='card-value')
                ], style={'margin': '10px', 'width': '220px'}),

                # Tarjetas para 'punta'
                html.Div(className='card', children=[
                    html.Div("Punta [$/kWh]", className="card-title"),
                    html.Div(id='card-mean-punta', className='card-value'),
                    html.Div(id='card-std-punta', className='card-value'),
                    html.Div(id='card-max-punta', className='card-value'),
                    html.Div(id='card-min-punta', className='card-value')
                ], style={'margin': '10px'}),

                # Tarjetas para 'distribucion'
                html.Div(className='card', children=[
                    html.Div("Distribución [$/kW]", className="card-title"),
                    html.Div(id='card-mean-distribucion', className='card-value'),
                    html.Div(id='card-std-distribucion', className='card-value'),
                    html.Div(id='card-max-distribucion', className='card-value'),
                    html.Div(id='card-min-distribucion', className='card-value')
                ], style={'margin': '10px', 'width': '220px'}),

                # Tarjetas para 'capacidad'
                html.Div(className='card', children=[
                    html.Div("Capacidad [$/kW]", className="card-title"),
                    html.Div(id='card-mean-capacidad', className='card-value'),
                    html.Div(id='card-std-capacidad', className='card-value'),
                    html.Div(id='card-max-capacidad', className='card-value'),
                    html.Div(id='card-min-capacidad', className='card-value')
                ], style={'margin': '10px', 'width': '220px'}),
            ], style={'display': 'flex', 'justify-content': 'space-around', 'flex-wrap': 'wrap'}),

            # Gráfico dinámico
            dcc.Graph(id='selected-graph')
        ])
    
    elif tab == 'tab-2':

        corr_matrix = data_grouped[['base', 'intermedia', 'punta', 'distribucion', 'capacidad']].corr()

        matrix_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='Viridis',
        zmin=-1, zmax=1
        ))

        matrix_corr.update_layout(
        title='Matriz de correlación entre tarifas del año 2021',
        xaxis_nticks=36,
        width=1000,
        height=800
        )

         # Añadir anotaciones en el heatmap
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                matrix_corr.add_annotation(
                    x=corr_matrix.columns[i],
                    y=corr_matrix.columns[j],
                    text=str(round(corr_matrix.values[i][j], 2)),
                    showarrow=False,
                    font=dict(color="white")  # Ajusta el color del texto
            )
                
        # Gráficos de dispersión para pares con correlación alta
        scatter_corr_pos = px.scatter(data_grouped,
                                      x = 'base',
                                      y = 'intermedia',
                                      title = 'Correlación positiva alta: Base vs Intermedia',
                                      labels = {'base': 'Base', 'intermedia': 'Intermedia'})
        
        scatter_corr_neg = px.scatter(data_grouped,
                                      x = 'base',
                                      y = 'capacidad',
                                      title = 'Correlación negativa alta: Base vs Capacidad',
                                      labels = {'base': 'Base', 'capacidad': 'Capacidad'})
        
        # Interpretación para la correlación

        interpretacion_corr = html.Div([
        html.H2('Interpretación de la correlación'),
        html.P('La correlación mide la relación entre dos variables.'
               'Los valores de correlación varían entre -1 y 1, donde:'),
        html.Ul([
            html.Li('1.0 a 0.7: Correlación positiva fuerte'),
            html.Li('0.7 a 0.3: Correlación positiva moderada'),
            html.Li('0.3 a 0.0: Correlación positiva débil'),
            html.Li('0.0 a -0.3: Correlación negativa débil'),
            html.Li('-0.3 a -0.7: Correlación negativa moderada'),
            html.Li('-0.7 a -1.0: Correlación negativa fuerte')
        ]),
        html.P('Una correlación positiva implica que ambas variables tienden a aumentar o '
               'disminuir juntas, mientras que una correlación negativa implica que una variable '
               'aumenta mientras la otra disminuye.'),
        html.P('Observamos que en la matriz de correlación ')
        ])


        #Contenido para análisis de correlación

        return html.Div([
        html.H1('Análisis de Correlación'),
        html.Div([
            # Colocar la matriz de correlación a la izquierda (más ancho) y la interpretación a la derecha (menos ancho)
            html.Div(dcc.Graph(figure=matrix_corr), style={'display': 'inline-block', 'width': '60%'}),
            html.Div(interpretacion_corr, style={'display': 'inline-block', 'width': '38%', 'verticalAlign': 'top'}),
        ]),
        html.Div([
            # Gráficos de dispersión
            dcc.Graph(figure=scatter_corr_pos, style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(figure=scatter_corr_neg, style={'display': 'inline-block', 'width': '50%'}),
        ])
    ])
    
    elif tab == 'tab-3':

        # Contenido para análisis de tendencias

        return html.Div([
            html.H1('Análisis de Tendencias'),

            # Dropdown para seleccionar la variable a visualizar

            html.Div(className = 'dropdown-container', children=[
                html.Label('Selecciona la variable que deseas visualizar:'),
                dcc.Dropdown(
                    id='tendencias-selector',
                    options=[
                    {'label': 'Base', 'value': 'base'},
                    {'label': 'Intermedia', 'value': 'intermedia'},
                    {'label': 'Punta', 'value': 'punta'},
                    {'label': 'Capacidad', 'value': 'capacidad'},
                    {'label': 'Distribución', 'value': 'distribucion'}
                    ],
                    value = 'base',
                    className = 'dropdown'
                )
            ]),

            dcc.Graph(id = 'tendencias-graph')
        ])

    elif tab == 'tab-4':
        
        return html.Div([
            html.H1('Comportamiento de las tarifas por Estado'),
            html.Label('Selecciona una tarifa:'),
            dcc.Dropdown(
                id='max-tarifa-selector',
                options=[
                    {'label': 'Base', 'value': 'base_max'},
                    {'label': 'Intermedia', 'value': 'intermedia_max'},
                    {'label': 'Distribución', 'value': 'distribucion_max'},
                    {'label': 'Capacidad', 'value': 'capacidad_max'}
                ],
                value = 'base_max',
                clearable = False
            ),
            dcc.Graph(id='max-tarifa-graph')
        ])
    
    elif tab == 'tab-5':

        return html.Div([
            html.H1("Visualización de tarifas por estado"),
            html.Label("Selecciona una tarifa:"),
            dcc.Dropdown(
                id='map-tarifa-selector',
                options=[
                    {'label': 'Base', 'value': 'base_mean'},
                    {'label': 'Intermedia', 'value': 'intermedia_mean'},
                    {'label': 'Punta', 'value': 'punta_mean'},
                    {'label': 'Distribución', 'value':'distribucion_mean'},
                    {'label': 'Capacidad', 'value': 'capacidad_mean'}
                ],
                value = 'base_mean',
                clearable=False,
                className='dropdown'
            ),
            dcc.Graph(id='map-graph')
        ])
        

# Callback para actualizar las tarjetas con estadísticas clave
@app.callback(
    [Output('card-mean-base', 'children'),
     Output('card-std-base', 'children'),
     Output('card-max-base', 'children'),
     Output('card-min-base', 'children'),
     Output('card-mean-intermedia', 'children'),
     Output('card-std-intermedia', 'children'),
     Output('card-max-intermedia', 'children'),
     Output('card-min-intermedia', 'children'),
     Output('card-mean-punta', 'children'),
     Output('card-std-punta', 'children'),
     Output('card-max-punta', 'children'),
     Output('card-min-punta', 'children'),
     Output('card-mean-distribucion', 'children'),
     Output('card-std-distribucion', 'children'),
     Output('card-max-distribucion', 'children'),
     Output('card-min-distribucion', 'children'),
     Output('card-mean-capacidad', 'children'),
     Output('card-std-capacidad', 'children'),
     Output('card-max-capacidad', 'children'),
     Output('card-min-capacidad', 'children')],
    [Input('graph-selector', 'value')]
)
def update_cards(selected_graph):
    # Estadísticas para cada variable
    base_stats = {
        'mean': merged_data['base'].mean(),
        'std': merged_data['base'].std(),
        'max': merged_data['base'].max(),
        'min': merged_data['base'].min()
    }
    intermedia_stats = {
        'mean': merged_data['intermedia'].mean(),
        'std': merged_data['intermedia'].std(),
        'max': merged_data['intermedia'].max(),
        'min': merged_data['intermedia'].min()
    }
    punta_stats = {
        'mean': merged_data['punta'].mean(),
        'std': merged_data['punta'].std(),
        'max': merged_data['punta'].max(),
        'min': merged_data['punta'].min()
    }
    distribucion_stats = {
        'mean': merged_data['distribucion'].mean(),
        'std': merged_data['distribucion'].std(),
        'max': merged_data['distribucion'].max(),
        'min': merged_data['distribucion'].min()
    }
    capacidad_stats = {
        'mean': merged_data['capacidad'].mean(),
        'std': merged_data['capacidad'].std(),
        'max': merged_data['capacidad'].max(),
        'min': merged_data['capacidad'].min()
    }

    # Devolver los valores a las tarjetas
    return [
        f"Promedio: {base_stats['mean']:.2f}",
        f"Std: {base_stats['std']:.2f}",
        f"Máximo: {base_stats['max']:.2f}",
        f"Mínimo: {base_stats['min']:.2f}",
        f"Promedio: {intermedia_stats['mean']:.2f}",
        f"Std: {intermedia_stats['std']:.2f}",
        f"Máximo: {intermedia_stats['max']:.2f}",
        f"Mínimo: {intermedia_stats['min']:.2f}",
        f"Promedio: {punta_stats['mean']:.2f}",
        f"Std: {punta_stats['std']:.2f}",
        f"Máximo: {punta_stats['max']:.2f}",
        f"Mínimo: {punta_stats['min']:.2f}",
        f"Promedio: {distribucion_stats['mean']:.2f}",
        f"Std: {distribucion_stats['std']:.2f}",
        f"Máximo: {distribucion_stats['max']:.2f}",
        f"Mínimo: {distribucion_stats['min']:.2f}",
        f"Promedio: {capacidad_stats['mean']:.2f}",
        f"Std: {capacidad_stats['std']:.2f}",
        f"Máximo: {capacidad_stats['max']:.2f}",
        f"Mínimo: {capacidad_stats['min']:.2f}"
    ]

# Callback para actualizar el gráfico dinámico según el tipo de gráfico seleccionado
@app.callback(
    Output('selected-graph', 'figure'),
    [Input('graph-selector', 'value')]
)
def update_graph(selected_graph):
    # Crear el gráfico dependiendo de la selección
    if selected_graph == 'histogram':
        # Crear el histograma de tarifas
        histograma_tarifas = go.Figure()
        histograma_tarifas.add_trace(go.Histogram(x=merged_data['base'], name='Tarifa Base', marker_color='blue'))
        histograma_tarifas.add_trace(go.Histogram(x=merged_data['intermedia'], name='Tarifa Intermedia', marker_color='green'))
        histograma_tarifas.add_trace(go.Histogram(x=merged_data['punta'], name='Tarifa Punta', marker_color='red'))
        histograma_tarifas.update_layout(
            title_text='Distribución de los datos de tarifas Base, Intermedia y Punta del año 2021',
            barmode='overlay',
            xaxis_title_text='$/kWh',
            yaxis_title_text='Frecuencia',
            bargap=0.2,
            bargroupgap=0.1
        )
        histograma_tarifas.update_traces(opacity=0.75)
        return histograma_tarifas
    
    elif selected_graph == 'infra_histogram':
        # Devolver el histograma de infraestructura
        return histograma_infraestructura
    
    elif selected_graph == 'boxplot_tarifas':
        return boxplots_tarifas
    
    elif selected_graph == 'boxplot_infraestructura':
        return boxplots_infraestructura

@app.callback(
    Output('tendencias-graph', 'figure'),
    [Input('tendencias-selector', 'value')]
)
def update_tendencias_graph(selected_variable):
    # Crear un gráfico basado en la variable seleccionada
    if selected_variable == 'base':
        fig = px.scatter(data_grouped, 
                         x='mes_x', 
                         y='base', 
                         color='division',
                         title='Tarifa Base por Mes y División',
                         labels={'base': 'Base', 'mes_x': 'Mes', 'division': 'División'})
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            yaxis_title_text = 'Base [$/kWh]',
            xaxis_tickfont = dict(size=12),
            yaxis_tickfont = dict(size=12)
        )
        
    elif selected_variable == 'intermedia':
        fig = px.scatter(data_grouped, 
                         x='mes_x', 
                         y='intermedia', 
                         color='division',
                         title='Tarifa Intermedia por Mes y División',
                         labels={'intermedia': 'Intermedia', 'mes_x': 'Mes', 'division': 'División'})
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            yaxis_title_text = 'Intermedia [$/kWh]',
            xaxis_tickfont = dict(size=12),
            yaxis_tickfont = dict(size=12)
        )
        
    elif selected_variable == 'punta':
        fig = px.scatter(data_grouped, 
                         x='mes_x', 
                         y='punta', 
                         color='division',
                         title='Tarifa Punta por Mes y División',
                         labels={'punta': 'Punta', 'mes_x': 'Mes', 'division': 'División'})
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            yaxis_title_text = 'Punta [$/kWh]',
            xaxis_tickfont = dict(size=12),
            yaxis_tickfont = dict(size=12)
        )
        
    elif selected_variable == 'capacidad':

        fig = px.scatter(data_grouped, 
                         x='mes_x', 
                         y='capacidad', 
                         color='division',
                         title='Tarifa Capacidad por Mes y División',
                         labels={'capacidad': 'Capacidad', 'mes_x': 'Mes', 'division': 'División'})
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            yaxis_title_text = 'Capacidad [$/kW]',
            xaxis_tickfont = dict(size=12),
            yaxis_tickfont = dict(size=12)
        )
        
    elif selected_variable == 'distribucion':

        fig = px.scatter(data_grouped, 
                         x='mes_x', 
                         y='distribucion', 
                         color='division',
                         title='Tarifa Punta por Mes y División',
                         labels={'distribucion': 'Distribución', 'mes_x': 'Mes', 'division': 'División'})
        fig.update_traces(mode='lines+markers')
        fig.update_layout(
            yaxis_title_text = 'Distribución [$/kW]',
            xaxis_tickfont = dict(size=12),
            yaxis_tickfont = dict(size=12)
        )

    # Retornar el gráfico
    return fig

@app.callback(
    Output('max-tarifa-graph', 'figure'),
    [Input('max-tarifa-selector', 'value')]
)

def update_max_tarifa_graph(selected_tarifa):

    # Extraemos los el top 10 de estados con la tarifa más alta seleccionada

    top_10_estados = data_grouped_estado.groupby('estado')[selected_tarifa].max().reset_index().sort_values(by = selected_tarifa, ascending = False).head(10)

    # Creamos la gráfica

    tarifa_name = selected_tarifa.split('_')[0].capitalize()

    fig = px.bar(top_10_estados,
                 x = selected_tarifa,
                 y = 'estado',
                 orientation = 'h',
                 title = f'Top 10 de estados con mayor tarifa {tarifa_name}',
                 labels = {selected_tarifa: f'Tarifa {tarifa_name} Máxima'},
                 text = selected_tarifa,
                 color = 'estado'
                 )
    
    fig.update_layout(
        xaxis_title = '$/kWh',
        yaxis_title = 'Estado',
        xaxis_tickfont = dict(size = 12),
        yaxis_tickfont = dict(size = 12)
    )

    return fig

# Diccionario de mapeo para nombres más amigables
tarifa_labels = {
    'base_mean': 'Tarifa Base',
    'intermedia_mean': 'Tarifa Intermedia',
    'punta_mean': 'Tarifa Punta',
    'distribucion_mean': 'Tarifa Distribución',
    'capacidad_mean': 'Tarifa Capacidad'
}

@app.callback(
    Output('map-graph', 'figure'),
    [Input('map-tarifa-selector', 'value')]
)

def update_map_graph(selected_tarifa):

    fig = px.choropleth_mapbox(
        data_grouped_estado,
        geojson=geojson_data,
        locations = 'estado',
        featureidkey='properties.sta_name[0]',
        color = selected_tarifa,
        mapbox_style='carto-positron',
        zoom = 4,
        center={"lat": 23.6345, "lon": -102.5528},
        opacity=0.7,
        labels={selected_tarifa: tarifa_labels[selected_tarifa]}
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

    

# Ejecutar la aplicación de Dash
if __name__ == '__main__':
    app.run_server(debug=True)
