import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from data_processing import get_gemini_insights

# Configuração da página
st.set_page_config(
    page_title="Análise de Despesas - Deputados",
    page_icon="📊",
    layout="wide"
)

@st.cache_data()
def load_despesas_dataset() -> pd.DataFrame:
    """
    Carrega o dataset de despesas dos deputados a partir do arquivo parquet.

    Returns:
        pd.DataFrame: DataFrame contendo os dados de despesas
    """
    file_path = Path('data/deputados/serie_despesas_diárias_deputados.parquet')
    df = pd.read_parquet(file_path)
    return df

def criar_gasto_por_partido(df):
    """Cria DF de gastos por partido"""
    gastos_partido = df.groupby('deputado_sigla_partido')['valorDocumento'].agg(['sum', 'count']).reset_index()
    gastos_partido.columns = ['Partido', 'Total Gasto', 'Quantidade de Despesas']
    gastos_partido = gastos_partido.sort_values('Total Gasto', ascending=False)
    return gastos_partido

def criar_grafico_partido(df):
    """Cria gráfico de gastos por partido"""
    gastos_partido = criar_gasto_por_partido(df)

    fig = px.bar(gastos_partido,
                 x='Partido',
                 y='Total Gasto',
                 title='Gastos Totais por Partido',
                 color='Total Gasto')

    fig.update_layout(xaxis_title="Partido",
                      yaxis_title="Valor Total (R$)")
    return fig

def criar_gasto_por_mes(df):
    """Cria DF de gastos por mês"""
    gastos_mes = df.groupby('mes')['valorDocumento'].sum().reset_index()
    return gastos_mes

def criar_grafico_temporal(df):
    """Cria gráfico de evolução temporal dos gastos"""
    gastos_mensais = criar_gasto_por_mes(df)

    fig = px.line(gastos_mensais,
                  x='mes',
                  y='valorDocumento',
                  title='Evolução dos Gastos ao Longo do Tempo',
                  markers=True)

    fig.update_layout(xaxis_title="Data",
                      yaxis_title="Valor Total (R$)")
    return fig

def criar_ranking_deputados(df):
    """Cria ranking dos deputados que mais gastaram"""
    ranking = df.groupby(['deputado_nome', 'deputado_sigla_partido', 'deputado_sigla_uf'])['valorDocumento'].agg(['sum', 'count']).reset_index()
    ranking.columns = ['Deputado', 'Partido', 'UF', 'Total Gasto', 'Quantidade de Despesas']
    ranking = ranking.sort_values('Total Gasto', ascending=False).head(10)
    return ranking

def criar_insights_gemini(df):
    """Cria insights com Gemini"""
    ranking = criar_ranking_deputados(df)
    gastos_mes = criar_gasto_por_mes(df)
    gastos_partido = criar_gasto_por_partido(df)
    return get_gemini_insights([ranking, gastos_mes, gastos_partido])



def main():
    # Título da página
    st.title("📊 Análise de Despesas dos Deputados")

    # Carregando os dados
    with st.spinner('Carregando dados...'):
        df = load_despesas_dataset()

    if not df.empty:
        # Métricas gerais
        st.subheader("Visão Geral")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Gasto", f"R$ {df['valorDocumento'].sum():,.2f}")
        with col2:
            st.metric("Quantidade de Deputados", f"{df['deputado_id'].nunique():,}")
        with col3:
            st.metric("Quantidade de Partidos", f"{df['deputado_sigla_partido'].nunique():,}")
        with col4:
            st.metric("Total de Registros", f"{len(df):,}")

        # Análise 1: Gastos por Partido
        st.subheader("Análise por Partido")
        fig_partido = criar_grafico_partido(df)
        st.plotly_chart(fig_partido, use_container_width=True)

        # Análise 2: Evolução Temporal
        st.subheader("Evolução Temporal dos Gastos")
        fig_temporal = criar_grafico_temporal(df)
        st.plotly_chart(fig_temporal, use_container_width=True)

        # Análise 3: Ranking de Deputados
        st.subheader("Top 10 Deputados por Gastos")
        ranking = criar_ranking_deputados(df)

        # Formatando a coluna de valor total
        ranking['Total Gasto Formatado'] = ranking['Total Gasto'].apply(lambda x: f'R$ {x:,.2f}')

        st.dataframe(
            ranking[['Deputado', 'Partido', 'UF', 'Total Gasto Formatado', 'Quantidade de Despesas']],
            use_container_width=True,
            hide_index=True
        )

        # Análise 4: Gerar insights com Gemini
        st.subheader("Insights com Gemini")
        with st.spinner('Gerando insights com Gemini...'):
            insights = criar_insights_gemini(df)
            st.write(insights)




if __name__ == "__main__":
    main()