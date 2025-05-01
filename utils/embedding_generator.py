# app/utils/embedding_generator.py

import os
import time
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer
from utils.data_cleaner import DataCleaner

class EmbeddingGenerator:
    def __init__(self, model_path, data_path, embeddings_path):
        self.model_path = model_path
        self.data_path = data_path
        self.embeddings_path = embeddings_path
        self.model = None
        self.questions = []
        self.contexts = []

    def load_model(self):
        if not os.path.exists(self.model_path):
            print("📥 Model not found. Downloading...")
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            os.makedirs(self.model_path, exist_ok=True)
            self.model.save(self.model_path)
        else:
            print(f"🧠 Loading model from {self.model_path}...")
            self.model = SentenceTransformer(self.model_path)

    def clean_and_load_data(self, question_col='questions', answer_col='answer'):
        cleaner = DataCleaner(self.data_path)
        cleaner.load_data()
        # cleaner.clean_columns(question_col, answer_col)
        cleaner.clean_columns("questions", "answer")

        df = cleaner.df
        self.questions = df[question_col].tolist()
        self.contexts = df[answer_col].tolist()
        print(f"📊 Loaded {len(self.questions)} Q&A pairs")

    def generate_embeddings(self):
        if not self.contexts:
            raise ValueError("❌ No contexts to embed. Load data first.")

        print(f"📦 Generating embeddings for {len(self.contexts):,} answers...")
        start = time.time()
        embeddings = self.model.encode(self.contexts, convert_to_tensor=True)
        duration = time.time() - start

        os.makedirs(os.path.dirname(self.embeddings_path), exist_ok=True)
        torch.save(embeddings, self.embeddings_path)

        print(f"✅ Embeddings saved to: {self.embeddings_path}")
        print(f"⏱️ Time taken: {duration:.2f} sec ({duration/60:.2f} min)")
        return embeddings

    def load_or_generate_embeddings(self):
        if os.path.exists(self.embeddings_path):
            print("📦 Loading cached embeddings...")
            return torch.load(self.embeddings_path)
        else:
            return self.generate_embeddings()