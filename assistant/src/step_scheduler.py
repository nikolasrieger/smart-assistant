from step_generator import StepRetriever

class InputHandler():
    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__step_retriever = StepRetriever()

    def add_input(self, input: str):
        pass