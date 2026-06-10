"""
============================================================
processors.py —— 数据处理逻辑

这是纯业务逻辑模块，独立于配置系统之外。
每条处理函数接收数据和当前状态，返回处理结果和状态更新。
"""

import os
import glob
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def collect_files(read_cfg):
    """
    收集匹配的输入文件

    参数:
        read_cfg: ReadConfig 实例

    返回:
        list[Path]: 匹配的文件路径列表
    """
    input_dir = read_cfg.input_dir or "."
    pattern = read_cfg.file_pattern
    exclude = read_cfg.exclude_pattern

    search_path = os.path.join(input_dir, pattern)
    files = [Path(p) for p in glob.glob(search_path, recursive=False)]

    if exclude:
        exclude_path = os.path.join(input_dir, exclude)
        excluded = set(Path(p) for p in glob.glob(exclude_path, recursive=False))
        files = [f for f in files if f not in excluded]

    files.sort()
    return files


def read_file(file_path, encoding="utf-8"):
    """
    读取文件内容

    返回:
        list[str]: 按行分割的文件内容
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read().splitlines()


def write_file(file_path, lines, encoding="utf-8"):
    """将行列表写入文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding=encoding) as f:
        f.write("\n".join(lines))
        f.write("\n")


def apply_transform(lines, transform_name):
    """对行列表应用单个转换"""
    tf = transform_name.lower()
    if tf == "upper":
        return [line.upper() for line in lines]
    elif tf == "lower":
        return [line.lower() for line in lines]
    elif tf == "capitalize":
        return [line.capitalize() for line in lines]
    elif tf == "title":
        return [line.title() for line in lines]
    elif tf == "reverse":
        return [line[::-1] for line in lines]
    elif tf == "strip":
        return [line.strip() for line in lines]
    else:
        raise ValueError(f"未知转换: {transform_name}")


def apply_transforms_chain(lines, transforms):
    """依次应用多个转换"""
    result = lines
    for tf in transforms:
        result = apply_transform(result, tf)
    return result


def apply_grep_filter(lines, keyword, case_sensitive=True):
    """按关键词过滤行"""
    if not keyword:
        return lines
    if case_sensitive:
        return [line for line in lines if keyword in line]
    else:
        keyword_lower = keyword.lower()
        return [line for line in lines if keyword_lower in line.lower()]


def apply_line_range(lines, start, end):
    """截取行范围"""
    if start > 0:
        lines = lines[start - 1:]
    if end > 0:
        lines = lines[:end]
    return lines


def add_line_numbers_to_lines(lines):
    """为每行添加行号"""
    width = len(str(len(lines)))
    return [f"{i:0{width}d}| {line}" for i, line in enumerate(lines, 1)]

# processors.py 刻意 没有 import config.py 中的类，
# 这是一个有意的架构选择——保持纯逻辑模块对配置系统的 零依赖
# 尽管没有类型注解， pipeline 内部通过 鸭子类型 访问它们。
# 每个 trait 通过 traitlets 的元类机制，被代理为普通的 Python 类型
# 这正是 traitlets 的设计： 声明时用类型约束，访问时像普通属性 。
def pipeline(read_cfg, transform_cfg, output_cfg):
    """
    执行完整的处理流水线

    返回:
        list[dict]: 每个文件的处理结果摘要
    """
    results = []

    files = collect_files(read_cfg)
    if not files:
        logger.warning("未找到匹配的文件: %s", read_cfg.file_pattern)
        return results

    for file_path in files:
        entry = {
            "file": str(file_path),
            "lines_in": 0,
            "lines_out": 0,
            "transforms": [],
        }

        if output_cfg.verbose:
            logger.info("处理文件: %s", file_path)

        lines = read_file(file_path, encoding=read_cfg.encoding)
        entry["lines_in"] = len(lines)

        # 应用转换链
        lines = apply_transforms_chain(lines, transform_cfg.transforms)
        entry["transforms"] = list(transform_cfg.transforms)

        # 应用 grep 过滤
        if transform_cfg.grep_filter:
            before = len(lines)
            lines = apply_grep_filter(
                lines,
                transform_cfg.grep_filter,
                transform_cfg.grep_case_sensitive,
            )
            entry["grep_before"] = before
            entry["grep_after"] = len(lines)

        # 应用行范围
        if transform_cfg.line_range_start or transform_cfg.line_range_end:
            lines = apply_line_range(
                lines,
                transform_cfg.line_range_start,
                transform_cfg.line_range_end,
            )

        # 添加行号
        if transform_cfg.add_line_numbers:
            lines = add_line_numbers_to_lines(lines)

        entry["lines_out"] = len(lines)

        # 输出
        if not output_cfg.dry_run:
            out_name = output_cfg.output_prefix + file_path.name
            out_path = os.path.join(output_cfg.output_dir, out_name)

            if not output_cfg.overwrite and os.path.exists(out_path):
                logger.warning("输出文件已存在, 跳过: %s", out_path)
                entry["skipped"] = True
            else:
                write_file(out_path, lines, encoding=read_cfg.encoding)
                entry["output"] = out_path
        else:
            entry["dry_run"] = True

        results.append(entry)

    return results


def get_stats(results):
    """从结果中生成统计信息"""
    if not results:
        return {"files": 0, "total_lines_in": 0, "total_lines_out": 0}

    return {
        "files": len(results),
        "total_lines_in": sum(r["lines_in"] for r in results),
        "total_lines_out": sum(r["lines_out"] for r in results),
        "skipped": sum(1 for r in results if r.get("skipped")),
        "dry_run": sum(1 for r in results if r.get("dry_run")),
    }
