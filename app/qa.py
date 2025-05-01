# qa.py

import time
from sentence_transformers import util
import torch

from utils.embedding_generator import EmbeddingGenerator

# إعداد المسارات
MODEL_PATH = './models/paraphrase-multilingual-MiniLM-L12-v2'
DATA_PATH="./data/dataset.csv"
EMBEDDINGS_PATH = './data/embeddings_ar.pt'

# إنشاء نسخة من الكلاس
generator = EmbeddingGenerator(MODEL_PATH, DATA_PATH, EMBEDDINGS_PATH)
generator.load_model()
generator.clean_and_load_data()

# حفظ المتغيرات للاستخدام
questions = generator.questions
contexts = generator.contexts
embeddings = generator.load_or_generate_embeddings()

def get_best_answer(user_question: str) -> str:
    print("🤖 Answering...")
    start_time = time.time()

    q_embed = generator.model.encode(user_question, convert_to_tensor=True)
    # print(q_embed)
    print (q_embed.shape)
    scores = util.pytorch_cos_sim(q_embed, embeddings)[0]
    # print (scores)
    print (scores.shape)
    best_idx = int(torch.argmax(scores))
    print (best_idx)
    answer = contexts[best_idx]

    elapsed = time.time() - start_time
    print(f"✅ Answer ready in {elapsed:.3f} seconds")
    return answer