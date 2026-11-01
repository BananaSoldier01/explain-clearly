#!/usr/bin/env bash
# 从仓库打出日常安装用的精简包。
# 在仓库根运行：./scripts/pack-skill.sh [输出.zip]
# 默认写出 dist/explain-clearly-slim.zip。
# 含 skills/explain-clearly/、LICENSE、USAGE.md 与安装要点。
# 不含 examples/screenshots、showcase 大图及其他演示。
# 用 python3 标准库 zipfile 打包，不依赖 zip 命令。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT="${1:-dist/explain-clearly-slim.zip}"
case "$OUT" in
  /*) ;;
  *) OUT="$ROOT/$OUT" ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
  echo "需要 python3" >&2
  exit 1
fi

STAGE="$(mktemp -d)"
cleanup() { rm -rf "$STAGE"; }
trap cleanup EXIT

DEST="$STAGE/explain-clearly-slim"
mkdir -p "$DEST/skills"
cp -a "$ROOT/skills/explain-clearly" "$DEST/skills/"
cp -a "$ROOT/LICENSE" "$ROOT/USAGE.md" "$DEST/"

cat > "$DEST/安装要点.md" << 'EOF'
# explain-clearly 安装要点

当前正式版：**v0.1.2**。

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
EOF

python3 - "$STAGE" "$OUT" << 'PY'
import sys
import zipfile
from pathlib import Path

stage = Path(sys.argv[1])
out = Path(sys.argv[2])
out.parent.mkdir(parents=True, exist_ok=True)
if out.exists():
    out.unlink()

names = []
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.name == ".DS_Store" or path.suffix == ".pyc":
            continue
        rel = path.relative_to(stage).as_posix()
        if (
            "examples/screenshots" in rel
            or "examples/showcase" in rel
            or "/examples/" in rel
            or rel.startswith("examples/")
        ):
            print(f"精简包意外包含演示：{rel}", file=sys.stderr)
            sys.exit(1)
        archive.write(path, rel)
        names.append(rel)

need = [
    "explain-clearly-slim/skills/explain-clearly/SKILL.md",
    "explain-clearly-slim/LICENSE",
    "explain-clearly-slim/USAGE.md",
    "explain-clearly-slim/安装要点.md",
]
missing = [name for name in need if name not in names]
if missing:
    print("精简包缺少：", *missing, sep="\n", file=sys.stderr)
    sys.exit(1)
print(f"已写出 {out}（{len(names)} 个条目）")
for name in names:
    print(name)
PY
