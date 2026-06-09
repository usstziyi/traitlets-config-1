# 这是一个 Python 配置文件
# 变量 c 是 Config 对象

# traitlets.config 提供的 内置函数 ，返回一个空的 Config 对象。
# 这个函数是在配置脚本的执行环境中自动注入的，所以不需要 import

# 约定的变量名， PyFileConfigLoader 执行完脚本后会读取这个 c 变量。 必须叫 c ，不能改名
# 告诉 linter（如 flake8）不要报 "c is an unused variable" 之类的警告，
# 因为这个变量虽然看起来没被使用，但实际上是被 traitlets 框架在幕后读取的

# get_config() 返回一个空 Config 对象
c = get_config()  # noqa

# 这些语句向 Config 中写入键值对
c.Server.host = "0.0.0.0"
c.Server.port = 9999
c.Server.debug = False
