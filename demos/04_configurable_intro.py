"""
============================================================
Demo 4: Configurable 入门 —— 让 trait 可被配置
============================================================

traitlets.config.Configurable 是 HasTraits 的子类，核心差异:
  1. 通过 .tag(config=True) 将 trait 标记为"可配置"的
  2. 可通过 Config 对象批量注入配置值
  3. Config 对象支持 c.ClassName.attr = value 的点号语法
  4. 支持配置继承 (子类继承父类的配置)
  5. update_config() 可以在运行时更新配置

本 demo 演示:
  - Configurable vs HasTraits
  - tag(config=True) 的用法
  - Config 对象的创建和使用
  - 构造时传入 config 参数
  - update_config() 运行时更新
"""

from traitlets.config import Configurable, Config
from traitlets import HasTraits, Int, Unicode, Float, Bool, List


# ============================================================
# 示例 1: 定义第一个 Configurable 类
# ============================================================
class Database(HasTraits):
    """普通 HasTraits: 不能通过 Config 配置"""
    host = Unicode("localhost")
    port = Int(5432)


class DatabaseConfigurable(Configurable):
    """Configurable: 可通过 Config 配置"""
    host = Unicode("localhost", help="数据库主机地址").tag(config=True)
    port = Int(5432, help="数据库端口").tag(config=True)
    max_connections = Int(100, help="最大连接数").tag(config=True)

    # 没有 tag(config=True) 的 trait 不会被配置系统管理
    internal_state = Unicode("idle")


print("=" * 60)
print("示例 1: Configurable 的定义")
print("=" * 60)

db = DatabaseConfigurable()
print(f"默认值: host={db.host!r}, port={db.port}, "
      f"max_connections={db.max_connections}, internal_state={db.internal_state!r}")

# ============================================================
# 示例 2: 使用 Config 对象注入配置
# ============================================================
print("\n" + "=" * 60)
print("示例 2: Config 对象注入")
print("=" * 60)

# 创建 Config 对象
# Config() 是 traitlets 配置系统中用于 批量注入配置值 的核心对象。
# 它就像一个"配置字典"，让你可以在不修改类定义的情况下，从外部批量设
# 置 Configurable 类的 trait 值。
#
# Config 的工作机制:
# 1. 点号语法: cfg.ClassName.trait_name = value
#    其中 ClassName 必须与目标 Configurable 类的名字完全一致
#    cfg.DatabaseConfigurable.host = "x" 内部存储为:
#    {"DatabaseConfigurable": {"host": "x"}}
#    同一个 Config 对象可以同时承载 多个类的多个属性。
#
# 2. 选择性生效: 只有被 .tag(config=True) 标记的 trait
#    才会被配置系统管理。未标记的 trait 即使写了也不会生效。
#
# 3. 构造时注入: 通过 DatabaseConfigurable(config=cfg) 传入，
#    配置值会在 __init__ 时自动注入到对应的 trait，覆盖默认值。
#
# 4. 继承: 子类自动继承父类的配置 (见示例 3)
cfg = Config()
cfg.DatabaseConfigurable.host = "192.168.1.100"
cfg.DatabaseConfigurable.port = 3306
cfg.DatabaseConfigurable.max_connections = 200
print(f"Config 对象: {cfg}")

# 通过 config= 参数在构造时注入配置
db2 = DatabaseConfigurable(config=cfg)
print(f"通过 Config 注入: host={db2.host!r}, port={db2.port}, "
      f"max_connections={db2.max_connections}")

# internal_state 没有被 config 系统管理, 保持默认值
print(f"未配置的 trait: internal_state={db2.internal_state!r}")

# 尝试配置 internal_state (没有 tag(config=True)) —— 会被忽略
cfg.DatabaseConfigurable.internal_state = "should_not_work"
db3 = DatabaseConfigurable(config=cfg)
print(f"尝试配置未标记的 trait: internal_state={db3.internal_state!r} (不起作用)")

# ============================================================
# 示例 3: 配置继承 —— 子类自动继承父类配置
# ============================================================
print("\n" + "=" * 60)
print("示例 3: 配置继承")
print("=" * 60)


class Animal(Configurable):
    name = Unicode("unknown", help="动物名称").tag(config=True)
    age = Int(0, help="年龄").tag(config=True)


class Dog(Animal):
    breed = Unicode("混血", help="品种").tag(config=True)
    can_bark = Bool(True, help="是否会叫").tag(config=True)


class Cat(Animal):
    color = Unicode("白色", help="颜色").tag(config=True)


cfg2 = Config()
# 配置父类 Animal —— 会影响所有 Animal 子类
cfg2.Animal.name = "通用动物"
cfg2.Animal.age = 1

# 配置子类特有属性
cfg2.Dog.breed = "金毛"
cfg2.Cat.color = "黑色"

dog = Dog(config=cfg2)
cat = Cat(config=cfg2)

print(f"Dog: name={dog.name!r}, age={dog.age}, breed={dog.breed!r}, can_bark={dog.can_bark}")
print(f"Cat: name={cat.name!r}, age={cat.age}, color={cat.color!r}")

# 子类配置可以覆盖父类配置
cfg2.Dog.name = "旺财"
dog2 = Dog(config=cfg2)
print(f"Dog (覆盖后): name={dog2.name!r} (子类覆盖了父类配置)")

# Cat 的名仍是 "通用动物" —— 来自父类 Animal 的配置
print(f"Cat: name={cat.name!r} (仍来自父类 Animal 配置)")


# ============================================================
# 示例 4: update_config() 运行时更新配置
# ============================================================
print("\n" + "=" * 60)
print("示例 4: update_config() 运行时更新")
print("=" * 60)

db4 = DatabaseConfigurable()
print(f"更新前: host={db4.host!r}, port={db4.port}")

cfg_update = Config()
cfg_update.DatabaseConfigurable.host = "10.0.0.1"
cfg_update.DatabaseConfigurable.port = 9999
db4.update_config(cfg_update)
print(f"更新后: host={db4.host!r}, port={db4.port}")


# ============================================================
# 示例 5: 嵌套 Configurable
# ============================================================
print("\n" + "=" * 60)
print("示例 5: 嵌套 Configurable")
print("=" * 60)


class CacheConfig(Configurable):
    backend = Unicode("redis", help="缓存后端").tag(config=True)
    ttl = Int(3600, help="过期时间(秒)").tag(config=True)


class WebAppConfig(Configurable):
    name = Unicode("myapp", help="应用名称").tag(config=True)
    port = Int(8080, help="监听端口").tag(config=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = CacheConfig(config=self.config)


cfg3 = Config()
cfg3.CacheConfig.backend = "memcached"
cfg3.CacheConfig.ttl = 7200
cfg3.WebAppConfig.name = "webapp-prod"
cfg3.WebAppConfig.port = 443

app = WebAppConfig(config=cfg3)
print(f"WebApp: name={app.name!r}, port={app.port}")
print(f"嵌套 Cache: backend={app.cache.backend!r}, ttl={app.cache.ttl}")

print("\n>>> Demo 4 结束: 理解了 Configurable + Config 的基本配置模式")
