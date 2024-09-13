from google.generativeai import embed_content, configure

class EmbeddingModel():
    def __init__(self, api_key: str):
        configure(api_key=api_key)

    def generate_embeddings(self, text: str):
        result = embed_content(
            model="models/embedding-001",
            content=text)
        return result["embedding"]
