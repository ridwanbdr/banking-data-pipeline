from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
import pandas as pd
import os
import json

# Definisikan Path sesuai mapping volume di docker-compose
# Ingat: di Docker tadi kita mapping ke /opt/airflow/data_source
DATA_PATH = '/opt/airflow/data_source/batch_source'

def load_csv_to_snowflake(filename, table_name, separator=','):
    file_path = os.path.join(DATA_PATH, filename)
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found. Skipping.")
        return

    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path, sep=separator)
    
    # Pastikan nama kolom di DF huruf besar semua agar cocok dengan Snowflake
    df.columns = [c.upper() for c in df.columns]
    
    # Init Hook Snowflake
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    engine = hook.get_sqlalchemy_engine()
    connection = engine.connect()

    # Load Data (if_exists='replace' berarti truncate & load - cocok untuk master data)
    print(f"Loading to Snowflake table {table_name}...")
    df.to_sql(table_name, con=engine, index=False, if_exists='replace', method='multi', chunksize=1000)
    connection.close()
    print("Done.")

def load_json_to_snowflake(filename, table_name):
    file_path = os.path.join(DATA_PATH, filename)
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print(f"Reading {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df.columns = [c.upper() for c in df.columns]

    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    engine = hook.get_sqlalchemy_engine()
    
    print(f"Loading to Snowflake table {table_name}...")
    connection = engine.connect()
    try:
        df.to_sql(table_name, con=connection, index=False, if_exists='replace', method='multi', chunksize=1000)
        print("Done.")
    finally:
        connection.close()

# Definisi DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('01_ingest_batch_data', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='load_location',
        python_callable=load_csv_to_snowflake,
        op_kwargs={'filename': 'location.txt', 'table_name': 'location', 'separator': '|'}
    )

    t2 = PythonOperator(
        task_id='load_bank',
        python_callable=load_csv_to_snowflake,
        op_kwargs={'filename': 'bank_info.txt', 'table_name': 'bank_info', 'separator': '|'}
    )

    t3 = PythonOperator(
        task_id='load_customer',
        python_callable=load_csv_to_snowflake,
        op_kwargs={'filename': 'customer.csv', 'table_name': 'customer', 'separator': ','}
    )

    t4 = PythonOperator(
        task_id='load_account',
        python_callable=load_json_to_snowflake,
        op_kwargs={'filename': 'account.json', 'table_name': 'account'}
    )

    [t1, t2, t3, t4] # Jalankan paralel