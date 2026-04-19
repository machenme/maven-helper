import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import threading
import webbrowser
import winreg
import ctypes

class JavaService:
    JAVA8_URL = "https://mirror.lzu.edu.cn/adoptium/8/jdk/x64/windows/"
    JAVA11_URL = "https://mirror.lzu.edu.cn/adoptium/11/jdk/x64/windows/"
    
    @staticmethod
    def check_java():
        """检查Java环境"""
        java_home = os.environ.get('JAVA_HOME')
        
        try:
            result = subprocess.run(['java', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout.strip()
                return True, output
        except Exception:
            pass
            
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stderr.strip() or result.stdout.strip()
                return True, output
        except Exception:
            pass
            
        return False, None
    
    @staticmethod
    def get_java_paths():
        """从PATH中获取所有Java路径"""
        paths = []
        path_env = os.environ.get('PATH', '')
        path_list = path_env.split(os.pathsep)
        
        for path in path_list:
            if path:
                java_exe = os.path.join(path, 'java.exe')
                if os.path.exists(java_exe):
                    # 检测版本
                    try:
                        result = subprocess.run([java_exe, '-version'], capture_output=True, text=True, timeout=3)
                        version_info = result.stderr.strip() or result.stdout.strip()
                        paths.append({
                            'path': path,
                            'version': version_info,
                            'exe': java_exe
                        })
                    except Exception:
                        continue
        
        return paths
    
    @staticmethod
    def get_registry_path(key, subkey, value_name):
        """从注册表获取PATH"""
        try:
            reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(reg_key, value_name)
            winreg.CloseKey(reg_key)
            return value
        except Exception:
            return None
    
    @staticmethod
    def set_registry_path(key, subkey, value_name, value):
        """设置注册表PATH"""
        try:
            reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_EXPAND_SZ, value)
            winreg.CloseKey(reg_key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def refresh_environment():
        """刷新环境变量"""
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        
        try:
            result = ctypes.c_long()
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0,
                'Environment', SMTO_ABORTIFHUNG, 5000,
                ctypes.byref(result)
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def show_java_sort_dialog(parent):
        """显示Java版本排序对话框"""
        java_paths = JavaService.get_java_paths()
        
        if len(java_paths) < 2:
            messagebox.showinfo("提示", "当前检测到的Java版本少于2个，无需排序")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Java 版本排序")
        dialog.geometry("700x500")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        tk.Label(dialog, text="当前检测到的Java版本（可调整顺序）:", font=("Microsoft YaHei UI", 12)).place(x=20, y=20)
        
        # 列表框
        listbox = tk.Listbox(dialog, font=("Microsoft YaHei UI", 10), height=15, width=80)
        listbox.place(x=20, y=60)
        
        for jp in java_paths:
            version_str = jp['version'].split('\n')[0] if '\n' in jp['version'] else jp['version']
            listbox.insert(tk.END, f"{version_str} - {jp['path']}")
        
        # 按钮
        def move_up():
            selection = listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                item = listbox.get(idx)
                listbox.delete(idx)
                listbox.insert(idx - 1, item)
                listbox.selection_set(idx - 1)
                
                # 同时更新数据
                java_paths[idx], java_paths[idx - 1] = java_paths[idx - 1], java_paths[idx]
        
        def move_down():
            selection = listbox.curselection()
            if selection and selection[0] < listbox.size() - 1:
                idx = selection[0]
                item = listbox.get(idx)
                listbox.delete(idx)
                listbox.insert(idx + 1, item)
                listbox.selection_set(idx + 1)
                
                # 同时更新数据
                java_paths[idx], java_paths[idx + 1] = java_paths[idx + 1], java_paths[idx]
        
        tk.Button(dialog, text="↑ 上移", font=("Microsoft YaHei UI", 11), width=10, command=move_up).place(x=550, y=100)
        tk.Button(dialog, text="↓ 下移", font=("Microsoft YaHei UI", 11), width=10, command=move_down).place(x=550, y=150)
        
        def apply_changes():
            # 获取当前PATH
            user_path = JavaService.get_registry_path(winreg.HKEY_CURRENT_USER, r'Environment', 'PATH') or ''
            system_path = JavaService.get_registry_path(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PATH') or ''
            
            # 收集所有Java路径
            all_java_paths = [jp['path'] for jp in java_paths]
            
            # 重建PATH
            def rebuild_path(old_path):
                path_list = old_path.split(os.pathsep)
                new_list = []
                # 先添加排序后的Java路径
                new_list.extend(all_java_paths)
                # 再添加其他路径（排除旧的Java路径）
                for p in path_list:
                    if p and p not in all_java_paths:
                        new_list.append(p)
                return os.pathsep.join(new_list)
            
            # 应用到用户变量
            user_success = JavaService.set_registry_path(winreg.HKEY_CURRENT_USER, r'Environment', 'PATH', rebuild_path(user_path))
            
            # 尝试应用到系统变量（可能需要管理员权限）
            system_success = JavaService.set_registry_path(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'PATH', rebuild_path(system_path))
            
            # 刷新环境变量
            JavaService.refresh_environment()
            
            if user_success:
                messagebox.showinfo("成功", "PATH 顺序已更新！\n\n请重启程序或重新打开命令行窗口生效")
                dialog.destroy()
            else:
                messagebox.showerror("失败", "修改 PATH 失败，请以管理员身份运行")
        
        tk.Button(dialog, text="应用更改", font=("Microsoft YaHei UI", 12), width=15, command=apply_changes).place(x=280, y=420)
        
        dialog.transient(parent)
        dialog.grab_set()
        dialog.wait_window()
    
    @staticmethod
    def show_java_dialog(parent):
        """显示Java下载和安装对话框"""
        has_java, java_info = JavaService.check_java()
        
        dialog = tk.Toplevel(parent)
        dialog.title("检查 Java 环境")
        dialog.geometry("600x450")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        if has_java:
            tk.Label(dialog, text="✅ Java 环境检测成功！", font=("Microsoft YaHei UI", 16, "bold"), fg="green").place(x=200, y=30)
            tk.Label(dialog, text="版本信息:", font=("Microsoft YaHei UI", 12)).place(x=50, y=80)
            
            text_area = tk.Text(dialog, font=("Consolas", 10), wrap=tk.WORD, height=8, width=70)
            text_area.place(x=50, y=120)
            text_area.insert(tk.END, java_info or "")
            text_area.config(state=tk.DISABLED)
            
            tk.Button(dialog, text="调整 Java 版本顺序", font=("Microsoft YaHei UI", 12), width=20, 
                     command=lambda: JavaService.show_java_sort_dialog(dialog)).place(x=220, y=280)
        else:
            tk.Label(dialog, text="❌ 未检测到 Java 环境", font=("Microsoft YaHei UI", 16, "bold"), fg="red").place(x=180, y=30)
            tk.Label(dialog, text="请下载并安装 Java:", font=("Microsoft YaHei UI", 12)).place(x=50, y=80)
            
            def open_java8():
                webbrowser.open(JavaService.JAVA8_URL)
            
            def open_java11():
                webbrowser.open(JavaService.JAVA11_URL)
            
            tk.Button(dialog, text="下载 Java 8", font=("Microsoft YaHei UI", 13), width=15, height=2, command=open_java8).place(x=100, y=150)
            tk.Button(dialog, text="下载 Java 11", font=("Microsoft YaHei UI", 13), width=15, height=2, command=open_java11).place(x=350, y=150)
            
            # 状态标签
            status_label = tk.Label(dialog, text="", font=("Microsoft YaHei UI", 10), fg="blue")
            status_label.place(x=200, y=380)
            
            def select_file():
                file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
                if file_path:
                    status_label.config(text="正在安装...")
                    
                    def install():
                        try:
                            subprocess.run([file_path, '/s'], shell=True, check=True)
                            dialog.after(0, lambda: status_label.config(text="✅ 安装完成！"))
                            dialog.after(0, lambda: messagebox.showinfo("成功", "Java 安装完成！"))
                        except Exception as e:
                            dialog.after(0, lambda: status_label.config(text="❌ 安装失败"))
                    
                    threading.Thread(target=install, daemon=True).start()
            
            tk.Button(dialog, text="选择安装文件", font=("Microsoft YaHei UI", 12), width=20, command=select_file).place(x=210, y=250)
            
        dialog.transient(parent)
        dialog.grab_set()
        dialog.wait_window()
