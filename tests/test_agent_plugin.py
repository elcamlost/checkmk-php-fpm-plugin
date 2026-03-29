import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

_agent_path = str(Path(__file__).parent.parent / "php-fpm" / "agents" / "plugins" / "php_fpm_pools")
_loader = SourceFileLoader("php_fpm_pools_agent", _agent_path)
_spec = importlib.util.spec_from_loader("php_fpm_pools_agent", _loader)
agent = importlib.util.module_from_spec(_spec)
_loader.exec_module(agent)


class TestParseIncludes:
    def test_plain_ascii_file(self, tmp_path):
        cfg = tmp_path / "pool.conf"
        cfg.write_text("[www]\nlisten = /run/php-fpm.sock\n", encoding="utf-8")
        lines = list(agent.parse_includes(str(cfg)))
        assert "[www]\n" in lines

    def test_non_ascii_comment_does_not_crash(self, tmp_path):
        cfg = tmp_path / "pool.conf"
        cfg.write_bytes(b"[www]\n; caf\xc3\xa9\nlisten = /run/php-fpm.sock\n")
        # Should not raise UnicodeDecodeError
        lines = list(agent.parse_includes(str(cfg)))
        assert any("listen" in line for line in lines)

    def test_non_ascii_in_latin1_does_not_crash(self, tmp_path):
        cfg = tmp_path / "pool.conf"
        # \xc2 is valid Latin-1 but not valid UTF-8 on its own
        cfg.write_bytes(b"[www]\n; caf\xe9\nlisten = /run/php-fpm.sock\n")
        lines = list(agent.parse_includes(str(cfg)))
        assert any("listen" in line for line in lines)


class TestDiscoverFpm:
    def test_non_ascii_cmdline_does_not_crash(self, tmp_path):
        # Simulate a /proc/PID/cmdline with a non-UTF-8 byte in the path
        cmdline = tmp_path / "cmdline"
        cmdline.write_bytes(b"php-fpm: master process (/etc/ph\xe9-fpm.conf)\x00")
        with patch.object(agent, "glob", return_value=[str(cmdline)]):
            result = list(agent.discover_fpm())
        # The match may or may not succeed depending on encoding, but must not crash
        assert isinstance(result, list)
