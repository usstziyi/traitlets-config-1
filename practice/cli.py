"""
============================================================
cli.py —— 文件处理器 CLI 入口

============================================================
项目概述
============================================================

这是一个基于 traitlets.config 实现的文件批处理命令行工具, 演示了
Configurable 和 Application 的完整实战用法。

功能:
  - 读取指定目录下的文本文件
  - 应用转换链 (upper, lower, capitalize, title, reverse, strip)
  - 支持 grep 行过滤
  - 支持行范围和行号
  - 输出处理结果到指定目录

架构设计:
  config.py        —— Configurable 配置类 (ReadConfig, TransformConfig, OutputConfig)
  processors.py    —— 纯处理逻辑 (独立于配置系统)
  cli.py           —— Application 入口 + 子命令

使用方式:
  # 处理文件 (多个转换用多次 --transforms)
  file-processor process --input ./data --transforms upper --transforms capitalize

  # 演练模式
  file-processor process --input ./data --transforms strip --dry-run --verbose

  # 使用 grep 过滤
  file-processor process --input ./data --grep-filter "ERROR" --output ./errors

  # 列出可用文件
  file-processor list --input ./data --pattern "*.log"

  # 生成配置文件
  file-processor process --generate-config

  # 使用配置文件
  file-processor process --config-file myconfig.py

============================================================
"""

import os
import sys
import logging

from traitlets.config import Application, Configurable, Config
from traitlets import Unicode, Bool, Int, List, validate, TraitError

try:
    from .config import ReadConfig, TransformConfig, OutputConfig
    from .processors import pipeline, collect_files, get_stats
except ImportError:
    from config import ReadConfig, TransformConfig, OutputConfig
    from processors import pipeline, collect_files, get_stats

logger = logging.getLogger(__name__)


# ============================================================
# 子命令: process —— 执行文件处理流水线
# ============================================================
class ProcessApp(Application):
    """执行文件处理流水线"""

    name = Unicode("process")
    description = Unicode("读取文件 -> 转换 -> 过滤 -> 输出")
    examples = """
示例:
  file-processor process --input ./data --transforms upper --transforms capitalize
  file-processor process --input ./data --transforms strip --dry-run --verbose
  file-processor process --input ./logs --grep-filter ERROR --grep-case-insensitive
  file-processor process --input ./data --transforms reverse --output ./reversed
  file-processor process --generate-config > file_processor_config.py
"""

    # 按需暴露（最小权限原则）,全部三个配置类都需要暴露
    classes = [ReadConfig, TransformConfig, OutputConfig]

    # ---- Aliases: 简化常用参数 ----
    aliases = {
        "input": "ReadConfig.input_dir",
        "encoding": "ReadConfig.encoding",
        "pattern": "ReadConfig.file_pattern",
        "exclude": "ReadConfig.exclude_pattern",
        "transforms": "TransformConfig.transforms",
        "grep-filter": "TransformConfig.grep_filter",
        "output": "OutputConfig.output_dir",
        "prefix": "OutputConfig.output_prefix",
    }

    # ---- Flags: 布尔开关 ----
    flags = {
        "dry-run": (
            {"OutputConfig": {"dry_run": True}},
            "演练模式: 只预览, 不写入文件",
        ),
        # OutputConfig.verbose 是 业务配置 ——它可以写在配置文件里，比如始终开启详细输出
        # log_level 是 日志系统配置 ——它控制的是日志基础设施的级别，独立于业务逻辑
        "verbose": (
            {"ProcessApp": {"log_level": logging.INFO}, "OutputConfig": {"verbose": True}},
            "详细输出",
        ),
        "overwrite": (
            {"OutputConfig": {"overwrite": True}},
            "覆盖已有输出文件",
        ),
        "line-numbers": (
            {"TransformConfig": {"add_line_numbers": True}},
            "为每行添加行号",
        ),
        "grep-case-insensitive": (
            {"TransformConfig": {"grep_case_sensitive": False}},
            "grep 过滤不区分大小写",
        ),
        "debug": (
            {"ProcessApp": {"log_level": logging.DEBUG}},
            "调试模式 (最详细输出)",
        ),
    }

    def start(self):
        """运行文件处理流水线"""
        read_cfg = ReadConfig(config=self.config)
        transform_cfg = TransformConfig(config=self.config)
        output_cfg = OutputConfig(config=self.config)

        logger.info("=== 文件处理器 ===")
        logger.info("输入目录: %s", read_cfg.input_dir)
        logger.info("文件模式: %s", read_cfg.file_pattern)
        logger.info("转换操作: %s", transform_cfg.transforms or "(无)")

        # 这一行是整个 ProcessApp 的 核心执行点 ——把配置注入纯业务逻辑 pipeline
        results = pipeline(read_cfg, transform_cfg, output_cfg)

        if not results:
            print(f"\n未找到匹配的文件 (目录: {read_cfg.input_dir!r}, "
                  f"模式: {read_cfg.file_pattern!r})")
            return

        # 打印结果摘要
        print(f"\n处理完成! 共 {len(results)} 个文件:\n")
        print(f"{'输入文件':<30} {'输入行':>6} {'输出行':>6} {'操作':<30} {'状态'}")
        print("-" * 85)

        for r in results:
            fname = os.path.basename(r["file"])
            if len(fname) > 28:
                fname = fname[:25] + "..."

            transforms_str = ",".join(r.get("transforms", []))
            if len(transforms_str) > 28:
                transforms_str = transforms_str[:25] + "..."

            if r.get("skipped"):
                status = "跳过 (已存在)"
            elif r.get("dry_run"):
                status = "演练 (未写入)"
            else:
                status = "已写入"

            print(
                f"  {fname:<28} {r['lines_in']:>6} {r['lines_out']:>6} "
                f"{transforms_str:<30} {status}"
            )

        stats = get_stats(results)
        print(f"\n统计: {stats['files']} 个文件, "
              f"输入 {stats['total_lines_in']} 行, "
              f"输出 {stats['total_lines_out']} 行")

        if stats["skipped"]:
            print(f"  (其中 {stats['skipped']} 个被跳过, "
                  f"{stats['dry_run']} 个为演练)")


