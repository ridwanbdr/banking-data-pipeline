import pandas as pd
import random
import json
import os
from faker import Faker
from datetime import datetime
from sqlalchemy import create_engine

fake = Faker('id_ID')

# --- KONEKSI KE POSTGRES ---
# User: airflow, Pass: airflow, DB: source_bank
DB_CONNECTION = 'postgresql://airflow:airflow@localhost:5432/source_bank'
try:
    db_engine = create_engine(DB_CONNECTION)
    connection = db_engine.connect()
    print("Sukses terkoneksi ke Postgres!")
    connection.close()
except Exception as e:
    print(f"Gagal koneksi ke Postgres. Pastikan port 5432 sudah di-expose di docker-compose. Error: {e}")
    exit()

# --- KONFIGURASI ---
NEW_CUSTOMERS_PER_RUN = 30     
NEW_ACCOUNTS_RATIO = 2         
NEW_TRANSACTIONS_PER_RUN = 10000  

# Path Output Streaming
BASE_DIR = os.getcwd() 
OUTPUT_FOLDER = 'dataset'
STREAM_FOLDER = os.path.join(BASE_DIR, OUTPUT_FOLDER, 'stream_source')
if not os.path.exists(STREAM_FOLDER):
    os.makedirs(STREAM_FOLDER)

# --- HELPER FUNCTIONS ---
def get_existing_ids(table_name, id_column='id'):
    """Mengambil list ID yang sudah ada di DB"""
    try:
        query = f"SELECT {id_column} FROM {table_name}"
        df = pd.read_sql(query, db_engine)
        return df[id_column].tolist()
    except:
        return []

def get_last_seq_from_db(table_name, id_column='id'):
    try:
        query = f"SELECT {id_column} FROM {table_name} ORDER BY {id_column} DESC LIMIT 1"
        df = pd.read_sql(query, db_engine)
        if not df.empty:
            last_id = df.iloc[0][id_column]
            return int(last_id.split('-')[1]) 
        return 0
    except:
        return 0

# --- POOLS ---
SEGMENTS = ['Gold', 'Silver', 'Platinum', 'Priority', 'Standard']
ACCOUNT_TYPES = ['Savings', 'Checking', 'Deposit', 'Loan']
TRANS_TYPES = ['Transfer', 'Payment', 'Withdrawal', 'Deposit']
TRANS_STATUS = ['Success', 'Pending', 'Failed']

print("--- Process Started ---")

# ==========================================
# 1. GENERATE MASTER DATA (Location & Bank)
# ==========================================

# A. LOCATION
all_loc_ids = get_existing_ids('location')
if not all_loc_ids:
    print("Generating Initial Locations...")
    CITIES_POOL = [f"Kota {fake.city_name()}" for _ in range(50)]
    PROVINCES_POOL = [fake.state() for _ in range(10)]
    loc_data = []
    for i in range(1, 51):
        loc_id = f"LOC-{i:03d}"
        loc_data.append({
            "id": loc_id,
            "kota": random.choice(CITIES_POOL),
            "provinsi": random.choice(PROVINCES_POOL)
        })
        all_loc_ids.append(loc_id)
    
    df_loc = pd.DataFrame(loc_data)
    df_loc.to_sql('location', db_engine, if_exists='append', index=False)
    print("Locations uploaded to Postgres.")

# B. BANK INFO
all_bank_ids = get_existing_ids('bank_info', 'bank_id')
if not all_bank_ids:
    print("Generating Initial Bank Info...")
    bank_pool = [
        ("Bank Rakyat Indonesia", "BRI", "Jakarta", "BUMN"),
        ("Bank Mandiri", "Mandiri", "Jakarta", "BUMN"),
        ("Bank Central Asia", "BCA", "Jakarta", "Swasta"),
        ("Bank Negara Indonesia", "BNI", "Jakarta", "BUMN"),
        ("Bank CIMB Niaga", "CIMB", "Jakarta", "Swasta"),
        ("Bank Tabungan Negara", "BTN", "Jakarta", "BUMN"),
        ("Bank Danamon Indonesia", "Danamon", "Jakarta", "Swasta"),
        ("Bank Permata", "Permata", "Jakarta", "Swasta"),
        ("Bank Maybank Indonesia", "Maybank", "Jakarta", "Swasta"),
        ("Bank OCBC NISP", "OCBC", "Jakarta", "Swasta"),
        ("Bank Panin", "Panin", "Jakarta", "Swasta"),
        ("Bank Syariah Indonesia", "BSI", "Jakarta", "Syariah"),
        ("Bank Muamalat Indonesia", "Muamalat", "Jakarta", "Syariah"),
        ("Bank Mega", "Mega", "Jakarta", "Swasta"),
        ("Bank UOB Indonesia", "UOB", "Jakarta", "Swasta")
    ]
    bank_data = []
    for i, b in enumerate(bank_pool, 1):
        bank_id = f"BANK-{i:03d}"
        bank_data.append({
            "bank_id": bank_id,
            "nama_bank": b[0],
            "singkatan": b[1],
            "kantor_pusat": b[2],
            "jenis_bank": b[3]
        })
        all_bank_ids.append(bank_id)
        
    df_bank = pd.DataFrame(bank_data)
    df_bank.to_sql('bank_info', db_engine, if_exists='append', index=False)
    print("Bank Info uploaded to Postgres.")

