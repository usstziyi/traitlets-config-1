"""
============================================================
config.py —— Configurable 配置类

定义文件处理流水线中每一步的配置:
  - ReadConfig:    输入源配置
  - TransformConfig: 转换链配置
  - OutputConfig:  输出目标配置

所有可配置项都用 tag(config=True) 标记, 支持:
  - 命令行参数 --Class.trait=value
  - 配置文件 c.Class.trait = value
  - Config 对象注入
"""

import os
from traitlets.config import Configurable
from traitlets import (
    Unicode, Int, Bool, List, Enum, validate, TraitError,
    default,
)

# 支持的转换操作
TRANSFORMS = ["upper", "lower", "capitalize", "title", "reverse", "strip"]


class ReadConfig(Configurable):
    """输入源配置 —— 控制从哪里读取文件"""

    input_dir = Unicode(
        ".", help="输入目录路径"
    ).tag(config=True)

    file_pattern = Unicode(
        "*.txt", help="文件匹配模式 (glob, e.g. *.txt, *.md, *.*)"
    ).tag(config=True)

    encoding = Unicode(
        "utf-8", help="文件编码"
    ).tag(config=True)

    exclude_pattern = Unicode(
        "", help="排除文件模式 (glob)"
    ).tag(config=True)

    @validate("input_dir")
    def _valid_input_dir(self, proposal):
        path = proposal["value"]
        if path and not os.path.isdir(path):
            raise TraitError(f"输入目录不存在: {path}")
        return path


class TransformConfig(Configurable):
    """转换配置 —— 定义对文件内容执行哪些转换操作"""

    transforms = List(
        trait=Enum(TRANSFORMS),
        default_value=["capitalize"],
        help="转换操作链, 可多选: " + ", ".join(TRANSFORMS),
    ).tag(config=True)

    add_line_numbers = Bool(
        False, help="是否添加行号"
    ).tag(config=True)

    grep_filter = Unicode(
        "", help="grep 过滤关键词 (空表示不过滤)"
    ).tag(config=True)

    grep_case_sensitive = Bool(
        True, help="grep 是否区分大小写"
    ).tag(config=True)

    line_range_start = Int(
        0, help="起始行号 (0=不限制)"
    ).tag(config=True)

    line_range_end = Int(
        0, help="结束行号 (0=不限制)"
    ).tag(config=True)

    @validate("transforms")
    def _valid_transforms(self, proposal):
        value = proposal["value"]
        invalid = [t for t in value if t not in TRANSFORMS]
        if invalid:
            raise TraitError(
                f"不支持的转换: {invalid}. 可用: {TRANSFORMS}"
            )
        return value


class OutputConfig(Configurable):
    """输出配置 —— 控制处理结果写到哪里"""

    output_dir = Unicode(
        "./output", help="输出目录路径"
    ).tag(config=True)

    output_prefix = Unicode(
        "processed_", help="输出文件名前缀"
    ).tag(config=True)

    dry_run = Bool(
        False, help="演练模式: 只显示将执行的操作, 不写入文件"
    ).tag(config=True)

    overwrite = Bool(
        False, help="是否覆盖已有输出文件"
    ).tag(config=True)

    verbose = Bool(
        False, help="详细输出模式"
    ).tag(config=True)
