from engine.step_engine.step_generator import StepRetriever
from lib.llm_models.prompts import ClassifyInputTemplate
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel
from engine.vision_engine.screen_analyzer import ScreenAnalyzer


#TODO: Incorporate ScreenAnalyzer
#TODO: Give new info to Step Retriever
class InputHandler:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__step_retriever = StepRetriever(model, embedding_model)
        self.__screen_analyzer = ScreenAnalyzer(model)
        self.__model = model
        self.__input_history = ""

    def add_input(self, input: str):
        template = ClassifyInputTemplate(self.__input_history, input)
        classification = self.__model.generate(
            template.prompt(), template.generation_config()
        )
        if classification == "Same":
            input_history = self.__input_history + input
            self.__step_retriever.add_additional_info("Old info: {}\n New info: {}".format(self.__input_history, input), "Old info: {}".format(input_history))
            self.__input_history += input_history
        else:
            self.__input_history = input
            self.__step_retriever.new_task(self.__model, input)
