from lib.llm_models.task_prompts import ClassifyInputTemplate
from lib.llm_models.model import Model
from engine.vision_engine.screen_analyzer import ScreenAnalyzer


class InputHandler:
    def __init__(self, model: Model):
        self.__screen_analyzer = ScreenAnalyzer(model)
        self.__model = model
        self.__input_history = ""
        self.__input = ""
        self.__cancel_task = False

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
            self.__cancel_task = True

    def cancel_task(self):
        cancel_task = self.__cancel_task
        self.__cancel_task = False
        return cancel_task

    def get_input(self):
        input = self.__input
        self.__input = ""
        if input == "":
            return "Info already known about the task: {}".format(input)
        else:
            return "Info already known about the task: {}\nInfo newly gained: {}".format(self.__input_history, input)
        
    def clean_input(self):
        self.__input = ""

    def get_screen_details(self):
        return self.__screen_analyzer.analyze_image_details()
