# 文件处理器 Python 配置文件示例
# 变量 c 是 traitlets.config.Config 对象

c = get_config()  # noqa

# ---- 输入配置 ----
c.ReadConfig.input_dir = "./sample_data"
c.ReadConfig.file_pattern = "*.txt"
c.ReadConfig.encoding = "utf-8"

# ---- 转换配置 ----
c.TransformConfig.transforms = ["upper", "capitalize"]
c.TransformConfig.add_line_numbers = True
c.TransformConfig.grep_filter = ""

# ---- 输出配置 ----
c.OutputConfig.output_dir = "./output"
c.OutputConfig.output_prefix = "result_"
c.OutputConfig.overwrite = True
c.OutputConfig.verbose = False
c.OutputConfig.dry_run = False
