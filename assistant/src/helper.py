from colorama import Fore
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
    tell,
    init_terminal,
    terminal,
)
from engine.vision_engine.screen_analyzer import ScreenAnalyzer
from lib.llm_models.task_prompts import ImproveTaskTemplate
from atexit import register
from json import loads
from time import sleep, time

DO_NOT_CHECK = [
    Tasks.CANCELTASK,
    Tasks.FINISHEDTASK,
    Tasks.SKIPSTEP,
    Tasks.LOCATE,
    Tasks.QUESTION,
    Tasks.TELL,
    Tasks.TERMINAL,
]

TIME_DELTA = 1
INFO_MESSAGES = True

# TODO: Add speech output
# TODO: find when done
# TODO: maybe something with Screen Delta?
# TODO: intelligent redo of internet search


class Assistant:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__model = model
        self.input_handler = InputHandler(model)
        self.__screen_analyzer = ScreenAnalyzer(model)
        self.__step_retriever = StepRetriever(
            model, embedding_model, self.input_handler
        )
        register(self.cleanup)
        init_terminal()

    def do_task(self, task: str):
        self.__step_retriever.new_task(task)
        counter = 0
        status = "Done"
        output, error = "", ""
        task = self.__step_retriever.get_task()
        while True:
            actual_time = time()
            if status == "Done":
                step = self.__step_retriever.retrieve_step(output + error)
            try:
                task_type = Tasks.from_string(step["step_name"])
            except ValueError:
                status = "Retry"
            if INFO_MESSAGES:
                self.__print_task(step, task_type)
            if task_type == Tasks.LEFTCLICK:
                click_left()
            elif task_type == Tasks.RIGHTCLICK:
                click_right()
            elif task_type == Tasks.DRAG:
                pos = self.__screen_analyzer.analyze_drag_coordinates(
                    step["description"]
                )
                if pos == [(None, None), (None, None)]:
                    task_type = Tasks.QUESTION
                    status = "Not-Done"
                else:
                    status = "Done"
                    locate(pos[0])
                    drag(pos[1])
            elif task_type == Tasks.DOUBLECLICK:
                double_click()
            elif task_type == Tasks.SCROLLDOWN:
                for _ in range(step["amount"]):
                    scroll_down()
            elif task_type == Tasks.SCROLLUP:
                for _ in range(step["amount"]):
                    scroll_up()
            elif task_type == Tasks.PRESSKEY:
                keys = step["keys"]
                press_key(keys)
            elif task_type == Tasks.TYPE:
                text = step["text"]
                pos = self.__screen_analyzer.analyze_image_coordinates(
                    "Locate the input field to type: " + step["description"]
                )
                if pos == (None, None):
                    task_type = Tasks.QUESTION
                    status = "Not-Done"
                else:
                    status = "Done"
                    locate(pos)
                    press_key(text)
            elif task_type == Tasks.LOCATE:
                pos = self.__screen_analyzer.analyze_image_coordinates(
                    step["description"]
                )
                if pos == (None, None):
                    task_type = Tasks.QUESTION
                    status = "Not-Done"
                else:
                    status = "Done"
                    locate(pos)
            elif task_type == Tasks.TERMINAL:
                print(
                    "Do you want to run this command? [y/n]: {} ".format(step["text"])
                )
                sleep(2)
                ans = "y" # to speech input
                if ans == "y":
                    output, error = terminal(step["text"] + "\n")
                else:
                    output, error = "Aborted by user", "Aborted by user"
                    status = "Not-Done"
                tell(Fore.BLUE + "[OmniAssist]: " + Fore.RESET + output)
            elif task_type == Tasks.CANCELTASK:
                break
            elif task_type == Tasks.FINISHEDTASK:
                break
            elif task_type == Tasks.SKIPSTEP:
                continue
            elif task_type == Tasks.QUESTION:
                tell(Fore.BLUE + "[OmniAssist]: " + Fore.RESET + step["text"])
            elif task_type == Tasks.TELL:
                tell(Fore.BLUE + "[OmniAssist]: " + Fore.RESET + step["text"])
            time_delta = time() - actual_time
            if time_delta < TIME_DELTA:
                sleep(TIME_DELTA - time_delta)
            if task_type not in DO_NOT_CHECK or status == "Retry":
                if status != "Retry":
                    status = self.__screen_analyzer.analzye_image_task(
                        step["description"]
                    )
                else:
                    status = "Not-Done"
            if status == "Not-Done":
                screen = self.__screen_analyzer.analyze_image_details()
                prompt = ImproveTaskTemplate(task, screen, step, Tasks)
                result = self.__model.generate(
                    prompt.prompt(), prompt.generation_config()
                )
                step = loads(result)
            if INFO_MESSAGES and task_type not in [
                Tasks.TELL,
                Tasks.CANCELTASK,
                Tasks.FINISHEDTASK,
                Tasks.SKIPSTEP,
                Tasks.QUESTION,
                Tasks.TERMINAL,
            ]:
                self.__print_status(status)
            counter += 1

    def __print_task(self, task: dict, task_type: Tasks):
        if task_type in DO_NOT_CHECK:
            print(
                Fore.YELLOW + "[INFO]:  " + Fore.RESET + task["step_name"],
                " - ",
                task["description"],
            )
        else:
            print(
                Fore.YELLOW + "[INFO]:  " + Fore.RESET + task["step_name"],
                " - ",
                task["description"],
                end=" ",
            )

    def __print_status(self, status: str):
        if status == "Done":
            print(Fore.GREEN + "[{}]".format(status) + Fore.RESET)
        else:
            print(Fore.RED + "[{}]".format(status) + Fore.RESET)

    def cleanup(self):
        self.__model.delete_files()

