import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'release_audit', Path(__file__).resolve().parents[1] / 'scripts' / 'public_release_audit.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PublicReleaseAuditTests(unittest.TestCase):
    def test_clean_public_document(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'README.md').write_text('Use localhost:8787 on macOS.')
            self.assertEqual(module.audit(Path(folder)), [])

    def test_rejects_auth_file_and_real_env(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.env').write_text('NOT_AN_ACTUAL_KEY=placeholder')
            (root / '.auth').mkdir()
            (root / '.auth' / 'codex.json').write_text('{}')
            self.assertTrue(module.audit(root))

    def test_rejects_embedded_email_and_home_path(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'README.md'
            p.write_text('Contact foo' + '@' + 'mail.example and see ' + '/' + 'Users/' + 'tester/secret')
            findings = [x[1] for x in module.audit(Path(folder))]
            self.assertIn('real-email-address', findings)
            self.assertIn('mac-user-home', findings)

    def test_rejects_nonloopback_ip(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / 'README.md').write_text('Remote 192.0.' + '2.1')
            self.assertTrue(module.audit(Path(folder)))


if __name__ == '__main__':
    unittest.main()
