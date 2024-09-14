from engine.step_engine.input_handler import InputHandler
from dotenv import load_dotenv
from os import getenv

if __name__ == "__main__":
    load_dotenv()
    input_handler = InputHandler(getenv("GEMINI_API_KEY"))
    while True:
        input_text = input("Enter input: ")
        input_handler.add_input(input_text)
        print(input_handler.get_input())