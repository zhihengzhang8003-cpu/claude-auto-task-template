# Claude 自动任务系统 — 使用指南

让 Claude Code 在夜间无人值守地持续完成工程任务。

---

## 文件结构

```
你的项目/
├─ runner.py                ← 主驱动脚本（从此处复制）
├─ CLAUDE.md                ← AI 行为规范（Claude 自动读取）
├─ Docs/
│   ├─ TaskPlan.md          ← 任务清单（runner 解析）
│   ├─ Architecture.md      ← 架构规范（每次调用注入）
│   ├─ CodeRules.md         ← 代码规范（每次调用注入）
│   └─ LessonsLearned.md    ← 跨任务经验库（Claude 自动追加）
└─ .claude/
    ├─ settings.json        ← 工具权限白名单
    └─ agents/
        └─ dev-agent.md     ← 可选：专用子 Agent
```

---

## 快速启动（5步）

**第1步：复制模板文件到你的项目**
```bash
cp runner.py          /你的项目/
cp CLAUDE.md          /你的项目/
cp -r Docs/           /你的项目/
cp -r .claude/        /你的项目/
```

**第2步：修改 runner.py 顶部配置**
```python
PROJECT_DIR = Path(r"C:\你的项目路径")   # 修改路径
# 修改 verify_project() 函数为对应的验证命令
```

**第3步：填写 Docs/Architecture.md**
- 项目目标
- 核心数据规格（数值、尺寸、API 等）
- 系统分层和依赖规则
- 验证命令

**第4步：在 Docs/TaskPlan.md 中写任务**
- 参考模板格式（`### T01 ⏳ 标题`）
- 每个任务写清楚：目标、不做什么、涉及文件（≤3）

**第5步：验证并启动**
```bash
# 确认项目编译基线为 0 错误
dotnet build ...   # 或 pytest / npm test 等

# 验证任务解析正确
python runner.py --dry-run 3

# 启动（执行前 3 个任务）
python runner.py 3

# 夜间全量执行
python runner.py
```

---

## 任务格式规范

### 进度表（格式必须精确，runner 用正则替换）

```markdown
| 状态 | 数量 |
|------|------|
| ⏳ 待办 | 10 |
| ✅ 完成 | 0 |
| ⚠️ 警告 | 0 |
```

### 任务块（runner 用 `### T\d+ ⏳ 标题` 解析）

```markdown
### T01 ⏳ 任务标题

**目标**
[精确描述：字段名、方法签名、默认值、判断条件]

**限制（不做）**
- 不实现 X
- 不改 Y

**涉及文件（最多3个）**
- `路径/File.cs`（新建）
```

---

## 任务粒度原则

| 写好任务的标志 | 写差任务的标志 |
|----------------|----------------|
| 包含字段名和类型 | "添加某个属性" |
| 包含方法签名 | "实现某个功能" |
| 明确写不做什么 | 只写要做什么 |
| 指定默认值 | 没有默认值 |
| ≤ 3 个文件 | 涉及 5+ 文件 |
| 任务自包含 | 引用"之前说的" |

**判断标准**：如果用 1 段话写不清楚目标，就需要拆分。

---

## 监控进度

```bash
# 查看实时日志
tail -20 Docs/runner-log.md

# 查看任务完成情况
grep -E "✅|⚠️|⏳" Docs/TaskPlan.md | head -30
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 重复执行同一任务 | dry-run 的正常行为，不是 bug |
| 中文乱码 | runner.py 顶部已有修复，确保 Python ≥ 3.9 |
| Claude 找不到 | 确认 `claude --version` 可执行 |
| 连续 ⚠️ 警告 | 手动检查，修复后将 ⚠️ 改回 ⏳ |
| 任务超时 | 增大 TASK_TIMEOUT 或拆细任务 |

---

## 完整参考文档

见同目录：`../ClaudeAutoTaskSystem.md`
