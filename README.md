# 🏦 Banking Data Engineering Pipeline

End-to-end Modern Data Stack (MDS) solution untuk memproses data perbankan heterogen menggunakan arsitektur Medallion (Bronze–Silver–Gold). Pipeline mengintegrasikan data nasabah dan akun dari PostgreSQL, transaksi real-time dalam format JSON, serta kurs mata uang dari public API, dengan hasil akhir berupa dashboard analitik interaktif dan model machine learning untuk deteksi fraud.

## 📋 Daftar Isi
- [Deskripsi Proyek](#deskripsi-proyek)
- [Arsitektur](#arsitektur)
- [Tech Stack](#tech-stack)
- [Prasyarat](#prasyarat)
- [Setup & Instalasi](#setup--instalasi)
- [Struktur Proyek](#struktur-proyek)
- [Data Pipeline](#data-pipeline)
- [Fitur Utama](#fitur-utama)
- [Cara Menggunakan](#cara-menggunakan)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)

## 📊 Deskripsi Proyek

Proyek ini mengimplementasikan data engineering pipeline yang komprehensif dengan fitur-fitur berikut:

- **Data Integration**: Mengintegrasikan 3 sumber data heterogen (PostgreSQL, Stream JSON, Public API)
- **Medallion Architecture**: Implementasi Bronze → Silver → Gold layer untuk kualitas data
- **Real-time Processing**: Stream data transaksi dengan Snowflake Snowpark
- **Transformasi & Modeling**: dbt untuk ELT dan semantic modeling di Gold layer
- **Advanced Analytics**: Enrichment nilai transaksi ke USD dengan kurs real-time
- **ML Pipeline**: Logistic Regression untuk klasifikasi status transaksi dengan Snowflake Model Registry
- **Interactive Dashboard**: Visualisasi tren transaksi, segmentasi nasabah, analisis geografis, dan indikator risiko

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐         │
│  │ PostgreSQL  │  │ JSON Stream │  │ Public API (Kurs)│         │
│  │ (Batch)     │  │ (Real-time) │  │ (Exchange Rates) │         │
│  └─────────────┘  └─────────────┘  └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          APACHE AIRFLOW + DOCKER (Orchestration)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐       │
│  │ Batch DAG    │  │ Stream DAG   │  │ API DAG          │       │
│  │ (PostgreSQL) │  │ (JSON)       │  │ (Exchange Rate)  │       │
│  └──────────────┘  └──────────────┘  └──────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SNOWFLAKE (Cloud DW)                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ BRONZE LAYER (Raw Data)                                │     │
│  │ - Raw accounts, customers, locations, transactions     │     │
│  └────────────────────────────────────────────────────────┘     │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ SILVER LAYER (Cleaned & Deduplicated)                  │     │
│  │ - Deduplikasi data                                     │     │
│  │ - Penanganan missing values (Snowpark)                 │     │
│  │ - Deteksi anomali transaksi                            │     │
│  └────────────────────────────────────────────────────────┘     │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ GOLD LAYER (Business Models + ML)                      │     │
│  │ - Fact & Dimension tables (dbt)                        │     │
│  │ - Enrichment nilai transaksi ke USD                    │     │
│  │ - ML Model (Logistic Regression - Status Transaksi)    │     │
│  │ - Snowflake Model Registry                             │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  VISUALIZATION & ANALYTICS                       │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Dashboard Analitik Interaktif                          │     │
│  │ - Tren transaksi & volume                              │     │
│  │ - Segmentasi nasabah (RFM)                             │     │
│  │ - Eksposur nilai tukar                                 │     │
│  │ - Analisis geografis (lokasi transaksi)                │     │
│  │ - Indikator risiko & fraud detection                   │     │
│  │ - ML Model predictions & scoring                       │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Orchestration** | Apache Airflow 3.1.5 |
| **Containerization** | Docker & Docker Compose |
| **Source Systems** | PostgreSQL, JSON APIs |
| **Data Warehouse** | Snowflake |
| **Processing** | Snowpark Python SDK |
| **Transformation** | dbt (Data Build Tool) 1.11 |
| **ML/Analytics** | Python, scikit-learn, Snowflake Model Registry |
| **Visualization** | (Dashboard tool - dapat disesuaikan) |

## 📦 Prasyarat

- **Docker & Docker Compose**: v20.10+
- **Python**: 3.11+
- **PostgreSQL**: 12+ (source database)
- **Snowflake**: Account dengan Warehouse & Database
- **Git**: Untuk version control
- **Credentials**: 
  - PostgreSQL credentials
  - Snowflake credentials (username, password, account)
  - API keys (jika diperlukan)

## 🚀 Setup & Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd banking_data_pipeline
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Konfigurasi Airflow
```bash
cd airflow

# Set Airflow environment variables
set AIRFLOW_HOME=%CD%

# Initialize Airflow database
airflow db init

# Create admin user (opsional)
airflow users create --username admin --password admin \
    --firstname Admin --lastname User --role Admin --email admin@example.com
```

### 4. Setup Snowflake Connection
Buat file `.env` di root project atau configure di Airflow UI:
```
SNOWFLAKE_USER=<username>
SNOWFLAKE_PASSWORD=<password>
SNOWFLAKE_ACCOUNT=<account_id>
SNOWFLAKE_WAREHOUSE=<warehouse_name>
SNOWFLAKE_DATABASE=<database_name>
SNOWFLAKE_SCHEMA=bronze
```

### 5. Setup PostgreSQL Connection
Pastikan PostgreSQL connection tersedia di Airflow atau sebagai environment variable:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=banking_db
```

### 6. Start Docker Containers
```bash
docker-compose up -d

# Monitor logs
docker-compose logs -f airflow-webserver
```

### 7. Access Airflow UI
Buka browser dan akses: `http://localhost:8080`

### 8. Configure dbt (opsional)
```bash
cd ../banking_dbt

# Setup dbt profiles
dbt debug

# Run dbt models
dbt run
dbt test
```

## 📁 Struktur Proyek

```
banking_data_pipeline/
├── README.md                           # Dokumentasi proyek
├── requirements.txt                    # Python dependencies
│
├── airflow/                            # Apache Airflow Configuration
│   ├── docker-compose.yaml             # Docker compose setup
│   ├── config/                         # Airflow configs
│   ├── dags/                           # DAG definitions
│   │   ├── ingest_batch_dag.py         # DAG: Batch data dari PostgreSQL
│   │   ├── ingest_stream_dag.py        # DAG: Stream data real-time (JSON)
│   │   ├── api_data_dag.py             # DAG: Exchange rate dari API
│   │   ├── postgres_to_airflow.py      # DAG: PostgreSQL integration
│   │   └── __pycache__/
│   ├── logs/                           # DAG execution logs
│   └── plugins/                        # Custom operators & hooks
│
├── banking_dbt/                        # dbt Transformation Project
│   ├── dbt_project.yml                 # dbt configuration
│   ├── models/
│   │   ├── staging/                    # Staging models (Silver layer)
│   │   │   ├── stg_accounts.sql
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_transactions.sql
│   │   │   ├── stg_banks.sql
│   │   │   ├── stg_locations.sql
│   │   │   └── stg_exchange_rates.sql
│   │   ├── marts/                      # Mart models (Gold layer)
│   │   │   ├── fact_transaction.sql
│   │   │   └── fact_transaction_enriched.sql
│   │   └── example/                    # Example models
│   ├── tests/                          # dbt tests
│   ├── seeds/                          # Static data
│   ├── macros/                         # dbt macros
│   └── target/                         # Compiled dbt models
│
├── data-generator/                     # Data Generation & Testing
│   ├── generate_data.py                # Script untuk generate sample data
│   └── dataset/
│       ├── batch_source/               # Batch data files
│       │   ├── account.json
│       │   ├── customer.csv
│       │   ├── location.txt
│       │   └── bank_info.txt
│       └── stream_source/              # Stream data files
│           └── transaction_*.json
│
├── dataset/                            # Data storage
│   ├── batch_source/                   # Batch data untuk pengujian
│   └── stream_source/                  # Stream data untuk pengujian
│
└── logs/                               # Application logs
```

## 🔄 Data Pipeline

### Phase 1: Data Ingestion (Bronze Layer)
Airflow DAGs mengintegrasikan tiga sumber data:

1. **Batch Data DAG** (`ingest_batch_dag.py`)
   - Source: PostgreSQL
   - Frequency: Daily (scheduled)
   - Tables: accounts, customers, locations, banks
   - Destination: Snowflake Bronze Layer

2. **Stream Data DAG** (`ingest_stream_dag.py`)
   - Source: JSON files (real-time transaction format)
   - Frequency: Every 5 minutes (configurable)
   - Format: Streaming JSON
   - Destination: Snowflake Bronze Layer

3. **Exchange Rate API DAG** (`api_data_dag.py`)
   - Source: Public API
   - Frequency: Daily
   - Purpose: Kurs mata uang untuk enrichment
   - Destination: Snowflake Bronze Layer

### Phase 2: Data Transformation (Silver Layer)
Snowpark Python untuk data quality:
- **Deduplikasi**: Remove duplicate transactions & accounts
- **Data Cleansing**: Handle missing values dan data types
- **Anomaly Detection**: Identifikasi transaksi mencurigakan
- **Validation**: Business rule validation

### Phase 3: Data Modeling (Gold Layer)
dbt transformation models:
- **Fact Tables**: 
  - `fact_transaction`: Granular transaction data
  - `fact_transaction_enriched`: With USD values
- **Dimension Tables**:
  - `dim_customers`: Customer master data
  - `dim_accounts`: Account information
  - `dim_locations`: Geographic dimensions
  - `dim_exchange_rates`: Currency conversion rates

### Phase 4: ML & Advanced Analytics
- **Feature Engineering**: Aggregate customer metrics
- **Model Training**: Logistic Regression untuk transaction status
- **Model Registry**: Managed via Snowflake Model Registry
- **Scoring**: Real-time prediction pipeline

## ✨ Fitur Utama

### 1. Multi-Source Data Integration
- PostgreSQL batch ingestion dengan full load & incremental
- Real-time JSON stream processing
- External API integration untuk dynamic data

### 2. Data Quality Framework
- Automated deduplikasi dengan Snowpark
- Missing value imputation
- Anomaly detection algorithms
- Data validation rules

### 3. Advanced Transformations
- Currency conversion (IDR → USD)
- Customer segmentation (RFM analysis)
- Aggregation & window functions
- Complex business logic implementation

### 4. Machine Learning Pipeline
- Logistic Regression model untuk transaction classification
- Model versioning & registry management
- Batch prediction capabilities
- Model performance monitoring

### 5. Analytics & Visualization
- Transaction trends & patterns
- Customer segmentation insights
- Geographic analysis
- Risk & fraud indicators
- Model prediction dashboards

## 💻 Cara Menggunakan

### Menjalankan Seluruh Pipeline

```bash
# 1. Pastikan Docker containers running
docker-compose up -d

# 2. Trigger DAG melalui Airflow UI
# - Buka http://localhost:8080
# - Cari DAG: 01_ingest_batch_data, 02_ingest_stream_data, 05_ingest_api_kurs
# - Klik "Trigger DAG"

# ATAU trigger via CLI
airflow dags trigger 01_ingest_batch_data
airflow dags trigger 02_ingest_stream_data
airflow dags trigger 05_ingest_api_kurs
```

### Menjalankan dbt Models

```bash
cd banking_dbt

# Run semua models
dbt run

# Run specific model
dbt run -s fact_transaction_enriched

# Run dengan tests
dbt run --tests

# Generate documentation
dbt docs generate
dbt docs serve
```

### Generate Sample Data

```bash
cd data-generator

# Generate batch data
python generate_data.py --type batch --output-path ../dataset/batch_source

# Generate stream data
python generate_data.py --type stream --output-path ../dataset/stream_source
```

### Monitoring Pipeline

**Via Airflow UI:**
- Tasks status & execution history
- Task logs & error messages
- DAG dependencies & relationships
- SLA tracking

**Via Snowflake:**
```sql
-- Check Bronze layer data
SELECT COUNT(*) FROM BANKING_DB.BRONZE.RAW_TRANSACTIONS;

-- Monitor Silver layer quality
SELECT COUNT(*) FROM BANKING_DB.SILVER.STG_TRANSACTIONS;

-- Query Gold layer analytics
SELECT * FROM BANKING_DB.GOLD.FACT_TRANSACTION_ENRICHED LIMIT 10;
```

## 🔍 Monitoring & Troubleshooting

### Common Issues

#### 1. Airflow DAG tidak terlihat di UI
```bash
# Check DAG parsing
airflow dags list

# Verify DAG syntax
python airflow/dags/ingest_batch_dag.py
```

#### 2. Snowflake connection failed
```bash
# Test connection
airflow connections test snowflake_default

# Verify credentials di Airflow Admin > Connections
```

#### 3. dbt model run failed
```bash
# Check dbt schema
dbt parse

# Run dengan debug
dbt run --debug

# Check compiled SQL
cat target/compiled/banking_dbt/models/...
```

#### 4. Stream data tidak masuk
```bash
# Check file format
# Ensure JSON files di dataset/stream_source/ valid format
# Verify DAG schedule interval

# Manual trigger
airflow tasks test 02_ingest_stream_data ingest_stream_task
```

### Log Files
- **Airflow**: `airflow/logs/dag_id=*/run_id=*/`
- **Docker**: `docker-compose logs <service-name>`
- **Snowflake**: Query history di Snowflake UI

## 📈 Performance Optimization

### Airflow
- Adjust `parallelism` & `dag_concurrency` di airflow.cfg
- Implement task pools untuk resource management
- Use XCom untuk data passing antar tasks

### Snowflake
- Optimize warehouse sizing berdasarkan workload
- Implement table clustering untuk query optimization
- Use result caching untuk recurring queries

### dbt
- Incremental models untuk large tables
- Proper indexing strategy
- Materialization strategy (table vs view vs incremental)