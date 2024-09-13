from lib.llm_models.prompts import EvaluateStepTemplate
from lib.llm_models.model import Model
from enum import Enum

class Tasks(Enum):
    LEFTCLICK = "Left-Click"
    RIGHTCLICK = "Right-Click"
    CLICKANDHOLD = "Click-and-Hold"
    DOUBLECLICK = "Double-Click"
    SCROLL = "Scroll"
    PRESSKEY = "Press-Key"
    LOCATE = "Locate"
    CANCEL_TASK = "Cancel-Task"
    FINISHED_TASK = "Finished-Task"
    SKIP_STEP = "Skip-Step"


class StepEvaluator():
    def __init__(self, api_key: str):
        self.__model = Model(api_key)
        self.__steps_done = []

    def add_finished_step(self, step: dict):
        self.__steps_done.append(step)

    def evaluate_next_step(self, next_step: dict, action_text: str, additional_info: str = ""):
        #take future steps into account
        template = EvaluateStepTemplate(action_text, self.__steps_done, next_step, Tasks, additional_info)
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result