from step_generator import StepGenerator
from lib.llm_models.prompts import EvaluateStepTemplate
from lib.llm_models.model import Model

class StepEvaluator():
    def __init__(self, api_key: str, step_generator: StepGenerator):
        self.__step_generator = step_generator
        self.__model = Model(api_key)
        self.__step_list, self.__index = self.__step_generator.get_steps()
        self.__steps_done = []

    def add_finished_step(self, step: dict):
        self.__steps_done.append(step)

    def evaluate_next_step(self, next_step: dict, action_text: str):
        #take future steps into account
        template = EvaluateStepTemplate(action_text, self.__steps_done, next_step)
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result