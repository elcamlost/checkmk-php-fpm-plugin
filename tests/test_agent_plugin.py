import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
from textwrap import dedent
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


class TestParseFpmConfig:
    def _parse(self, ini_text):
        return list(agent.parse_fpm_config(iter(ini_text.splitlines(keepends=True))))

    def test_uses_listen_as_socket(self):
        result = self._parse(
            dedent("""\
            [www]
            listen = /run/php-fpm.sock
            pm.status_path = /status
            """)
        )
        assert result[0]["socket"] == "/run/php-fpm.sock"

    def test_uses_status_listen_when_set(self):
        result = self._parse(
            dedent("""\
            [www]
            listen = /run/php-fpm.sock
            pm.status_listen = /run/php-fpm-status.sock
            pm.status_path = /status
            """)
        )
        assert result[0]["socket"] == "/run/php-fpm-status.sock"

    def test_falls_back_to_listen_when_status_listen_empty(self):
        result = self._parse(
            dedent("""\
            [www]
            listen = /run/php-fpm.sock
            pm.status_listen =
            pm.status_path = /status
            """)
        )
        assert result[0]["socket"] == "/run/php-fpm.sock"

    def test_result_includes_pool_name(self):
        result = self._parse(
            dedent("""\
            [mypool]
            listen = /run/php-fpm.sock
            pm.status_path = /status
            """)
        )
        assert result[0]["pool_name"] == "mypool"

    def test_status_listen_supports_pool_variable(self):
        result = self._parse(
            dedent("""\
            [mypool]
            listen = /run/php-fpm.sock
            pm.status_listen = /run/$pool-status.sock
            pm.status_path = /status
            """)
        )
        assert result[0]["socket"] == "/run/mypool-status.sock"


class TestFCGIStatusClientPrintStatus:
    def _make_client(self, pool="www", pm="dynamic"):
        client = agent.FCGIStatusClient.__new__(agent.FCGIStatusClient)
        client.pool_name = None
        client.status_data = (
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
            + json.dumps({"pool": pool, "process manager": pm, "active processes": 1}).encode()
        )
        return client

    def test_output_has_four_fields(self, capsys):
        self._make_client().print_status()
        fields = capsys.readouterr().out.splitlines()[0].split()
        assert len(fields) == 4

    def test_pool_name_is_first_field(self, capsys):
        self._make_client(pool="www@a1b2c3d4").print_status()
        line = capsys.readouterr().out.splitlines()[0]
        assert line.split()[0] == "www@a1b2c3d4"


class TestMakeQualifier:
    def test_extracts_version_from_debian_path(self):
        assert agent.make_qualifier("/etc/php/8.1/fpm/php-fpm.conf") == "8.1"

    def test_extracts_version_from_php84_path(self):
        assert agent.make_qualifier("/etc/php/8.4/fpm/php-fpm.conf") == "8.4"

    def test_falls_back_to_sha_when_no_version(self):
        result = agent.make_qualifier("/etc/php-fpm.conf")
        assert len(result) == 8
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha_is_stable(self):
        assert agent.make_qualifier("/etc/php-fpm.conf") == agent.make_qualifier("/etc/php-fpm.conf")

    def test_different_paths_give_different_sha(self):
        assert agent.make_qualifier("/etc/php-fpm-a.conf") != agent.make_qualifier("/etc/php-fpm-b.conf")

    def test_collision_falls_back_to_sha(self):
        # Two paths that would produce the same version qualifier
        q1 = agent.make_qualifier("/etc/php/8.1/fpm/php-fpm.conf", taken={"8.1"})
        assert len(q1) == 8  # SHA fallback

    def test_no_collision_returns_version(self):
        q1 = agent.make_qualifier("/etc/php/8.1/fpm/php-fpm.conf", taken={"8.4"})
        assert q1 == "8.1"


class TestDiscoverFpm:
    def test_yields_configfile_and_pid(self, tmp_path):
        proc_dir = tmp_path / "1234"
        proc_dir.mkdir()
        cmdline = proc_dir / "cmdline"
        cmdline.write_bytes(b"php-fpm: master process (/etc/php-fpm.conf)\x00")
        with patch.object(agent, "glob", return_value=[str(cmdline)]):
            result = list(agent.discover_fpm())
        assert len(result) == 1
        configfile, pid = result[0]
        assert configfile == "/etc/php-fpm.conf"
        assert pid == 1234

    def test_non_ascii_cmdline_does_not_crash(self, tmp_path):
        proc_dir = tmp_path / "5678"
        proc_dir.mkdir()
        cmdline = proc_dir / "cmdline"
        cmdline.write_bytes(b"php-fpm: master process (/etc/ph\xe9-fpm.conf)\x00")
        with patch.object(agent, "glob", return_value=[str(cmdline)]):
            result = list(agent.discover_fpm())
        assert isinstance(result, list)


class TestGetWorkerRss:
    def _make_proc(self, tmp_path, pid, cmdline, vmrss_kb):
        proc_dir = tmp_path / str(pid)
        proc_dir.mkdir()
        (proc_dir / "cmdline").write_text(cmdline, encoding="utf-8")
        (proc_dir / "status").write_text("VmRSS:\t%d kB\n" % vmrss_kb, encoding="utf-8")

    def _make_master(self, tmp_path, master_pid, child_pids):
        master_dir = tmp_path / str(master_pid) / "task" / str(master_pid)
        master_dir.mkdir(parents=True)
        (master_dir / "children").write_text(" ".join(str(p) for p in child_pids), encoding="utf-8")

    def test_returns_rss_for_matching_workers(self, tmp_path):
        self._make_master(tmp_path, master_pid=10, child_pids=[101, 102])
        self._make_proc(tmp_path, 101, "php-fpm: pool www", vmrss_kb=1024)
        self._make_proc(tmp_path, 102, "php-fpm: pool www", vmrss_kb=2048)
        total_rss, avg_rss = agent.get_worker_rss(10, "www", proc_root=str(tmp_path))
        assert total_rss == 3 * 1024 * 1024
        assert avg_rss == 3 * 1024 * 512

    def test_excludes_wrong_pool(self, tmp_path):
        self._make_master(tmp_path, master_pid=10, child_pids=[101, 102])
        self._make_proc(tmp_path, 101, "php-fpm: pool www", vmrss_kb=1024)
        self._make_proc(tmp_path, 102, "php-fpm: pool api", vmrss_kb=2048)
        total_rss, avg_rss = agent.get_worker_rss(10, "www", proc_root=str(tmp_path))
        assert total_rss == 1 * 1024 * 1024
        assert avg_rss == 1 * 1024 * 1024

    def test_returns_empty_when_no_workers(self, tmp_path):
        self._make_master(tmp_path, master_pid=10, child_pids=[])
        total_rss, avg_rss = agent.get_worker_rss(10, "www", proc_root=str(tmp_path))
        assert total_rss is None
        assert avg_rss is None

    def test_returns_empty_when_children_file_missing(self, tmp_path):
        total_rss, avg_rss = agent.get_worker_rss(99999, "www", proc_root=str(tmp_path))
        assert total_rss is None
        assert avg_rss is None
