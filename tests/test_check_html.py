"""真实临时 HTML 正反测试；所有临时文件都在交付包 tests 内，并在结束时移除。"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/explain-clearly/scripts/check_html.py'
SPEC = importlib.util.spec_from_file_location('check_html', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class HtmlChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='html-test-', dir=ROOT / 'tests')
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def codes(self, html, files=None):
        for name, text in (files or {}).items():
            self.write(name, text)
        path = self.write('index.html', html)
        return {i.code for i in MODULE.check_html(path, self.root)}

    def test_valid_local_and_external_navigation(self):
        self.assertEqual(self.codes('<p id="yes">好</p><a href="#yes">内部</a>'
                                    '<img src="a.svg"><a href="https://example.com">资料</a>',
                                    {'a.svg': '<svg xmlns="http://www.w3.org/2000/svg"/>'}), set())

    def test_duplicate_ids(self):
        self.assertIn('duplicate-id', self.codes('<p id="x"></p><span id="x"></span>'))

    def test_missing_image(self):
        self.assertIn('missing-local', self.codes('<img src="missing.png">'))

    def test_missing_fragment(self):
        self.assertIn('missing-fragment', self.codes('<a href="#missing">链接</a>'))

    def test_other_file_fragment_and_encoded_path(self):
        self.assertEqual(self.codes('<a href="other%20page.html#target">链接</a>',
                                    {'other page.html': '<p id="target">目标</p>'}), set())
        self.assertIn('missing-fragment', self.codes('<a href="other.html#gone">链接</a>',
                                                    {'other.html': '<p id="target">目标</p>'}))

    def test_external_script(self):
        self.assertIn('external-runtime', self.codes('<script src="https://cdn.example/a.js"></script>'))

    def test_protocol_relative_style(self):
        self.assertIn('external-runtime', self.codes('<link rel="stylesheet" href="//cdn.example/a.css">'))

    def test_css_url_and_import(self):
        for css in ('body{background:url(https://example.com/a.png)}',
                    '@import "https://example.com/a.css";'):
            with self.subTest(css=css):
                self.assertIn('external-runtime', self.codes('<style>' + css + '</style>'))

    def test_recursive_local_css(self):
        self.assertIn('missing-local', self.codes('<link rel="stylesheet" href="a.css">',
                                                 {'a.css': 'body{background:url(missing.svg)}'}))

    def test_recursive_local_js_import(self):
        self.assertIn('external-runtime', self.codes('<script src="a.js"></script>',
            {'a.js': 'import "./b.js";', 'b.js': 'fetch("https://example.com/data");'}))

    def test_literal_network_calls(self):
        for js in ('fetch("https://api.example/data")', 'new WebSocket("wss://api.example")',
                   'xhr.open("GET", "https://api.example/data")',
                   'navigator.sendBeacon("https://api.example/metrics", "x")',
                   'import("https://cdn.example/mod.js")'):
            with self.subTest(js=js):
                self.assertIn('external-runtime', self.codes('<script>' + js + '</script>'))

    def test_srcset(self):
        self.assertIn('missing-local', self.codes('<img srcset="ok.png 1x, gone.png 2x">', {'ok.png': 'x'}))
        self.assertIn('unsupported-inline-resource', self.codes('<img srcset="data:image/png;base64,AAAA 1x">'))

    def test_external_form_and_refresh(self):
        for html in ('<form action="https://example.com/upload"></form>',
                     '<meta http-equiv="refresh" content="0; url=https://example.com">'):
            with self.subTest(html=html):
                self.assertIn('external-runtime', self.codes(html))

    def test_unsupported_base_and_srcdoc(self):
        for html in ('<base href="https://example.com/">', '<iframe srcdoc="&lt;p&gt;x&lt;/p&gt;"></iframe>'):
            self.assertIn('unsupported-inline-resource', self.codes(html))

    def test_data_resource(self):
        self.assertEqual(self.codes('<img src="data:image/png;base64,AAAA">'), set())

    def test_executable_url(self):
        self.assertIn('executable-url', self.codes('<a href="javascript:alert(1)">运行</a>'))

    def test_outside_scope(self):
        self.assertIn('outside-root', self.codes('<img src="../outside.png">'))

    def test_cycle_terminates(self):
        self.assertEqual(self.codes('<a href="second.html">下一页</a>',
                                    {'second.html': '<a href="index.html">返回</a>'}), set())

    def test_missing_entry_and_non_utf8(self):
        self.assertEqual(MODULE.check_html(self.root / 'absent.html', self.root)[0].code, 'unreadable')
        path = self.root / 'bad.html'
        path.write_bytes(b'\xff')
        self.assertEqual(MODULE.check_html(path, self.root)[0].code, 'unreadable')

    def test_cli_exit_codes_and_json(self):
        path = self.write('index.html', '<p id="x">有效</p>')
        good = subprocess.run([sys.executable, str(SCRIPT), str(path), '--json'], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0)
        self.assertTrue(json.loads(good.stdout)['ok'])
        path.write_text('<p id="x"></p><p id="x"></p>')
        bad = subprocess.run([sys.executable, str(SCRIPT), str(path), '--json'], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertFalse(json.loads(bad.stdout)['ok'])

    def test_known_dynamic_address_limit(self):
        # 明确保留能力边界：这不会被字面量提取器识别；不是“已证明离线”。
        self.assertEqual(self.codes('<script>const endpoint = "https://api.example"; fetch(endpoint)</script>'), set())

    def test_delivered_html(self):
        for path in (ROOT / 'examples/interactive.html', ROOT / 'skills/explain-clearly/assets/explainer.html'):
            with self.subTest(path=path):
                self.assertEqual(MODULE.check_html(path, ROOT), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
