from app import create_app
from utils.embedding_generator import EmbeddingGenerator


# أنشئ تطبيق Flask من خلال الدالة create_app() الموجودة في app/__init__.py
app = create_app()

if __name__ == "__main__":

    generator = EmbeddingGenerator(        
        model_path="./models/paraphrase-multilingual-MiniLM-L12-v2",        
        data_path="./data/dataset.csv",
        embeddings_path="./data/embeddings.pt"
    )
     
    # 🟢 تشغيل السيرفر (محليًا)
    app.run(debug=True, host="0.0.0.0", port=5000)
