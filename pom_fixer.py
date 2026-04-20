import os
import re


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
        count = 0
        current_dir = os.getcwd()

        for root, dirs, files in os.walk(current_dir):
            dirs[:] = [d for d in dirs if d not in PomFixer.SKIP_DIRS and not d.startswith('.')]

            if 'pom.xml' in files:
                path = os.path.join(root, 'pom.xml')
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                regex = re.compile(r'<(maven.compiler.source|maven.compiler.target)>(.*?)</\1>', re.IGNORECASE)

                def replace_func(match):
                    nonlocal count
                    version_str = match.group(2)
                    try:
                        version = float(version_str)
                        if version < 1.8:
                            count += 1
                            return f"<{match.group(1)}>1.8</{match.group(1)}>"
                    except ValueError:
                        pass
                    return match.group(0)

                new_content = regex.sub(replace_func, content)

                if content != new_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

        return f"🎉 已优化 {count // 2} 个项目的版本配置。"
