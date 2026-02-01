{{ config(materialized='table') }}

with transactions as (
    select * from {{ ref('stg_transactions') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
)

select
    t.transaction_id,
    t.account_id,
    a.customer_id, -- Trazemos o customer_id para a fato para evitar joins desnecessários depois
    t.transaction_type,
    t.amount,
    t.counterparty_bank,
    t.status,
    t.transaction_at,
    -- Colunas derivadas úteis para BI
    case 
        when t.transaction_type in ('PIX_IN', 'TED_IN') then 'INFLOW'
        else 'OUTFLOW'
    end as movement_type
from transactions t
left join accounts a on t.account_id = a.account_id