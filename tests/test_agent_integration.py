from unittest.mock import patch

from tests.conftest import (
    FakeFCGISocket,
    agent,
    make_fcgi_response,
    make_master,
    make_pool_config,
    make_worker,
    patch_tcp_sockets,
    patch_unix_sockets,
)

POOL_STATUS = {
    "pool": "www",
    "process manager": "dynamic",
    "active processes": 1,
    "idle processes": 2,
    "accepted conn": 100,
    "listen queue": 0,
    "max listen queue": 5,
    "max active processes": 3,
    "max children reached": 0,
    "slow requests": 0,
    "total processes": 3,
    "start since": 3600,
    "start time": 1700000000,
}


def run_main(tmp_path, responses):
    with patch_unix_sockets(responses):
        agent.main(root=str(tmp_path))


def parsed_lines(output):
    return [line.split() for line in output.splitlines() if line and not line.startswith("<")]


# ---------------------------------------------------------------------------
# TestBasicOutput
# ---------------------------------------------------------------------------


class TestBasicOutput:
    def _setup(self, tmp_path, pool_name="www", socket_path="/run/php-fpm.sock", vmrss_kb=1024):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[101])
        make_worker(tmp_path, pid=101, pool_name=pool_name, vmrss_kb=vmrss_kb)
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": pool_name, "listen": socket_path}])
        return {socket_path: {**POOL_STATUS, "pool": pool_name}}

    def test_output_starts_with_section_header(self, tmp_path, capsys):
        responses = self._setup(tmp_path)
        run_main(tmp_path, responses)
        assert capsys.readouterr().out.splitlines()[0] == "<<<php_fpm_pools>>>"

    def test_each_metric_line_has_four_fields(self, tmp_path, capsys):
        responses = self._setup(tmp_path)
        run_main(tmp_path, responses)
        for fields in parsed_lines(capsys.readouterr().out):
            assert len(fields) == 4

    def test_pool_name_is_first_field(self, tmp_path, capsys):
        responses = self._setup(tmp_path, pool_name="mypool")
        run_main(tmp_path, responses)
        for fields in parsed_lines(capsys.readouterr().out):
            assert fields[0] == "mypool"

    def test_pm_type_is_second_field(self, tmp_path, capsys):
        responses = self._setup(tmp_path)
        run_main(tmp_path, responses)
        for fields in parsed_lines(capsys.readouterr().out):
            assert fields[1] == "dynamic"

    def test_metric_value_is_integer(self, tmp_path, capsys):
        responses = self._setup(tmp_path)
        run_main(tmp_path, responses)
        for fields in parsed_lines(capsys.readouterr().out):
            assert fields[3].lstrip("-").isdigit()

    def test_known_metrics_present(self, tmp_path, capsys):
        responses = self._setup(tmp_path)
        run_main(tmp_path, responses)
        metrics = {f[2] for f in parsed_lines(capsys.readouterr().out)}
        for expected in ("active_processes", "idle_processes", "listen_queue", "accepted_conn"):
            assert expected in metrics


# ---------------------------------------------------------------------------
# TestMemoryMetrics
# ---------------------------------------------------------------------------


