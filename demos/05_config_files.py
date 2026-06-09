"""
============================================================
Demo 5: 配置文件 —— Python 脚本与 JSON 配置
============================================================

traitlets.config 支持两种配置文件格式:
  1. Python 脚本 (.py)   —— 灵活, 可写复杂逻辑
  2. JSON 文件 (.json)   —— 结构化, 易于机器生成

本 demo 演示:
  - Python 配置文件的写法 (c.ClassName.attr = value)
  - JSON 配置文件的格式
  - load_subconfig() 配置继承
  - Application.load_config_file() 加载配置
  - 配置优先级: CLI > config file > class defaults
"""

import json
import os
from traitlets.config import Application, Configurable, Config
from traitlets.config.loader import PyFileConfigLoader, JSONFileConfigLoader
from traitlets import Int, Unicode, Float, Bool

# 配置文件所在的目录
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)


# ============================================================
# 准备: 写配置文件到 configs/ 目录
# ============================================================

# Python 配置文件
py_config = """\
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
"""

# JSON 配置文件
json_config = {
    "Server": {
        "host": "127.0.0.1",
        "port": 8888,
        "debug": True,
    }
}

# 配置继承: base_config.py
base_py_config = """\
c = get_config()  # noqa

c.Server.name = "base-server"
c.Server.port = 3000
"""

# 配置继承: main_config.py (继承 base)
main_py_config = """\
c = get_config()  # noqa

# 加载并合并 base_config.py 中的所有配置到当前 c 中
load_subconfig("base_config.py")


# 覆盖从 base 继承来的 name
c.Server.name = "main-server"
# 新增配置项（base 中没有定义 host）
c.Server.host = "10.0.0.1"
"""

with open(os.path.join(CONFIG_DIR, "server_config.py"), "w") as f:
    f.write(py_config)
with open(os.path.join(CONFIG_DIR, "server_config.json"), "w") as f:
    # 将 Python 对象 序列化并写入文件
    json.dump(json_config, f, indent=2)
with open(os.path.join(CONFIG_DIR, "base_config.py"), "w") as f:
    f.write(base_py_config)
with open(os.path.join(CONFIG_DIR, "main_config.py"), "w") as f:
    f.write(main_py_config)

print(f"配置文件已写入: {CONFIG_DIR}/")

# 调试工具: 打印 Config 的内部嵌套字典结构
def print_config(cfg):
    """调试工具: 打印 Config 的内部嵌套字典结构"""
    import json
    print(f"Config 内部结构:")
    print(json.dumps(dict(cfg), indent=2, ensure_ascii=False))

# ============================================================
# 定义一个 Configurable 类
# ============================================================
class Server(Configurable):
    """模拟的服务器配置类"""
    name = Unicode("default-server", help="服务器名称").tag(config=True)
    host = Unicode("localhost", help="监听地址").tag(config=True)
    port = Int(8000, help="监听端口").tag(config=True)
    debug = Bool(False, help="调试模式").tag(config=True)
    timeout = Float(30.0, help="超时时间").tag(config=True)


print("=" * 60)
print("示例 1: 无配置文件的默认值")
print("=" * 60)
s = Server()
print(f"  默认: name={s.name!r}, host={s.host!r}, port={s.port}, debug={s.debug}")


# ============================================================
# 示例 2: 加载 Python 配置文件
# ============================================================
print("\n" + "=" * 60)
print("示例 2: Python 配置文件")
print("=" * 60)

# PyFileConfigLoader 会读取并 执行 configs/server_config.py 这个 Python 脚本
# 执行后，loader 对象内部就持有了脚本中定义的 c 这个 Config 对象
loader = PyFileConfigLoader("server_config.py", path=CONFIG_DIR)
config = loader.load_config()

# 打印 Config 的内部嵌套字典结构
print_config(config)

# 使用加载的 config 创建 Server 实例
# traitlets 会自动将 Config 中的配置值应用到对应的 trait 属性上
# 这里 config.Server.host 会赋值给 s2.host, config.Server.port 赋值给 s2.port 等
s2 = Server(config=config)
print(f"host={s2.host!r}, port={s2.port}, debug={s2.debug}")

