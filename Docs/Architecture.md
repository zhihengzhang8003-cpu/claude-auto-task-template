# 架构规范

> 本文件会注入到每一次 Claude 调用中。把"所有任务都需要知道的具体参数"放在这里，避免每个任务重复定义。

---

## 项目目标

[一句话描述项目目标，包含关键数字或核心约束]

示例 A（游戏）：复刻 Kill Team Lite 规则，10 步兵 vs 10 步兵，输出可游玩 Unity Demo。
示例 B（工具）：命令行库存管理工具，支持增删查，数据存内存，响应时间 < 50ms。
示例 C（服务）：REST API 服务，提供用户认证和文章 CRUD，部署在 Docker 容器中。

---

## 核心数据规格

> 把所有具体参数集中到这里：数值常量、坐标范围、API 端点、字段默认值等。

| 参数 | 值 | 说明 |
|------|----|------|
| [参数名] | [具体数值] | [为什么是这个值] |

示例行（填写时删除）：
| MAX_RETRIES | 3 | 外部 API 调用失败时的最大重试次数 |
| PAGE_SIZE | 20 | 列表接口默认每页条数 |
| TOKEN_TTL | 3600 | JWT 有效期，单位秒 |

---

## 系统分层

```
[层1：最底层，无依赖]   ← 纯数据结构、工具函数、接口定义
[层2：业务规则]         ← 核心逻辑，不依赖框架或 IO
[层3：应用流程]         ← 调用业务规则，协调数据流
[层4：最外层，表现/接口] ← HTTP 接口、CLI、UI、MonoBehaviour
```

**依赖规则（必须遵守）**：
- 底层不得导入上层的任何模块
- 业务规则层不得引用框架（Django ORM、Unity API 等）
- 表现层不得包含业务计算逻辑

示例（Python 项目）：
```
src/models/       ← 纯数据类，无依赖
src/domain/       ← 业务规则，只依赖 models
src/application/  ← 流程控制，依赖 domain
src/api/ 或 cli/  ← 对外接口，依赖 application
```

---

## 文件路径约定

```
[根目录结构按实际项目填写]

示例（Python）：
src/
  models/       ← dataclass / pydantic 数据模型
  domain/       ← 纯业务规则
  application/  ← 用例、服务层
  api/          ← FastAPI / Flask 路由
tests/          ← pytest 测试，镜像 src 结构
```

---

## 关键接口与基类

[列出 Claude 需要实现或继承的核心抽象，让 Claude 知道该遵守哪些契约]

示例（Python）：
```python
# 所有存储类必须实现此接口
class IStore(ABC):
    @abstractmethod
    def add(self, item) -> None: ...
    @abstractmethod
    def get(self, id: str): ...
```

示例（C#）：
```csharp
interface IAction {
    ActionResult Execute(ActionRequest request, GameContext ctx);
}
interface IRepository<T> {
    T GetById(string id);
    void Save(T entity);
}
```

---

## 验证命令

> Claude 完成每个任务后必须执行此命令，返回码 0 才算成功。
> runner.py 的 verify_project() 会自动检测，也可在此手动指定。

```bash
# C# / Unity（自动检测 *.csproj）
dotnet build MyProject.csproj -v quiet --nologo

# Python（自动检测 requirements.txt / pyproject.toml）
pytest tests/ -q --tb=short --no-header

# Node.js（自动检测 package.json）
npm test -- --passWithNoTests

# Go（自动检测 go.mod）
go build ./...
```
