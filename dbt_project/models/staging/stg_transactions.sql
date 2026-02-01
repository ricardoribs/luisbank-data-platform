{{ config(materialized='view') }}

select
    id as transaction_id,
    account_id,
    amount,
    transaction_type,
    cast(transaction_date as timestamp) as transaction_at,
    counterparty_bank,
    status
from {{ source('landing_zone', 'transactions') }}