from lib.llm_models.prompts import PromptTemplate


class ImageCoordinatesTemplate(PromptTemplate):
    def __init__(self, object_name: str):
        super().__init__()
        prompt = f"""
        Identify the bounding box for the {object_name} in the image. 
        Return it in the format: [y_min, x_min, y_max, x_max]. 
        If the object is not present, return an empty list.
        """
        self._set_prompt(prompt)


class ImageDetailsTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = """
        Analyze the image and provide a description.
        """
        self._set_prompt(prompt)


class ImageTODOSTemplate(PromptTemplate):
    def __init__(self):
        super().__init__()
        prompt = """
        Analyze the image and list any tasks to perform. Possible tasks include:
        - Fill out forms if present.
        - Respond to any messages.
        - Close or interact with popups if visible.

        If no tasks are needed, return an empty list.
        """
        self._set_prompt(prompt)


class TaskDoneScreenTemplate(PromptTemplate):
    def __init__(self, task: str):
        super().__init__()
        prompt = f"""
        You are assisting a user with the task: {task}. 
        Describe how the screen would look when the task is completed. 
        Keep the answer brief and objective.
        """
        self._set_prompt(prompt)


class DragPositionTemplate(PromptTemplate):
    def __init__(self, description: str):
        super().__init__()
        prompt = f"""
        You need to perform the following drag task: {description}. 
        Return the start and end coordinates in this format: [start_x, start_y, end_x, end_y].
        """
        self._set_prompt(prompt)