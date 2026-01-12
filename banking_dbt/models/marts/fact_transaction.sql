with 
transactions as (
    select * from {{ ref('stg_transactions') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

locations as (
    select * from {{ ref('stg_locations') }}
),

banks as (
    select * from {{ ref('stg_banks') }}
),

rates as (
    select * from {{ ref('stg_exchange_rates') }}
    where target_currency = 'IDR' -- Ambil kurs IDR
),

joined as (
    select
        -- Transaction Info
        t.transaction_id,
        t.transaction_date,
        t.transaction_type,
        t.transaction_status,
        t.amount as amount_idr,
        
        -- Business Logic: Konversi ke USD
        -- Jika rate tidak ketemu di tanggal itu, pakai rate terakhir yg ada (fallback logic bisa ditambahkan, tapi ini simple join)
        (t.amount / nullif(r.rate, 0)) as amount_usd_est,
        
        -- Account Info
        a.account_id,
        
        -- Customer Info
        c.customer_id,
        
        -- Location Info
        l.location_id,
        
        -- Bank Info
        b.bank_id

    from transactions t
    join accounts a on t.account_id = a.account_id
    join customers c on a.customer_id = c.customer_id
    join locations l on c.location_id = l.location_id
    join banks b on c.bank_id = b.bank_id
    -- Join Kurs berdasarkan Tanggal Transaksi
    join rates r on t.transaction_date = r.rate_date
)

select * from joined