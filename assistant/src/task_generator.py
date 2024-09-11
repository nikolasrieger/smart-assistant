from step_generator import StepGenerator
from lib.llm_models.prompts import ExtractTaskTemplate
from lib.llm_models.model import Model
from dotenv import load_dotenv
from os import getenv
from enum import Enum
from json import loads

class Tasks(Enum):
    LEFTCLICK = "Left-Click"
    RIGHTCLICK = "Right-Click"
    CLICKANDHOLD = "Click-and-Hold"
    DOUBLECLICK = "Double-Click"
    SCROLL = "Scroll"
    PRESSKEY = "Press-Key"
    LOCATE = "Locate"


class TaskGenerator():
    def __init__(self, api_key: str, action_text: str):
        self.__step_generator = StepGenerator(api_key)
        self.__step_list = loads(self.__step_generator.generate_step_from_action(action_text))
        self.__model = Model(api_key)
        self.__index = 0

    def next_task(self):
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
    model = TaskGenerator(getenv("GEMINI_API_KEY"), "Open the Google Chrome Browser")
    task = model.next_task()
    while task != None:
        print(task)
        task =model.next_task()