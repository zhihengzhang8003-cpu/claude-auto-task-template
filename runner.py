#!/usr/bin/env python3
"""
Claude 自动任务 Runner — 通用模板

用法:
  python runner.py              # 持续运行直到所有任务完成
  python runner.py 5            # 最多执行 5 个任务
  python runner.py --dry-run    # 只打印任务，不执行

前提:
  - claude CLI 在 PATH 中（Claude Code CLI）
  - 项目验证命令可用（dotnet / pytest / npm test 等）
  - TaskPlan.md 存在且包含 ⏳ 任务
"""

import subprocess
import sys
import re
import shutil
import os
import io
from pathlib import Path
from datetime import datetime

# 修复 Windows 中文乱码
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════
# 配置区 — 每个项目只需修改这里
# ═══════════════════════════════════════════════════════════

PROJECT_DIR  = Path(r"C:\替换为你的项目路径")   # ← 必须修改
TASK_PLAN    = PROJECT_DIR / "Docs" / "TaskPlan.md"
LESSONS      = PROJECT_DIR / "Docs" / "LessonsLearned.md"
ARCH_DOC     = PROJECT_DIR / "Docs" / "Architecture.md"
CODE_RULES   = PROJECT_DIR / "Docs" / "CodeRules.md"
LOG_FILE     = PROJECT_DIR / "Docs" / "runner-log.md"

CLAUDE_CMD   = "claude"
MAX_RETRIES  = 2      # 验证失败后最多重试次数
TASK_TIMEOUT = 600    # 每个任务 Claude 调用超时（秒）


def verify_project() -> tuple[bool, str]:
    """
    自动检测项目类型并执行验证。
    检测顺序：Unity csproj → 任意 csproj → Python → Node.js → Go → 跳过

    如需手动指定，注释掉自动检测部分，直接赋值 cmd：
        cmd = ["dotnet", "build", "MyProject.csproj", "-v", "quiet", "--nologo"]
        cmd = ["pytest", "tests/", "-q", "--tb=short"]
        cmd = ["npm", "test", "--", "--passWithNoTests"]
        cmd = ["go", "build", "./..."]
    """
    # 自动检测
    unity_csproj = PROJECT_DIR / "Assembly-CSharp.csproj"
    any_csproj   = list(PROJECT_DIR.glob("*.csproj"))
    has_pytest   = (PROJECT_DIR / "requirements.txt").exists() or (PROJECT_DIR / "pyproject.toml").exists()
    has_npm      = (PROJECT_DIR / "package.json").exists()
    has_go       = (PROJECT_DIR / "go.mod").exists()

    if unity_csproj.exists():
        cmd = ["dotnet", "build", str(unity_csproj), "-v", "quiet", "--nologo"]
    elif any_csproj:
        cmd = ["dotnet", "build", str(any_csproj[0]), "-v", "quiet", "--nologo"]
    elif has_pytest:
        cmd = ["pytest", "tests/", "-q", "--tb=short", "--no-header"]
    elif has_npm:
        cmd = ["npm", "test", "--", "--passWithNoTests"]
    elif has_go:
        cmd = ["go", "build", "./..."]
    else:
        return True, ""   # 无法识别的项目类型，跳过验证

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_DIR),
        timeout=120,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        return True, ""
    output = result.stdout + result.stderr
    errors = [
        l for l in output.splitlines()
        if re.search(r"\berror\b", l, re.IGNORECASE) and not l.strip().startswith("//")
    ]
    return False, "\n".join(errors[:30]) if errors else output[:500]

# ═══════════════════════════════════════════════════════════
# 以下一般不需要修改
# ═══════════════════════════════════════════════════════════


def now() -> str:
    return datetime.now().strftime("%y%m%d %H%M")


def log(msg: str) -> None:
    line = f"- {now()} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def get_next_task() -> tuple[str | None, str | None, str | None]:
    """返回第一个 ⏳ 任务的 (id, title, 完整任务块)"""
    content = read_file(TASK_PLAN)
    match = re.search(r"### (T\d+) ⏳ (.+)", content)
    if not match:
        return None, None, None
    task_id = match.group(1)
    title   = match.group(2).strip()
    start   = match.start()
    nxt     = re.search(r"\n### T\d+", content[start + 1:])
    end     = start + 1 + nxt.start() if nxt else len(content)
    return task_id, title, content[start:end].strip()


