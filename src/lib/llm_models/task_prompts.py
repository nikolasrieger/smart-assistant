from lib.llm_models.model import Model
from enum import Enum
from lib.llm_models.prompts import TaskChoices, TaskDone, PromptTemplate, OS, KEYS

action_description = """
- You can use any program on the computer, but specify the program you’re interacting with.
- If using `PRESSKEY`, include the keys pressed in the 'keys' field. Keys: {KEYS}. (Multiple keys are held until the last key is pressed.)
- If using `TYPE`, include the text in the 'text' field.
- For `SCROLLUP` or `SCROLLDOWN`, provide the scroll amount (number of clicks) in the 'amount' field.
- If using `TELL` or `QUESTION`, include any spoken feedback or responses in the 'text' field. Answer fully without repeating.
- For `TERMINAL`, include any command in the 'text' field.
"""


class GenerateTasksTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum, context: str = ""):
        super().__init__()
        prompt = f"""
        You are an intelligent assistant with both visual and textual capabilities, helping a user complete computer-related tasks. 
        Task: {action_text}. OS: {OS}.
        Context (if applicable): {context}.
        
        Break down the task into simple, logical steps. Choose from these tasks: {list(tasks)}. 

        {action_description}
        
        Return steps as a list of JSON objects with this structure:
        {{
            "step_name": Task, 
            "description": str, 
            "keys": str, 
            "text": str, 
            "amount": int
        }}. 
        
        If unsure of how to proceed or the task cannot be done on a computer, return an empty list.
        """
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class EvaluateStepTemplate(PromptTemplate):
    def __init__(self, action_text: str, finished_steps: list, next_step: dict, tasks: Enum, additional_info: str, console_output: str, screen_details: str):
        super().__init__()
        extra_info = f"You received additional info from the user: {additional_info}. " if additional_info else ""
        if console_output:
            extra_info += f"Console output: {console_output}. "

        prompt = f"""
        You are assisting a user with a task: {action_text}. OS: {OS}. 
        Screen details: {screen_details}. {extra_info}
        
        Completed steps: {finished_steps}. 

        Evaluate the next step: {next_step}. Adjust it if necessary to fit the task’s progression. Only use available tasks: {list(tasks)}. Avoid repeating completed steps.
        Do the most logical step, do not overcomplicate it, and ensure it is correct.

        {action_description}

        Use the structure:
        List{{
            "step_name": Task, 
            "description": str, 
            "keys": str, 
            "text": str, 
            "amount": int
        }}.
        
        Return 'FINISHEDTASK' if the task is completed or 'CANCELTASK' if it cannot be done. You may ask the user for clarification with 'QUESTION' and provide the question in 'text'. 
        If no steps are left, return an empty list.
        """
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class ClassifyInputTemplate(PromptTemplate):
    def __init__(self, input_history: str, input: str):
        super().__init__()
        prompt = f"""
        You are a classification expert. Review the user’s input history: {input_history}. 
        Classify the new input: '{input}' as either a new task or the same task.
        """
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="text/x.enum", response_schema=TaskChoices)


class TaskDoneTemplate(PromptTemplate):
    def __init__(self, task: str, screen_details: str, screen_details_predicted: str):
        super().__init__()
        prompt = f"""
        You are a smart assistant determining if a task is complete. 
        Task: {task}. 
        Current screen: {screen_details}. 
        Expected screen if task were done: {screen_details_predicted}.
        
        If you are sure the task is done, return 'done'. Return 'not done' only if you are 100% certain it’s incomplete.
        """
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="text/x.enum", response_schema=TaskDone)


class ImproveTaskTemplate(PromptTemplate):
    def __init__(self, action_text: str, screen_details: str, step: dict, tasks: Enum):
        super().__init__()
        prompt = f"""
        You are an intelligent assistant optimizing a task step. 
        Task: {action_text}. Screen: {screen_details}. 

        The step needs improvement: {step}. Simplify it to make it work correctly.

        Use tasks from the list: {list(tasks)} and provide clear descriptions of what to do.

        {action_description}

        Return the improved step in the same format:
        {{
            "step_name": Task, 
            "description": str, 
            "keys": str, 
            "text": str, 
            "amount": int
        }}.
        """
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")
