import streamlit as st
import yaml
from PIL import Image
import json
import pandas as pd
import plotly.express as px

from data_processing import generate_self_ask_questions, generate_self_ask_response
from vetorization import TextVectorizer

# Configuração da página
st.set_page_config(
    page_title="Portal da Câmara",
    page_icon="🏛️",
    layout="wide"
)

# Carrega o arquivo de configuração
try:
    with open('data/config.yml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
except:
    config = {"overview_summary": "Erro ao carregar arquivo de configuração"}

# Carrega o arquivo de insights
try:
    with open('data/deputados/insights_distribuicao_deputados.json', 'r', encoding='utf-8') as file:
        insights = json.load(file)
except:
    insights = {"insight": "Erro ao carregar arquivo de insights"}

# Carrega o arquivo de insights de proposições
try:
    with open('data/deputados/sumarizacao_proposicoes.json', 'r', encoding='utf-8') as file:
        insights_propositions = json.load(file)
except:
    insights_propositions = {"insight": "Erro ao carregar arquivo de proposition_insights"}

# Carrega o arquivo de insights de despesas
try:
    with open('data/deputados/insights_despesas_deputados.json', 'r', encoding='utf-8') as file:
        insights_despesas = json.load(file)
except:
    insights_despesas = {"insights": "Erro ao carregar arquivo de insights de despesas"}

# Carrega o dataset de despesas
try:
    df_despesas = pd.read_parquet('data/deputados/serie_despesas_diárias_deputados.parquet')
except:
    df_despesas = pd.DataFrame()

# Carrega o dataset de proposições
try:
    df_proposicoes = pd.read_parquet('data/deputados/proposicoes.parquet')
except:
    df_proposicoes = pd.DataFrame()

def get_vector_database():
    # Cria o vetorizador
    vectorizer = TextVectorizer()
    vectorizer.load()

    # Carrega todos os textos da base de dados
    return vectorizer

def generate_self_ask(query: str):
    vector_database = get_vector_database()
    results = vector_database.search(query)

    questions = generate_self_ask_questions(query)
    answer = generate_self_ask_response(questions, optional_data=results)
    st.write(answer)

tab1, tab2, tab3 = st.tabs(["Overview", "Despesas", "Proposições"])

with tab1:
    st.title("Portal da Câmara dos Deputados")
    st.markdown("""
        Este portal tem como objetivo trazer transparência e facilitar o acesso
        às informações da Câmara dos Deputados do Brasil.
    """)

    st.subheader("Como funciona a Câmara dos Deputados")
    st.write(config.get("overview_summary", ""))

    st.subheader("Distribuição de Despesas dos Deputados")

    try:
        imagem = Image.open('docs/distribuicao_deputados.png')
        st.image(imagem, caption='Distribuição de Despesas por Deputado', width=600)
        st.write(insights.get("insight", ""))
    except:
        st.error("Não foi possível carregar a imagem. Verifique se o arquivo existe no caminho especificado.")

with tab2:
    st.title("Análise de Despesas")

    # Exibe insights sobre despesas
    st.subheader("Insights sobre Despesas")
    st.write(insights_despesas.get("insights", ""))

    # Selectbox para escolha do deputado
    if not df_despesas.empty:
        deputados = sorted(df_despesas['deputado_nome'].unique())
        deputado_selecionado = st.selectbox("Selecione um Deputado:", deputados)

        # Filtra dados do deputado selecionado
        dados_deputado = df_despesas[df_despesas['deputado_nome'] == deputado_selecionado]

        # Agrupa dados por ano e mês
        dados_agrupados = dados_deputado.groupby(['ano', 'mes'])['valorDocumento'].sum().reset_index()
        dados_agrupados['data'] = pd.to_datetime(dados_agrupados['ano'].astype(str) + '-' + dados_agrupados['mes'].astype(str) + '-01')

        # Cria gráfico de barras
        fig = px.bar(
            dados_agrupados,
            x='data',
            y='valorDocumento',
            title=f'Despesas mensais do deputado {deputado_selecionado}',
            labels={'data': 'Data', 'valorDocumento': 'Valor (R$)'}
        )
        st.plotly_chart(fig)
    else:
        st.error("Não foi possível carregar os dados de despesas")

with tab3:
    st.title("Análise das Proposições")
    st.subheader("Resumo das Proposições em Educação, Ciências e Economia")
    st.write(insights_propositions.get("insight", ""))

    # Exibe tabela de proposições
    if not df_proposicoes.empty:
        st.subheader("Tabela de Proposições")
        st.dataframe(df_proposicoes)
    else:
        st.error("Não foi possível carregar os dados das proposições")

    st.subheader("Busca por palavra ou frase")

    text_input = st.text_input("Insira uma palavra ou frase para procurar:", key="self_ask")
    if text_input:
        with st.spinner("Buscando resposta..."):
            generate_self_ask(text_input)

# Rodapé
st.markdown("""
---
*Portal desenvolvido para acompanhamento das atividades parlamentares*
""")