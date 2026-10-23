"""Distribution and HTML checks use temporary directories and fictitious data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
manage=load('manage',ROOT/'tools/manage.py')
inspect=load('inspect_html',ROOT/'tools/inspect_html.py')

class Distribution(unittest.TestCase):
    def test_upgrade_retains_private_output_and_other_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp); other=parent/'another-skill';other.mkdir()
            target=manage.install('codex',parent)
            (target/'output').mkdir(); (target/'output/private.txt').write_text('user-owned')
            (target/'obsolete.txt').write_text('retired implementation')
            manage.install('codex',parent)
            self.assertEqual((target/'output/private.txt').read_text(),'user-owned')
            self.assertFalse((target/'obsolete.txt').exists()); self.assertTrue(other.exists())
    def test_png_exports_have_real_png_headers_and_sufficient_resolution(self):
        import struct
        for folder in (ROOT/'docs',ROOT/'skills/claim-atlas/assets'):
            for image in folder.glob('*.png'):
                self.assertEqual(image.read_bytes()[:8],b'\x89PNG\r\n\x1a\n',image.name)
        for relative,minimum in [('docs/logo-preview.png',2400),('docs/preview-desktop.png',2400),('skills/claim-atlas/assets/logo-mark.png',1024)]:
            width,height=struct.unpack('>II',(ROOT/relative).read_bytes()[16:24])
            self.assertGreaterEqual(width,minimum)
            self.assertGreater(height,0)

    def test_resource_order_is_platform_independent(self):
        names=[name for name,_ in manage.sources()]
        self.assertEqual(names,sorted(names))

    def test_binary_assets_preserve_all_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            skill=Path(temp); payload=b'\x89PNG\r\n\x1a\nraw\r\nbytes'
            (skill/'mark.png').write_bytes(payload)
            with patch.object(manage,'SKILL',skill):
                self.assertEqual(dict(manage.sources())['mark.png'],payload)

    def test_release_is_deterministic_and_private_files_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp);manage.build(directory)
            first=(directory/'claim-atlas.zip').read_bytes();manage.build(directory)
            self.assertEqual(first,(directory/'claim-atlas.zip').read_bytes())
            self.assertEqual(first,(directory/'claim-atlas.skill').read_bytes())
            with zipfile.ZipFile(directory/'claim-atlas.zip') as archive:
                self.assertFalse(any('/output/' in p or '__pycache__' in p for p in archive.namelist()))
                self.assertIn('claim-atlas/LICENSE',archive.namelist())
    def test_failed_replacement_restores_install(self):
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp);target=manage.install('agents',parent)
            (target/'sentinel').write_text('keep')
            real=Path.rename
            def rename(path,dest):
                if path.name=='skill': raise OSError('simulated final rename failure')
                return real(path,dest)
            with patch.object(Path,'rename',rename):
                with self.assertRaises(OSError):manage.install('agents',parent)
            self.assertEqual((target/'sentinel').read_text(),'keep')
    def test_symlink_install_is_refused_when_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            parent=Path(temp);other=parent/'linked';other.mkdir()
            try:(parent/'claim-atlas').symlink_to(other,target_is_directory=True)
            except OSError:self.skipTest('Platform does not permit creating symlinks')
            with self.assertRaises(ValueError):manage.install('agents',parent)
    def test_inspector_rejects_script_and_broken_links(self):
        original=(ROOT/'docs/demo-report.html').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'report.html';path.write_text(original.replace('</body>','<script>bad()</script><a href="#absent">missing</a></body>'),encoding='utf-8')
            issues=inspect.audit(path)
            self.assertIn('Unexpected active or external-resource element',issues)
            self.assertIn('Broken internal reference',issues)
