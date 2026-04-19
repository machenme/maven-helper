import tkinter as tk
from tkinter import messagebox
from maven_service import MavenService
from pom_fixer import PomFixer
from deal_sql import DealSQLService


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Maven Helper")
        self.root.geometry("800x450")
        
        self.setup_ui()
    
    def setup_ui(self):
        button1 = tk.Button(
            self.root,
            text="配置 Maven",
            font=("Microsoft YaHei UI", 16),
            width=12,
            height=3,
            command=self.on_button1_click
        )
        button1.place(x=12, y=12)
        
        button2 = tk.Button(
            self.root,
            text="优化 POM",
            font=("Microsoft YaHei UI", 16),
            width=12,
            height=3,
            command=self.on_button2_click
        )
        button2.place(x=195, y=12)
        
        button3 = tk.Button(
            self.root,
            text="执行 SQL",
            font=("Microsoft YaHei UI", 16),
            width=12,
            height=3,
            command=self.on_button3_click
        )
        button3.place(x=378, y=12)
    
    def on_button1_click(self):
        result = MavenService.setup()
        messagebox.showinfo("结果", result)
    
    def on_button2_click(self):
        result = PomFixer.fix()
        messagebox.showinfo("结果", result)
    
    def on_button3_click(self):
        result = DealSQLService.deal()
        messagebox.showinfo("结果", result)
    
    def run(self):
        self.root.mainloop()
