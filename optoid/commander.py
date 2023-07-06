import time
import asyncio

import win32con
import win32gui
import win32process


from .find_window import (
    find_command_line_inputs,
    close_register_windows,
    find_window_of_title,
)
from .window_title import window_title


def bring_window_to_front(window_handle):
    # 親ウィンドウ内で最前面に移動する
    win32gui.SetWindowPos(
        window_handle,
        win32con.HWND_TOP,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )


def bring_window_to_back(window_handle):
    # 親ウィンドウ内で最背面に移動する
    win32gui.SetWindowPos(
        window_handle,
        win32con.HWND_BOTTOM,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )


def is_highest_window(hwnd):
    parent_hwnd = win32gui.GetParent(hwnd)
    highest_hwnd = win32gui.GetTopWindow(parent_hwnd)
    return highest_hwnd == hwnd


def send_complex_command(hwnd_edit, command):
    sub_commands = command.split(";")
    command_groups = []
    command_group = []
    for sub_command in sub_commands:
        if sub_command.strip() == "len":
            command_groups.append(command_group)
            command_groups.append([sub_command])
            command_group = []
        else:
            command_group.append(sub_command)
    if len(command_group) > 0:
        command_groups.append(command_group)

    commands = []
    for command_group in command_groups:
        commands.append(";".join(command_group))

    for command in commands:
        send_command(hwnd_edit, command)


def send_command(hwnd_edit, command):
    # テキストをセットするためのメッセージを送信する
    win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, None, command)

    # エンターキーを押すためのメッセージを送信する
    win32gui.PostMessage(hwnd_edit, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    win32gui.PostMessage(hwnd_edit, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

    # PostMessage は非同期であるため、念のためここで少し待つ必要がある
    time.sleep(0.1)

    # 以下の処理により、コマンドが完了するまで待つことができる
    win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, None, "")

    if command.strip() == "len":
        # len コマンドの場合、確認ダイアログが表示されるため、まずはそれを待つ
        time.sleep(0.5)
        # 確認ダイアログを探す
        hwnd_confirm = find_window_of_title(
            "New Lens", win32process.GetWindowThreadProcessId(hwnd_edit)[1]
        )
        if hwnd_confirm is not None:
            win32gui.PostMessage(
                hwnd_confirm, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0
            )
            win32gui.PostMessage(hwnd_confirm, win32con.WM_KEYUP, win32con.VK_RETURN, 0)

            # PostMessage は非同期であるため、念のためここで少し待つ必要がある
            time.sleep(0.1)

    # error が発生していないか確認する
    error = find_window_of_title(
        "Error", win32process.GetWindowThreadProcessId(hwnd_edit)[1]
    )
    if error is not None:
        raise Exception("Failed to send command: " + command)


async def send_command_tmo_async(hwnd_edit, text_to_set, timeout_seconds):
    # イベントループを取得
    loop = asyncio.get_event_loop()

    try:
        # 実行を開始
        task = loop.run_in_executor(None, send_complex_command, hwnd_edit, text_to_set)

        # 実行が完了するか、タイムアウトが発生するまで待機
        result = await asyncio.wait_for(task, timeout_seconds)
    except asyncio.TimeoutError:
        # タイムアウトが発生した場合、例外を投げる
        task.cancel()  # タスクをキャンセル
        raise

    return result


def send_command_tmo(hwnd_edit, text_to_set, timeout_seconds):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        send_command_tmo_async(hwnd_edit, text_to_set, timeout_seconds)
    )


class Commander:
    def __init__(self):
        self._command_line_inputs = {}

    def attach(self, search_title=window_title()):
        close_register_windows(search_title)

        command_line_inputs = find_command_line_inputs(search_title)
        if len(command_line_inputs) <= 0:
            raise Exception("Failed to attach: Command line input not found.")
        self._command_line_inputs = command_line_inputs

    def send_command(self, command, timeout_sec=60):
        if self._command_line_inputs is None:
            raise Exception("Failed to send command: Attach first.")

        if "text_window" in self._command_line_inputs:
            cli = self._command_line_inputs["text_window"]
            try:
                title = win32gui.GetWindowText(cli["root"])
                assert title == cli["title"]
            except Exception as e:
                del self._command_line_inputs["text_window"]
                print("text window is not found. deleted from command_line_inputs")
                print(e)
            else:
                bring_back = False
                # 最前面に持ってこないと、コマンドが実行されない
                if not is_highest_window(cli["root"]):
                    bring_back = True
                    bring_window_to_front(cli["root"])
                    time.sleep(0.5)

                send_command_tmo(cli["edit"], command, timeout_sec)
                if bring_back:
                    bring_window_to_back(cli["root"])
                return

        raise Exception("Failed to send command: Please attach again.")
