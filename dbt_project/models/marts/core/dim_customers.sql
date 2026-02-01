{{ config(materialized='table') }}

select
    customer_id,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    email,
    cpf,
    risk_profile,
    created_at,
    updated_at,
    dbt_valid_from as valid_from,
    dbt_valid_to as valid_to,
    case when dbt_valid_to is null then true else false end as is_current
from {{ ref('dim_customers_snapshot') }}
