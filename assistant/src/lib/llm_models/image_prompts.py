from lib.llm_models.prompts import PromptTemplate


class ImageCoordinatesTemplate(PromptTemplate):
    def __init__(self, object_name: str):
        super().__init__()
        prompt = """Return the bounding box around the {} in exact this format: [y_min, x_min, y_max, x_max]. If the object is not present return an empty list.
        """.format(object_name)
        self._set_prompt(prompt)


class ImageDetailsTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = (
            """Analyze the following image and return a description of the image."""
        )
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
        How would the resulting screen look like if the task is done? Answer as short and objective as possible. Do not ask questions.
        """.format(task)
        self._set_prompt(prompt)


class DragPositionTemplate(PromptTemplate):
    def __init__(self, description: str):
        super().__init__()
        prompt = """You need to do following task, which involves some dragging: {}.
        return the start and end coordinates of the drag in this format: [start_x, start_y, end_x, end_y].""".format(
            description
        )
        self._set_prompt(prompt)
