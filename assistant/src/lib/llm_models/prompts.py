from lib.llm_models.model import Model
from enum import Enum
from sys import platform

OS = platform

KEYS = [
    "\t",
    "\n",
    "\r",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "'",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "`",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "accept",
    "add",
    "alt",
    "altleft",
    "altright",
    "apps",
    "backspace",
    "browserback",
    "browserfavorites",
    "browserforward",
    "browserhome",
    "browserrefresh",
    "browsersearch",
    "browserstop",
    "capslock",
    "clear",
    "convert",
    "ctrl",
    "ctrlleft",
    "ctrlright",
    "decimal",
    "del",
    "delete",
    "divide",
    "down",
    "end",
    "enter",
    "esc",
    "escape",
    "execute",
    "f1",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f2",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "final",
    "fn",
    "hanguel",
    "hangul",
    "hanja",
    "help",
    "home",
    "insert",
    "junja",
    "kana",
    "kanji",
    "launchapp1",
    "launchapp2",
    "launchmail",
    "launchmediaselect",
    "left",
    "modechange",
    "multiply",
    "nexttrack",
    "nonconvert",
    "num0",
    "num1",
    "num2",
    "num3",
    "num4",
    "num5",
    "num6",
    "num7",
    "num8",
    "num9",
    "numlock",
    "pagedown",
    "pageup",
    "pause",
    "pgdn",
    "pgup",
    "playpause",
    "prevtrack",
    "print",
    "printscreen",
    "prntscrn",
    "prtsc",
    "prtscr",
    "return",
    "right",
    "scrolllock",
    "select",
    "separator",
    "shift",
    "shiftleft",
    "shiftright",
    "sleep",
    "space",
    "stop",
    "subtract",
    "tab",
    "up",
    "volumedown",
    "volumemute",
    "volumeup",
    "win",
    "winleft",
    "winright",
    "yen",
    "command",
    "option",
    "optionleft",
    "optionright",
]


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


# TODO: Delete old and incorporate new tasks
# TODO: Evaluate all future tasks based on the previous tasks

class GenerateTasksTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum, context: str = ""):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant helping a user to perform tasks. 
        You got the following computer-related task from the user: {}. The OS is {}.
        Here is some context to help you from a quick internet search: {}. Use it only, if it helps you to perform the task.
        Perform the task in the most logial and easy way. Do not make it too complicated.
        Break down the task into smaller actions based on your knowledge. 
        Following tasks are possible: Task={}. Choose only from the list!
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}). 
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose PRESSKEY and want to write a text, add the text to the 'text' field.
        Do not fill the 'text' and 'keys' field at the same time.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str}}
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
        screen_details: str,
    ):
        super().__init__()
        if additional_info != "":
            info = "You got this additional info from the user: {}, include it in your evaluation.".format(
                additional_info
            )
        else:
            info = ""
        prompt = """Imagine you are a smart computer assistant helping a user to perform tasks. 
        You got the following computer-related task from the user: {}. {} The OS is {}.
        This is what you see on your screen: {}. Do not make it more complicated than it is, just as simple as possible.
        Here is a list of steps you already performed: {}. If the task from the user is done, return 'FINISHEDTASK'.
        Evaluate the next steps: {} you have to perform, based on your knowledge and the previous steps. Return the old or changed new steps.
        You have a list of possible tasks you can choose from: Task={}. Choose only from the list!
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str}}
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}).
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose PRESSKEY and want to write a text, add the text to the 'text' field.
        Do not fill the 'text' and 'keys' field at the same time.
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        The last step should be 'FINISHEDTASK'.
        If the there is any additional information to cancel the task, then include 'CANCELTASK' as only step.""".format(
            action_text,
            info,
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


class ImageCoordinatesTemplate(PromptTemplate):
    def __init__(self, object_name: str):
        super().__init__()
        prompt = """Return the bounding box around the {} in exact this format: [y_min, x_min, y_max, x_max]. If the object is not present return an empty list.
        """.format(object_name)
        self._set_prompt(prompt)


class ImageDetailsTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = """Analyze the following image and return a description of the image."""
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


class TaskDoneScreenTemplate(PromptTemplate):
    def __init__(self, task: str):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant helping a user to perform tasks. You get following task from the user: {}. 
        How would the resulting screen look like if the task is done? Do not make it more complicated or philosophical than it is.
        Answer as short as possible.
        """.format(task)
        self._set_prompt(prompt)


class TaskDoneTemplate(PromptTemplate):
    def __init__(self, task: str, screen_details: str, screen_details_predicted: str):
        super().__init__()
        prompt = """Imagine you are a smart computer assistant helping a user to perform tasks. You get following task from the user: {}. 
        This is what you see: {}. This is what you would probably see, if the task was completed: {}.
        If you cannot see the task completion or it is possible/ likely, return done.
        Return not done only if you are sure the task was not completed.
        """.format(task, screen_details, screen_details_predicted)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(
            response_mime_type="text/x.enum", response_schema=TaskDone
        )
