"""从无 .git 的源目录打精简包，检查打包内容与失败后的状态。"""
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from check_package import REQUIRED


ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = [name for name in REQUIRED if name.startswith('skills/')]
INPUTS = ['LICENSE', 'USAGE.md', *SKILL_FILES]


@unittest.skipUnless(os.name == 'posix' and shutil.which('bash'), '打包脚本需要 POSIX 环境和 Bash')
class SlimPackageTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name in ['scripts/pack-skill.sh', *INPUTS]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        self.output = self.root / 'dist/explain-clearly-slim.zip'

    def pack(self, *args):
        return subprocess.run([str(self.root / 'scripts/pack-skill.sh'), *args],
                              capture_output=True, text=True)

    def test_package_contains_only_install_files(self):
        (self.root / 'skills/explain-clearly/local-notes.txt').write_text('本机笔记')
        result = self.pack()
        self.assertEqual(result.returncode, 0, result.stderr)
        prefix = 'explain-clearly-slim/'
        with ZipFile(self.output) as archive:
            self.assertCountEqual(archive.namelist(), [prefix + name for name in [*INPUTS, '安装要点.md']])
            for name in INPUTS:
                self.assertEqual(archive.read(prefix + name), (self.root / name).read_bytes())

    def test_source_error_preserves_previous_package(self):
        self.assertEqual(self.pack().returncode, 0)
        previous = self.output.read_bytes()
        source = self.root / 'skills/explain-clearly/assets/explainer.html'
        source.unlink()
        for scenario in ('missing', 'symlink'):
            with self.subTest(scenario=scenario):
                if scenario == 'symlink':
                    source.symlink_to(self.root / 'USAGE.md')
                self.assertNotEqual(self.pack().returncode, 0)
                self.assertEqual(self.output.read_bytes(), previous)

    def test_rejects_source_output_paths(self):
        usage = self.root / 'USAGE.md'
        original = usage.read_bytes()
        self.assertNotEqual(self.pack(usage).returncode, 0)
        self.assertEqual(usage.read_bytes(), original)
        nested = self.root / 'skills/explain-clearly/package.zip'
        self.assertNotEqual(self.pack(nested).returncode, 0)
        self.assertFalse(nested.exists())


if __name__ == '__main__':
    unittest.main()
