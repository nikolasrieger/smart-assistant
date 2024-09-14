from PIL import ImageGrab

class ScreenHandler():
    def __init__(self):
        self.__image = None

    def get_active_screen(self):
        self.__image = ImageGrab.grab()
        return self.__image