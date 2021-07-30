import asyncio

import pyautogui


async def handle_restart():
    """Send a key-combination on the host to trigger the Auto-Hotkey script reload"""
    pyautogui.keyDown('ctrl')
    pyautogui.press('r')
    await asyncio.sleep(1)
    pyautogui.press('q')
    pyautogui.keyUp('ctrl')