class TestMemoryMetrics:
    def test_memory_total_rss_is_sum_of_worker_rss(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[101, 102])
        make_worker(tmp_path, pid=101, pool_name="www", vmrss_kb=1024)
        make_worker(tmp_path, pid=102, pool_name="www", vmrss_kb=2048)
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/php-fpm.sock"}])
        run_main(tmp_path, {"/run/php-fpm.sock": POOL_STATUS})

        lines = {f[2]: int(f[3]) for f in parsed_lines(capsys.readouterr().out)}
        assert lines["memory_total_rss"] == (1024 + 2048) * 1024

    def test_memory_avg_rss_is_floor_average(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[101, 102])
        make_worker(tmp_path, pid=101, pool_name="www", vmrss_kb=1024)
        make_worker(tmp_path, pid=102, pool_name="www", vmrss_kb=2048)
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/php-fpm.sock"}])
        run_main(tmp_path, {"/run/php-fpm.sock": POOL_STATUS})

        lines = {f[2]: int(f[3]) for f in parsed_lines(capsys.readouterr().out)}
        assert lines["memory_avg_rss"] == (1024 + 2048) * 1024 // 2

    def test_memory_not_emitted_when_no_workers(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/php-fpm.sock"}])
        run_main(tmp_path, {"/run/php-fpm.sock": POOL_STATUS})

        metrics = {f[2] for f in parsed_lines(capsys.readouterr().out)}
        assert "memory_total_rss" not in metrics
        assert "memory_avg_rss" not in metrics

    def test_memory_not_emitted_when_children_file_missing(self, tmp_path, capsys):
        master_dir = tmp_path / "proc" / "100"
        master_dir.mkdir(parents=True)
        (master_dir / "cmdline").write_bytes(b"php-fpm: master process (/etc/php-fpm.conf)\0")
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/php-fpm.sock"}])
        run_main(tmp_path, {"/run/php-fpm.sock": POOL_STATUS})

        metrics = {f[2] for f in parsed_lines(capsys.readouterr().out)}
        assert "memory_total_rss" not in metrics
        assert "memory_avg_rss" not in metrics


# ---------------------------------------------------------------------------
# TestMultiplePools
# ---------------------------------------------------------------------------


class TestMultiplePools:
    def test_two_pools_same_master(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [
                {"name": "www", "listen": "/run/www.sock"},
                {"name": "api", "listen": "/run/api.sock"},
            ],
        )
        run_main(
            tmp_path,
            {
                "/run/www.sock": {**POOL_STATUS, "pool": "www"},
                "/run/api.sock": {**POOL_STATUS, "pool": "api", "process manager": "ondemand"},
            },
        )

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" in pool_names
        assert "api" in pool_names

    def test_two_masters_same_pool_name_get_version_qualifier(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php/8.1/fpm/php-fpm.conf", worker_pids=[])
        make_master(tmp_path, master_pid=200, config_path="/etc/php/8.2/fpm/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php/8.1/fpm/php-fpm.conf", [{"name": "www", "listen": "/run/81.sock"}])
        make_pool_config(tmp_path, "/etc/php/8.2/fpm/php-fpm.conf", [{"name": "www", "listen": "/run/82.sock"}])
        run_main(
            tmp_path,
            {
                "/run/81.sock": {**POOL_STATUS, "pool": "www"},
                "/run/82.sock": {**POOL_STATUS, "pool": "www"},
            },
        )

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www@8.1" in pool_names
        assert "www@8.2" in pool_names

    def test_two_masters_same_pool_name_no_version_get_sha_qualifier(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/fpm-a/php-fpm.conf", worker_pids=[])
        make_master(tmp_path, master_pid=200, config_path="/etc/fpm-b/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/fpm-a/php-fpm.conf", [{"name": "www", "listen": "/run/a.sock"}])
        make_pool_config(tmp_path, "/etc/fpm-b/php-fpm.conf", [{"name": "www", "listen": "/run/b.sock"}])
        run_main(
            tmp_path,
            {
                "/run/a.sock": {**POOL_STATUS, "pool": "www"},
                "/run/b.sock": {**POOL_STATUS, "pool": "www"},
            },
        )

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" not in pool_names
        assert any(name.startswith("www@") for name in pool_names)

    def test_two_masters_multiple_duplicate_pools_share_qualifier(self, tmp_path, capsys):
        """One configfile with two pools both duplicated: qualifier assigned once per configfile."""
        make_master(tmp_path, master_pid=100, config_path="/etc/php/8.1/fpm/php-fpm.conf", worker_pids=[])
        make_master(tmp_path, master_pid=200, config_path="/etc/php/8.2/fpm/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php/8.1/fpm/php-fpm.conf",
            [
                {"name": "www", "listen": "/run/81-www.sock"},
                {"name": "api", "listen": "/run/81-api.sock"},
            ],
        )
        make_pool_config(
            tmp_path,
            "/etc/php/8.2/fpm/php-fpm.conf",
            [
                {"name": "www", "listen": "/run/82-www.sock"},
                {"name": "api", "listen": "/run/82-api.sock"},
            ],
        )
        run_main(
            tmp_path,
            {
                "/run/81-www.sock": {**POOL_STATUS, "pool": "www"},
                "/run/81-api.sock": {**POOL_STATUS, "pool": "api"},
                "/run/82-www.sock": {**POOL_STATUS, "pool": "www"},
                "/run/82-api.sock": {**POOL_STATUS, "pool": "api"},
            },
        )

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www@8.1" in pool_names
        assert "www@8.2" in pool_names
        assert "api@8.1" in pool_names
        assert "api@8.2" in pool_names


# ---------------------------------------------------------------------------
# TestSocketFailure
# ---------------------------------------------------------------------------


class TestSocketFailure:
    def test_socket_error_does_not_crash(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/www.sock"}])
        with patch("php_fpm_pools_agent.socket.socket", side_effect=OSError("refused")):
            agent.main(root=str(tmp_path))  # must not raise
        assert "<<<php_fpm_pools>>>" in capsys.readouterr().out

    def test_socket_error_written_to_stderr(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "/run/www.sock"}])
        with patch("php_fpm_pools_agent.socket.socket", side_effect=OSError("refused")):
            agent.main(root=str(tmp_path))
        assert "Exception" in capsys.readouterr().err

    def test_socket_error_other_pools_unaffected(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [
                {"name": "www", "listen": "/run/www.sock"},
                {"name": "api", "listen": "/run/api.sock"},
            ],
        )
        api_response = {**POOL_STATUS, "pool": "api", "process manager": "ondemand"}

        class SelectiveFakeSocket:
            def __init__(self, *args, **kwargs):
                self._inner = None

            def connect(self, path):
                if "www" in path:
                    raise OSError("refused")
                self._inner = FakeFCGISocket({path: make_fcgi_response(api_response)})
                self._inner.connect(path)

            def settimeout(self, t):
                pass

            def send(self, d):
                self._inner and self._inner.send(d)

            def recv(self, n):
                return self._inner.recv(n) if self._inner else b""

            def close(self):
                pass

        with patch("php_fpm_pools_agent.socket.socket", side_effect=lambda *a, **k: SelectiveFakeSocket()):
            agent.main(root=str(tmp_path))

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "api" in pool_names
        assert "www" not in pool_names


# ---------------------------------------------------------------------------
# TestStatusListenSocket
# ---------------------------------------------------------------------------


class TestStatusListenSocket:
    def test_uses_pm_status_listen_when_set(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [
                {
                    "name": "www",
                    "listen": "/run/php-fpm.sock",
                    "status_listen": "/run/php-fpm-status.sock",
                }
            ],
        )
        run_main(tmp_path, {"/run/php-fpm-status.sock": POOL_STATUS})

        metrics = {f[2] for f in parsed_lines(capsys.readouterr().out)}
        assert "active_processes" in metrics


# ---------------------------------------------------------------------------
# TestIncludes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# TestTCPSocketParsing
# ---------------------------------------------------------------------------


class TestTCPSocketParsing:
    """
    Pools configured with listen = host:port (TCP) must be discovered.
    Before the fix these pools were silently skipped because a non-path listen
    value without a prefix= directive hit a 'continue' in _parse_fpm_config.
    """

    def test_pool_with_ip_port_listen_is_discovered(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "127.0.0.1:9000"}])
        with patch_tcp_sockets({("127.0.0.1", "9000"): POOL_STATUS}):
            agent.main(root=str(tmp_path))

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" in pool_names

    def test_pool_with_wildcard_ip_listen_is_discovered(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "0.0.0.0:9000"}])
        with patch_tcp_sockets({("0.0.0.0", "9000"): POOL_STATUS}):
            agent.main(root=str(tmp_path))

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" in pool_names

    def test_tcp_pool_emits_metrics(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(tmp_path, "/etc/php-fpm.conf", [{"name": "www", "listen": "127.0.0.1:9000"}])
        with patch_tcp_sockets({("127.0.0.1", "9000"): POOL_STATUS}):
            agent.main(root=str(tmp_path))

        metrics = {f[2] for f in parsed_lines(capsys.readouterr().out)}
        for expected in ("active_processes", "idle_processes", "listen_queue", "accepted_conn"):
            assert expected in metrics

    def test_tcp_pool_with_status_listen_uses_override_address(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [{"name": "www", "listen": "127.0.0.1:9000", "status_listen": "127.0.0.1:9001"}],
        )
        with patch_tcp_sockets({("127.0.0.1", "9001"): POOL_STATUS}):
            agent.main(root=str(tmp_path))

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" in pool_names

    def test_tcp_and_unix_pools_both_discovered(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [
                {"name": "unix_pool", "listen": "/run/php-fpm.sock"},
                {"name": "tcp_pool", "listen": "127.0.0.1:9000"},
            ],
        )
        unix_response = {**POOL_STATUS, "pool": "unix_pool"}
        tcp_response = {**POOL_STATUS, "pool": "tcp_pool"}
        unix_bytes = {"/run/php-fpm.sock": unix_response}
        tcp_bytes = {("127.0.0.1", "9000"): tcp_response}

        from unittest.mock import patch as _patch

        from tests.conftest import FakeFCGISocket, make_fcgi_response

        unix_response_bytes = {path: make_fcgi_response(data) for path, data in unix_bytes.items()}
        tcp_response_bytes = {addr: make_fcgi_response(data) for addr, data in tcp_bytes.items()}

        def socket_factory(*args, **kwargs):
            return FakeFCGISocket(unix_response_bytes)

        def create_connection_factory(address, timeout=None):
            sock = FakeFCGISocket(tcp_response_bytes)
            sock._data = tcp_response_bytes[address]
            sock._pos = 0
            return sock

        with _patch("php_fpm_pools_agent.socket.socket", side_effect=socket_factory):
            with _patch("php_fpm_pools_agent.socket.create_connection", side_effect=create_connection_factory):
                agent.main(root=str(tmp_path))

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "unix_pool" in pool_names
        assert "tcp_pool" in pool_names


# ---------------------------------------------------------------------------
# TestIncludes
# ---------------------------------------------------------------------------


class TestIncludes:
    def test_pool_loaded_via_include(self, tmp_path, capsys):
        make_master(tmp_path, master_pid=100, config_path="/etc/php-fpm.conf", worker_pids=[])
        make_pool_config(
            tmp_path,
            "/etc/php-fpm.conf",
            [{"name": "www", "listen": "/run/www.sock"}],
            include_dir="/etc/php-fpm.d",
        )
        run_main(tmp_path, {"/run/www.sock": POOL_STATUS})

        pool_names = {f[0] for f in parsed_lines(capsys.readouterr().out)}
        assert "www" in pool_names