# ============================================================
# 子命令: list —— 列出可用文件
# ============================================================
class ListApp(Application):
    """列出输入目录中匹配的文件"""

    name = Unicode("list")
    description = Unicode("列出输入目录中匹配的文件及相关信息")
    examples = """
示例:
  file-processor list --input ./data
  file-processor list --input ./logs --pattern "*.log"
  file-processor list --input ./data --pattern "*.txt" --exclude "test_*"
"""

    # 按需暴露（最小权限原则）,只需要读文件配置
    classes = [ReadConfig]

    aliases = {
        "input": "ReadConfig.input_dir",
        "pattern": "ReadConfig.file_pattern",
        "exclude": "ReadConfig.exclude_pattern",
    }

    def start(self):
        read_cfg = ReadConfig(config=self.config)

        print(f"\n扫描目录: {read_cfg.input_dir!r}")
        print(f"文件模式: {read_cfg.file_pattern!r}")
        if read_cfg.exclude_pattern:
            print(f"排除模式: {read_cfg.exclude_pattern!r}")
        print()

        files = collect_files(read_cfg)

        if not files:
            print("  未找到匹配的文件")
            return

        total_lines = 0
        total_size = 0
        for f in files:
            try:
                size = os.path.getsize(f)
                total_size += size
                with open(f, "r", encoding=read_cfg.encoding) as fh:
                    line_count = sum(1 for _ in fh)
                total_lines += line_count
                print(f"  {f.name:<40} {line_count:>6} 行  {size:>8} bytes")
            except Exception as e:
                print(f"  {f.name:<40} {'ERROR':>6}     {e!s}")

        print(f"\n  共 {len(files)} 个文件, {total_lines} 行, "
              f"{total_size} bytes")


# ============================================================
# 子命令: stats —— 统计信息
# ============================================================
class StatsApp(Application):
    """显示文件和处理的统计信息"""

    name = Unicode("stats")
    description = Unicode("显示文件统计信息")
    examples = """
示例:
  file-processor stats --input ./data
  file-processor stats --input ./logs --pattern "*.log"
"""

    # 按需暴露（最小权限原则）,只需要读文件配置
    classes = [ReadConfig]

    aliases = {
        "input": "ReadConfig.input_dir",
        "pattern": "ReadConfig.file_pattern",
    }

    def start(self):
        read_cfg = ReadConfig(config=self.config)
        files = collect_files(read_cfg)

        if not files:
            print(f"\n未找到匹配的文件 ({read_cfg.input_dir!r}, {read_cfg.file_pattern!r})")
            return

        extensions = {}
        total_size = 0
        total_lines = 0

        print(f"\n文件统计 - 目录: {read_cfg.input_dir!r}")
        print(f"{'扩展名':<12} {'数量':>6} {'总行数':>8} {'总大小':>10}")
        print("-" * 40)

        for f in files:
            ext = f.suffix or "(无)"
            size = os.path.getsize(f)
            total_size += size
            try:
                with open(f, "r", encoding=read_cfg.encoding) as fh:
                    lines = sum(1 for _ in fh)
            except Exception:
                lines = 0
            total_lines += lines

            if ext not in extensions:
                extensions[ext] = {"count": 0, "lines": 0, "size": 0}
            extensions[ext]["count"] += 1
            extensions[ext]["lines"] += lines
            extensions[ext]["size"] += size

        for ext, info in sorted(extensions.items()):
            print(f"  {ext:<10} {info['count']:>6} {info['lines']:>8} {info['size']:>10}")

        print("-" * 40)
        print(f"  {'合计':<10} {len(files):>6} {total_lines:>8} {total_size:>10}")


