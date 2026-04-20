import os
import sys
import pymysql
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class DealSQLService:
    SKIP_DIRS = {
        '__pycache__', '.git', '.svn', '.hg',
        'node_modules', 'bower_components',
        'target', 'build', 'dist', 'out',
        '.idea', '.vscode', '.settings',
        '.gradle', '.mvn',
        'apache-maven-', 'apache-tomcat-',
    }

    @staticmethod
    def find_yml():
        """查找当前目录下所有的 application.yml 或 config.properties"""
        target_files = ['application.yml', 'config.properties']
        results = []
        for root, dirs, files in os.walk(os.getcwd()):
            dirs[:] = [d for d in dirs if d not in DealSQLService.SKIP_DIRS and not d.startswith('.')]
            for file in files:
                if file in target_files:
                    results.append(os.path.join(root, file))
        return results

    @staticmethod
    def find_sql_files():
        """查找当前目录下除了 maven/tomcat 目录以外的 SQL 文件"""
        results = []

        for root, dirs, files in os.walk(os.getcwd()):
            dirs[:] = [d for d in dirs if d not in DealSQLService.SKIP_DIRS and not d.startswith('.')]

            for file in files:
                if file.endswith('.sql'):
                    results.append(os.path.join(root, file))
        return results

    @staticmethod
    def parse_sql_file(sql_file):
        """解析 SQL 文件，查找 create database 和 use 语句"""
        db_name = None
        has_create_db = False
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line_upper = line.strip().upper()
                
                if 'CREATE DATABASE' in line_upper or 'CREATE SCHEMA' in line_upper:
                    has_create_db = True
                
                if line_upper.startswith('USE'):
                    import re
                    match = re.search(r'USE\s+[`"]?(\w+)[`"]?', line.strip(), re.IGNORECASE)
                    if match:
                        db_name = match.group(1)
                        
        except Exception as e:
            pass
            
        return db_name, has_create_db

    @staticmethod
    def get_sql_preview(sql_file, max_lines=50):
        """获取 SQL 文件预览（前50行）"""
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            preview = ''.join(lines[:max_lines])
            if len(lines) > max_lines:
                preview += f'\n\n... (共 {len(lines)} 行)'
            return preview
        except Exception as e:
            return f'读取文件失败：{str(e)}'

    @staticmethod
    def execute_sql_file(conn, sql_file, db_name=None):
        """执行 SQL 文件，可选指定数据库"""
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                
            cursor = conn.cursor()
            
            if db_name:
                try:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    conn.commit()
                except Exception:
                    pass
                    
                try:
                    cursor.execute(f"USE `{db_name}`")
                except Exception:
                    pass
            
            statements = sql_content.split(';')
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        pass
            conn.commit()
            return True
        except Exception as e:
            return False

    @staticmethod
    def deal():
        result = {"user": None, "password": None, "port": None}
        
        def on_ok():
            result["user"] = entry_user.get() or "root"
            result["password"] = entry_password.get() or "123456"
            try:
                result["port"] = int(entry_port.get() or "3306")
            except ValueError:
                result["port"] = 3306
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 创建数据库配置对话框
        dialog = tk.Toplevel()
        dialog.title("数据库配置")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # 用户名
        tk.Label(dialog, text="用户名(root):", font=("Microsoft YaHei UI", 11)).place(x=30, y=30)
        entry_user = tk.Entry(dialog, font=("Microsoft YaHei UI", 11), width=25)
        entry_user.place(x=120, y=30)
        entry_user.insert(0, "root")
        
        # 密码
        tk.Label(dialog, text="密码(123456):", font=("Microsoft YaHei UI", 11)).place(x=30, y=80)
        entry_password = tk.Entry(dialog, font=("Microsoft YaHei UI", 11), width=25, show="*")
        entry_password.place(x=120, y=80)
        entry_password.insert(0, "123456")
        
        # 端口
        tk.Label(dialog, text="端口(3306):", font=("Microsoft YaHei UI", 11)).place(x=30, y=130)
        entry_port = tk.Entry(dialog, font=("Microsoft YaHei UI", 11), width=25)
        entry_port.place(x=120, y=130)
        entry_port.insert(0, "3306")
        
        # 按钮
        tk.Button(dialog, text="确定", font=("Microsoft YaHei UI", 11), width=10, command=on_ok).place(x=80, y=180)
        tk.Button(dialog, text="取消", font=("Microsoft YaHei UI", 11), width=10, command=on_cancel).place(x=220, y=180)
        
        dialog.transient(dialog.master)
        dialog.grab_set()
        dialog.wait_window()
        
        if result["user"] is None:
            return "操作已取消"
        
        try:
            # 查找 SQL 文件
            sql_files = DealSQLService.find_sql_files()
            if not sql_files:
                return "未找到可执行的SQL文件"
            
            selected_file = None
            
            if len(sql_files) == 1:
                selected_file = sql_files[0]
                preview = DealSQLService.get_sql_preview(selected_file)
                
                # 显示预览
                preview_dialog = tk.Toplevel()
                preview_dialog.title("SQL 文件预览")
                preview_dialog.geometry("700x500")
                
                # 居中显示
                preview_dialog.update_idletasks()
                width = preview_dialog.winfo_width()
                height = preview_dialog.winfo_height()
                x = (preview_dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (preview_dialog.winfo_screenheight() // 2) - (height // 2)
                preview_dialog.geometry(f'{width}x{height}+{x}+{y}')
                
                tk.Label(preview_dialog, text=f"找到 1 个 SQL 文件: {os.path.basename(selected_file)}", 
                        font=("Microsoft YaHei UI", 12)).place(x=20, y=20)
                
                text_area = scrolledtext.ScrolledText(preview_dialog, font=("Consolas", 10), wrap=tk.WORD)
                text_area.place(x=20, y=60, width=660, height=380)
                text_area.insert(tk.END, preview)
                text_area.config(state=tk.DISABLED)
                
                confirmed = {"result": False}
                
                def on_confirm():
                    confirmed["result"] = True
                    preview_dialog.destroy()
                
                def on_cancel_preview():
                    preview_dialog.destroy()
                
                tk.Button(preview_dialog, text="执行", font=("Microsoft YaHei UI", 11), width=10, command=on_confirm).place(x=250, y=450)
                tk.Button(preview_dialog, text="取消", font=("Microsoft YaHei UI", 11), width=10, command=on_cancel_preview).place(x=380, y=450)
                
                preview_dialog.transient(preview_dialog.master)
                preview_dialog.grab_set()
                preview_dialog.wait_window()
                
                if not confirmed["result"]:
                    return "操作已取消"
            else:
                # 多个文件，显示选择列表
                selected = {"file": None}
                
                list_dialog = tk.Toplevel()
                list_dialog.title("选择 SQL 文件")
                list_dialog.geometry("600x450")
                
                # 居中显示
                list_dialog.update_idletasks()
                width = list_dialog.winfo_width()
                height = list_dialog.winfo_height()
                x = (list_dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (list_dialog.winfo_screenheight() // 2) - (height // 2)
                list_dialog.geometry(f'{width}x{height}+{x}+{y}')
                
                tk.Label(list_dialog, text=f"找到 {len(sql_files)} 个 SQL 文件，请选择:", 
                        font=("Microsoft YaHei UI", 12)).place(x=20, y=20)
                
                listbox = tk.Listbox(list_dialog, font=("Microsoft YaHei UI", 11))
                listbox.place(x=20, y=60, width=560, height=300)
                
                for f in sql_files:
                    listbox.insert(tk.END, f)
                
                def on_select():
                    selection = listbox.curselection()
                    if selection:
                        selected["file"] = sql_files[selection[0]]
                        list_dialog.destroy()
                
                def on_cancel_list():
                    list_dialog.destroy()
                
                tk.Button(list_dialog, text="确定", font=("Microsoft YaHei UI", 11), width=10, command=on_select).place(x=200, y=380)
                tk.Button(list_dialog, text="取消", font=("Microsoft YaHei UI", 11), width=10, command=on_cancel_list).place(x=330, y=380)
                
                list_dialog.transient(list_dialog.master)
                list_dialog.grab_set()
                list_dialog.wait_window()
                
                if not selected["file"]:
                    return "操作已取消"
                selected_file = selected["file"]
            
            # 解析 SQL 文件
            db_name, has_create_db = DealSQLService.parse_sql_file(selected_file)
            
            # 尝试连接数据库
            try:
                conn = pymysql.connect(
                    host="localhost",
                    user=result["user"],
                    password=result["password"],
                    port=result["port"],
                    charset='utf8mb4'
                )
            except Exception as e:
                return f"连接数据库失败：{str(e)}"
            
            # 执行 SQL
            success = DealSQLService.execute_sql_file(conn, selected_file, db_name)
            conn.close()
            
            if success:
                return f"成功执行: {os.path.basename(selected_file)}"
            else:
                return f"执行失败: {os.path.basename(selected_file)}"
            
        except Exception as e:
            return f"发生错误：{str(e)}"
