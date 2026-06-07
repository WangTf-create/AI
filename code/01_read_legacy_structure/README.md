# 遗留结构扫描输入

这个目录服务前三个连续演示点：

1. 让 AI 读懂遗留代码，产出职责板块、状态地图、可疑行为清单。
2. 把当前行为写成 spec，并生成特征测试。
3. 保留入口，小步重构，并用红绿测试证明行为没有变。

## 输入 1：上帝文件订单系统

[god_file_order_system/order_system.py](god_file_order_system/order_system.py)

- 3000+ 行单文件。
- 一个 `OrderSystem` 类承担计价、折扣、税、运费、库存、风控、持久化等多种职责。
- 核心入口是 `checkout()`。
- 适合完整演示「架构梳理 → spec → 特征测试 → 小步重构 → 故意改坏被抓红」。

运行：

```bash
python god_file_order_system/order_system.py
```

## 输入 2：结构耦合订单系统

[advanced_modular_coupling/](advanced_modular_coupling/)

- 多模块，但靠全局状态、近循环依赖、import 副作用、共享 context 绑在一起。
- 适合补充说明：大项目的难不只在体量，也在结构。
- 课堂只建议演示「依赖 / 状态图」，不建议展开完整重构。

运行：

```bash
cd advanced_modular_coupling
python runner.py
```