# ============================================================
# 主 Application: file-processor
# ============================================================
class FileProcessorApp(Application):
    """文件批处理 CLI 工具 —— traitlets.config 实战项目

    功能:
      - 读取指定目录下的文本文件
      - 应用多种转换操作 (upper, lower, capitalize, title, reverse, strip)
      - 支持 grep 行过滤
      - 支持行范围截取和行号添加
      - 支持 Python/JSON 配置文件
    """

    name = Unicode("file-processor")
    description = Unicode(__doc__ or "文件批处理 CLI 工具")
    version = "1.0.0"
    examples = """
使用示例:

  # 列出可用文件
  file-processor list --input ./data --pattern "*.txt"

  # 查看文件统计
  file-processor stats --input ./data

  # 处理文件 (大写 + 首字母大写)
  file-processor process --input ./data --transforms upper --transforms capitalize

  # 演练模式 (预览效果)
  file-processor process --input ./data --transforms strip --dry-run --verbose

  # grep 过滤 + 行号
  file-processor process --input ./logs --grep-filter ERROR  \\
      --grep-case-insensitive --line-numbers --output ./errors

  # 生成配置文件
  file-processor process --generate-config > myconfig.py

  # 使用配置文件
  file-processor process --config-file myconfig.py

  # 查看帮助
  file-processor --help
  file-processor process --help
"""

    # 按需暴露（最小权限原则）,父级本身不处理业务逻辑
    # classes = []

    subcommands = {
        "process": (ProcessApp, "执行文件处理流水线"),
        "list": (ListApp, "列出输入目录中匹配的文件"),
        "stats": (StatsApp, "显示文件统计信息"),
    }

    show_version = Bool(False).tag(config=True)

    # 顶层 flags
    flags = {
        "version": (
            {"FileProcessorApp": {"show_version": True}},
            "显示版本号",
        ),
    }

    def start(self):
        # 如果有子应用，就转发给子应用的 start()
        if self.subapp is not None:
            return self.subapp.start()
        if self.show_version:
            print(f"file-processor v{self.version}")
        else:
            self.print_help()


# ============================================================
# 程序入口
# ============================================================
def main():
    """程序入口函数, 供 pyproject.toml 中的 [project.scripts] 使用"""
    FileProcessorApp.launch_instance()


if __name__ == "__main__":
    main()


"""
┌─────────────────────────────────────────────────┐
│  cli.py (Application 层)                         │
│  ┌───────────┐ ┌──────────┐ ┌───────────────┐   │
│  │ProcessApp │ │ ListApp  │ │FileProcessorApp│   │
│  │classes=[  │ │classes=  │ │ subcommands=  │   │
│  │  Read,    │ │ [Read]   │ │  {process,    │   │
│  │  Transform│ │          │ │   list, stats} │   │
│  │  Output]  │ │          │ │               │   │
│  └─────┬─────┘ └────┬─────┘ └───────┬───────┘   │
│        │            │               │            │
│   wires CLI args → Config objects   │            │
│        │            │               │            │
├────────┼────────────┼───────────────┼────────────┤
│ config.py (Configurable 层)          │            │
│  ReadConfig / TransformConfig / OutputConfig     │
│  定义"什么可以被配置" + 验证规则                  │
│        │                                         │
├────────┼─────────────────────────────────────────┤
│ processors.py (纯逻辑层)                          │
│  collect_files / pipeline / apply_transform ...  │
│  接收 Config 对象 → 执行纯业务逻辑                │
└─────────────────────────────────────────────────┘
"""