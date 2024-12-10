import streamlit as st
import yaml
from PIL import Image
import json

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

# Definição das abas
tab1, tab2, tab3 = st.tabs(["Overview", "Despesas", "Proposições"])

with tab1:
    st.title("Portal da Câmara dos Deputados")
    st.markdown("""
        Este portal tem como objetivo trazer transparência e facilitar o acesso
        às informações da Câmara dos Deputados do Brasil.
    """)

    st.subheader("Como funciona a Câmara dos Deputados")
    st.write(config.get("overview_summary", ""))

with tab2:
    st.subheader("Distribuição de Despesas dos Deputados")

    try:
        imagem = Image.open('docs/distribuicao_deputados.png')
        st.image(imagem, caption='Distribuição de Despesas por Deputado', width=600)
    except:
        st.error("Não foi possível carregar a imagem. Verifique se o arquivo existe no caminho especificado.")

with tab3:
    st.title("Análise das Proposições")
    st.subheader("Resumo das Proposições em Educação, Ciências e Economia")
    st.write(insights.get("insight", ""))

# Rodapé
st.markdown("""
---
*Portal desenvolvido para acompanhamento das atividades parlamentares*
""")