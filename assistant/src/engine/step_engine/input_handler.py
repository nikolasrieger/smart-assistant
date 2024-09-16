from engine.step_engine.step_generator import StepRetriever
from lib.llm_models.prompts import ClassifyInputTemplate
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel


class InputHandler:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__step_retriever = StepRetriever(model, embedding_model)
        self.__model = model
        self.__input_history = ""

    def add_input(self, input: str):
        template = ClassifyInputTemplate(self.__input_history, input)
        classification = self.__model.generate(
            template.prompt(), template.generation_config()
        )
        if classification == "Same":
            self.__input_history += input
        else:
            self.__input_history = input
            self.__step_retriever.new_task(self.__model, input)

    def get_input(self):
        return self.__input_history
