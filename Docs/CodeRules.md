# 代码规范

---

## 命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 类、接口 | PascalCase | `BattleContext`, `IAction` |
| 公共方法 | PascalCase | `Execute()`, `IsValid()` |
| 私有字段 | _camelCase | `_unitList` |
| 公共属性 | PascalCase | `MaxWounds` |
| 局部变量 | camelCase | `targetUnit` |

---

## 类职责

- 一个类只做一件事
- 不允许 God Object（承担超过 3 种职责的类）
- 工具/辅助类用静态类，有状态的逻辑用实例类

---

## 注释

- 不写描述"是什么"的注释（代码本身表达）
- 只写"为什么"的注释：隐藏约束、规避的 bug、非直觉的设计选择
- 禁止任务编号注释（`// T03: added`），这属于 git commit message

---

## 禁止事项

- 禁止 UI 层直接计算业务逻辑
- 禁止硬编码业务数值（放入 Architecture.md 或配置类）
- 禁止在底层（Domain）引用上层（Presentation）的命名空间

---

## 特定语言补充规范

### C# / Unity
- MonoBehaviour 只做：输入转发、事件订阅、位置同步
- 业务数据用纯 C# 类（Plain C# Object），不放在 MonoBehaviour
- 不在 Update() 中做重计算，用事件驱动

### Python
- 类型注解必须（函数参数和返回值）
- 不用全局变量，依赖注入代替

### TypeScript / Node
- 严格模式（`"strict": true`）
- 异步操作统一用 async/await，不混用 callback
