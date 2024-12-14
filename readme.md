# Dashboard de Análise da Câmara dos Deputados (AT Prompt Engineering)

## Descrição do Projeto
Este projeto consiste em uma dashboard interativa para análise de dados da Câmara dos Deputados Federal do Brasil, utilizando técnicas avançadas de Prompt Engineering. O sistema integra:

- Dashboard interativa com visualizações dinâmicas
- Sistema RAG (Retrieval-Augmented Generation) utilizando Gemini
- Integração com a API oficial da Câmara dos Deputados
- Análises estatísticas e insights sobre a atividade parlamentar

Foram implementadas técnicas de Prompt Engineering como:
- Chain of Thought (CoT) para raciocínio estruturado
- Self-Ask para refinamento de consultas
- Few-Shot Learning para melhor precisão nas respostas

## Tecnologias Utilizadas
- Python 3.9+
- Streamlit
- Google Gemini
- Pandas
- Plotly
- FastAPI

## Como Rodar o Projeto

### 1. Criação do Ambiente Virtual
```bash
conda create -n camara-dashboard python=3.9
```

### 2. Ativação do Ambiente
```bash
conda activate camara-dashboard
```

### 3. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração das Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
GEMINI_API_KEY=sua_chave_api
CAMARA_API_TOKEN=seu_token_api
```

### 5. Carregamento dos Dados (Opcional)
```bash
python data_prep.py
```
Este script baixa e processa os dados mais recentes da Câmara dos Deputados.

### 6. Execução da Interface
```bash
streamlit run app/main.py
```
