#!/usr/bin/env bash
# 从仓库生成日常安装用的精简包：./scripts/pack-skill.sh [输出.zip]
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - "$@" <<'PYTHON'
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

if len(sys.argv) > 2:
    sys.exit("用法：./scripts/pack-skill.sh [输出.zip]")
out = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("dist/explain-clearly-slim.zip")
if out.suffix.lower() != ".zip":
    sys.exit("输出文件须以 .zip 结尾")

skill = Path("skills/explain-clearly")
if skill.resolve() in out.resolve().parents:
    sys.exit("请把精简包写在 Skill 源目录之外")

# 只收录发布所需文件，避免带入本地笔记、备份或缓存。
files = [Path("LICENSE"), Path("USAGE.md")]
files.extend(skill / name for name in (
    "SKILL.md",
    "agents/openai.yaml",
    "assets/explainer.html",
    "references/diagrams.md",
    "references/interactive-html.md",
    "references/text.md",
    "scripts/check_html.py",
))
notes = """# explain-clearly 安装要点

本精简包只含日常安装 Skill 所需文件：

- `skills/explain-clearly/`（实际 Skill）
- `LICENSE`
- `USAGE.md`
- 本文件

完整仓库和 GitHub Release 的 explain-clearly.zip 还包含案例、工作流程演示和截图。那些演示不是安装 Skill 所必需的。本包不含 `examples/screenshots` 与 showcase 大图。

## 安装

把 `skills/explain-clearly/` 整个目录复制到当前 Agent 的技能目录，保留其中的参考、模板和脚本。各宿主的常见位置见 `USAGE.md`。

也可以把下面这段发给 Codex、Claude Code、WorkBuddy、Cursor 等 Agent：

> 请帮我安装 explain-clearly Skill。源目录是本包中的 skills/explain-clearly/。请按你当前 Agent 支持的安装方式完成安装，保留该目录内的参考、模板和脚本。已有同名技能时先核对来源，不覆盖其他内容；不要修改 AGENTS.md 或 CLAUDE.md。完成后告诉我如何使用，以及是否需要重启或新开对话。

Cursor 的常见目录是用户级 `~/.cursor/skills/` 或项目 `.cursor/skills/`，以 Cursor 公开文档为准。文档推导、未在 Cursor 上做统一实测。
"""

prefix = "explain-clearly-slim/"
out.parent.mkdir(parents=True, exist_ok=True)
# 在输出目录内写完再替换，打包中断时保留原来的 ZIP。
with TemporaryDirectory(dir=out.parent) as work:
    staged = Path(work) / "package.zip"
    with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            if path.absolute() != path.resolve() or not path.is_file():
                sys.exit(f"打包源文件须为普通文件，路径中不能含符号链接：{path}")
            archive.write(path, prefix + path.as_posix())
        archive.writestr(prefix + "安装要点.md", notes)
    staged.replace(out)
print(f"已写出 {out}（{len(files) + 1} 个条目）")
PYTHON
