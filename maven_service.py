import os
import zipfile
import winreg
import sys
import shutil


class MavenService:
    @staticmethod
    def setup():
        # 处理 PyInstaller 打包后的路径
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
            run_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            run_dir = base_dir
        
        try:
            maven_dir = None
            tomcat_dir = None
            
            for name in os.listdir(run_dir):
                if name.startswith("apache-maven") and os.path.isdir(os.path.join(run_dir, name)):
                    old_dir = os.path.join(run_dir, name)
                    shutil.rmtree(old_dir)
                if name.startswith("apache-tomcat") and os.path.isdir(os.path.join(run_dir, name)):
                    old_dir = os.path.join(run_dir, name)
                    shutil.rmtree(old_dir)
            
            zip_path = None
            for name in os.listdir(base_dir):
                if name.startswith("apache-maven") and name.endswith(".zip") and os.path.isfile(os.path.join(base_dir, name)):
                    zip_path = os.path.join(base_dir, name)
                    break
            
            if zip_path and os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(run_dir)
                
                for name in os.listdir(run_dir):
                    if name.startswith("apache-maven") and os.path.isdir(os.path.join(run_dir, name)):
                        maven_dir = os.path.join(run_dir, name)
                        break
            
            tomcat_zip_path = None
            for name in os.listdir(base_dir):
                if name.startswith("apache-tomcat") and name.endswith(".zip") and os.path.isfile(os.path.join(base_dir, name)):
                    tomcat_zip_path = os.path.join(base_dir, name)
                    break
            
            if tomcat_zip_path and os.path.exists(tomcat_zip_path):
                with zipfile.ZipFile(tomcat_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(run_dir)
                
                for name in os.listdir(run_dir):
                    if name.startswith("apache-tomcat") and os.path.isdir(os.path.join(run_dir, name)):
                        tomcat_dir = os.path.join(run_dir, name)
                        break
            
            if not maven_dir:
                return "❌ 错误：未能提取或识别 Maven 目录。"
            
            custom_settings = os.path.join(base_dir, "data", "maven_settings.xml")
            target_settings = os.path.join(maven_dir, "conf", "settings.xml")
            if os.path.exists(custom_settings):
                shutil.copyfile(custom_settings, target_settings)
            
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"System\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "MAVEN_HOME", 0, winreg.REG_SZ, maven_dir)
                winreg.CloseKey(key)
                
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"System\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
                old_path, _ = winreg.QueryValueEx(key, "Path")
                winreg.CloseKey(key)
                
                maven_path_entry = r"%MAVEN_HOME%\bin"
                path_parts = old_path.split(';')
                
                if maven_path_entry not in [p.strip() for p in path_parts]:
                    new_path = maven_path_entry + ";" + old_path
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"System\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    winreg.CloseKey(key)
            
            except PermissionError:
                return "❌ 权限不足：请确保以管理员身份运行此程序。"
            
            result_msg = f"✅ 成功！\n已部署 Maven 至: {maven_dir}\n环境变量已配置完成。"
            if tomcat_dir:
                result_msg += f"\n已部署 Tomcat 至: {tomcat_dir}"
            
            return result_msg
        
        except Exception as ex:
            return f"❌ 发生错误：{str(ex)}"
