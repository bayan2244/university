# app/utils/data_cleaner.py

import pandas as pd
import re

class DataCleaner:
    def __init__(self, path):
        self.path = path
        self.df = None

    def load_data(self):
        print(f"📄 Loading dataset: {self.path}")
        self.df = pd.read_csv(self.path).dropna()
        print(f"✅ Loaded {len(self.df)} rows")        
        print("📋 Available columns:", self.df.columns.tolist())


    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub(r"http\S+", "", text)  # Remove URLs
        text = re.sub(r"[^ء-يa-zA-Z0-9\s.,!?؟]", "", text)  # Keep Arabic/English and punctuations
        text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
        return text

    def clean_columns(self, question_col='questions', answer_col='answer'):
        if self.df is None:
            raise ValueError("❌ Please load data first.")
        print("🧼 Cleaning data...")
        self.df[question_col] = self.df[question_col].apply(self._clean_text)
        self.df[answer_col] = self.df[answer_col].apply(self._clean_text)
        self.df.dropna(subset=[question_col, answer_col], inplace=True)
        print(f"✅ Cleaned data: {self.df.shape[0]} rows remaining")

    def save_cleaned(self, output_path):
        if self.df is None:
            raise ValueError("❌ No cleaned data to save.")
        self.df.to_csv(output_path, index=False)
        print(f"💾 Cleaned data saved to: {output_path}")
