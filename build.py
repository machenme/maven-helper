import PyInstaller.__main__
import shutil
import os

def build_exe():
    # 定义打包参数
    opts = [
        'main.py',                  # 主文件
        '--onefile',               # 打包成单文件
        '--windowed',              # 不显示控制台（GUI程序）
        '--name=MavenHelper',      # 程序名称
        '--add-data=data;data',    # 附加数据 (Windows 格式: "源;目标")
    ]
    
    # 添加所有 apache-maven*.zip 文件
    for name in os.listdir('.'):
        if name.startswith('apache-maven') and name.endswith('.zip'):
            opts.append(f'--add-data={name};.')
    
    # 添加所有 apache-tomcat*.zip 文件
    for name in os.listdir('.'):
        if name.startswith('apache-tomcat') and name.endswith('.zip'):
            opts.append(f'--add-data={name};.')

    print(f"开始打包 [MavenHelper]...")
    
    # 调用 PyInstaller
    PyInstaller.__main__.run(opts)
    
    print("\n打包完成！EXE 文件位于 dist 目录中。")

if __name__ == "__main__":
    build_exe()