c = get_config()  # noqa

# 继承 base_config.py 的所有配置
load_subconfig("base_config.py")

# 覆盖部分配置
c.Server.name = "main-server"
c.Server.host = "10.0.0.1"
