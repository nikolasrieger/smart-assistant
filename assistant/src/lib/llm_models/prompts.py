from lib.llm_models.model import Model
from enum import Enum
from sys import platform

OS = platform


class TaskChoices(Enum):
    DIFFERENT = "Different"
    SAME = "Same"


class TaskDone(Enum):
    Done = "Done"
    NOTDONE = "Not-Done"


class PromptTemplate:
    def __init__(self):
        self.__prompt = ""

    def _set_prompt(self, prompt: str):
        self.__prompt = prompt

    def prompt(self):
        return self.__prompt

    def generation_config(self):
        return Model.set_generation_config()


class GenerateStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str, context: str = ""):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following computer-related task from your boss: {}. Your OS is {}.
        Here is some context to help you from a quick internet search: {}.
        Break down the task into smaller actions based on your knowledge. Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform or you can't perform it on a comptuer, 
        return an empty JSON.""".format(action_text, OS, context)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class ExtractTaskTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task: {}. Your OS is {}.
        Break down the task into smaller tasks based on your knowledge. 
        You have a list of possible tasks you can choose from: Task={}. Return one or more tasks from the list, you have to perform in the correct order.
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc. 
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        """.format(action_text, OS, list(tasks))
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class EvaluateStepTemplate(PromptTemplate):
    def __init__(
        self,
        action_text: str,
        finished_steps: list,
        next_step: dict,
        tasks: Enum,
        additional_info: str,
        screen_details: str,
    ):
        super().__init__()
        if additional_info != "":
            info = "You got this additional info from your boss: {}, include it in your evaluation.".format(
                additional_info
            )
        else:
            info = ""
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. {} Your OS is {}. 
        This is what you see on your screen: {}.
        Here is a list of steps you already performed: {}. 
        Evaluate the next step: {} you have to perform, if it is not done and makes sense, just return it, else return a fitting next step.
        You have a list of possible tasks you can choose from: Task={}. 
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        If the there is any additional information to cancel the task, then include 'Cancel-task' as only step.""".format(
            action_text,
            info,
            OS,
            screen_details,
            finished_steps,
            next_step,
            list(tasks),
        )
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class ClassifyInputTemplate(PromptTemplate):
    def __init__(self, input_history: str, input: str):
        super().__init__()
        prompt = """Imagine you are a professional classification specialist. You have a history of inputs from a user: {}.
        Classify the new input as different task or same task: '{}'. """.format(
            input_history, input
        )
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(
            response_mime_type="text/x.enum", response_schema=TaskChoices
        )


class ImageCoordinatesTemplate(PromptTemplate):
    def __init__(self, object_name: str):
        super().__init__()
        prompt = """Return the bounding box around the {} in exact this format: [y_min, x_min, y_max, x_max]. If the object is not present return an empty list.
        """.format(object_name)
        self._set_prompt(prompt)


class ImageDetailsTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = """Analyze the following image and return a destription of the image with as many details as possible."""
        self._set_prompt(prompt)


class ImageTODOSTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = """Analyze the following image and return a list of tasks you need to do. 
        Possible Tasks could be: 
        - If there is a form displayed, fill out the form.
        - If there is some message, answer it or react accordingly.
        - If there is some popup, close it or react accordingly.
        If there are no tasks to do, return an empty list."""
        self._set_prompt(prompt)


class ImageTaskDoneTemplate(PromptTemplate):
    def __init__(self, task: str):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. Analyze with the screenshot provided if the
        task is done or not.
        """.format(task)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(
            response_mime_type="text/x.enum", response_schema=TaskDone
        )
