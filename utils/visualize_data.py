# utils/visualize_data.py

import pymongo
import plotly.graph_objs as go

# Función para visualizar datos con Plotly desde MongoDB
def visualize_data(db_name):
    # Conectar a MongoDB
    client = pymongo.MongoClient("localhost", 27017)
    db = client[db_name]

    # Consultar datos desde MongoDB
    citas = db["Citas"]
    data = citas.aggregate([
        {"$group": {"_id": "$genero", "count": {"$sum": 1}}}
    ])

    # Preparar datos para Plotly
    generos = []
    num_citas = []

    for item in data:
        generos.append(item["_id"])
        num_citas.append(item["count"])

    # Configurar la figura de Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=generos,
        y=num_citas,
        marker_color='rgb(55, 83, 109)',
        name='Número de Citas'
    ))

    fig.update_layout(
        title='Número de Citas por Género',
        xaxis=dict(title='Género'),
        yaxis=dict(title='Número de Citas')
    )

    # Mostrar la figura (o guardarla en un archivo HTML)
    fig.show()

# Ejecutar la función al llamar al script
if __name__ == "__main__":
    db_name = "nombre_de_tu_base_de_datos"
    visualize_data(db_name)
