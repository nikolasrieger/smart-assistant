from lib.llm_models.model import Model
from enum import Enum
from lib.llm_models.prompts import TaskChoices, TaskDone, PromptTemplate, OS, KEYS


class GenerateTasksTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum, context: str = ""):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant with textual and visual understanding helping a user to perform tasks. 
        You can see the screen, do things on the computer and interact with the user. You got the following computer-related task from the user: {}. The OS is {}.
        Here is some context to help you from a quick internet search: {}. Use it only, if it helps you to perform the task.
        Perform the task in the most logial and easy way. Do not make it too complicated.
        Break down the task into smaller actions based on your knowledge. 
        Following tasks are possible: Task={}. Choose only from the list!
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}). 
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose TYPE and want to write a text, add the text to the 'text' field.
        If you chose SCROLLUP or SCROLLDOWN, add the amount of scrolling in the 'amount' field (= number of clicks on the scrolling bar).
        If you chose TELL, add all the text you want to tell the user in the 'text' field. Answer the complete question, do not leave anything out. 
        Do not tell the same thing twice (check the completed tasks) and do not leave the answer out.
        You have the permission to use the terminal. If you want to run a command on the computer, choose TERMINAL, you have to add the command you want to run in the 'text' field.
        Use the context from the internet search for real time data. If you don't know the answer, say so.
        Do not fill the 'text' and 'keys' field at the same time.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str, "amount:" int}}
        Return a 'list[Step]'. If you don't know which steps to perform or you can't perform it on a comptuer, 
        return an empty JSON.""".format(action_text, OS, context, list(tasks), KEYS)
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
        console_output: str,
        screen_details: str,
    ):
        super().__init__()
        if additional_info != "":
            additional_info = "You got this additional info from the user: {}, include it in your evaluation.".format(
                additional_info
            )
        if console_output != "":
            additional_info += "The console output of the last executed command is: {}, include it in your evaluation.".format(
                console_output
            )
        prompt = """Imagine you are a smart computer assistant with textual and visual understanding helping a user to perform tasks. 
        You can see the screen, do things on the computer and interact with the user. You got the following computer-related task from the user: {}. {} The OS is {}.
        This is what you see on your screen in this moment, try to use it for real-time data: {}. 
        Do not make it more complicated than it is, just as simple as possible.
        Here is a list of steps you already performed: {}. If the task from the user is done, return 'FINISHEDTASK'.
        Evaluate the next steps: {} you have to perform, based on your knowledge and the previous steps. Return the old or changed new steps.
        You have a list of possible tasks you can choose from: Task={}. Choose only from the list! Do not add steps which already are done.
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str, "amount:" int}}
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}).
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose TYPE and want to write a text, add the text to the 'text' field.
        If you chose SCROLLUP or SCROLLDOWN, add the amount of scrolling in the 'amount' field (= number of clicks on the scrolling bar).
        If you chose TELL, add all the text you want to tell the user in the 'text' field. Answer the complete question, do not leave anything out. 
        Do not tell the same thing twice (check the completed tasks) and do not leave the answer out.
        You have the permission to use the terminal. If you want to run a command on the computer, choose TERMINAL, you have to add the command you want to run in the 'text' field.
        If you completed the task, return 'FINISHEDTASK'. Do not do any steps more than once (except they failed). Do not retrun steps which are already done.
        If you are sure, you cannot complete the task, return 'CANCELTASK' or 'QUESTION' if you need any help from the user. Add the Question in the 'text' field.
        Do not fill the 'text' and 'keys' field at the same time.
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        The last step should be 'FINISHEDTASK'.
        If the there is any additional information to cancel the task, then include 'CANCELTASK' as only step.""".format(
            action_text,
            additional_info,
            OS,
            screen_details,
            finished_steps,
            next_step,
            list(tasks),
            KEYS,
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


class TaskDoneTemplate(PromptTemplate):
    def __init__(self, task: str, screen_details: str, screen_details_predicted: str):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant with textual and visual understanding helping a user to perform tasks. You get following task from the user: {}. 
        This is what you see: {}. This is what you would probably see, if the task was completed: {}.
        If you cannot see the task completion or it is possible that the task was completed, return done.
        Return not done only if you are a 100 per cent sure the task was not completed.
        """.format(task, screen_details, screen_details_predicted)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(
            response_mime_type="text/x.enum", response_schema=TaskDone
        )


class ImproveTaskTemplate(PromptTemplate):
    def __init__(self, action_text: str, screen_details: str, step: dict, tasks: Enum):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant with textual and visual understanding helping a user to perform tasks. 
        You can see the screen, do things on the computer and interact with the user. This is the task you got from the user: {}.
        You assessed to do this step: {}. Unfortunately, this task is either in the wrong format or did not work as expected
        This is what you see on your screen: {}. Do not make it more complicated than it is, just as simple as possible.
        Improve the task in a way that it can be executed successfully. Return the improved task in the same format as the original task.
        You have a list of possible tasks you can choose from: Task={}. Choose only from the list! Do not add steps which already are done.
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str, amount: int}}
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}).
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose TYPE and want to write a text, add the text to the 'text' field.
        If you chose SCROLLUP or SCROLLDOWN, add the amount of scrolling in the 'amount' field (= number of clicks on the scrolling bar).
        If you chose TELL, add all the text you want to tell the user in the 'text' field. Answer the complete question, do not leave anything out. 
        Do not tell the same thing twice (check the completed steps) and do not leave the answer out.
        You have the permission to use the terminal. If you want to run a command on the computer, choose TERMINAL, you have to add the command you want to run in the 'text' field.
        If you are sure, you cannot complete the task, return 'CANCELTASK' or 'QUESTION' if you need any help from the user. Add the Question in the 'text' field.
        Do not fill the 'text' and 'keys' field at the same time.
        Return a 'Step'. If you don't know which steps to perform return an empty JSON.""".format(
            action_text,
            step,
            screen_details,
            list(tasks),
            KEYS,
        )
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")
