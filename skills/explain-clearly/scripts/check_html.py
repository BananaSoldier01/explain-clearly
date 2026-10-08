#!/usr/bin/env python3
"""约定的静态 HTML 检查；不是安全、语义或可访问性认证。仅用标准库。"""
import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class Issue:
    code: str
    file: str
    detail: str


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.refs = []  # (URL, 是否运行资源)
        self.css = []
        self.js = []
        self.inline_tag = None
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in ('style', 'script'):
            self.inline_tag = tag
        if attrs.get('style'):
            self.css.append(attrs['style'])
        # href 在普通链接中是导航；样式表等 link 是运行资源。
        if tag == 'base':
            self.refs.append(('UNSUPPORTED_BASE', True))
        if attrs.get('href'):
            rel = set(attrs.get('rel', '').lower().split())
            runtime = tag == 'link' and bool(rel & {
                'stylesheet', 'preload', 'modulepreload', 'prefetch',
                'preconnect', 'dns-prefetch', 'icon', 'manifest',
            })
            self.refs.append((attrs['href'], runtime))
        for key in ('src', 'poster', 'data', 'background'):
            if attrs.get(key):
                self.refs.append((attrs[key], True))
        if attrs.get('srcset'):
            # 数据 URL 中的逗号需要更完整的 srcset 语法解析，明确报告未支持。
            if 'data:' in attrs['srcset'].lower():
                self.refs.append(('UNSUPPORTED_SRCSET', True))
            else:
                self.refs.extend((v.strip().split()[0], True)
                                 for v in attrs['srcset'].split(',') if v.strip())
        if attrs.get('action'):
            self.refs.append((attrs['action'], True))
        if attrs.get('formaction'):
            self.refs.append((attrs['formaction'], True))
        if attrs.get('srcdoc'):
            self.refs.append(('UNSUPPORTED_SRCDOC', True))
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            match = re.search(r'url\s*=\s*(.+)', attrs.get('content', ''), re.I)
            if match:
                self.refs.append((match.group(1).strip().strip('\"\''), True))
        for key, value in attributes:
            if key.startswith('on') and value:
                self.js.append(value)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ('style', 'script'):
            self.inline_tag = None

    def handle_endtag(self, tag):
        if tag == self.inline_tag:
            self.inline_tag = None

    def handle_data(self, data):
        if self.inline_tag == 'style':
            self.css.append(data)
        elif self.inline_tag == 'script':
            self.js.append(data)


def css_urls(text):
    # 不实现完整 CSS 语法；覆盖直接 url(...) 与字符串 @import。
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    urls = re.findall(r'url\(\s*[\"\']?([^\"\')]+)[\"\']?\s*\)', text, re.I)
    urls += re.findall(r'@import\s+[\"\']([^\"\']+)[\"\']', text, re.I)
    return [value.strip() for value in urls]


def js_urls(text):
    # 只识别直接字面量。动态地址、模板表达式和包装后的调用均可能漏检。
    imports = re.findall(r'\b(?:import|export)\s+(?:[^;\n]*?\s+from\s+)?[\"\']([^\"\']+)[\"\']', text)
    imports += re.findall(r'\bimport\s*\(\s*[\"\']([^\"\']+)[\"\']', text)
    calls = re.findall(r'\b(?:fetch|WebSocket|EventSource|Worker|SharedWorker|importScripts)\s*\(\s*[\"\']([^\"\']+)[\"\']', text)
    calls += re.findall(r'\.open\s*\(\s*[\"\'][^\"\']+[\"\']\s*,\s*[\"\']([^\"\']+)[\"\']', text)
    calls += re.findall(r'\bsendBeacon\s*\(\s*[\"\']([^\"\']+)[\"\']', text)
    return imports + calls


def check_html(html_path, root=None):
    entry = Path(html_path).resolve()
    scope = Path(root).resolve() if root else entry.parent
    issues, visited, documents = [], set(), {}

    def report(code, path, detail):
        issues.append(Issue(code, str(path), detail))

    def contained(path):
        return path.is_relative_to(scope)

    def load_doc(path):
        if path not in documents:
            documents[path] = Document(path.read_text(encoding='utf-8'))
        return documents[path]

    def reference(origin, raw, runtime):
        if raw.startswith('UNSUPPORTED_'):
            report('unsupported-inline-resource', origin, raw)
            return
        parts = urlsplit(raw.strip())
        scheme = parts.scheme.lower()
        if scheme == 'javascript':
            report('executable-url', origin, raw)
            return
        if scheme or parts.netloc:
            if runtime and scheme != 'data':
                report('external-runtime', origin, raw)
            return  # 普通 http/mailto 等导航不属于自动运行依赖。
        target = (origin.parent / unquote(parts.path)).resolve() if parts.path else origin
        if not contained(target):
            report('outside-root', origin, raw)
            return
        if not target.is_file():
            report('missing-local', origin, raw)
            return
        if parts.fragment and target.suffix.lower() in ('.html', '.htm'):
            try:
                ids = load_doc(target).ids
                if unquote(parts.fragment) not in ids:
                    report('missing-fragment', origin, raw)
            except (OSError, UnicodeError) as error:
                report('unreadable', target, str(error))
        # 导航到另一 HTML 时也检查其结构；CSS/JS 只作为运行资源递归。
        if target.suffix.lower() in ('.html', '.htm') or (
            runtime and target.suffix.lower() in ('.css', '.js', '.mjs')
        ):
            visit(target)

    def visit(path):
        if path in visited:
            return
        visited.add(path)
        if not contained(path):
            report('outside-root', path, '入口不在指定交付目录内')
            return
        try:
            suffix = path.suffix.lower()
            if suffix in ('.html', '.htm'):
                doc = load_doc(path)
                for identifier, count in Counter(doc.ids).items():
                    if count > 1:
                        report('duplicate-id', path, f'{identifier!r} 出现 {count} 次')
                for raw, runtime in doc.refs:
                    reference(path, raw, runtime)
                for style in doc.css:
                    for raw in css_urls(style):
                        reference(path, raw, True)
                for script in doc.js:
                    for raw in js_urls(script):
                        reference(path, raw, True)
            else:
                text = path.read_text(encoding='utf-8')
                for raw in css_urls(text) if suffix == '.css' else js_urls(text):
                    reference(path, raw, True)
        except (OSError, UnicodeError, ValueError) as error:
            report('unreadable', path, str(error))

    visit(entry)
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('--root', type=Path, help='允许本地引用的交付目录，默认 HTML 所在目录')
    parser.add_argument('--json', action='store_true', help='输出机器可读结果')
    args = parser.parse_args()
    issues = check_html(args.html, args.root)
    if args.json:
        print(json.dumps({'ok': not issues, 'issues': [asdict(i) for i in issues],
                          'scope': '约定的静态检查；不证明语义、全安全或完整可访问性'},
                         ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f'{issue.code}: {issue.file}: {issue.detail}')
    else:
        print('PASS：约定的静态规则未发现问题（非语义、安全或可访问性认证）。')
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
