from pyautogui import moveTo, click, scroll, dragTo, press, write


def locate(pos: tuple[int, int]):
    moveTo(pos[0], pos[1])


def click_left():
    click()


def click_right():
    click(button="right")


def double_click():
    click(clicks=2)


def scroll_up():
    scroll(10)


def scroll_down():
    scroll(-10)


def drag(pos: tuple[int, int]):
    dragTo(pos[0], pos[1])


def press_key(key: str, write_text: bool = True):
    if write_text:
        write(key)
    else:
        press(key)
