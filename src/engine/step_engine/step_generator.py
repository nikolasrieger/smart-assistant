from lib.llm_models.model import Model
from lib.llm_models.task_prompts import GenerateTasksTemplate
from lib.web_search.search_engine import SearchEngine
from engine.step_engine.context_generator import ContextGenerator
from lib.llm_models.embeddings import EmbeddingModel
from engine.step_engine.step_evaluator import StepEvaluator
from engine.step_engine.input_handler import InputHandler
from json import loads


class StepGenerator:
    def __init__(self, model: Model, embedding_model: EmbeddingModel, action_text: str):
        self.__model = model
        self.__context = ContextGenerator(embedding_model)
        self.__evaluator = StepEvaluator(model)
        self.__index = 0
        self.__task = action_text
        context = self.__context.generate_context(action_text)
        self.__step_list = loads(self.__generate_step_from_action(action_text, context))

    def __generate_step_from_action(self, action_text: str, context: list = []):
        context_text = ""
        for webpage in context:
            context_text += SearchEngine.get_text_from_url(webpage.url) + "\n"
        template = GenerateTasksTemplate(action_text, context_text)
        steps = self.__model.generate(template.prompt(), template.generation_config())
        if len(loads(steps)) == 0 or steps is None:
            return "[{'step_name': 'SKIPSTEP'}]"
        self.__index = 0
        return steps

    def get_steps(self):
        return self.__step_list, self.__index

    def next_step(self, screen_details: str, console_output: str, additional_info: str):
        result = self.__evaluator.evaluate_next_step(
            self.__step_list[self.__index :],
            self.__task,
            additional_info,
            console_output,
            screen_details,
        )
        if result is None:
            return {"step_name": "SKIPSTEP"}
        self.__step_list = loads(result)
        self.__index = 1
        self.__evaluator.add_finished_step(self.__step_list[0])
        return self.__step_list[0]


class StepRetriever:
    def __init__(
        self, model: Model, embedding_model: EmbeddingModel, input_handler: InputHandler
    ):
        self.__queue = []
        self.__step_generator = None
        self.__model = model
        self.__embedding_model = embedding_model
        self.__input_handler = input_handler
        self.__task = ""

    def new_task(self, action_text: str):
        self.__task = action_text
        self.__step_generator = StepGenerator(
            self.__model, self.__embedding_model, action_text
        )
        screen_details = self.__input_handler.get_screen_details()
        if screen_details is None:
            self.__queue = [{"step_name": "SKIPSTEP"}]
        else:
            self.__queue = [self.__step_generator.next_step(screen_details, "", "")]

    def get_task(self):
        return self.__task

    def retrieve_step(self, console_output: str = ""):
        if self.__step_generator is None:
            raise Exception("Step generator not set")
        if self.__input_handler.cancel_task():
            task_info = self.__input_handler.get_input()
            self.new_task(task_info)
        if len(self.__queue) == 0:
            additional_info = self.__input_handler.get_input()
            screen_details = self.__input_handler.get_screen_details()
            if screen_details is None:
                return {"step_name": "SKIPSTEP"}
            self.__queue += [
                self.__step_generator.next_step(screen_details, console_output, additional_info)
            ]
        return self.__queue.pop(0)
