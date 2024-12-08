import streamlit as st
import plotly.express as px

from data_processing import get_deputy_arrangement_pizza_data


@st.cache_data()
def get_deputy_data():
    return get_deputy_arrangement_pizza_data()

deputy_data = get_deputy_data()

fig = px.pie(
    deputy_data,
    names="Partido",
    values="Numero_Total_Deputados",
    title="Distribuição dos Deputados por Partido",
)

st.title("Gráfico de Pizza - Deputados por Partido")
st.plotly_chart(fig)

