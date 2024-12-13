import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
import numpy as np
from typing import List, Dict
import pickle

class TextVectorizer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        self.model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.path = 'data/index.bin'

        self.dimension = 768
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_text = {}
        self.current_id = 0

    def get_bert_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=512,
                                return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        return embeddings[0]

    def add_text(self, text: str):
        vector = self.get_bert_embedding(text)

        faiss.normalize_L2(vector.reshape(1, -1))
        self.index.add(vector.reshape(1, -1))

        self.id_to_text[self.current_id] = text
        self.current_id += 1

    def add_dataset(self, df: pd.DataFrame):

        text_lines = df.apply(lambda row: ", ".join(f"{col}: {value}" for col, value in row.items()), axis=1)

        for text_line in text_lines:
            text = str(text_line)
            print("Texto adicionado: ", text)
            vector = self.get_bert_embedding(text)

            faiss.normalize_L2(vector.reshape(1, -1))
            self.index.add(vector.reshape(1, -1))

            self.id_to_text[self.current_id] = text
            self.current_id += 1

    def save(self):
        faiss.write_index(self.index, self.path)
        with open('data/id_to_text.pkl', 'wb') as f:
            pickle.dump(self.id_to_text, f)

    def load(self):
        self.index = faiss.read_index(self.path)
        with open('data/id_to_text.pkl', 'rb') as f:
            self.id_to_text = pickle.load(f)

    def search(self, query: str, k: int = 5) -> List[Dict]:
        query_vector = self.get_bert_embedding(query)
        faiss.normalize_L2(query_vector.reshape(1, -1))

        distances, indices = self.index.search(query_vector.reshape(1, -1), k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.id_to_text[idx])

        return results
