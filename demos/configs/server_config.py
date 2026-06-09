# 这是一个 Python 配置文件
# 变量 c 是 Config 对象

c = get_config()  # noqa

c.Server.host = "0.0.0.0"
c.Server.port = 9999
c.Server.debug = False
