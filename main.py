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


if __name__ == "__main__":
    if not is_admin():
        request_admin_privileges()
    app = MainWindow()
    app.run()
