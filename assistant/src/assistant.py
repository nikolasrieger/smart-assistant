#from engine.step_engine.input_handler import InputHandler
from dotenv import load_dotenv
from os import getenv
from PIL import Image
from engine.vision_engine.screen_analyzer import ScreenAnalyzer
from lib.llm_models.model import Model
from lib.llm_models.embeddings import EmbeddingModel

#TODO: Add visual Information to InputHandler
#TODO: Add speech support
#TODO: Actually do the tasks

if __name__ == "__main__":
    screen = Image.open("home_screen.png")
    load_dotenv()
    model = Model(getenv("GEMINI_API_KEY"))
    embedding_model = EmbeddingModel(getenv("GEMINI_API_KEY"))
    """
    input_handler = InputHandler(model, embedding_model)
    while True:
        input_text = input("Enter input: ")
        input_handler.add_input(input_text)
        print(input_handler.get_input())"""
    screen_analyzer = ScreenAnalyzer(model)
    print(screen_analyzer.analyze_image_details(screen))
    # best_positions = screen_analyzer.analyze_image_coordinates(screen, "home_screen.pn", "Mozilla Thunderbird Icon")
