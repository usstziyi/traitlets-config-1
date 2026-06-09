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

c = get_config()  # noqa

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

# 继承 base_config.py 的所有配置
load_subconfig("base_config.py")

# 覆盖部分配置
c.Server.name = "main-server"
c.Server.host = "10.0.0.1"
"""

with open(os.path.join(CONFIG_DIR, "server_config.py"), "w") as f:
    f.write(py_config)
with open(os.path.join(CONFIG_DIR, "server_config.json"), "w") as f:
    json.dump(json_config, f, indent=2)
with open(os.path.join(CONFIG_DIR, "base_config.py"), "w") as f:
    f.write(base_py_config)
with open(os.path.join(CONFIG_DIR, "main_config.py"), "w") as f:
    f.write(main_py_config)

print(f"配置文件已写入: {CONFIG_DIR}/")


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

loader = PyFileConfigLoader("server_config.py", path=CONFIG_DIR)
config = loader.load_config()
print(f"  Python config 内容: {dict(config.Server)}")

s2 = Server(config=config)
print(f"  host={s2.host!r}, port={s2.port}, debug={s2.debug}")


# ============================================================
# 示例 3: 加载 JSON 配置文件
# ============================================================
print("\n" + "=" * 60)
print("示例 3: JSON 配置文件")
print("=" * 60)

loader_json = JSONFileConfigLoader("server_config.json", path=CONFIG_DIR)
config_json = loader_json.load_config()
print(f"  JSON config 内容: {dict(config_json.Server)}")

s3 = Server(config=config_json)
print(f"  host={s3.host!r}, port={s3.port}, debug={s3.debug}")


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
py_config.merge(json_config)
print(f"  合并后 Server: {dict(py_config.Server)}")

s4 = Server(config=py_config)
print(f"  最终: host={s4.host!r}, port={s4.port}, debug={s4.debug}")
print(f"  (JSON 的 host=127.0.0.1, debug=True 覆盖了 Python 的 host=0.0.0.0, debug=False)")


# ============================================================
# 示例 5: 配置继承 —— load_subconfig
# ============================================================
print("\n" + "=" * 60)
print("示例 5: load_subconfig 配置继承")
print("=" * 60)

main_loader = PyFileConfigLoader("main_config.py", path=CONFIG_DIR)
main_config = main_loader.load_config()
print(f"  main_config 合并后 Server: {dict(main_config.Server)}")

s5 = Server(config=main_config)
print(f"  name={s5.name!r}, host={s5.host!r}, port={s5.port}")
print(f"  (name 来自 main, host 来自 main, port 来自 base)")


# ============================================================
# 示例 6: 使用 Application 自动加载配置文件
# ============================================================
print("\n" + "=" * 60)
print("示例 6: Application.load_config_file()")
print("=" * 60)


class MyApp(Application):
    name = Unicode("myapp")
    description = Unicode("配置文件加载演示")

    classes = [Server]

    def start(self):
        # 获取配置并创建 Server
        srv = Server(config=self.config)
        print(f"  Application 自动加载的配置:")
        print(f"    host={srv.host!r}, port={srv.port}, debug={srv.debug}, name={srv.name!r}")


# 通过 class-level 属性设置配置路径和文件名
# 然后直接构造实例 (避免 singleton 冲突)
MyApp.config_file_paths = [CONFIG_DIR]
MyApp.config_file_name = "server_config"
app = MyApp()
app.initialize([])
print("  Application.load_config_file 加载完成")

server = Server(config=app.config)
print(f"  Server: name={server.name!r}, host={server.host!r}, port={server.port}")

print("\n>>> Demo 5 结束: 掌握了 Python 和 JSON 两种配置文件方式")
