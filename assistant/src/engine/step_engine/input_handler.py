from lib.llm_models.prompts import ClassifyInputTemplate
from lib.llm_models.model import Model
from engine.vision_engine.screen_analyzer import ScreenAnalyzer


#TODO: Incorporate ScreenAnalyzer (Details + TODOS)
class InputHandler:
    def __init__(self, model: Model):
        self.__screen_analyzer = ScreenAnalyzer(model)
        self.__model = model
        self.__input_history = ""
        self.__input = ""

    def add_input(self, input: str):
        template = ClassifyInputTemplate(self.__input_history, input)
        classification = self.__model.generate(
            template.prompt(), template.generation_config()
        )
        if classification == "Same":
            input_history = self.__input_history + input
            self.__input_history += input_history
        else:
            self.__input_history = input
    
    def get_input(self):
        input = self.__input
        self.__input = ""
        if input == "":
            return "Oldinfo: {}".format(input)
        else:
            return "Old info: {}\nNew info: {}".format(self.__input_history, input)
