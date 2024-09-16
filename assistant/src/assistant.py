from dotenv import load_dotenv
from os import getenv
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel

#TODO: Add speech support
#TODO: Actually do the tasks (Coordinates, Task Done)
#TODO: maybe something with Screen Delta?

if __name__ == "__main__":
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
