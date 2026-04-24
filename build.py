import PyInstaller.__main__
import shutil
import os


def build_exe():
    opts = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=MavenHelper',
        '--add-data=data;data',
        '--hidden-import=psutil',
        '--hidden-import=pymysql',
    ]

    for name in os.listdir('.'):
        if name.startswith('apache-maven') and name.endswith('.zip'):
            opts.append(f'--add-data={name};.')

    for name in os.listdir('.'):
        if name.startswith('apache-tomcat') and name.endswith('.zip'):
            opts.append(f'--add-data={name};.')

    print(f"开始打包 [MavenHelper]...")

    PyInstaller.__main__.run(opts)

    print("\n打包完成！EXE 文件位于 dist 目录中。")


if __name__ == "__main__":
    build_exe()
