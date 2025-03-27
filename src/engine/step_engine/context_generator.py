from lib.llm_models.embeddings import EmbeddingModel
from lib.web_search.search_engine import SearchResult, SearchEngine
from numpy import array, float32
from faiss import IndexFlatL2


class ContextIndex:
    def __init__(self, embedding_model: EmbeddingModel):
        self.__embedding_model = embedding_model
        test_embedding = self.__embedding_model.generate_embeddings(
            "embedding length test"
        )
        while test_embedding is None:
            test_embedding = self.__embedding_model.generate_embeddings(
                "embedding length test"
            )
        embedding_len = len(test_embedding)
        self.__index = IndexFlatL2(embedding_len)
        self.__data = []

    def add_data(self, texts: list[SearchResult]):
        for text in texts:
            embedding = self.__embedding_model.generate_embeddings(
                text.url + " " + text.info
            )
            while embedding is None:
                embedding = self.__embedding_model.generate_embeddings(
                    text.url + " " + text.info
                )
            embedding_array = array([embedding], dtype=float32)
            self.__index.add(embedding_array)
            self.__data.append(text)

    def search(self, search_text: str, top_k: int = 2):
        embedding = self.__embedding_model.generate_embeddings(search_text)
        while embedding is None:
            embedding = self.__embedding_model.generate_embeddings(search_text)
        embedding_array = array([embedding], dtype=float32)
        _, indices = self.__index.search(embedding_array, top_k)
        try:
            results = [self.__data[idx] for idx in indices[0]]
        except IndexError:
            results = []
        return results

    def remove_data(self, text: list[SearchResult]):
        for data in text:
            index = self.__data.index(data)
            if index != -1:
                self.__remove_index(index)

    def __remove_index(self, index: int):
        self.__index.remove(index)
        self.__data.pop(index)


class ContextGenerator:
    def __init__(self, embedding_model: EmbeddingModel):
        self.__context_index = ContextIndex(embedding_model)

    def generate_context(self, search_text: str):
        search_results = SearchEngine.search(search_text)
        self.__context_index.add_data(search_results)
        search_results = self.__context_index.search(search_text)
        return search_results
