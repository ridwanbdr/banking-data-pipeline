with source as (
    select * from {{ source('banking_bronze', 'bronze_locations') }}
),

cleaned as (
    select
        id as location_id,
        kota as city,
        provinsi as province
    from source
)

select * from cleaned