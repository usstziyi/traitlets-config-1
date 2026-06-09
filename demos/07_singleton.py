"""
============================================================
Demo 7: SingletonConfigurable —— 单例模式
============================================================

SingletonConfigurable 是 Configurable 的子类，保证整个应用
中只有一个"权威实例"。常用于需要全局共享的组件:
  - 数据库连接池
  - 配置管理器
  - 日志服务
  - Application 本身就是 SingletonConfigurable

关键 API:
  - Class.instance()   : 获取/创建全局唯一实例
  - Class.initialized(): 是否已创建实例
  - Class.clear_instance(): 清除当前实例 (测试用)

本 demo 演示:
  - 单例的基本行为
  - 子类共享父类的单例
  - 单例 + 配置注入
  - 实际场景: 全局数据库连接池
"""

from traitlets.config import SingletonConfigurable, Config
from traitlets import Int, Unicode, Bool


# ============================================================
# 示例 1: SingletonConfigurable 基本行为
# ============================================================
class AppSettings(SingletonConfigurable):
    theme = Unicode("light", help="界面主题").tag(config=True)
    language = Unicode("zh-CN", help="界面语言").tag(config=True)
    font_size = Int(14, help="字体大小").tag(config=True)


print("=" * 60)
print("示例 1: SingletonConfigurable 基本行为")
print("=" * 60)

# instance() 第一次调用创建实例
settings1 = AppSettings.instance()
print(f"第一次 instance(): {settings1}")
print(f"  theme={settings1.theme!r}, language={settings1.language!r}")

# 再次调用 instance() 返回同一个实例
settings2 = AppSettings.instance()
print(f"第二次 instance(): {settings2}")
print(f"  是同一个对象吗? {settings1 is settings2}")

# initialized() 检查是否已初始化
print(f"  AppSettings.initialized() = {AppSettings.initialized()}")


# ============================================================
# 示例 2: 修改单例属性 —— 全局生效
# ============================================================
print("\n" + "=" * 60)
print("示例 2: 单例属性全局生效")
print("=" * 60)

settings1.theme = "dark"
print(f"settings1.theme = {settings1.theme!r}")
print(f"settings2.theme = {settings2.theme!r}  (自动同步, 因为是同一个对象!)")


# ============================================================
# 示例 3: 子类共享父类的单例
# ============================================================
print("\n" + "=" * 60)
print("示例 3: 子类共享父类单例")
print("=" * 60)

AppSettings.clear_instance()  # 先清除之前的单例


class ProSettings(AppSettings):
    pro_feature = Bool(True, help="是否启用高级功能").tag(config=True)


# 通过子类创建单例
pro = ProSettings.instance()
print(f"  ProSettings.instance() 类型: {type(pro).__name__}")

# 通过父类获取单例 —— 返回同一个 ProSettings 实例!
parent = AppSettings.instance()
print(f"  AppSettings.instance() 类型: {type(parent).__name__}")
print(f"  是同一个对象吗? {pro is parent}")


# ============================================================
# 示例 4: 单例 + 配置注入 (首次 instance 时)
# ============================================================
print("\n" + "=" * 60)
print("示例 4: 单例 + 配置注入")
print("=" * 60)

AppSettings.clear_instance()
ProSettings.clear_instance()


class DatabasePool(SingletonConfigurable):
    host = Unicode("localhost", help="数据库主机").tag(config=True)
    port = Int(5432, help="数据库端口").tag(config=True)
    max_size = Int(10, help="连接池大小").tag(config=True)


# 在首次 instance() 时传入参数
cfg = Config()
cfg.DatabasePool.host = "db.internal.example.com"
cfg.DatabasePool.port = 5432
cfg.DatabasePool.max_size = 20

pool = DatabasePool.instance(config=cfg)
print(f"  host={pool.host!r}, port={pool.port}, max_size={pool.max_size}")


# ============================================================
# 示例 5: 实际场景 —— 全局数据库连接池
# ============================================================
print("\n" + "=" * 60)
print("示例 5: 实际应用场景")
print("=" * 60)

DatabasePool.clear_instance()


class ConnectionPool(SingletonConfigurable):
    """模拟的数据库连接池 —— 全局唯一"""
    dsn = Unicode("postgresql://localhost:5432/mydb", help="数据源名称").tag(config=True)
    pool_size = Int(5, help="连接池大小").tag(config=True)
    timeout = Int(30, help="连接超时(秒)").tag(config=True)

    _connections = []

    def get_connection(self):
        if not self._connections:
            self._connections.append(f"conn-{len(self._connections)+1}")
        return self._connections[-1]

    def close_all(self):
        self._connections.clear()
        print("  所有连接已关闭")


class UserService:
    """使用全局连接池的服务"""

    def __init__(self):
        self.pool = ConnectionPool.instance()

    def query(self, sql):
        conn = self.pool.get_connection()
        return f"[{conn}] 执行: {sql}"


class OrderService:
    """另一个使用全局连接池的服务"""

    def __init__(self):
        self.pool = ConnectionPool.instance()

    def create_order(self, item):
        conn = self.pool.get_connection()
        return f"[{conn}] 创建订单: {item}"


# 配置连接池
cfg_pool = Config()
cfg_pool.ConnectionPool.dsn = "postgresql://prod-db:5432/appdb"
cfg_pool.ConnectionPool.pool_size = 20

# 首次创建连接池单例
ConnectionPool.instance(config=cfg_pool)

user_svc = UserService()
order_svc = OrderService()

print(f"  UserService:  {user_svc.query('SELECT * FROM users')}")
print(f"  OrderService: {order_svc.create_order('商品A')}")
print(f"  它们共享同一个连接池: "
      f"{user_svc.pool is order_svc.pool}")

# 关闭连接
ConnectionPool.instance().close_all()

print("\n>>> Demo 7 结束: 理解了 SingletonConfigurable 的用法")
