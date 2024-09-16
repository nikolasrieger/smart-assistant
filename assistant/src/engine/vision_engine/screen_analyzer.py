from engine.vision_engine.screen_handler import ScreenHandler
from PIL import Image
from cv2 import rectangle, imwrite
from numpy import array
from lib.llm_models.model import Model
from lib.llm_models.prompts import ImageCoordinatesTemplate, ImageDetailsTemplate, ImageTODOSTemplate, ImageTaskDoneTemplate
from json import loads

class ScreenAnalyzer():
    def __init__(self, api_key: str):
        self.__model = Model(api_key)
        self.__screen_handler = ScreenHandler()

    def analyze_image_coordinates(self, prompt: str, image: Image = None):
        if image is None:
            image = self.__screen_handler.get_active_screen()
        template = ImageCoordinatesTemplate(prompt)
        result = self.__model.generate_with_image(template.prompt(), image, template.generation_config())
        coordinates = loads(result)
        print(coordinates)
        x1, y1 = self.__convert_pos((coordinates[1], coordinates[0]), image.size)
        x2, y2 = self.__convert_pos((coordinates[3], coordinates[2]), image.size)
        self.__save_image(image, ((x1, y1), (x2, y2)))
        return (self.__mid_pos(x1, x2), self.__mid_pos(y1, y2))
    
    def analyze_image_details(self, image: Image = None):
        if image is None:
            image = self.__screen_handler.get_active_screen()
        template = ImageDetailsTemplate()
        result = self.__model.generate_with_image(template.prompt(), image, template.generation_config())
        return result
    
    def analyze_image_todos(self, image: Image = None):
        if image is None:
            image = self.__screen_handler.get_active_screen()
        template = ImageTODOSTemplate()
        result = self.__model.generate_with_image(template.prompt(), image, template.generation_config())
        return result
    
    def analzye_image_task(self, task: str, image: Image = None):
        if image is None:
            image = self.__screen_handler.get_active_screen()
        template = ImageTaskDoneTemplate(task)
        result = self.__model.generate_with_image(template.prompt(), image, template.generation_config())
        return result

    def __save_image(self, image: Image, coordinates: tuple[tuple[int, int], tuple[int, int]], path: str = "image.png"):
        img_np = array(image)
        x1, y1 = coordinates[0]
        x2, y2 = coordinates[1]
        img_with_box = rectangle(img_np.copy(), (x1, y1), (x2, y2), (255, 255, 255), 5)
        imwrite(path, img_with_box)

    def __convert_pos(self, pos: tuple[str, str], screen_size: tuple[int, int], image_size: tuple[int, int] = (1000, 1000)):
        return (self.__scale_pos(pos[0], screen_size[0], image_size[0]), self.__scale_pos(pos[1], screen_size[1], image_size[1]))
    
    def __scale_pos(self, pos: str, screen_size: int, image_size: int):
        return int(int(pos) / image_size * screen_size)
    
    def __mid_pos(self, pos1: int, pos2: int):
        return int((pos1 + pos2) / 2)