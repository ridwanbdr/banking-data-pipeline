with source as (
    select * from {{ source('banking_bronze', 'bronze_accounts') }}
),

cleaned as (
    select
        id as account_id,
        customer_id,
        tipe_akun as account_type,
        saldo as balance
    from source
)

select * from cleaned