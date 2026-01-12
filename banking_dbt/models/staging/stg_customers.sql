with source as (
    select * from {{ source('banking_bronze', 'bronze_customers') }}
),

cleaned as (
    select
        id as customer_id,
        nama_depan as first_name,
        nama_belakang as last_name,
        -- Menggabungkan nama
        concat(nama_depan, ' ', nama_belakang) as full_name,
        email,
        segmen as customer_segment,
        location_id,
        bank_id
    from source
)

select * from cleaned