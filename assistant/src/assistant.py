from dotenv import load_dotenv
from os import getenv
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel
from engine.step_engine.input_handler import InputHandler
from engine.step_engine.step_generator import StepRetriever
from engine.step_engine.step_evaluator import Tasks
from engine.action_engine.actions import (
    locate,
    click_left,
    click_right,
    double_click,
    drag,
    scroll_up,
    scroll_down,
    press_key,
)
from engine.vision_engine.screen_analyzer import ScreenAnalyzer
from atexit import register

DO_NOT_CHECK = [
    Tasks.CANCELTASK,
    Tasks.FINISHEDTASK,
    Tasks.SKIPSTEP,
    Tasks.LOCATE,
    Tasks.QUESTION,
]

# TODO: Add speech support
# TODO: maybe something with Screen Delta?


class Assistant:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__model = model
        self.__input_handler = InputHandler(model)
        self.__screen_analyzer = ScreenAnalyzer(model)
        self.__step_retriever = StepRetriever(
            model, embedding_model, self.__input_handler
        )
        register(self.cleanup)

    def do_task(self, task: str):
        self.__step_retriever.new_task(task)
        counter = 0
        while counter < 3:
            step = self.__step_retriever.retrieve_step()
            task_type = Tasks.from_string(step["step_name"])
            self.__print_task(step)
            if task_type == Tasks.LEFTCLICK:
                click_left()
            elif task_type == Tasks.RIGHTCLICK:
                click_right()
            elif task_type == Tasks.DRAG:
                pass  # TODO: add position
            elif task_type == Tasks.DOUBLECLICK:
                double_click()
            elif task_type == Tasks.SCROLLDOWN:
                scroll_down()  # TODO: add amount
            elif task_type == Tasks.SCROLLUP:
                scroll_up()  # TODO: add amount
            elif task_type == Tasks.PRESSKEY:
                try:
                    keys = step["keys"]
                    press_key(keys)
                except KeyError:
                    text = step["text"]
                    pos = self.__screen_analyzer.analyze_image_coordinates(
                        "Locate the input field to type: " + step["description"]
                    )
                    if pos == (None, None):
                        task_type = Tasks.QUESTION
                    else:
                        locate(pos)
                        press_key(text)
            elif task_type == Tasks.LOCATE:
                pos = self.__screen_analyzer.analyze_image_coordinates(
                    step["description"]
                )
                print(pos)
                if pos == (None, None):
                    task_type = Tasks.QUESTION
                else:
                    locate(pos)
            elif task_type == Tasks.CANCELTASK:
                break
            elif task_type == Tasks.FINISHEDTASK:
                break
            elif task_type == Tasks.SKIPSTEP:
                continue
            elif task_type == Tasks.QUESTION:
                pass  # TODO: interact with user
            if task_type not in DO_NOT_CHECK:
                pass  # TODO: Check if task completed
            counter += 1

    def __print_task(self, task: dict):
        print("[INFO]:  ", task["step_name"], " - ", task["description"])

    def cleanup(self):
        self.__model.delete_files()


if __name__ == "__main__":
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    assistant = Assistant(model, embedding_model)
    assistant.do_task("Open Mozilla Firefox")
