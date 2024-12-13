import json

import pandas as pd
from decouple import config
import google.generativeai as genai
import plotly.express as px

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

def generate_self_ask_questions(base_question:str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Com base na pergunta abaixo, retorne uma lista de perguntas relacionadas ao que foi perguntado:
    
    Além disso, melhore a questão base.
    
    {base_question}

    """

    return model.generate_content(prompt).text

def generate_self_ask_response(questions:str, optional_data=""):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Com base nos dados apresentados, responda todas as perguntas abaixo detalhadamente e separadamente, responada em markdown:
    
    <dados>
        {optional_data}
    <dados>
    
    {questions}
    """

    return model.generate_content(prompt).text

def chunking_text(text:str):
    text = text.split(" ")
    chunk_size = 100
    chunk_interception = 20

    chunks : list[list[str]] = []

    for i in range(0, len(text), chunk_size):
        start = 0 if i < chunk_interception else i - chunk_interception
        end = chunk_size + i
        chunk = text[start:i + end]
        chunks.append(chunk)

    return chunks

def summarize_text(text:str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are a summarization system. Your job is to make a consice summary of brazilian laws proposals.
    
    1. The summary must be in portuguese.
    
    Summarize the following text:
    <TEXT>
        {text}
    </TEXT>

    """
    return model.generate_content(prompt).text

def summarize_chunks(chunks):

    summaries = []

    for chunk in chunks:
        text = " ".join(chunk)
        summaries.append(summarize_text(text))

    summary = " ".join(summaries)
    summary = summarize_text(summary)

    return summary

def create_deputy_arrangement_pizza_figure(deputy_data):
    fig = px.pie(
        deputy_data,
        names="Partido",
        values="Numero_Total_Deputados",
        title="Distribuição dos Deputados por Partido",
    )
    return fig


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
