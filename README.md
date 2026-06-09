# traitlets.config 学习教程

基于 [traitlets](https://github.com/ipython/traitlets) 官方文档编写的 `Configurable` / `Application` 渐进式教程，由浅入深，最终以一个实战 CLI 工具收尾。

## 项目结构

```
traitlets-config-1/
├── pyproject.toml                    # uv 项目配置
├── 01_has_traits_basics.py           # HasTraits 基础
├── 02_observe_pattern.py             # 观察者模式
├── 03_validation.py                  # 自定义验证
├── 04_configurable_intro.py          # Configurable 入门
├── 05_config_files.py                # Python/JSON 配置文件
├── 06_flags_and_aliases.py           # Flags 与 Aliases
├── 07_singleton.py                   # SingletonConfigurable
├── 08_application.py                 # Application 类
├── 09_subcommands.py                 # Subcommands
├── 10_project/                       # 实战: 文件处理器 CLI
│   ├── config.py                     # Configurable 配置类
│   ├── processors.py                 # 纯业务逻辑
│   └── cli.py                        # Application 入口
└── sample_data/                      # 示例数据
```

## 运行

```bash
uv sync

# 依次运行各 Demo
python3 01_has_traits_basics.py
python3 02_observe_pattern.py
# ...

# 实战 CLI 工具
cd 10_project && python3 cli.py --help
python3 cli.py process --input ../sample_data --transforms upper --dry-run
```

## 知识点速览

| Demo | 核心概念 |
|------|---------|
| 01   | `HasTraits`, `@default`, `read_only`, 类型检查 |
| 02   | `observe()`, `@observe`, `change` 对象 |
| 03   | `@validate`, 交叉验证, `hold_trait_notifications`, 回滚 |
| 04   | `.tag(config=True)`, `Config` 对象, 配置继承 |
| 05   | Python/JSON 配置, `load_subconfig`, `Config.merge` |
| 06   | `--flags`, `--aliases`, `--generate-config` |
| 07   | `instance()`, `clear_instance()`, 子类共享单例 |
| 08   | `launch_instance()`, `initialize()`, `start()`, 日志系统 |
| 09   | `subcommands` 字典, 嵌套子命令 |
| 10   | 完整 CLI: 读文件→转换链→过滤→输出 |

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://trae.ai">SOLO</a></sub>
</p>