# # ==========================================
# # 2. GENERATE CUSTOMER (Insert to Postgres)
# # ==========================================
# print("Generating Customers...")
# last_seq_cust = get_last_seq_from_db('customer')
# new_customers = []
# curr_seq = last_seq_cust + 1

# for _ in range(NEW_CUSTOMERS_PER_RUN):
#     cust_id = f"CUST-{curr_seq:04d}"
#     new_customers.append({
#         "id": cust_id,
#         "nama_depan": fake.first_name(),
#         "nama_belakang": fake.last_name(),
#         "email": f"user{curr_seq}@example.com",
#         "segmen": random.choice(SEGMENTS),
#         "location_id": random.choice(all_loc_ids),
#         "bank_id": random.choice(all_bank_ids)
#     })
#     curr_seq += 1

# if new_customers:
#     df_cust = pd.DataFrame(new_customers)
#     df_cust.to_sql('customer', db_engine, if_exists='append', index=False)
#     print(f"Inserted {len(new_customers)} customers to Postgres.")

# # ==========================================
# # 3. GENERATE ACCOUNT (Insert to Postgres)
# # ==========================================
# print("Generating Accounts...")
# last_seq_acc = get_last_seq_from_db('account')
# new_accounts = []
# curr_seq_acc = last_seq_acc + 1

# for cust in new_customers:
#     for _ in range(NEW_ACCOUNTS_RATIO):
#         acc_id = f"ACC-{curr_seq_acc:05d}"
#         new_accounts.append({
#             "id": acc_id,
#             "customer_id": cust['id'],
#             "tipe_akun": random.choice(ACCOUNT_TYPES),
#             "saldo": round(random.uniform(100000, 50000000), 2)
#         })
#         curr_seq_acc += 1

# if new_accounts:
#     df_acc = pd.DataFrame(new_accounts)
#     df_acc.to_sql('account', db_engine, if_exists='append', index=False)
#     print(f"Inserted {len(new_accounts)} accounts to Postgres.")

# ==========================================
# 4. GENERATE TRANSACTION (Streaming - JSON File)
# ==========================================
print("Generating Transactions (Stream)...")

# Ambil semua Account ID dari Postgres
all_acc_ids = get_existing_ids('account')

if len(all_acc_ids) < 2:
    print("Not enough accounts for transactions.")
else:
    new_transactions = []
    # Logic Transaction Sequence (Lokal File)
    SEQ_FILE = os.path.join(BASE_DIR, 'transaction_seq.tmp')
    if os.path.exists(SEQ_FILE):
        with open(SEQ_FILE, 'r') as f:
            last_seq_trans = int(f.read().strip())
    else:
        last_seq_trans = 0
    
    curr_seq_trans = last_seq_trans + 1
    
    for _ in range(NEW_TRANSACTIONS_PER_RUN):
        src = random.choice(all_acc_ids)
        dst = random.choice(all_acc_ids)
        while dst == src: dst = random.choice(all_acc_ids)

        new_transactions.append({
            "id": f"TRX-{curr_seq_trans:06d}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "account_id": src,
            "jumlah_transaksi": round(random.uniform(50000, 2000000), 2),
            "tipe_transaksi": random.choice(TRANS_TYPES),
            "akun_tujuan": dst,
            "status": random.choice(TRANS_STATUS)
        })
        curr_seq_trans += 1
    
    # Save JSON Stream
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transaction_{timestamp_str}.json"
    with open(os.path.join(STREAM_FOLDER, filename), 'w') as f:
        json.dump(new_transactions, f, indent=4)
    
    # Update Seq File
    with open(SEQ_FILE, 'w') as f:
        f.write(str(curr_seq_trans - 1))
        
    print(f"Streamed {len(new_transactions)} transactions to {filename}")

print("--- Process Complete ---")