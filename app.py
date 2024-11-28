import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

# Configuración de conexión a PostgreSQL usando SQLAlchemy en Render
engine = create_engine("postgresql://odonto_user:LL2eqeYoNymQWJy2hnZ1amMb4ZIq7KSt@dpg-csqhjraj1k6c738ik110-a.virginia-postgres.render.com/odonto")

# Función para obtener datos de PostgreSQL
def obtener_datos():
    try:
        # Consulta para obtener número de pacientes
        total_pacientes = pd.read_sql("SELECT COUNT(*) AS total_pacientes FROM Pacientes", engine).iloc[0, 0]
        
        # Consulta para obtener número de citas
        total_citas = pd.read_sql("SELECT COUNT(*) AS total_citas FROM Citas", engine).iloc[0, 0]
        
        # Consulta para obtener ingresos totales por pagos
        total_ingresos = pd.read_sql("SELECT SUM(monto) AS total_ingresos FROM Pagos", engine).iloc[0, 0]

        # Consulta para obtener ingresos por año
        ingresos_anuales = pd.read_sql("""
            SELECT DATE_PART('year', fecha) AS año, SUM(monto) AS ingresos
            FROM Pagos
            GROUP BY año
            ORDER BY año;
        """, engine)

        # Consulta para obtener el estado de las facturas (pagadas o pendientes)
        estado_cuentas = pd.read_sql("""
            SELECT estado, COUNT(*) AS total
            FROM Facturas
            GROUP BY estado;
        """, engine)

        # Consulta para obtener los días más saturados
        dias_saturados = pd.read_sql("""
            SELECT TO_CHAR(fecha_hora, 'Day') AS dia, COUNT(*) AS total_citas
            FROM Citas
            GROUP BY dia
            ORDER BY total_citas DESC;
        """, engine)

    except Exception as e:
        print("Error al obtener datos:", e)
        total_pacientes = 0
        total_citas = 0
        total_ingresos = 0.0
        ingresos_anuales = pd.DataFrame(columns=['año', 'ingresos'])
        estado_cuentas = pd.DataFrame(columns=['estado', 'total'])
        dias_saturados = pd.DataFrame(columns=['dia', 'total_citas'])

    return total_pacientes, total_citas, total_ingresos, ingresos_anuales, estado_cuentas, dias_saturados

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación con dcc.Interval para actualizar
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f9f9f9', 'padding': '20px'}, children=[
    html.H1(children='Dashboard de Clínica Dental', style={'textAlign': 'center', 'color': '#333333'}),
    
    html.Div(children='''Análisis y visualización de datos clínicos.''', style={'textAlign': 'center', 'marginBottom': '40px', 'color': '#555555'}),

    # Widgets de información general
    html.Div(id='widgets-container', style={'display': 'flex', 'justifyContent': 'space-between', 'flexWrap': 'wrap'}),

    # Gráficos de KPI's
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between'}, children=[
        html.Div(style={'flex': '1 1 45%', 'margin': '10px'}, children=[dcc.Graph(id='grafico-ingresos-anuales')]),
        html.Div(style={'flex': '1 1 45%', 'margin': '10px'}, children=[dcc.Graph(id='grafico-estado-cuentas')]),
        html.Div(style={'flex': '1 1 45%', 'margin': '10px'}, children=[dcc.Graph(id='grafico-dias-saturados')]),
    ]),

    # Intervalo de actualización cada 60 segundos
    dcc.Interval(
        id='interval-component',
        interval=3*1000,  # 3 segundos
        n_intervals=0
    )
])

# Callback para actualizar los widgets de información general
@app.callback(
    Output('widgets-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def actualizar_widgets(n):
    total_pacientes, total_citas, total_ingresos, _, _, _ = obtener_datos()
    return [
        create_widget('PACIENTES', f"{total_pacientes:,}", False, 'Cantidad de pacientes', '👥', 'crimson'),
        create_widget('CITAS', f"{total_citas:,}", False, 'Cantidad de citas', '📅', 'goldenrod'),
        create_widget('INGRESOS', f"{total_ingresos:,.2f}", True, 'Ingresos totales', '💲', 'green')
    ]

# Callback para actualizar los gráficos
@app.callback(
    Output('grafico-ingresos-anuales', 'figure'),
    Output('grafico-estado-cuentas', 'figure'),
    Output('grafico-dias-saturados', 'figure'),
    Input('interval-component', 'n_intervals')
)
def actualizar_graficos(n):
    _, _, _, ingresos_anuales, estado_cuentas, dias_saturados = obtener_datos()
    
    # Crear figuras
    fig_ingresos_anuales = px.bar(ingresos_anuales, x='año', y='ingresos', title='Ingresos por Año')
    fig_estado_cuentas = px.pie(estado_cuentas, names='estado', values='total', title='Estado de Cuentas (Pagadas vs Pendientes)')
    fig_dias_saturados = px.pie(dias_saturados, names='dia', values='total_citas', title='Días Más Saturados en la Clínica')
    
    return fig_ingresos_anuales, fig_estado_cuentas, fig_dias_saturados

# Función para crear widgets
def create_widget(title, amount, is_money, link, icon, color):
    return html.Div(className='widget', style={
        'backgroundColor': '#f0f0f5',
        'color': '#333',
        'border': '2px solid #d7d6f6',
        'borderRadius': '10px',
        'padding': '20px',
        'flex': '1',
        'margin': '10px',
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }, children=[
        html.Div(className='left', style={'flex': '1'}, children=[
            html.Span(className='title', style={'fontSize': '16px', 'fontWeight': 'bold', 'display': 'block'}, children=title),
            html.Span(className='counter', style={'fontSize': '24px', 'fontWeight': '300', 'display': 'block', 'margin': '5px 0'}, children=f"{'$' if is_money else ''}{amount}"),
            html.Span(className='link', style={'fontSize': '12px', 'color': color, 'textDecoration': 'underline'}, children=link)
        ]),
        html.Div(className='right', style={'flex': '0 0 auto'}, children=[
            html.Div(className='icon', style={'fontSize': '32px', 'color': color}, children=icon)
        ])
    ])

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
