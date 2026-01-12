with source as (
    select * from {{ source('banking_bronze', 'bronze_banks') }}
),

cleaned as (
    select
        bank_id,
        nama_bank as bank_name,
        jenis_bank as bank_type
    from source
)

select * from cleaned