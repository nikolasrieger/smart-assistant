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

# TODO: Add speech support
# TODO: maybe something with Screen Delta?


class Assistant:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__model = model
        self.__embedding_model = embedding_model
        self.__input_handler = InputHandler(model)
        self.__step_retriever = StepRetriever(
            model, embedding_model, self.__input_handler
        )

    def do_task(self, task: str):
        self.__step_retriever.new_task(task)
        while True:
            step = self.__step_retriever.retrieve_step()
            task_type = Tasks.from_string(step["step_name"])
            if task_type == Tasks.LEFTCLICK:
                click_left()
            elif task_type == Tasks.RIGHTCLICK:
                click_right()
            elif task_type == Tasks.DRAG:
                pass # TODO: add position
            elif task_type == Tasks.DOUBLECLICK:
                double_click()
            elif task_type == Tasks.SCROLLDOWN:
                scroll_down() # TODO: add amount
            elif task_type == Tasks.SCROLLUP:
                scroll_up() # TODO: add amount
            elif task_type == Tasks.PRESSKEY:
                pass # TODO: extract key
            elif task_type == Tasks.LOCATE:
                pass # TODO: extract position
            elif task_type == Tasks.CANCELTASK:
                break
            elif task_type == Tasks.FINISHEDTASK:
                break
            elif task_type == Tasks.SKIPSTEP:
                continue
            elif task_type == Tasks.QUESTION:
                pass # TODO: interact with user
            break


if __name__ == "__main__":
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    assistant = Assistant(model, embedding_model)
    assistant.do_task("Open Mozilla Firefox")
