{{ config(materialized='table') }}

with accounts as (
    select * from {{ ref('stg_accounts') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
)

select
    a.account_id,
    a.customer_id,
    c.first_name || ' ' || c.last_name as customer_name,
    a.account_number,
    a.agency,
    a.account_type,
    a.status,
    a.initial_balance_snapshot,
    a.opened_at
from accounts a
left join customers c on a.customer_id = c.customer_id