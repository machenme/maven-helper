# Usage: 确保以管理员权限运行以获得最佳兼容性
import os
import re
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PomFixer:
    SKIP_DIRS = {
        '__pycache__', '.git', '.svn', '.hg',
        'node_modules', 'bower_components',
        'target', 'build', 'dist', 'out',
        '.idea', '.vscode', '.settings',
        '.gradle', '.mvn',
        'apache-maven-', 'apache-tomcat-',
    }

    @staticmethod
    def fix():
        modified_count = 0
        current_dir = os.getcwd()

        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if d not in PomFixer.SKIP_DIRS and not d.startswith('.')]

            if 'pom.xml' in files:
                path = os.path.join(root, 'pom.xml')
                with open(path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()

                regex = re.compile(r'<(maven.compiler.source|maven.compiler.target)>(.*?)</\1>', re.IGNORECASE)

                def replace_func(match):
                    version_str = match.group(2).strip()
                    try:
                        version = float(version_str)
                        if 0 < version < 1.8:
                            return f"<{match.group(1)}>1.8</{match.group(1)}>"
                    except ValueError:
                        pass
                    return match.group(0)

                new_content = regex.sub(replace_func, content)

                if content != new_content:
                    with open(path, 'w', encoding='utf-8-sig') as f:
                        f.write(new_content)
                    modified_count += 1

        return f"🎉 已优化 {modified_count} 个项目的版本配置。"

    @staticmethod
    def find_maven_projects():
        """查找当前目录下所有的 Maven 项目"""
        projects = []
        current_dir = os.getcwd()

        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if d not in PomFixer.SKIP_DIRS and not d.startswith('.')]

            if 'pom.xml' in files:
                projects.append(root)

        return projects

    @staticmethod
    def run_maven_command(project_dir, command):
        """执行 Maven 命令"""
        try:
            subprocess.Popen(
                f'start "" cmd /c "cd /d "{project_dir}" & {command}"',
                shell=True
            )
            return True
        except Exception as e:
            return False

    @staticmethod
    def kill_port_8080():
        """只杀死占用 8080 端口的程序"""
        if not PSUTIL_AVAILABLE:
            messagebox.showerror("错误", "请先安装 psutil 库 (pip install psutil)")
            return False

        port = 8080
        killed = False
        access_denied = False
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections(kind='inet')
                    for conn in connections:
                        if conn.laddr.port == port:
                            try:
                                try:
                                    parent = proc.parent()
                                    if parent and parent.name() == "cmd.exe":
                                        parent.kill()
                                except Exception:
                                    pass
                                proc.kill()
                                killed = True
                            except psutil.AccessDenied:
                                access_denied = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if access_denied:
                messagebox.showwarning("权限不足", "请以管理员身份运行此工具以获得最佳兼容性")
            return killed
        except Exception:
            return False

    @staticmethod
    def wait_for_port_release(port, timeout=3):
        """等待端口释放"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        connections = proc.connections(kind='inet')
                        for conn in connections:
                            if conn.laddr.port == port and conn.status == 'LISTENING':
                                time.sleep(0.5)
                                break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return True
            except Exception:
                pass
        return False

    @staticmethod
    def kill_and_restart_spring(project_dir, callback=None):
        """关闭并重启 Spring Boot"""
        if not PSUTIL_AVAILABLE:
            messagebox.showerror("错误", "请先安装 psutil 库 (pip install psutil)")
            return False

        import threading
        def run_in_thread():
            PomFixer.kill_port_8080()
            PomFixer.wait_for_port_release(8080, timeout=3)
            PomFixer.run_maven_command(project_dir, "mvn spring-boot:run")
            if callback:
                callback()

        threading.Thread(target=run_in_thread, daemon=True).start()
        return True

    @staticmethod
    def open_pom_directory(project_dir):
        """打开 pom 文件所在目录"""
        try:
            subprocess.Popen(f'explorer "{project_dir}"', shell=True)
            return True
        except Exception as e:
            return False

    @staticmethod
    def show_maven_runner_dialog(parent):
        """显示 Maven 项目运行器对话框"""
        projects = PomFixer.find_maven_projects()

        if not projects:
            from tkinter import messagebox
            messagebox.showinfo("提示", "未找到 Maven 项目")
            return

        dialog = tk.Toplevel(parent)
        dialog.title("Maven 项目运行器")
        dialog.geometry("700x550")
        dialog.withdraw()

        dialog.update_idletasks()
        dialog.geometry(f"700x550+{((dialog.winfo_screenwidth()-700)//2)}+{((dialog.winfo_screenheight()-550)//2)}")
        dialog.deiconify()

        tk.Label(dialog, text="选择 Maven 项目:", font=("Microsoft YaHei UI", 12)).place(x=20, y=20)

        listbox = tk.Listbox(dialog, font=("Microsoft YaHei UI", 10), height=12, width=80)
        listbox.place(x=20, y=50)

        for project in projects:
            listbox.insert(tk.END, project)

        if projects:
            listbox.select_set(0)

        def on_clean_install():
            selection = listbox.curselection()
            if selection:
                project_dir = projects[selection[0]]
                PomFixer.run_maven_command(project_dir, "mvn clean install")

        def on_spring_boot_run():
            selection = listbox.curselection()
            if selection:
                project_dir = projects[selection[0]]
                PomFixer.run_maven_command(project_dir, "mvn spring-boot:run")

        def on_custom_command():
            selection = listbox.curselection()
            if selection:
                project_dir = projects[selection[0]]
                custom = custom_entry.get().strip()
                if custom:
                    PomFixer.run_maven_command(project_dir, custom)

        tk.Label(dialog, text="自定义命令:", font=("Microsoft YaHei UI", 11)).place(x=20, y=270)
        custom_entry = tk.Entry(dialog, font=("Consolas", 10), width=60)
        custom_entry.place(x=20, y=295)

        btn_frame = tk.Frame(dialog)
        btn_frame.place(x=20, y=340)

        def on_open_directory():
            selection = listbox.curselection()
            if selection:
                project_dir = projects[selection[0]]
                PomFixer.open_pom_directory(project_dir)

        def on_kill_and_restart():
            selection = listbox.curselection()
            if selection:
                project_dir = projects[selection[0]]
                PomFixer.kill_and_restart_spring(project_dir)

        buttons = [
            ("mvn clean install", on_clean_install),
            ("mvn spring-boot:run", on_spring_boot_run),
            ("执行自定义命令", on_custom_command),
            ("停止 Spring Boot", PomFixer.kill_port_8080),
            ("打开项目目录", on_open_directory),
            ("关闭并重启", on_kill_and_restart),
        ]

        for i, (text, cmd) in enumerate(buttons):
            row = i // 3
            col = i % 3
            tk.Button(btn_frame, text=text, font=("Microsoft YaHei UI", 11), width=18, height=2,
                      command=cmd).grid(row=row, column=col, padx=8, pady=5)

        tk.Label(dialog, text="命令将在新窗口中执行", font=("Microsoft YaHei UI", 9), fg="gray").place(x=20, y=500)

        dialog.transient(parent)
        dialog.grab_set()
        dialog.wait_window()
