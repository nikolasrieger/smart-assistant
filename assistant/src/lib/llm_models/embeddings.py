from google.generativeai import embed_content, configure
from google.api_core.exceptions import InternalServerError, ServiceUnavailable


class EmbeddingModel:
    def __init__(self, api_key: str):
        configure(api_key=api_key)
        self.__errors = 0

    def generate_embeddings(self, text: str):
        try:
            result = embed_content(model="models/embedding-001", content=text)
            self.__errors = 0
        except InternalServerError:
            print("[ERROR]:  Internal Server Error")
            self.check_abort()
            return
        except ServiceUnavailable:
            print("[ERROR]:  Service Unavailable")
            self.check_abort()
            return
        return result["embedding"]

    def check_abort(self):
        if self.__errors > 5:
            raise Exception("Failed to connect to the embedding model too many times.")
