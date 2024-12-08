import json

import pandas as pd
from decouple import config
import google.generativeai as genai

genai.configure(api_key=config('GOOGLE_API_KEY'))

def get_deputy_data():
    return pd.read_parquet('data/deputados/deputados.parquet')

def get_deputy_spending_data():
    return pd.read_parquet('data/deputados/despesas.parquet')

def get_gemini_insights(any):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Com base nos dados abaixo, retorne insights valisoso sobre a informação abaixo:
    
    {any}

    """

    return model.generate_content(prompt).text

def get_deputy_arrangement_pizza_data():
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
          Com base nos dados abaixo, retorne uma resposta em JSON no seguinte formato:
        
          [ 
            {{
              "Partido": "PL"
              "Numero_Total_Deputados": 100,
            }}
            {{
              "Partido": "PL"
              "Numero_Total_Deputados": 100,
            }}
          ]
          
          1. Faça um desse por partido, e junte todos em uma lista
        
          <DATA>
            {get_deputy_data()}
          </DATA>
    """

    response = model.generate_content(prompt,
                                      generation_config=genai.GenerationConfig(response_mime_type="application/json",))

    return json.loads(response.text)
