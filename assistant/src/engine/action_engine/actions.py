from pyautogui import moveTo, click, scroll, dragTo, press, write, hold
from subprocess import Popen, PIPE
from sys import platform
from colorama import Fore
from pyttsx3 import init

OS = platform
process = None


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


def press_key(text: str = "", keys: list = []):
    if text != "":
        write(text)
    else:
        if len(keys) == 1:
            press(keys[0])
        elif len(keys) == 2:
            with hold(keys[0]):
                press(keys[1])
        else:
            with hold(keys[0]):
                hold_key(keys[1], keys[2:])


def hold_key(key: str, keys: list):
    with hold(key):
        if len(keys) == 1:
            press(keys[0])
        else:
            hold_key(keys[0], keys[1:])


def tell(text: str):
    print(Fore.BLUE + "[OmniAssist]: " + Fore.RESET + text)
    engine = init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'en' in voice.languages:
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()


def init_terminal():
    global process
    if OS.startswith("win"):
        terminal = "cmd.exe"
        encoding = "cp1252"  
    else:
        terminal = "bash"
        encoding = "utf-8" 

    process = Popen(
        [terminal],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        shell=True,
        text=True,
        encoding=encoding, 
    )


def terminal(text: str):
    global process
    process.stdin.write(text)
    process.stdin.flush()
    output, error = process.communicate()
    return output, error