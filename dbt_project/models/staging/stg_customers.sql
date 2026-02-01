{{ config(materialized='view') }}

select
    id as customer_id,
    first_name,
    last_name,
    email,
    cpf,
    risk_profile,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at
from {{ source('landing_zone', 'customers') }}