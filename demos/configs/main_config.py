c = get_config()  # noqa

# 加载并合并 base_config.py 中的所有配置到当前 c 中
load_subconfig("base_config.py")


# 覆盖从 base 继承来的 name
c.Server.name = "main-server"
# 新增配置项（base 中没有定义 host）
c.Server.host = "10.0.0.1"
