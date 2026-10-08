#!/usr/bin/env python3
"""此包的文件、精简元数据、Python语法及Markdown相对文件链接检查；非通用Skill认证。"""
import ast
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    'README.md', 'LICENSE', 'skills/explain-clearly/SKILL.md',
    'skills/explain-clearly/agents/openai.yaml',
    'skills/explain-clearly/references/text.md',
    'skills/explain-clearly/references/diagrams.md',
    'skills/explain-clearly/references/interactive-html.md',
    'skills/explain-clearly/assets/explainer.html',
    'skills/explain-clearly/scripts/check_html.py',
    'examples/text.md', 'examples/diagram.md', 'examples/interactive.html',
    'tests/acceptance.md', 'fixtures/source-report.md', 'tests/test_check_html.py',
)


def check():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file() or not (ROOT / name).stat().st_size:
            errors.append('缺失或空文件：' + name)
    skill = (ROOT / 'skills/explain-clearly/SKILL.md').read_text()
    front = re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n', skill)
    if not front or front[1] != 'explain-clearly' or len(front[2]) > 1024:
        errors.append('入口的两字段frontmatter格式或值不符')
    ui = (ROOT / 'skills/explain-clearly/agents/openai.yaml').read_text()
    for field in ('display_name', 'short_description', 'default_prompt'):
        found = re.search(r'^  ' + field + r': "([^"\n]+)"$', ui, re.M)
        if not found:
            errors.append('UI字段缺失或非本包双引号格式：' + field)
        elif field == 'short_description' and not 25 <= len(found[1]) <= 64:
            errors.append('UI简述长度超限')
        elif field == 'default_prompt' and '$explain-clearly' not in found[1]:
            errors.append('默认提示缺少技能名')
    if 'allow_implicit_invocation: true' not in ui:
        errors.append('UI自动选择声明不符')
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        if path.name == 'AGENTS.md' or '.agents' in path.parts or '.codex' in path.parts:
            errors.append('包中有不应出现的自动发现/指引路径：' + str(path))
        if path.suffix == '.py':
            try:
                ast.parse(path.read_text(), filename=str(path))
            except SyntaxError as e:
                errors.append(str(e))
        if path.suffix == '.md':
            # 本包不使用相对标题锚点；仅验证 Markdown 的本地文件链接。
            body = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
            for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', body):
                raw = match[1].strip().strip('<>')
                parts = urlsplit(raw)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                target = (path.parent / unquote(parts.path)).resolve()
                if not target.is_relative_to(ROOT) or not target.is_file():
                    errors.append(f'{path.relative_to(ROOT)}：无效相对链接 {raw}')
    return errors


if __name__ == '__main__':
    findings = check()
    for finding in findings:
        print(finding)
    if not findings:
        print('PASS：包结构、当前元数据格式、Python语法、Markdown本地文件链接。')
    raise SystemExit(bool(findings))
