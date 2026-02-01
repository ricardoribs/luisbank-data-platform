{{ config(materialized='incremental', unique_key='transaction_id') }}

with transactions as (
    select * from {{ ref('stg_transactions') }}
    {% if is_incremental() %}
        where transaction_at > (
            select coalesce(max(transaction_at), timestamp '1900-01-01') from {{ this }}
        )
    {% endif %}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
)

select
    t.transaction_id,
    t.account_id,
    a.customer_id,
    t.transaction_type,
    t.amount,
    t.counterparty_bank,
    t.status,
    t.transaction_at,
    case
        when t.transaction_type in ('PIX_IN', 'TED_IN') then 'INFLOW'
        else 'OUTFLOW'
    end as movement_type
from transactions t
left join accounts a on t.account_id = a.account_id
