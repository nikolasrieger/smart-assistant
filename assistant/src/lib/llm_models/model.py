from google.generativeai import configure, GenerativeModel, GenerationConfig
from PIL import Image


class Model:
    def __init__(self, api_key: str):
        configure(api_key=api_key)
        self.__model = GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str, generation_config: GenerationConfig):
        res = self.__model.generate_content(prompt, generation_config=generation_config)
        return res.text

    def generate_with_image(
        self, prompt: str, image: Image, generation_config: GenerationConfig
    ):
        res = self.__model.generate_content(
            [image, prompt], generation_config=generation_config
        )
        return res.text

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
