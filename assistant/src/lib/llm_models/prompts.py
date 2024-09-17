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


class GenerateStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str, context: str = ""):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following computer-related task from your boss: {}. Your OS is {}.
        Here is some context to help you from a quick internet search: {}. If the internet search makes everything more complicated, do not use that context.
        Perform only the most fitting and logical next step. Do not make it more complicated than it is.
        Break down the task into smaller actions based on your knowledge. Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform or you can't perform it on a comptuer, 
        return an empty JSON.""".format(action_text, OS, context)
        print(context)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type="application/json")


class ExtractTaskTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task: {}. Your OS is {}.
        Break down the task into smaller tasks based on your knowledge. Perform only the most fitting and logical next step. Do not make it more complicated than it is.
        You have a list of possible tasks you can choose from: Task={}. Return one or more tasks from the list, you have to perform in the correct order.
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc. 
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str}}
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}). 
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose PRESSKEY and want to write a text, add the text to the 'text' field.
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        """.format(action_text, OS, list(tasks), KEYS)
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
        This is what you see on your screen: {}. Perform only the most fitting and logical next step. Do not make it more complicated than it is.
        Here is a list of steps you already performed: {}. 
        Evaluate the next step: {} you have to perform, if it is not done and makes sense, just return it, else return a fitting next step.
        You have a list of possible tasks you can choose from: Task={}. 
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str, "keys": str, "text": str}}
        If you chose PRESSKEY as step_name, then you have to add the a list of keys you pressed in the 'keys' field. (possible keys are: {}).
        If the list contains more than one key, be aware, that the all keys will be held down until the last key is pressed.
        If you chose PRESSKEY and want to write a text, add the text to the 'text' field.
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        If the there is any additional information to cancel the task, then include 'Cancel-task' as only step.""".format(
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
