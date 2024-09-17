from lib.llm_models.prompts import EvaluateStepTemplate
from lib.llm_models.model import Model
from enum import Enum


class Tasks(Enum):
    LEFTCLICK = "Left-Click"
    RIGHTCLICK = "Right-Click"
    DRAG = "Drag"
    DOUBLECLICK = "Double-Click"
    SCROLLDOWN = "Scroll-Down"
    SCROLLUP = "Scroll-Up"
    PRESSKEY = "Press-Key"
    LOCATE = "Locate"
    CANCEL_TASK = "Cancel-Task"
    FINISHED_TASK = "Finished-Task"
    SKIP_STEP = "Skip-Step"
    QUESTION = "Question"


class Task:
    def __init__(self, task: Tasks, task_info: dict):
        self.task = task
        self.task_info = task_info


class StepEvaluator:
    def __init__(self, model: Model):
        self.__model = model
        self.__steps_done = []

    def add_finished_step(self, step: dict):
        self.__steps_done.append(step)

    def evaluate_next_step(
        self, next_step: dict, action_text: str, screen_details: str, additional_info: str = ""
    ):
        template = EvaluateStepTemplate(
            action_text, self.__steps_done, next_step, Tasks, additional_info, screen_details
        )
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result
