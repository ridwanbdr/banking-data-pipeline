with source as (
    select * from {{ source('banking_bronze', 'bronze_transactions') }}
),

cleaned as (
    select
        id as transaction_id,
        to_date(date) as transaction_date,
        -- Mengambil jam dari kolom timestamp jika ada, atau biarkan string
        timestamp as transaction_timestamp,
        account_id,
        jumlah_transaksi as amount,
        tipe_transaksi as transaction_type,
        akun_tujuan as target_account,
        status as transaction_status
    from source
)

select * from cleaned