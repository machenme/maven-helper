import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
import os
import webbrowser
import subprocess
import codecs


class URLExtractorService:
    SKIP_DIRS = {
        '__pycache__', '.git', '.svn', '.hg',
        'node_modules', 'bower_components',
        'target', 'build', 'dist', 'out',
        '.idea', '.vscode', '.settings',
        '.gradle', '.mvn',
        'apache-maven-', 'apache-tomcat-',
    }

    @staticmethod
    def extract_urls_by_line(content):
        """按行匹配URL并根据关键字(backend/front)分类"""
        lines = content.split('\n')
        backend_url = ""
        frontend_url = ""

        url_pattern = re.compile(r'(https?://[^\s,，。；;]+)')

        for line in lines:
            urls = url_pattern.findall(line)
            for url in urls:
                clean_url = re.sub(r'[,.;，。；;]+$', '', url)

                lower_line = line.lower()
                if "back" in lower_line or "admin" in lower_line:
                    backend_url = clean_url
                elif "front" in lower_line:
                    frontend_url = clean_url

        return backend_url, frontend_url

    @staticmethod
    def read_file_with_encoding(file_path):
        """尝试多种编码读取文件防止乱码"""
        encodings = ['utf-8', 'gb2312', 'gbk', 'iso-8859-1']
        for enc in encodings:
            try:
                with codecs.open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""

    @staticmethod
    def find_explanation_file():
        """自动在当前目录搜索包含'说明'的txt文件"""
        try:
            cwd = os.getcwd()
            for root, dirs, files in os.walk(cwd):
                dirs[:] = [d for d in dirs if d not in URLExtractorService.SKIP_DIRS and not d.startswith('.')]
                for file in files:
                    if file.endswith('.txt') and '说明' in file:
                        return os.path.join(root, file)
        except Exception:
            pass
        return None


class URLExtractorWindow:
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("管理网地址提取器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.withdraw()

        if parent:
            self.root.transient(parent)
            self.root.attributes('-topmost', True)

        self.root.update_idletasks()
        self.root.geometry(f"600x500+{((self.root.winfo_screenwidth()-600)//2)}+{((self.root.winfo_screenheight()-500)//2)}")

        self.backend_url_var = tk.StringVar()
        self.frontend_url_var = tk.StringVar()
        self.file_path_var = tk.StringVar()

        self.create_widgets()
        self.auto_find_and_load_doc()
        self.root.deiconify()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        open_button = tk.Button(top_frame, text="打开说明文档", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5)

        file_path_label = tk.Label(top_frame, textvariable=self.file_path_var, anchor='w')
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(mid_frame, text="后台管理网地址:").grid(row=0, column=0, sticky='w', pady=2)
        self.backend_url_entry = tk.Entry(mid_frame, textvariable=self.backend_url_var, width=50)
        self.backend_url_entry.grid(row=0, column=1, padx=5)

        tk.Label(mid_frame, text="前台管理网地址:").grid(row=1, column=0, sticky='w', pady=2)
        self.frontend_url_entry = tk.Entry(mid_frame, textvariable=self.frontend_url_var, width=50)
        self.frontend_url_entry.grid(row=1, column=1, padx=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(button_frame, text="打开后台网地址", command=lambda: self.open_url(self.backend_url_var.get())).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="打开前台网地址", command=lambda: self.open_url(self.frontend_url_var.get())).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="复制后台网地址", command=lambda: self.copy_to_clipboard(self.backend_url_var.get())).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="复制前台网地址", command=lambda: self.copy_to_clipboard(self.frontend_url_var.get())).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="打开Webapps目录", command=self.open_webapps_directory).pack(side=tk.LEFT, padx=2)

        bottom_frame = tk.LabelFrame(self.root, text="文件内容")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.content_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True)

    def auto_find_and_load_doc(self):
        file_path = URLExtractorService.find_explanation_file()
        if file_path:
            self.process_file(file_path)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        try:
            self.file_path_var.set(file_path)
            content = URLExtractorService.read_file_with_encoding(file_path)

            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, content)

            backend_url, frontend_url = URLExtractorService.extract_urls_by_line(content)

            if backend_url:
                self.backend_url_var.set(backend_url)
            if frontend_url:
                self.frontend_url_var.set(frontend_url)

            if not backend_url and not frontend_url:
                messagebox.showinfo("提示", "未能在文件中找到管理网地址信息")

        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错: {str(e)}")

    def copy_to_clipboard(self, text):
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("复制成功", "网地址已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的网地址")

    def open_url(self, url):
        if url:
            try:
                webbrowser.open(url)
            except Exception as e:
                messagebox.showerror("错误", f"打开网地址时出错: {str(e)}")
        else:
            messagebox.showwarning("警告", "没有可打开的网地址")

    def open_webapps_directory(self):
        webapps_path = r"C:\java\apache-tomcat-9.0.106\webapps"
        try:
            if os.path.exists(webapps_path):
                subprocess.Popen(f'explorer "{webapps_path}"')
            else:
                messagebox.showerror("错误", f"目录不存在: {webapps_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {str(e)}")

    def show(self):
        self.root.wait_window()


def show_dialog(parent=None):
    window = URLExtractorWindow(parent)
    window.show()
