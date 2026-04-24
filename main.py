import ctypes
import os
import sys
from main_window import MainWindow


def is_admin():
    """检查当前脚本是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin_privileges():
    """使用 'runas' 重新启动自身以请求管理员权限"""
    script = os.path.abspath(sys.argv[0])
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, script, None, 1
        )
    except Exception as e:
        pass
    sys.exit(0)


def find_maven_helper_window():
    """查找已存在的 Maven Helper 窗口"""
    try:
        user32 = ctypes.windll.user32

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
        found = ctypes.c_int(0)

        def callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    if "Maven Helper" in buff.value:
                        user32.ShowWindow(hwnd, 9)
                        user32.SetForegroundWindow(hwnd)
                        found.value = 1
                        return 0
            return 1

        user32.EnumWindows(EnumWindowsProc(callback), 0)
        return found.value == 1
    except:
        return False


if __name__ == "__main__":
    if not is_admin():
        request_admin_privileges()

    if find_maven_helper_window():
        sys.exit(0)

    app = MainWindow()
    app.run()
