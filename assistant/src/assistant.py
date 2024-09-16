from engine.step_engine.input_handler import InputHandler
from dotenv import load_dotenv
from os import getenv
from PIL import Image
from engine.vision_engine.screen_analyzer import ScreenAnalyzer

if __name__ == "__main__":
    """load_dotenv()
    input_handler = InputHandler(getenv("GEMINI_API_KEY"))
    while True:
        input_text = input("Enter input: ")
        input_handler.add_input(input_text)
        print(input_handler.get_input())"""
    screen = Image.open("home_screen.png")
    load_dotenv()
    screen_analyzer = ScreenAnalyzer(getenv("GEMINI_API_KEY"))
    print(screen_analyzer.analyze_image_details(screen))
    #best_positions = screen_analyzer.analyze_image_coordinates(screen, "home_screen.pn", "Mozilla Thunderbird Icon")