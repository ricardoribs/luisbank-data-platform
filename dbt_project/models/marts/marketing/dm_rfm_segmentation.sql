{{ config(materialized='table') }}

with rfm_base as (
    -- 1. Calcular as métricas brutas por cliente
    select 
        customer_id,
        max(transaction_at) as last_transaction_date,
        date_diff('day', max(transaction_at), current_date) as recency_days,
        count(distinct transaction_id) as frequency,
        sum(amount) as monetary
    from {{ ref('fct_transactions') }}
    group by 1
),

rfm_scores as (
    -- 2. Atribuir notas de 1 a 5 (Quintis)
    select 
        customer_id,
        recency_days,
        frequency,
        monetary,
        -- Para Recência: Quem tem MENOS dias ganha nota MAIOR (5)
        ntile(5) over (order by recency_days desc) as r_score,
        -- Para Frequência e Monetário: Quem tem MAIS ganha nota MAIOR (5)
        ntile(5) over (order by frequency asc) as f_score,
        ntile(5) over (order by monetary asc) as m_score
    from rfm_base
)

select 
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    -- Concatena as notas (Ex: 555 é o melhor cliente, 111 é o pior)
    cast(r_score as varchar) || cast(f_score as varchar) || cast(m_score as varchar) as rfm_code,
    
    -- 3. Segmentação Humanizada (Lógica de Negócio Sênior)
    case 
        when r_score >= 4 and f_score >= 4 and m_score >= 4 then 'Champions 🏆'
        when r_score >= 3 and f_score >= 3 and m_score >= 3 then 'Loyal Customers 💎'
        when r_score >= 3 and f_score >= 1 and m_score >= 2 then 'Promising 🌱'
        when r_score <= 2 and f_score >= 3 and m_score >= 3 then 'At Risk ⚠️' -- Comprava muito mas parou
        when r_score = 1 and f_score = 1 then 'Lost/Hibernating 💤'
        else 'Standard'
    end as customer_segment
from rfm_scores