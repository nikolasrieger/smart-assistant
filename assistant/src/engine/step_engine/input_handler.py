from engine.step_engine.step_generator import StepRetriever
from lib.llm_models.prompts import ClassifyInputTemplate
from lib.llm_models.model import Model


class InputHandler:
    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__step_retriever = StepRetriever()
        self.__model = Model(api_key)
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
            self.__step_retriever.new_task(self.__api_key, input)

    def get_input(self):
        return self.__input_history
