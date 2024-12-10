import requests
import json
import pandas as pd
import google.generativeai as genai
from decouple import config

from data_processing import get_gemini_insights, create_deputy_arrangement_pizza_figure, \
    get_deputy_arrangement_pizza_data

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/"

genai.configure(api_key=config('GOOGLE_API_KEY'))

def collect_data():
    response = requests.get(BASE_URL + "/deputados").text
    response_obj = json.loads(response)
    df = pd.DataFrame(response_obj['dados'])
    return df

def collect_proposition_data():
    response = requests.get(BASE_URL + "/proposicoes?codTema=62,40,46&ordem=ASC&ordenarPor=id").text
    response_obj = json.loads(response)
    df = pd.DataFrame(response_obj['dados'])

    df['subjects'] = None

    for index, row in df.iterrows():
        subjects = []
        id = row["id"]
        url = BASE_URL + f"/proposicoes/{id}/temas"
        result = json.loads(requests.get(url).text)
        for subject in result['dados']:
            subjects.append(subject['codTema'])

        df.at[index, 'subjects'] = subjects

    return df

def collect_spending_data():

    df = pd.read_parquet('data/deputados/deputados.parquet')

    results = None

    for index, row in df.iterrows():
        id = row["id"]
        url = BASE_URL + f"/deputados/{id}/despesas"
        result = json.loads(requests.get(url).text)
        df = pd.DataFrame(result['dados'])

        if not "mes" in df.columns or not "ano" in df.columns:
            continue

        df = df.groupby(["ano", "mes"], dropna=True, as_index=False).agg({'valorDocumento': 'sum'})

        df["deputado_id"] = id
        df["deputado_nome"] = row["nome"]
        df["deputado_sigla_partido"] = row["siglaPartido"]
        df["deputado_sigla_uf"] = row["siglaUf"]

        results = pd.concat([results, df])

    return results

def collect_spends_per_political_party(df):
    spends_per_party = df.groupby('deputado_sigla_partido')['valorDocumento'].agg(['sum', 'count']).reset_index()
    spends_per_party.columns = ['Partido', 'Total Gasto', 'Quantidade de Despesas']
    spends_per_party = spends_per_party.sort_values('Total Gasto', ascending=False)
    spends_per_party.to_parquet('data/deputados/gastos_por_partido.parquet')

def collect_spends_per_month(df):
    spends_per_month = df.groupby('mes')['valorDocumento'].sum().reset_index()
    spends_per_month.to_parquet('data/deputados/gastos_por_mes.parquet')

def collect_political_ranking(df):
    ranking = df.groupby(['deputado_nome', 'deputado_sigla_partido', 'deputado_sigla_uf'])['valorDocumento'].agg(['sum', 'count']).reset_index()
    ranking.columns = ['Deputado', 'Partido', 'UF', 'Total Gasto', 'Quantidade de Despesas']
    ranking = ranking.sort_values('Total Gasto', ascending=False).head(10)
    ranking.to_parquet('data/deputados/ranking_politica.parquet')

def collect_and_save_pizza_insights_gemini(pizza_data):
    insights = get_gemini_insights(pizza_data)

    with open('data/deputados/insights_distribuicao_deputados.json', 'w') as f:
        json.dump({"insight": insights}, f)

if __name__ == "__main__":
    deputy_data = collect_data()
    deputy_data.to_parquet('data/deputados/deputados.parquet')

    proposition_data = collect_proposition_data()
    proposition_data.to_parquet('data/deputados/proposicoes.parquet')

    spends = collect_spending_data()
    spends.to_parquet('data/deputados/serie_despesas_diárias_deputados.parquet')

    #Question 3 - Visualization
    pizza_data = get_deputy_arrangement_pizza_data()
    figure = create_deputy_arrangement_pizza_figure(pizza_data)
    figure.write_image('docs/distribuicao_deputados.png')

    #Question 4 - Analysis
    collect_spends_per_political_party(spends)
    collect_political_ranking(spends)
    collect_spends_per_month(spends)
    collect_and_save_pizza_insights_gemini(pizza_data)

