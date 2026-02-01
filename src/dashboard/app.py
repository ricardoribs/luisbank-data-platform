import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# --- 1. Configuração da Página ---
st.set_page_config(
    page_title="LuisBank | Executive Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS para visual corporativo ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 0rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Conexão Otimizada ---
DB_PATH = "data/luisbank.duckdb"

@st.cache_data(ttl=300)
def get_data(query, params=None):
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        if params:
            df = con.execute(query, params).df()
        else:
            df = con.execute(query).df()
        return df
    finally:
        con.close()

# --- 3. Sidebar de Filtros ---
with st.sidebar:
    st.title("Parâmetros")
    
    try:
        dates_df = get_data(
            "SELECT min(transaction_at) as min_d, max(transaction_at) as max_d FROM main.fct_transactions"
        )
        min_date = dates_df['min_d'][0].date()
        max_date = dates_df['max_d'][0].date()
    except:
        min_date = date.today()
        max_date = date.today()

    date_range = st.date_input(
        "Período de Análise (Transacional)",
        value=(max_date - timedelta(days=30), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = date_range[0], date_range[0]

    st.caption("Filtro ativo para abas Financeiras.")
    st.markdown("---")
    
    all_types = ["PIX_IN", "PIX_OUT", "TED_IN", "TED_OUT", "BOLETO_PAY"]
    tipo_transacao = st.multiselect(
        "Tipo de Transação",
        all_types,
        default=all_types
    )

# --- 4. Query Principal (Financeiro) ---
if not tipo_transacao:
    st.warning("Selecione um tipo de transação.")
    st.stop()

formatted_types = ", ".join([f"'{x}'" for x in tipo_transacao])
main_query = f"""
    SELECT * FROM main.fct_transactions 
    WHERE cast(transaction_at as date) BETWEEN ? AND ?
    AND transaction_type IN ({formatted_types})
"""
df_main = get_data(main_query, [start_date, end_date])

# --- 5. Lógica de KPIs ---
total_vol = df_main['amount'].sum()
total_txns = df_main.shape[0]
avg_ticket = df_main['amount'].mean() if total_txns > 0 else 0
risk_txns = df_main[df_main['amount'] > 5000].shape[0]

# --- 6. Layout ---
st.title("LuisBank Financial Overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Volume Total", f"R$ {total_vol:,.2f}", "12.5%")
c2.metric("Transações", f"{total_txns}", "-2.1%")
c3.metric("Ticket Médio", f"R$ {avg_ticket:,.2f}")
c4.metric(
    "Risco (>5k)",
    risk_txns,
    "High" if risk_txns > 10 else "Low",
    delta_color="inverse"
)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Visão Temporal",
    "Composição",
    "Marketing & CRM",
    "Auditoria"
])

# TAB 1: Temporal
with tab1:
    if not df_main.empty:
        daily_df = (
            df_main
            .groupby(df_main['transaction_at'].dt.date)['amount']
            .sum()
            .reset_index()
        )
        fig = px.area(
            daily_df,
            x='transaction_at',
            y='amount',
            title="Tendência de Volume",
            markers=True
        )
        fig.update_layout(
            template="plotly_white",
            xaxis_title=None,
            yaxis_title=None
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados no período.")

# TAB 2: Composição
with tab2:
    if not df_main.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            type_df = (
                df_main
                .groupby('transaction_type')['amount']
                .sum()
                .reset_index()
            )
            fig_bar = px.bar(
                type_df,
                y='transaction_type',
                x='amount',
                orientation='h',
                title="Distribuição por Tipo",
                text_auto='.2s'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_b:
            fig_scat = px.scatter(
                df_main,
                x='transaction_at',
                y='amount',
                color='transaction_type',
                title="Dispersão de Transações"
            )
            st.plotly_chart(fig_scat, use_container_width=True)
    else:
        st.info("Sem dados no período.")

# TAB 3: Marketing & CRM
with tab3:
    st.subheader("Segmentação Inteligente (RFM)")
    
    try:
        rfm_query = """
            SELECT
                customer_segment,
                count(*) as clientes,
                avg(monetary) as ticket_medio,
                sum(monetary) as ltv_total
            FROM main.dm_rfm_segmentation
            GROUP BY 1
            ORDER BY 2 DESC
        """
        df_rfm = get_data(rfm_query)
        
        col_crm1, col_crm2, col_crm3 = st.columns(3)
        champions = df_rfm[
            df_rfm['customer_segment'].str.contains('Champions')
        ]['clientes'].sum()
        at_risk = df_rfm[
            df_rfm['customer_segment'].str.contains('Risk')
        ]['clientes'].sum()
        
        col_crm1.metric("Champions", champions)
        col_crm2.metric("Em Risco", at_risk, delta_color="inverse")
        col_crm3.metric("Total Segmentados", df_rfm['clientes'].sum())
        
        fig_tree = px.treemap(
            df_rfm,
            path=['customer_segment'],
            values='clientes',
            color='customer_segment',
            title="Distribuição da Base de Clientes (RFM)"
        )
        fig_tree.update_traces(
            textinfo="label+value+percent entry",
            textfont=dict(size=14),
            textposition="middle center"
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.markdown("#### Ação Recomendada: Resgatar Clientes em Risco")
        st.caption("Baixe a lista abaixo e envie para o time de Marketing.")
        
        risk_list_query = """
            SELECT
                r.customer_id,
                c.email,
                c.first_name,
                r.recency_days,
                r.monetary as total_gasto
            FROM main.dm_rfm_segmentation r
            JOIN main.dim_customers c
              ON r.customer_id = c.customer_id
            WHERE r.customer_segment LIKE '%Risk%'
            ORDER BY r.monetary DESC
        """
        df_risk_list = get_data(risk_list_query)
        
        st.dataframe(
            df_risk_list,
            hide_index=True,
            use_container_width=True
        )
        
        st.download_button(
            "Baixar Lista de Resgate (CSV)",
            data=df_risk_list.to_csv(index=False).encode('utf-8'),
            file_name="campanha_winback_luisbank.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(
            "Erro ao carregar dados de Marketing. "
            "Execute o pipeline completo (make pipeline). "
            f"Detalhe: {e}"
        )

# TAB 4: Auditoria
with tab4:
    if not df_main.empty:
        st.subheader("Auditoria de Transações")
        audit_df = (
            df_main[df_main['amount'] > 1000]
            .sort_values('amount', ascending=False)
        )
        st.dataframe(
            audit_df[
                ['transaction_id', 'amount', 'status', 'counterparty_bank']
            ],
            use_container_width=True
        )
    else:
        st.info("Sem dados no período.")