def mark_task(task_id: str, status: str) -> None:
    """status: 'done'(✅) 或 'warn'(⚠️)"""
    content = read_file(TASK_PLAN)
    symbol  = "✅" if status == "done" else "⚠️"
    content = re.sub(rf"(### {task_id}) ⏳", rf"\1 {symbol}", content, count=1)
    done = len(re.findall(r"✅", content))
    warn = len(re.findall(r"⚠️", content))
    pend = len(re.findall(r"⏳", content))
    content = re.sub(r"\| ⏳ 待办 \| \d+ \|", f"| ⏳ 待办 | {pend} |", content)
    content = re.sub(r"\| ✅ 完成 \| \d+ \|", f"| ✅ 完成 | {done} |", content)
    content = re.sub(r"\| ⚠️ 警告 \| \d+ \|", f"| ⚠️ 警告 | {warn} |", content)
    TASK_PLAN.write_text(content, encoding="utf-8")


def build_prompt(task_block: str, error_context: str = "") -> str:
    arch    = read_file(ARCH_DOC)
    rules   = read_file(CODE_RULES)
    lessons = read_file(LESSONS)

    error_section = ""
    if error_context:
        error_section = f"""
## 上次验证失败，请修复以下错误
```
{error_context[:1500]}
```
只修复错误，不添加新功能。
"""

    return f"""你是本项目的开发工程师。

## 当前任务
{task_block}

---

## 架构规范（必须遵守）
{arch}

## 代码规范
{rules}

## 经验教训（避免已知坑）
{lessons if lessons.strip() else "（暂无）"}

---

## 执行规则
1. 只实现上述任务要求，不扩展
2. 最多新建/修改 3 个文件
3. 完成后执行验证（见 Architecture.md 末尾的验证命令）
4. 若发现新的经验教训，追加到 Docs/LessonsLearned.md
5. 最后输出修改的文件路径列表（每行一个路径）
{error_section}
直接执行，无需确认。
"""


def run_claude(prompt: str) -> tuple[str, int]:
    cmd = [
        CLAUDE_CMD,
        "--print",
        "--output-format", "text",
        "--allowedTools", "Read,Edit,Write,Bash,Glob,Grep",
        "-p", prompt,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR),
            timeout=TASK_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        log(f"⏱ Claude 调用超时（{TASK_TIMEOUT}s）")
        return "", 1
    except FileNotFoundError:
        log(f"❌ 找不到 claude 命令：{CLAUDE_CMD}")
        log("   请确认 Claude Code CLI 已安装并在 PATH 中")
        sys.exit(1)


def check_prerequisites() -> bool:
    ok = True
    if "替换" in str(PROJECT_DIR) or not PROJECT_DIR.exists():
        print(f"❌ PROJECT_DIR 未配置或路径不存在：{PROJECT_DIR}")
        print("   请编辑 runner.py 顶部的 PROJECT_DIR = Path(r'...')")
        ok = False
    if not shutil.which(CLAUDE_CMD):
        print(f"❌ {CLAUDE_CMD} 未找到，请确认 Claude Code CLI 已安装")
        ok = False
    if not TASK_PLAN.exists():
        print(f"❌ 找不到 {TASK_PLAN}")
        ok = False
    return ok


def run(max_tasks: int = 999, dry_run: bool = False) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## runner 启动 {now()}\n")

    log(f"=== Runner 启动 | max_tasks={max_tasks} dry_run={dry_run} ===")

    if not check_prerequisites():
        sys.exit(1)

    tasks_done = 0

    while tasks_done < max_tasks:
        task_id, title, task_block = get_next_task()
        if task_id is None:
            log("🎉 所有任务已完成！")
            break

        log(f"── 开始 {task_id}: {title}")

        if dry_run:
            log("[dry-run] 跳过执行")
            tasks_done += 1
            continue

        error_context = ""
        success       = False

        for attempt in range(1, MAX_RETRIES + 2):
            if attempt == 1:
                log("调用 Claude Code...")
            else:
                log(f"第 {attempt} 次尝试（修复验证错误）...")

            prompt       = build_prompt(task_block, error_context)
            stdout, code = run_claude(prompt)

            if code != 0:
                log(f"⚠ Claude 返回 exit={code}，跳过此任务")
                break

            ok, error_context = verify_project()
            if ok:
                success = True
                log(f"✅ {task_id} 验证通过")
                break
            else:
                log(f"验证失败（attempt {attempt}/{MAX_RETRIES + 1}）")
                if attempt >= MAX_RETRIES + 1:
                    log("⚠ 超过最大重试次数，标记警告，请人工检查")

        mark_task(task_id, "done" if success else "warn")
        tasks_done += 1
        log(f"── 完成 {task_id} ({'✅' if success else '⚠️'}) | 进度 {tasks_done}/{max_tasks}")

    log("=== Runner 结束 ===")


if __name__ == "__main__":
    args      = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags     = [a for a in sys.argv[1:] if a.startswith("--")]
    max_tasks = int(args[0]) if args else 999
    dry_run   = "--dry-run" in flags
    run(max_tasks, dry_run)
