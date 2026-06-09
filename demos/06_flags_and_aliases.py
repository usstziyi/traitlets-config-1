"""
============================================================
Demo 6: 命令行参数 —— Flags 与 Aliases
============================================================

Application 支持解析命令行参数, 有两种简化方式:

  Flags (开关):
    - 布尔型: --debug / --no-debug
    - 字典定义: {"FlagName": ({"Class": {"trait": value}}, "help")}

  Aliases (别名):
    - 将 --alias-name 映射到 --Class.trait
    - 字典定义: {"alias": "Class.trait"}

  参数格式:
    --Class.trait=value   (完整形式)
    --alias value         (使用别名)
    --flag                (使用开关)

本 demo 演示:
  - flags 和 aliases 的定义
  - --generate-config 生成配置模板
  - --help 查看帮助
  - --show-config 查看当前配置
"""

import sys
from traitlets.config import Application, Configurable
from traitlets import Int, Unicode, Bool, Float, List, default


class Worker(Configurable):
    name = Unicode("worker-001", help="Worker 名称").tag(config=True)
    threads = Int(4, help="工作线程数").tag(config=True)
    verbose = Bool(False, help="详细输出").tag(config=True)


class WorkerApp(Application):
    name = Unicode("worker-app")
    description = Unicode("一个演示 flags 和 aliases 的 Worker 应用")
    version = "1.0.0"
    examples = """
使用示例:
  python 06_flags_and_aliases.py --worker-name myworker --threads 8
  python 06_flags_and_aliases.py --verbose --threads 2
  python 06_flags_and_aliases.py --help
  python 06_flags_and_aliases.py --generate-config
"""

    classes = [Worker]

    # ---- Flags: 布尔开关 ----
    flags = {
        "verbose": (
            {"WorkerApp": {"log_level": 10}, "Worker": {"verbose": True}},
            "启用详细日志输出",
        ),
        "debug": (
            {"Worker": {"verbose": True}, "WorkerApp": {"log_level": 10}},
            "启用调试模式 (等同于 --verbose --log-level=DEBUG)",
        ),
    }

    # ---- Aliases: 参数别名 ----
    aliases = {
        "worker-name": "Worker.name",
        "threads": "Worker.threads",
        ("w", "worker-name-short"): "Worker.name",
        ("t", "threads-short"): "Worker.threads",
    }

    def start(self):
        worker = Worker(config=self.config)
        print(f"\nWorker 已启动:")
        print(f"  name    = {worker.name!r}")
        print(f"  threads = {worker.threads}")
        print(f"  verbose = {worker.verbose}")


if __name__ == "__main__":
    # 演示不同的命令行参数场景
    if len(sys.argv) > 1:
        WorkerApp.launch_instance()
    else:
        print("=" * 60)
        print("Demo 6: Flags 与 Aliases")
        print("=" * 60)
        print()
        print("本 demo 需要命令行参数. 请尝试以下命令:")
        print()
        print("  # 查看帮助")
        print("  python 06_flags_and_aliases.py --help")
        print()
        print("  # 查看所有配置项帮助")
        print("  python 06_flags_and_aliases.py --help-all")
        print()
        print("  # 使用别名")
        print("  python 06_flags_and_aliases.py --worker-name myworker --threads 8")
        print()
        print("  # 使用 flag")
        print("  python 06_flags_and_aliases.py --verbose")
        print()
        print("  # 使用完整路径")
        print("  python 06_flags_and_aliases.py --Worker.name custom --Worker.threads 16")
        print()
        print("  # 生成配置文件模板")
        print("  python 06_flags_and_aliases.py --generate-config")
        print()
        print("  # 显示当前配置")
        print("  python 06_flags_and_aliases.py --show-config")
        print()
        print(">>> Demo 6 准备就绪: 请用命令行参数运行上述命令")
