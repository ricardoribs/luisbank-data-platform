{{ config(materialized='view') }}

select
    id as account_id,
    customer_id,
    account_number,
    agency,
    balance as initial_balance_snapshot,
    account_type,
    status,
    cast(created_at as timestamp) as opened_at
from {{ source('landing_zone', 'accounts') }}