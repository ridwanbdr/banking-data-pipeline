with source as (
    select * from {{ source('banking_bronze', 'bronze_exchange_rates') }}
),

cleaned as (
    select
        base_currency,
        target_currency,
        rate,
        to_date(date) as rate_date, -- Pastikan format tanggal benar
        loaded_at
    from source
    -- Ambil data paling baru saja (deduplikasi sederhana)
    qualify row_number() over (partition by rate_date order by loaded_at desc) = 1
)

select * from cleaned