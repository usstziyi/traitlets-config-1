"""
============================================================
Demo 9: Subcommands —— 子命令支持
============================================================

Application 支持像 git 那样的子命令模式:

  myapp serve --port 8080
  myapp migrate --target v2
  myapp seed --count 100

实现方式:
  1. 为每个子命令创建一个 Application 子类
  2. 在主 Application 中定义 subcommands 字典
  3. 子命令自动获得自己的 --help, flags, aliases

本 demo 演示:
  - 定义子命令 Application
  - 子命令的 flags 和 aliases
  - 子命令的嵌套
  - 实际场景: 任务管理 CLI
"""

import sys
from traitlets.config import Application, Configurable
from traitlets import Int, Unicode, Bool, List


# ============================================================
# 定义一个共享的 Configurable
# ============================================================
class TaskConfig(Configurable):
    """任务配置"""
    priority = Int(1, help="默认优先级 (1-5)").tag(config=True)
    assignee = Unicode("nobody", help="默认负责人").tag(config=True)


# ============================================================
# 子命令 1: task add
# ============================================================
class AddTaskApp(Application):
    name = Unicode("add")
    description = Unicode("添加新任务")

    title = Unicode("", help="任务标题").tag(config=True)
    count = Int(1, help="添加数量").tag(config=True)

    aliases = {
        "title": "AddTaskApp.title",
        "count": "AddTaskApp.count",
    }

    flags = {
        "urgent": (
            {"TaskConfig": {"priority": 5}},
            "标记为紧急任务 (priority=5)",
        ),
    }

    def start(self):
        cfg = TaskConfig(config=self.config)
        print(f"添加 {self.count} 个任务:")
        for i in range(self.count):
            title = self.title or f"任务-{i+1}"
            print(f"  [#{i+1}] {title!r} (优先级: {cfg.priority}, 负责人: {cfg.assignee!r})")


# ============================================================
# 子命令 2: task list
# ============================================================
class ListTaskApp(Application):
    name = Unicode("list")
    description = Unicode("列出所有任务")

    filter_status = Unicode("all", help="按状态过滤").tag(config=True)
    limit = Int(20, help="最大显示数量").tag(config=True)

    aliases = {
        "status": "ListTaskApp.filter_status",
        "limit": "ListTaskApp.limit",
    }

    def start(self):
        cfg = TaskConfig(config=self.config)
        print(f"列出任务 (状态: {self.filter_status!r}, 限制: {self.limit}):")
        tasks = [
            ("修复登录页面bug", 3, "张三"),
            ("编写API文档", 2, "李四"),
            ("数据库性能优化", 4, "王五"),
            ("代码审查", 1, "赵六"),
        ]
        for title, pri, assignee in tasks[:self.limit]:
            print(f"  - {title!r} (优先级: {pri}, 负责人: {assignee})")


# ============================================================
# 主 Application: task
# ============================================================
class TaskApp(Application):
    name = Unicode("task")
    description = Unicode("任务管理 CLI 工具")
    version = "1.0.0"
    examples = """
示例:
  task add --title "修复bug" --urgent
  task add --count 3
  task list --status todo --limit 10
  task --help
"""

    classes = [TaskConfig]

    aliases = {
        "assignee": "TaskConfig.assignee",
    }

    subcommands = {
        "add": (AddTaskApp, "添加新任务"),
        "list": (ListTaskApp, "列出所有任务"),
    }

    def start(self):
        self.print_help()


# ============================================================
# 示例 2: 嵌套子命令 (更复杂的场景)
# ============================================================
class DatabaseMigrateApp(Application):
    name = Unicode("migrate")
    description = Unicode("数据库迁移")

    target = Unicode("latest", help="目标版本").tag(config=True)

    aliases = {"target": "DatabaseMigrateApp.target"}

    def start(self):
        print(f"数据库迁移到版本: {self.target!r}")


class DatabaseSeedApp(Application):
    name = Unicode("seed")
    description = Unicode("填充种子数据")

    count = Int(100, help="数据条数").tag(config=True)

    aliases = {"count": "DatabaseSeedApp.count"}

    def start(self):
        print(f"填充 {self.count} 条种子数据")


class DatabaseApp(Application):
    name = Unicode("db")
    description = Unicode("数据库管理工具")

    subcommands = {
        "migrate": (DatabaseMigrateApp, "运行数据库迁移"),
        "seed": (DatabaseSeedApp, "填充种子数据"),
    }

    def start(self):
        self.print_help()


# ============================================================
# 顶层 Application: 带嵌套子命令
# ============================================================
class MainApp(Application):
    name = Unicode("demo-cli")
    description = Unicode("演示子命令的顶层应用")
    version = "2.0.0"
    examples = """
示例:
  demo-cli task add --title "新功能" --urgent
  demo-cli task list --status todo
  demo-cli db migrate --target v2
  demo-cli db seed --count 500
"""

    subcommands = {
        "task": (TaskApp, "任务管理"),
        "db": (DatabaseApp, "数据库管理"),
    }

    def start(self):
        self.print_help()


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("=" * 60)
        print("Demo 9: Subcommands")
        print("=" * 60)
        print()
        print("本 demo 演示子命令功能. 请尝试:")
        print()
        print("  # 查看顶层帮助")
        print("  python 09_subcommands.py --help")
        print()
        print("  # 添加任务")
        print("  python 09_subcommands.py task add --title \"修复登录bug\" --urgent")
        print()
        print("  # 添加多个任务")
        print("  python 09_subcommands.py task add --count 3 --assignee 张三")
        print()
        print("  # 列出任务")
        print("  python 09_subcommands.py task list --status=done --limit=5")
        print()
        print("  # 数据库子命令")
        print("  python 09_subcommands.py db migrate --target v3.0")
        print("  python 09_subcommands.py db seed --count 1000")
        print()
    else:
        MainApp.launch_instance()
