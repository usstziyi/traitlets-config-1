"""
============================================================
Demo 2: observe 观察者模式 —— 属性变化通知
============================================================

traitlets 实现了观察者模式（Observer Pattern），当 trait 的值发生
变化时，可以自动触发回调函数。这是构建响应式应用的基础。

本 demo 演示:
  - obj.observe(handler, names=[...]) 注册观察者
  - @observe("trait_name") 装饰器语法
  - change 对象的结构: old, new, owner, name
  - 观察多个 trait
  - 观察容器类型 trait 的变化 (List/Dict)
"""

from traitlets import (
    HasTraits, Int, Unicode, Bool, List, Dict, observe,
)


# ============================================================
# 示例 1: 使用 obj.observe() 注册外部观察者
# ============================================================
class Counter(HasTraits):
    value = Int(0)


print("=" * 60)
print("示例 1: obj.observe() 注册观察者")
print("=" * 60)

c = Counter()


def on_value_change(change):
    """当 value 变化时被调用"""
    print(f"  [观察者] value 变化: {change['old']} -> {change['new']}")


c.observe(on_value_change, names=["value"])

c.value = 10
c.value = 20
c.value = 30


# ============================================================
# 示例 2: @observe 装饰器 —— 类内观察者
# ============================================================
class Temperature(HasTraits):
    celsius = Int(0)
    fahrenheit = Int(32)

    @observe("celsius")
    def _on_celsius_change(self, change):
        """当摄氏度变化时自动更新华氏度"""
        self.fahrenheit = int(change["new"] * 9 / 5 + 32)
        print(f"  [自动转换] {change['old']}°C -> {change['new']}°C"
              f"  =>  华氏度: {self.fahrenheit}°F")


print("\n" + "=" * 60)
print("示例 2: @observe 装饰器自动联动")
print("=" * 60)

t = Temperature()
t.celsius = 0
t.celsius = 25
t.celsius = 100


# ============================================================
# 示例 3: change 对象的完整结构
# ============================================================
print("\n" + "=" * 60)
print("示例 3: change 对象的完整信息")
print("=" * 60)


class UserProfile(HasTraits):
    username = Unicode("guest")
    login_count = Int(0)
    is_admin = Bool(False)

    @observe("username")
    def _on_username_change(self, change):
        print(f"  name={change['name']!r}")
        print(f"  old={change['old']!r}")
        print(f"  new={change['new']!r}")
        print(f"  owner={type(change['owner']).__name__}")


u = UserProfile()
u.username = "admin001"


# ============================================================
# 示例 4: 观察容器类型 trait 的变化
# ============================================================
class TaskBoard(HasTraits):
    tasks = List(trait=Unicode(), default_value=[])

    @observe("tasks")
    def _on_tasks_change(self, change):
        print(f"  [TaskBoard] 任务列表变化: {change['old']} -> {change['new']}")


print("\n" + "=" * 60)
print("示例 4: 容器类型 trait 的变化通知")
print("=" * 60)

board = TaskBoard()

# 整个替换会触发通知
board.tasks = ["任务1", "任务2"]

# 就地修改 (append) 不会自动触发 —— 需要整个替换
# 解决方案: 替换整个列表
board.tasks = board.tasks + ["任务3"]

print("\n>>> Demo 2 结束: 理解了观察者模式的基本用法")
