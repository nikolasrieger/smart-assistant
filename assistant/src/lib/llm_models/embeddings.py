from google.generativeai import embed_content, configure
from google.api_core.exceptions import InternalServerError, ServiceUnavailable


class EmbeddingModel:
    def __init__(self, api_key: str):
        configure(api_key=api_key)

    def generate_embeddings(self, text: str):
        try:
            result = embed_content(model="models/embedding-001", content=text)
        except InternalServerError:
            print("[ERROR]:  Internal Server Error")
            return
        except ServiceUnavailable:
            print("[ERROR]:  Service Unavailable")
            return
        return result["embedding"]
