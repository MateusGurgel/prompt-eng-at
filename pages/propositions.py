import streamlit as st
import pandas as pd

from data_processing import chunking_text, summarize_chunks


def get_selected_propositions_text():
    df = pd.read_parquet('data/deputados/proposicoes.parquet')

    document = ' '.join(df.astype(str).values.flatten())
    return document

def main():
    st.title("📊 Resumo de Proposições de Economia, Educação e Ciência")

    with st.spinner('Gerando resumo...'):
        chunks = chunking_text(get_selected_propositions_text())
        summary = summarize_chunks(chunks)
        st.write(summary)

if __name__ == "__main__":
    main()