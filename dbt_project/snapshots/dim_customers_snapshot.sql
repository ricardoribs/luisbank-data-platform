{% snapshot dim_customers_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='check',
        check_cols=['risk_profile', 'email', 'first_name', 'last_name']
    )
}}

select
    customer_id,
    first_name,
    last_name,
    email,
    cpf,
    risk_profile,
    created_at,
    updated_at
from {{ ref('stg_customers') }}

{% endsnapshot %}
