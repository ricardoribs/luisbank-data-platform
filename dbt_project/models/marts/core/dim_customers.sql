{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('stg_customers') }}
)

select
    customer_id,
    first_name,
    last_name,
    -- Criamos o nome completo para facilitar dashboards
    first_name || ' ' || last_name as full_name,
    email,
    cpf,
    risk_profile,
    created_at,
    updated_at
from customers