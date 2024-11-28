# utils/populate_mongodb.py

import pymongo
from faker import Faker
import random

# Función para poblar MongoDB con datos ficticios
def populate_mongodb(db_name):
    # Conectar a MongoDB
    client = pymongo.MongoClient("localhost", 27017)
    db = client[db_name]

    # Poblar datos de pacientes
    pacientes = db["Pacientes"]
    fake = Faker()
    for _ in range(500):
        paciente = {
            "nombre": fake.first_name(),
            "apellido": fake.last_name(),
            "edad": random.randint(18, 90),
            "genero": random.choice(["Masculino", "Femenino"]),
            "direccion": fake.address(),
            "telefono": fake.phone_number(),
            "email": fake.email()
        }
        pacientes.insert_one(paciente)

    # Poblar datos de citas
    citas = db["Citas"]
    for _ in range(1000):
        cita = {
            "id_paciente": random.randint(1, 500),  # Ids de pacientes simulados
            "fecha": fake.date_this_year(before_today=True),
            "detalle": fake.text()
        }
        citas.insert_one(cita)

    print("Datos insertados exitosamente en MongoDB.")

# Ejecutar la función al llamar al script
if __name__ == "__main__":
    db_name = "nombre_de_tu_base_de_datos"
    populate_mongodb(db_name)
