from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import shutil

# Path Configuration
SOURCE_PATH = '/opt/airflow/data_source/stream_source'
ARCHIVE_PATH = '/opt/airflow/processed_stream' # Folder ini harus dibuat dulu (kita handle di script)

if not os.path.exists(ARCHIVE_PATH):
    os.makedirs(ARCHIVE_PATH)

def process_stream_files():
    # 1. Ambil list semua file json di folder source
    files = [f for f in os.listdir(SOURCE_PATH) if f.endswith('.json')]
    
    if not files:
        print("No new files found via streaming.")
        return

    print(f"Found {len(files)} files to process.")
    
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    engine = hook.get_sqlalchemy_engine()

    for file_name in files:
        full_path = os.path.join(SOURCE_PATH, file_name)
        
        try:
            # 2. Baca File
            with open(full_path, 'r') as f:
                data = json.load(f)
            
            if not data:
                print(f"File {file_name} is empty, skipping.")
                continue

            df = pd.DataFrame(data)
            df.columns = [c.upper() for c in df.columns]

            # 3. Load ke Snowflake (APPEND MODE)
            # if_exists='append' kuncinya disini
            df.to_sql('transaction', con=engine, index=False, if_exists='append', method='multi', chunksize=1000)
            print(f"Loaded {file_name} to Snowflake.")

            # 4. Pindahkan ke Archive
            shutil.move(full_path, os.path.join(ARCHIVE_PATH, file_name))
            print(f"Moved {file_name} to processed folder.")
            
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
            # File error dibiarkan di folder source atau dipindah ke folder error (opsional)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
}

# Jalan setiap 30 menit
with DAG('02_ingest_stream_data', 
         default_args=default_args, 
         schedule_interval='*/10 * * * *', 
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='process_transactions',
        python_callable=process_stream_files
    )