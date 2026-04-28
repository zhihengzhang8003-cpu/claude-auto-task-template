# TaskPlan — [项目名称]

> 使用说明：将 [方括号内容] 替换为你的实际内容。T01-T03 是示例任务，展示正确格式，使用前请替换为真实任务。

## 概述

[一句话描述项目目标和核心验收标准]

## 进度

| 状态 | 数量 |
|------|------|
| ⏳ 待办 | 3 |
| ✅ 完成 | 0 |
| ⚠️ 警告 | 0 |

---

## Phase A：核心逻辑

### T01 ⏳ 数据模型基础字段

**目标**
新建 `src/models/item.py`，定义 `Item` 数据类：
```python
@dataclass
class Item:
    id: str
    name: str
    quantity: int = 0
    price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
```
新建 `src/models/__init__.py`（空文件，使 models 成为 package）。
确保 `from src.models.item import Item` 可正常导入。

**限制（不做）**
- 不实现数据库存储（T02 做）
- 不实现 API 接口（T03 做）
- 不添加验证逻辑

**涉及文件（最多3个）**
- `src/models/__init__.py`（新建）
- `src/models/item.py`（新建）

---

### T02 ⏳ 内存存储层

**目标**
新建 `src/storage/item_store.py`，实现 `ItemStore` 类：
```python
class ItemStore:
    def add(self, item: Item) -> None: ...
    def get(self, item_id: str) -> Item | None: ...
    def list_all(self) -> list[Item]: ...
    def delete(self, item_id: str) -> bool: ...  # 返回 False 表示 id 不存在
```
内部用 `dict[str, Item]` 存储，键为 `item.id`。
新建 `src/storage/__init__.py`。

**限制（不做）**
- 不实现持久化（内存存储即可）
- 不实现搜索/过滤功能
- 不改 Item 数据类

**涉及文件（最多3个）**
- `src/storage/__init__.py`（新建）
- `src/storage/item_store.py`（新建）

---

### T03 ⏳ CLI 入口

**目标**
新建 `src/cli.py`，实现命令行界面：
- `add <name> <quantity> <price>` → 创建 Item（id 自动用 `uuid4()` 生成），打印 `已添加: {id} {name}`
- `list` → 打印所有 Item（格式：`{id[:8]}  {name}  数量:{quantity}  单价:{price}`）
- `delete <id>` → 删除，打印 `已删除` 或 `未找到`

使用 `argparse`，无需第三方库。
`ItemStore` 在进程内单例（模块级变量），不做持久化。

**限制（不做）**
- 不做数据持久化
- 不做输入验证（价格格式、负数等）
- 不添加 update 命令

**涉及文件（最多2个）**
- `src/cli.py`（新建）

---

## Phase B：[下一阶段名称]

<!-- 继续在此添加任务，格式同上 -->

---

## 完成标准

- 验证命令返回 0（见 Architecture.md 末尾）
- [列出其他可验证的核心功能标准]
