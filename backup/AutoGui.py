import pyautogui

def clickAt(x, y):
    pyautogui.click(x, y)

def doubleClickAt(x, y):
    pyautogui.doubleClick(x, y)

def hotKey(*args, **kwargs):
    """
    @param args: e.g. "Ctrl", "c"
    @param kwargs:
    @return:
    """
    pyautogui.hotkey(*args, **kwargs)