from google.generativeai import embed_content, configure
from dotenv import load_dotenv
from os import getenv


class EmbeddingModel:
    def __init__(self, api_key: str):
        configure(api_key=api_key)

    def generate_embeddings(self, text: str):
        result = embed_content(model="models/embedding-001", content=text)
        return result["embedding"]
    
if __name__ == "__main__":
    load_dotenv()
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    print(embedding_model.generate_embeddings("Hello, world!"))
    print(embedding_model.generate_embeddings("Goodbye, world!"))
    print(embedding_model.generate_embeddings("Hello, world!"))
