import pandas as pd 
import numpy as np 
import requests
import psycopg2

# reading

df = pd.read_csv('elaboracion_lactea_chile.csv')

# Get tokens 

def connect_to_db(host, db, port, user, password):
    try:
        conn = psycopg2.connect(host=host,
                                database = db,
                                port=port,
                                user = user,
                                password = password,)

    except psycopg2.OperationalError as e:
        raise e
    else:
        print('Connected')
    return conn

conn.execute("DROP TABLE IF EXISTS 'odepa_products'")

#execute the database
conn = connect_to_db(hostname, database, port, user, password)

#Create table if not exists
conn.execute("CREATE TABLE IF NOT EXISTS 'odepa_products' (Año integer Factory_Name varchar Product varchar Unit varchar Mes varchar Quantity integer)")

myfile = Open('elaboracion_lactea_chile.csv')

SQL_STATEMENT = """
COPY %s FROM STDIN WITH
CSV
HEADER
DELIMITER AS ','
"""
# Add values to db 
conn.copy_expert(SQL_STATEMENT,  )


