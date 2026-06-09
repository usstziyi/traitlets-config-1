"""
============================================================
Demo 1: HasTraits 基础 —— 类型检查与动态默认值
============================================================

traitlets 的核心是 HasTraits 类。任何继承 HasTraits 的类都可以
声明带有类型检查、动态默认值和变化通知的属性（trait）。

本 demo 演示:
  - 基本 trait 类型: Int, Float, Unicode, Bool, List, Dict
  - 类型检查: 赋值时自动校验类型
  - @default 装饰器: 动态计算默认值
  - 实例化时传入初始值
  - 只读 trait (read_only=True)
"""

from traitlets import (
    HasTraits, Int, Float, Unicode, Bool, List, Dict, default,
    TraitError, observe,
)


# ============================================================
# 示例 1: 最简单的 HasTraits 类
# ============================================================
class Person(HasTraits):
    """一个简单的人物类，演示基本 trait 定义"""
    name = Unicode("未命名")
    age = Int(0)
    height = Float(0.0)
    is_student = Bool(False)
    hobbies = List(trait=Unicode(), default_value=[])
    scores = Dict(key_trait=Unicode(), value_trait=Float(), default_value={})


print("=" * 60)
print("示例 1: 基本 trait 定义与默认值")
print("=" * 60)

p = Person()
print(f"默认值 -> name={p.name!r}, age={p.age}, height={p.height}, "
      f"is_student={p.is_student}, hobbies={p.hobbies}, scores={p.scores}")



# ============================================================
# 示例 2: 类型检查 —— 自动校验
# ============================================================
print("\n" + "=" * 60)
print("示例 2: 类型检查")
print("=" * 60)

# 正常赋值 —— 类型匹配
p.name = "张三"
p.age = 25
p.height = 1.75
p.hobbies = ["阅读", "编程"]
p.scores = {"数学": 95.5, "语文": 88.0}
print(f"赋值后 -> name={p.name!r}, age={p.age}, height={p.height}")
print(f"  hobbies={p.hobbies}, scores={p.scores}")

# 错误类型赋值 —— 会抛出 TraitError
try:
    p.age = "二十五"
except TraitError as e:
    print(f"\n类型错误被捕获: {e}")


# ============================================================
# 示例 3: @default 装饰器 —— 动态默认值
# ============================================================
class ServerConfig(HasTraits):
    """服务器配置类，演示动态默认值"""
    host = Unicode("0.0.0.0")
    port = Int(8000)

    # 动态默认值: 每次实例化时都会计算
    @default("host")
    def _default_host(self):
        import socket
        return socket.gethostname()


print("\n" + "=" * 60)
print("示例 3: @default 动态默认值")
print("=" * 60)

cfg = ServerConfig()
print(f"host 动态默认值 = {cfg.host!r} (本机主机名)")
print(f"port 静态默认值 = {cfg.port}")


# ============================================================
# 示例 4: 构造时传入初始值
# ============================================================
print("\n" + "=" * 60)
print("示例 4: 构造时传入初始值")
print("=" * 60)

p2 = Person(name="李四", age=30, height=1.80)
print(f"构造传入 -> name={p2.name!r}, age={p2.age}, height={p2.height}")

# 构造时类型错误也会被捕获
try:
    Person(age="三十")
except TraitError as e:
    print(f"构造时类型错误: {e}")


# ============================================================
# 示例 5: 只读 trait
# ============================================================
class ReadOnlyExample(HasTraits):
    normal = Unicode("可修改")
    read_only = Unicode("不可修改", read_only=True)


print("\n" + "=" * 60)
print("示例 5: read_only trait")
print("=" * 60)

ro = ReadOnlyExample()
print(f"read_only 初始值: {ro.read_only!r}")

try:
    ro.read_only = "尝试修改"
except TraitError as e:
    print(f"修改 read_only 被阻止: {e}")

ro.normal = "已修改"
print(f"normal 可以修改: {ro.normal!r}")

print("\n>>> Demo 1 结束: 理解了 HasTraits 的基本 trait 定义与类型检查")