# ============================================================
# 示例 3: 加载 JSON 配置文件
# ============================================================
print("\n" + "=" * 60)
print("示例 3: JSON 配置文件")
print("=" * 60)

loader_json = JSONFileConfigLoader("server_config.json", path=CONFIG_DIR)
config_json = loader_json.load_config()

# 打印 Config 的内部嵌套字典结构
print_config(config_json)

s3 = Server(config=config_json)
print(f"host={s3.host!r}, port={s3.port}, debug={s3.debug}")

# ============================================================
# 示例 4: 配置优先级合并
# ============================================================
print("\n" + "=" * 60)
print("示例 4: 配置合并与优先级")
print("=" * 60)

py_loader = PyFileConfigLoader("server_config.py", path=CONFIG_DIR)
py_config = py_loader.load_config()

json_loader = JSONFileConfigLoader("server_config.json", path=CONFIG_DIR)
json_config = json_loader.load_config()

# merge: json 配置合并到 py 配置中, json 优先级更高
# 合并规则: a.merge(b) 表示 b 覆盖 a
# a.merge(b) = 让 b 的值覆盖 a 的值
# merge() 的参数优先级更高。
py_config.merge(json_config)
print("合并后:")
print_config(py_config)

s4 = Server(config=py_config)
print("合并后配置:")
print(f"host={s4.host!r}, port={s4.port}, debug={s4.debug}")

# ============================================================
# 示例 5: 配置继承 —— load_subconfig
# ============================================================
print("\n" + "=" * 60)
print("示例 5: load_subconfig 配置继承")
print("=" * 60)

main_loader = PyFileConfigLoader("main_config.py", path=CONFIG_DIR)
main_config = main_loader.load_config()
print("main_config 合并后 Server:")
print_config(main_config)

s5 = Server(config=main_config)
print(f"  name={s5.name!r}, host={s5.host!r}, port={s5.port}")
print(f"  (name 来自 main, host 来自 main, port 来自 base)")


# ============================================================
# 示例 6: 使用 Application 自动加载配置文件
# ============================================================
print("\n" + "=" * 60)
print("示例 6: Application.load_config_file()")
print("=" * 60)

# MyApp 继承自 traitlets.config.Application，
# 这是 traitlets 配置系统的核心入口类。
# Application 提供了自动发现和加载配置文件的能力，
# 如从命令行参数、环境变量、配置文件目录等位置加载。
# MyApp → Application → SingletonConfigurable → Configurable → HasTraits
class MyApp(Application):
    name = Unicode("myapp")
    description = Unicode("配置文件加载演示")

    # 告诉 Application 这个应用用到了 Server 类，
    # 这样配置文件中的 c.Server.xxx 段落才能被正确解析
    classes = [Server]

    # 覆写 initialize，在 CLI 解析后手动加载配置文件
    def initialize(self, argv=None):
        # 基类只做 parse_command_line
        super().initialize(argv)  
        # 加载 .py 和 .json（.json 后加载，优先级更高）                    #    
        self.load_config_file("server_config", path=[CONFIG_DIR])  

    def start(self):
        srv = Server(config=self.config)
        print(f"  Application 自动加载的配置:")
        print(f"    name={srv.name!r}, host={srv.host!r}, port={srv.port}, debug={srv.debug}")


# 手动构造实例，依次调用 initialize() → start()
app = MyApp()
app.initialize()   # Application 自动取 sys.argv[1:] 解析 CLI 参数
app.start()              # 执行业务逻辑
print("  Application.load_config_file 加载完成")

server = Server(config=app.config)
print(f"    Server: name={server.name!r}, host={server.host!r}, port={server.port}")

print("\n>>> Demo 5 结束: 掌握了 Python 和 JSON 两种配置文件方式")

# 示例 6: 从命令行参数覆盖配置
# uv run python demos/05_config_files.py --Server.port=6666