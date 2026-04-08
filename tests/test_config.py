import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_REAL_CONFIG = Path(__file__).parents[1] / "config.toml"
_MINIMAL_TOML = b'[bitcoin.price]\nservice_endpoint = "http://example.com"\n'


class TestConfigLoader(unittest.TestCase):
    def _fresh_config_module(self):
        sys.modules.pop("btcticker.config", None)
        import btcticker.config

        return btcticker.config

    def test_loads_from_cwd_when_config_toml_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd_config = Path(tmpdir) / "config.toml"
            cwd_config.write_bytes(_MINIMAL_TOML)

            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                mod = self._fresh_config_module()

            self.assertEqual(mod._CONFIG_PATH, cwd_config)
            result = mod.config()
            self.assertIn("bitcoin", result)

    def test_falls_back_to_repo_config_when_no_cwd_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                mod = self._fresh_config_module()

            self.assertEqual(mod._CONFIG_PATH, mod._REPO_CONFIG)

    def test_config_loads_from_repo_config(self):
        mod = self._fresh_config_module()
        mod._CONFIG_PATH = _REAL_CONFIG
        mod.config.cache_clear()
        result = mod.config()
        self.assertIsInstance(result, dict)
        self.assertIn("bitcoin", result)

    def tearDown(self) -> None:
        sys.modules.pop("btcticker.config", None)


if __name__ == "__main__":
    unittest.main()
