from dotenv import load_dotenv
from os import getenv
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel
from engine.step_engine.input_handler import InputHandler
from engine.step_engine.step_generator import StepRetriever

# TODO: Add speech support
# TODO: Actually do the tasks (Task Done, TODOS) -> press key/ writing
# TODO: maybe something with Screen Delta?

if __name__ == "__main__":
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    input_handler = InputHandler(model)
    step_retriever = StepRetriever(model, embedding_model, input_handler)
    step_retriever.new_task("Open Mozilla Firefox")
    print(step_retriever.retrieve_step())
