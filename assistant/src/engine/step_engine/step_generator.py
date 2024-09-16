from lib.llm_models.model import Model
from lib.llm_models.prompts import (
    GenerateStepsTemplate,
    ReflectStepsTemplate,
    ExtractTaskTemplate,
)
from lib.web_search.search_engine import SearchEngine
from engine.step_engine.context_generator import ContextGenerator
from lib.llm_models.embeddings import EmbeddingModel
from engine.step_engine.step_evaluator import StepEvaluator, Tasks
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
        self.__additional_info = ""

    def __generate_step_from_action(self, action_text: str, context: list = []):
        context_text = ""
        for webpage in context:
            context_text += SearchEngine.get_text_from_url(webpage.url) + "\n"
        template = GenerateStepsTemplate(action_text, context_text)
        draft_steps = self.__model.generate(
            template.prompt(), template.generation_config()
        )
        if len(loads(draft_steps)) == 0:
            raise IndexError("No steps generated")
        reflected_steps = self.__reflect_on_steps(action_text, draft_steps)
        self.__index = 0
        return reflected_steps

    def get_steps(self):
        return self.__step_list, self.__index

    def __reflect_on_steps(self, action_text: str, steps: list):
        template = ReflectStepsTemplate(action_text, steps)
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result

    def next_step(self, additional_info: str = ""):
        if len(self.__step_list) <= self.__index:
            return None
        if additional_info != "":
            self.__additional_info += additional_info + " "
        step = self.__step_list[self.__index]
        description = step["step_name"]
        task_list = loads(self.__get_tasks(description))
        self.__evaluator.evaluate_next_step(
            task_list, self.__task, self.__additional_info
        )
        self.__index += 1
        self.__evaluator.add_finished_step(task_list)
        return task_list

    def __get_tasks(self, step_description: str):
        template = ExtractTaskTemplate(step_description, Tasks)
        tasks = self.__model.generate(template.prompt(), template.generation_config())
        return tasks


class StepRetriever:
    def __init__(self, model: Model, embedding_model: EmbeddingModel):
        self.__queue = []
        self.__step_generator = None
        self.__model = model
        self.__embedding_model = embedding_model
        self.__additional_info = ""
        self.__override_additional_info = ""

    def new_task(self, action_text: str):
        self.__step_generator = StepGenerator(self.__model, self.__embedding_model, action_text)
        self.__queue += self.__step_generator.next_step()

    def add_additional_info(self, additional_info: str, overrider: str):
        self.__additional_info = additional_info
        self.__override_additional_info = overrider

    def retrieve_step(self):
        if self.__step_generator is None:
            raise Exception("Step generator not set")
        if len(self.__queue) == 0:
            self.__queue += self.__step_generator.next_step(self.__additional_info)
        self.__additional_info = self.__override_additional_info
        return self.__queue.pop(0)
