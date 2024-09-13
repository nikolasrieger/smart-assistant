from lib.llm_models.embeddings import EmbeddingModel
from lib.web_search.search_engine import SearchResult, SearchEngine
from numpy import array, float32
from faiss import IndexFlatL2
from dotenv import load_dotenv
from os import getenv

class ContextGenerator:
    def __init__(self, api_key: str):
        self.__embedding_model = EmbeddingModel(api_key)
        embedding_len = len(self.__embedding_model.generate_embeddings("embedding length test"))
        self.__index = IndexFlatL2(embedding_len)
        self.__data = []
        
    def add_data(self, texts: list[SearchResult]):
        for text in texts:
            embedding = self.__embedding_model.generate_embeddings(text.url + " " + text.info)
            embedding_array = array([embedding], dtype=float32)
            self.__index.add(embedding_array)
            self.__data.append(text)

    def search(self, search_text: str):
        embedding = self.__embedding_model.generate_embeddings(search_text)
        embedding_array = array([embedding], dtype=float32)
        _, indices = self.__index.search(embedding_array, 3)
        results = [self.__data[idx] for idx in indices[0]]
        return results
    
    def remove_data(self, text: list[SearchResult]):
        for data in text:
            index = self.__data.index(data)
            if index != -1: self.__remove_index(index)

    def __remove_index(self, index: int):
        self.__index.remove(index)
        self.__data.pop(index)
    

if __name__ == "__main__":
    load_dotenv()
    context = ContextGenerator(getenv("GEMINI_API_KEY"))
    search = SearchEngine()
    context.add_data(search.search("How to code an AI?"))
    print(context.search("How to code an AI?"))
