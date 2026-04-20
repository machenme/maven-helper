# Maven Helper

一个基于 Python 的 Maven 开发辅助工具，提供 Maven 配置、POM 优化、SQL 执行和 Java 环境管理等功能。

## 功能特性

- **配置 Maven** - 自动解压并配置 Apache Maven，替换 settings.xml 配置文件
- **配置 Tomcat** - 自动解压并配置 Apache Tomcat
- **优化 POM** - 优化 Maven 项目的 pom.xml 文件
- **执行 SQL** - 自动检测并执行 SQL 文件，支持数据库自动创建
- **检查 Java** - 检测 Java 环境，支持 Java 8/11 下载安装，可调整多个 Java 版本在 PATH 中的顺序

## 环境要求

- Windows 操作系统

## 使用方法

1. 安装依赖：
   ```bash
   uv sync
   ```

2. 运行程序：
   ```bash
   uv run main.py
   ```

## 打包

使用 PyInstaller 打包为单文件可执行程序：

```bash
uv run build.py
```

打包后的文件位于 `dist/MavenHelper.exe`

## 文件结构

```
maven-helper/
├── main.py              # 主程序入口
├── main_window.py       # 主窗口界面
├── maven_service.py     # Maven/Tomcat 配置服务
├── pom_fixer.py         # POM 优化模块
├── deal_sql.py          # SQL 执行服务
├── java_service.py      # Java 环境管理服务
├── build.py             # PyInstaller 打包脚本
├── data/                # 数据文件目录
│   ├── maven_settings.xml  # Maven 配置模板
├── apache-maven-*.zip   # Maven 压缩包
└── apache-tomcat-*.zip  # Tomcat 压缩包
```
