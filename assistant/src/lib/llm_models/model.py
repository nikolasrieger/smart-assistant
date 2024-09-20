from google.generativeai import configure, GenerativeModel, GenerationConfig, list_files
from google.api_core.exceptions import InternalServerError, ServiceUnavailable
from PIL import Image
from colorama import Fore


class Model:
    def __init__(self, api_key: str):
        configure(api_key=api_key)
        self.__model = GenerativeModel("gemini-1.5-flash")
        self.__errors = 0

    def delete_files(self):
        for f in list_files():
            f.delete()

    def generate(self, prompt: str, generation_config: GenerationConfig):
        try:
            res = self.__model.generate_content(
                prompt, generation_config=generation_config
            )
            self.__errors = 0
        except InternalServerError:
            print(Fore.RED + "[ERROR]:  Internal Server Error", prompt + Fore.RESET)
            self.check_abort()
            return
        except ServiceUnavailable:
            print(Fore.RED + "[ERROR]:  Service Unavailable" + Fore.RESET)
            self.check_abort()
            return
        return res.text

    def generate_with_image(
        self, prompt: str, image: Image, generation_config: GenerationConfig
    ):
        try:
            res = self.__model.generate_content(
                [image, prompt], generation_config=generation_config
            )
            self.__errors = 0
        except InternalServerError:
            print(Fore.RED + "[ERROR]:  Internal Server Error" + Fore.RESET)
            self.check_abort()
            return
        except ServiceUnavailable:
            print(Fore.RED + "[ERROR]:  Service Unavailable" + Fore.RESET)
            self.check_abort()
            return
        return res.text

    def check_abort(self):
        self.__errors += 1
        if self.__errors > 5:
            raise Exception("Failed to connect to the model too many times.")

    @staticmethod
    def set_generation_config(
        candidate_count=None,
        stop_sequences=None,
        max_output_tokens=None,
        temperature=None,
        top_p=None,
        top_k=None,
        response_mime_type=None,
        response_schema=None,
    ):
        return GenerationConfig(
            candidate_count,
            stop_sequences,
            max_output_tokens,
            temperature,
            top_p,
            top_k,
            response_mime_type,
            response_schema,
        )
