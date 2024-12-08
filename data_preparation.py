import requests
import json
import pandas as pd
import google.generativeai as genai
from decouple import config


BASE_URL = "https://dadosabertos.camara.leg.br/api/v2/"

genai.configure(api_key=config('GOOGLE_API_KEY'))

def collect_data():
    response = requests.get(BASE_URL + "/deputados").text
    response_obj = json.loads(response)
    df = pd.DataFrame(response_obj['dados'])
    df.to_parquet('data/deputados/deputados.parquet')

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

    df.to_parquet('data/deputados/proposicoes.parquet')

def collect_pricing_data():

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

    results.to_parquet('data/deputados/serie_despesas_diárias_deputados.parquet')

if __name__ == "__main__":
    collect_data()
    collect_pricing_data()
    collect_proposition_data()
