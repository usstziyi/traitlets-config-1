"""
============================================================
Demo 3: 自定义验证 —— Validate 与 Cross-Validation
============================================================

traitlets 提供了强大的验证机制:
  - @validate("trait_name") 装饰器: 自定义单个 trait 的验证逻辑
  - proposal 对象: 包含 value 属性
  - 跨属性交叉验证: 根据其他 trait 的值来校验当前 trait
  - hold_trait_notifications(): 批量修改时暂缓验证
  - 容器 trait 的嵌套验证 (per_key_traits, value_trait)

本 demo 演示:
  - 简单的单属性验证
  - 跨属性的交叉验证
  - hold_trait_notifications 的用法
  - Dict trait 的嵌套验证
"""

from traitlets import (
    HasTraits, Int, Unicode, List, Dict, Bool,
    validate, TraitError, observe,
)


# ============================================================
# 示例 1: 简单的单属性验证
# ============================================================
class ScoreCard(HasTraits):
    score = Int(0)

    @validate("score")
    def _valid_score(self, proposal):
        """验证分数必须在 0-100 之间"""
        value = proposal["value"]
        if value < 0 or value > 100:
            raise TraitError(f"分数必须在 0-100 之间, 收到: {value}")
        return value


print("=" * 60)
print("示例 1: 单属性验证")
print("=" * 60)

s = ScoreCard(score=85)
print(f"有效分数: {s.score}")

try:
    s.score = 150
except TraitError as e:
    print(f"验证失败: {e}")

try:
    s.score = -10
except TraitError as e:
    print(f"验证失败: {e}")


# ============================================================
# 示例 2: 跨属性交叉验证 —— 密码与确认密码
# ============================================================
class PasswordForm(HasTraits):
    password = Unicode("")
    confirm_password = Unicode("")

    @validate("password")
    def _valid_password(self, proposal):
        value = proposal["value"]
        if len(value) < 6:
            raise TraitError("密码至少需要 6 个字符")
        if self.confirm_password and value != self.confirm_password:
            raise TraitError("两次输入的密码不一致")
        return value

    @validate("confirm_password")
    def _valid_confirm(self, proposal):
        value = proposal["value"]
        if value != self.password:
            raise TraitError("确认密码与密码不一致")
        return value


print("\n" + "=" * 60)
print("示例 2: 跨属性交叉验证")
print("=" * 60)

pf = PasswordForm(password="abcdef", confirm_password="abcdef")
print(f"密码设置成功: password={pf.password!r}")

try:
    pf.confirm_password = "xyz"
except TraitError as e:
    print(f"确认密码验证失败: {e}")

try:
    pf.password = "123456"
except TraitError as e:
    print(f"密码太短验证失败: {e}")


# ============================================================
# 示例 3: hold_trait_notifications —— 批量修改
# ============================================================
print("\n" + "=" * 60)
print("示例 3: hold_trait_notifications 批量修改")
print("=" * 60)

# 从同一状态开始
pf2 = PasswordForm(password="abcdef", confirm_password="abcdef")
print(f"初始状态: password={pf2.password!r}, confirm={pf2.confirm_password!r}")

# 单独修改密码 (先改 password 为 "123456"，但同时 confirm 还是 "abcdef" 会不一致)
try:
    pf2.password = "123456"
except TraitError as e:
    print(f"单独修改失败 (符合预期): {e}")

# 使用 hold_trait_notifications 批量修改
# 保持状态通知, 避免在批量修改时触发验证
with pf2.hold_trait_notifications():
    pf2.password = "newpwd123" # 不触发验证
    pf2.confirm_password = "newpwd123" # 不触发验证
# 离开上下文时触发验证

print(f"批量修改后: password={pf2.password!r}, confirm={pf2.confirm_password!r}")


# ============================================================
# 示例 4: 变更回滚 —— 验证失败时自动回滚
# ============================================================
print("\n" + "=" * 60)
print("示例 4: 验证失败时的自动回滚")
print("=" * 60)

pf3 = PasswordForm(password="original", confirm_password="original")
print(f"回滚前: password={pf3.password!r}, confirm={pf3.confirm_password!r}")

try:
    # hold_trait_notifications() 有内置的自动回滚功能
    with pf3.hold_trait_notifications():
        pf3.password = "newpass"
        pf3.confirm_password = "mismatch"  # 与 newpass 不一致
        # 离开上下文时交叉验证失败, 所有修改回滚
except TraitError as e:
    print(f"交叉验证失败, 自动回滚: {e}")

print(f"回滚后: password={pf3.password!r}, confirm={pf3.confirm_password!r}")


# ============================================================
# 示例 5: Dict 的嵌套验证
# ============================================================
class ConfigStore(HasTraits):
    settings = Dict(
        # 单独定义每个键的 trait 类型
        per_key_traits={
            "host": Unicode(),
            "port": Int(),
            "debug": Bool(),
        },
        default_value={
            "host": "localhost", 
            "port": 8080, 
            "debug": False
        },
    )


print("\n" + "=" * 60)
print("示例 5: Dict 嵌套验证")
print("=" * 60)

cs = ConfigStore()
print(f"默认配置: {cs.settings}")

cs.settings = {"host": "0.0.0.0", "port": 3000, "debug": True}
print(f"修改后: {cs.settings}")

# 示例 5 演示的是： per_key_traits 是持续生效的类型守卫，
# 任何时候给 settings 赋新字典，traitlets 都会对每个 key 做类型校验，
# 任何一个字段类型不符都会阻止整个赋值。
try:
    cs.settings = {"host": "localhost", "port": "不是数字", "debug": False}
except TraitError as e:
    print(f"嵌套验证失败: {e}")

print("\n>>> Demo 3 结束: 理解了 traitlets 的验证机制")
