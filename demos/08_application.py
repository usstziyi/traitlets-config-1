"""
============================================================
Demo 8: Application 类 —— 程序入口点
============================================================

Application 是 traitlets.config 的终极抽象，它是:
  1. SingletonConfigurable (单例)
  2. 自动解析命令行参数
  3. 自动加载配置文件 (Python + JSON)
  4. 自动设置日志系统
  5. 提供 --help / --help-all / --generate-config / --show-config

Application 的生命周期:
  launch_instance(argv)
    -> initialize(argv)
      -> parse_command_line(argv)   # 解析 CLI
      -> load_config_file(...)      # 加载配置文件
      -> init_logging()             # 初始化日志
    -> start()                      # 用户定义的业务逻辑

本 demo 演示:
  - 编写一个最简应用
  - Application 的各个钩子方法
  - 日志系统
  - --generate-config 生成配置模板
  - 多个 Application 协作
"""

import sys
import os
from traitlets.config import Application, Configurable
from traitlets import Int, Unicode, Bool, List


# ============================================================
# 示例 1: 最简的 Application
# ============================================================
class HelloApp(Application):
    name = Unicode("hello-app")
    description = Unicode("最简 traitlets.config Application 示例")
    version = "1.0.0"

    def start(self):
        print("Hello from HelloApp!")
    

# print("HelloApp.class_traits():")
# for name, trait in HelloApp.class_traits().items():
#     print(f"  {name:20s} {trait.__class__.__name__}")
# print()
# print("HelloApp.class_own_traits():")
# for name, trait in HelloApp.class_own_traits().items():
#     print(f"  {name:20s} {trait.__class__.__name__}")


if len(sys.argv) > 1 and sys.argv[1] == "--run-hello":
    print("=" * 60)
    print("示例 1: 最简 Application")
    print("=" * 60)
    # 它内部会完成完整的生命周期： 解析 CLI → 加载配置文件 → 初始化日志 → 调用 start()
    HelloApp.launch_instance(sys.argv[2:] if len(sys.argv) > 2 else [])
    

# ============================================================
# 示例 2: 带 Configurable 的 Application
# ============================================================
class ReportConfig(Configurable):
    """报告生成配置"""
    title = Unicode("日报", help="报告标题").tag(config=True)
    output_dir = Unicode("./output", help="输出目录").tag(config=True)
    max_items = Int(100, help="最大条目数").tag(config=True)
    enable_html = Bool(True, help="生成 HTML 报告").tag(config=True)
    enable_pdf = Bool(False, help="生成 PDF 报告").tag(config=True)


class ReportApp(Application):
    name = Unicode("report-app")
    description = Unicode("报告生成应用 - 演示带 Configurable 的 Application")

    classes = [ReportConfig]

    # 应用级配置
    verbose = Bool(False, help="详细输出").tag(config=True)
    input_file = Unicode("", help="输入文件路径").tag(config=True)

    aliases = {
        "input": "ReportApp.input_file",
        "output": "ReportConfig.output_dir",
        "title": "ReportConfig.title",
    }
    flags = {
        "verbose": ({"ReportApp": {"verbose": True}}, "启用详细输出"),
        "html": ({"ReportConfig": {"enable_html": True}}, "生成 HTML"),
        "pdf": ({"ReportConfig": {"enable_pdf": True}}, "生成 PDF"),
    }

    def start(self):
        report = ReportConfig(config=self.config)

        print(f"\n报告配置:")
        print(f"  标题:     {report.title!r}")
        print(f"  输出目录: {report.output_dir!r}")
        print(f"  最大条目: {report.max_items}")
        print(f"  HTML:     {report.enable_html}")
        print(f"  PDF:      {report.enable_pdf}")

        if self.verbose:
            print(f"  [verbose] 输入文件: {self.input_file!r}")

        print(f"\n报告生成完毕!")


if len(sys.argv) > 1 and sys.argv[1] == "--run-report":
    print("=" * 60)
    print("示例 2: 带 Configurable 的 Application")
    print("=" * 60)
    ReportApp.launch_instance(sys.argv[2:] if len(sys.argv) > 2 else [])
    print()

# uv run python demos/08_application.py --run-report  --input main.c --verbose

# ============================================================
# 无参数时显示使用说明
# ============================================================
if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ("--run-hello", "--run-report")):
    print("=" * 60)
    print("Demo 8: Application 类")
    print("=" * 60)
    print()
    print("本 demo 包含两个子场景。使用方式:")
    print()
    print("  场景 1 - 最简应用:")
    print("    python 08_application.py --run-hello")
    print("    python 08_application.py --run-hello --help")
    print()
    print("  场景 2 - 带 Configurable 的应用:")
    print("    python 08_application.py --run-report --title='周报' --output=./reports --html --pdf")
    print("    python 08_application.py --run-report --help")
    print("    python 08_application.py --run-report --help-all")
    print("    python 08_application.py --run-report --generate-config")
    print()
    print(">>> Demo 8 准备就绪: 请用上面命令运行")
