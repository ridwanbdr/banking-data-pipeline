from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime
import requests
import pandas as pd

# URL API Gratis (Update harian)
# Base: USD
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"

def fetch_and_load_rate():
    print(f"Fetching data from API: {API_URL}...")
    
    try:
        # 1. GET Request ke API
        response = requests.get(API_URL)
        response.raise_for_status() # Cek jika error 404/500
        data = response.json()
        
        # 2. Parsing Data (Kita ambil USD ke IDR)
        rate_idr = data['rates'].get('IDR', 15000) # Default 15000 jika key tidak ada
        date_api = data['date']
        base_curr = data['base']
        
        print(f"Rate found: 1 {base_curr} = {rate_idr} IDR per {date_api}")
        
        # 3. Buat DataFrame
        df = pd.DataFrame([{
            'BASE_CURRENCY': base_curr,
            'TARGET_CURRENCY': 'IDR',
            'RATE': rate_idr,
            'DATE': date_api,
            'LOADED_AT': datetime.now()
        }])
        
        # 4. Load ke Snowflake
        hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
        engine = hook.get_sqlalchemy_engine()
        
        print("Loading to Snowflake table: exchange_rates...")
        df.to_sql('exchange_rates', con=engine, index=False, if_exists='append', method='multi')
        print("Success!")
        
    except Exception as e:
        print(f"Error fetching API: {e}")
        raise e

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('05_ingest_api_kurs', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False) as dag:

    t1 = PythonOperator(
        task_id='fetch_kurs_usd_idr',
        python_callable=fetch_and_load_rate
    )