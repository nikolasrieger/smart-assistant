from lib.llm_models.model import Model
from lib.llm_models.prompts import GenerateStepsTemplate, ReflectStepsTemplate, ExtractTaskTemplate
from enum import Enum
from json import loads
from dotenv import load_dotenv
from os import getenv

class Tasks(Enum):
    LEFTCLICK = "Left-Click"
    RIGHTCLICK = "Right-Click"
    CLICKANDHOLD = "Click-and-Hold"
    DOUBLECLICK = "Double-Click"
    SCROLL = "Scroll"
    PRESSKEY = "Press-Key"
    LOCATE = "Locate"


class StepGenerator():
    def __init__(self, api_key: str, action_text: str):
        self.__model = Model(api_key)
        self.__index = 0
        self.__generate_step_from_action(action_text)

    def __generate_step_from_action(self, action_text: str):
        template = GenerateStepsTemplate(action_text)
        draft_steps = self.__model.generate(template.prompt(), template.generation_config())
        reflected_steps = self.__reflect_on_steps(action_text, draft_steps)
        self.__index = 0
        return reflected_steps
    
    def __reflect_on_steps(self, action_text: str, steps: list):
        template = ReflectStepsTemplate(action_text, steps)
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result
    
    def next_step(self):
        if len(self.__step_list) <= self.__index: return None
        step = self.__step_list[self.__index]
        description = step["step_name"]
        task_list = self.__get_tasks(description)
        self.__index += 1
        return task_list

    def __get_tasks(self, step_description: str):
        template = ExtractTaskTemplate(step_description, Tasks)
        tasks = self.__model.generate(template.prompt(), template.generation_config())
        return tasks


if __name__ == "__main__":
    load_dotenv()
    model = StepGenerator(getenv("GEMINI_API_KEY"), "Open the Google Chrome Browser")
    task = model.next_step()
    while task is not None:
        print(task)
        task =model.next_step()