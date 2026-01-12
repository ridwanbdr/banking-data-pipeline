{{ config(
    materialized='table'
) }}

with transactions as (
    select * from {{ source('banking_bronze', 'bronze_transactions') }}
),

accounts as (
    select * from {{ source('banking_bronze', 'bronze_accounts') }}
),

customers as (
    select * from {{ source('banking_bronze', 'bronze_customers') }}
),

locations as (
    select * from {{ source('banking_bronze', 'bronze_locations') }}
),

banks as (
    select * from {{ source('banking_bronze', 'bronze_banks') }}
),

rates as (
    select * from {{ source('banking_bronze', 'bronze_exchange_rates') }}
    where target_currency = 'IDR'
),

joined as (
    select
        -- 1. TRANSACTION INFO (Wajib Ada)
        t.transaction_id,
        t.transaction_date,
        t.transaction_type,
        t.transaction_status,
        t.amount as amount_idr,
        
        -- 2. KONVERSI USD (Safe Division)
        -- Jika rate NULL (karena gagal join), hasilnya NULL, bukan error/hilang
        (t.amount / nullif(r.rate, 0)) as amount_usd_est,
        
        -- 3. DIMENSI (Menggunakan COALESCE agar rapi di Dashboard)
        -- Jika data master tidak ketemu, isi dengan 'Unknown'
        coalesce(a.account_type, 'Unknown Account') as account_type,
        
        coalesce(c.full_name, 'Unknown Customer') as customer_name,
        coalesce(c.customer_segment, 'N/A') as customer_segment,
        c.email,
        
        coalesce(l.city, 'Unknown City') as city,
        coalesce(l.province, 'Unknown Province') as province,
        
        coalesce(b.bank_name, 'Unknown Bank') as bank_name,
        b.bank_type

    from transactions t
    -- GANTI SEMUA 'JOIN' MENJADI 'LEFT JOIN' (Best Practice untuk Fact Table)
    left join accounts a on t.account_id = a.account_id
    left join customers c on a.customer_id = c.customer_id
    left join locations l on c.location_id = l.location_id
    left join banks b on c.bank_id = b.bank_id
    -- Paling Kritis: Left Join ke Rates
    left join rates r on t.transaction_date = r.rate_date
)

select * from joined