from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd

# Daftar tabel yang mau dipindahkan dari Postgres ke Snowflake
TABLES_TO_SYNC = ['location', 'bank_info', 'customer', 'account']

def extract_load_table(table_name):
    print(f"--- Processing Table: {table_name} ---")
    
    # 1. EXTRACT dari Postgres
    # Menggunakan Connection ID yang baru kita buat di UI
    pg_hook = PostgresHook(postgres_conn_id='postgres_source_bank')
    pg_engine = pg_hook.get_sqlalchemy_engine()
    
    print(f"Extracting data from Postgres table: {table_name}...")
    # Baca semua data ke Pandas DataFrame
    df = pd.read_sql(f"SELECT * FROM {table_name}", pg_engine)
    
    print(f"Extracted {len(df)} rows.")
    
    if df.empty:
        print("Table is empty, skipping load.")
        return

    # 2. TRANSFORM (Sedikit perapihan)
    # Ubah nama kolom jadi HURUF BESAR (Snowflake standard)
    df.columns = [c.upper() for c in df.columns]
    
    # Tambahkan audit trail (timestamp kapan data ditarik)
    df['LOADED_AT'] = datetime.now()

    # 3. LOAD ke Snowflake
    sf_hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    sf_engine = sf_hook.get_sqlalchemy_engine()
    
    print(f"Loading to Snowflake table: {table_name}...")
    # if_exists='replace' -> Truncate & Insert (Cocok untuk full load master data)
    df.to_sql(table_name, con=sf_engine, index=False, if_exists='replace', method='multi', chunksize=1000)
    
    print("Success!")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('04_ingest_postgres_to_snowflake', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False) as dag:

    # Kita buat Task secara dinamis menggunakan Loop
    # Jadi tidak perlu copy paste kode untuk setiap tabel
    for table in TABLES_TO_SYNC:
        task = PythonOperator(
            task_id=f'sync_{table}',
            python_callable=extract_load_table,
            op_kwargs={'table_name': table}
        )