import time

import win32gui
import win32process
import win32con

# from .window_title import window_title


def close_register_windows(search_title):
    register_windows = find_windows_with_title("Registration")

    if len(register_windows) == 0:
        return

    main_windows = find_windows_with_title(search_title)
    main_window_of_pid = {}
    for main_window in main_windows:
        process_id = win32process.GetWindowThreadProcessId(main_window)[1]
        main_window_of_pid[process_id] = main_window

    for register_window in register_windows:
        process_id = win32process.GetWindowThreadProcessId(register_window)[1]
        if process_id in main_window_of_pid:
            win32gui.PostMessage(register_window, win32con.WM_CLOSE, 0, 0)

    time.sleep(5)


def find_windows_with_title(title):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def find_child_window_with_title(parent_hwnd, title):
    def callback(hwnd, hwnds):
        if win32gui.GetWindowText(hwnd) == title:
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumChildWindows(parent_hwnd, callback, hwnds)
    return hwnds[0] if hwnds else None


def enumerate_edit_handles(hwnd):
    edit_handles = []

    def callback(hwnd, edit_handles):
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "Edit":
            edit_handles.append(hwnd)
        return True

    win32gui.EnumChildWindows(hwnd, callback, edit_handles)

    return edit_handles


def find_window_of_title(title, process_id):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and title == win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    for hwnd in hwnds:
        if win32process.GetWindowThreadProcessId(hwnd)[1] == process_id:
            return hwnd
    return None


def find_command_line_inputs(window_search):
    command_line_inputs = {}
    main_window_hwnds = find_windows_with_title(window_search)

    floating_window_hwnds = find_windows_with_title("Floating Command Line")
    floating_window_hwnd_of_pid = {}
    for floating_window_hwnd in floating_window_hwnds:
        pid = win32process.GetWindowThreadProcessId(floating_window_hwnd)[1]
        floating_window_hwnd_of_pid[pid] = floating_window_hwnd

    if len(main_window_hwnds) == 0:
        return {}

    for main_window_hwnd in main_window_hwnds:
        process_id = win32process.GetWindowThreadProcessId(main_window_hwnd)[1]
        if process_id in floating_window_hwnd_of_pid:
            floating_hwnd = floating_window_hwnd_of_pid[process_id]
            edit_handles = enumerate_edit_handles(floating_hwnd)
            if len(edit_handles) > 0:
                command_line_inputs["floating"] = {
                    "edit": edit_handles[0],
                    "root": floating_hwnd,
                    "title": "Floating Command Line",
                }
                break

    for main_window_hwnd in main_window_hwnds:
        if main_window_hwnd:
            # "Text Window" の子ウィンドウのハンドルを取得
            text_window_title = "Text Window"
            text_window_hwnd = find_child_window_with_title(
                main_window_hwnd, text_window_title
            )

            if text_window_hwnd != 0:
                # "Edit" クラスの子ウィンドウのハンドルを列挙
                edit_handles = enumerate_edit_handles(text_window_hwnd)

                # 結果を出力
                if len(edit_handles) > 0:
                    command_line_inputs["text_window"] = {
                        "edit": edit_handles[0],
                        "root": text_window_hwnd,
                        "title": "Text Window",
                    }
                    break
                else:
                    pass
                    # print("Editウィンドウが見つかりませんでした。")
            else:
                pass
                # print("Text Windowが見つかりませんでした。")

    return command_line_inputs
