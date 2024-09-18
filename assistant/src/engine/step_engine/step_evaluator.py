from lib.llm_models.prompts import EvaluateStepTemplate
from lib.llm_models.model import Model
from enum import Enum


class Tasks(Enum):
    LEFTCLICK = "LEFTCLICK"
    RIGHTCLICK = "RIGHTCLICK"
    DRAG = "DRAG"
    DOUBLECLICK = "DOUBLECLICK"
    SCROLLDOWN = "SCROLLDOWN"
    SCROLLUP = "SCROLLUP"
    PRESSKEY = "PRESSKEY"
    TYPE = "TYPE"
    LOCATE = "LOCATE"
    CANCELTASK = "CANCELTASK"
    FINISHEDTASK = "FINISHEDTASK"
    SKIPSTEP = "SKIPSTEP"
    QUESTION = "QUESTION"

    @classmethod
    def from_string(cls, string: str):
        return cls(string)


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
        self,
        next_steps: list,
        action_text: str,
        screen_details: str,
        additional_info: str = "",
    ):
        template = EvaluateStepTemplate(
            action_text,
            self.__steps_done,
            next_steps,
            Tasks,
            additional_info,
            screen_details,
        )
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result
