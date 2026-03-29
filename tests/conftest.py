"""
Shared test configuration and fixtures.
"""

import importlib.util
import json
import struct
import sys
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Load agent plugin module (no .py extension)
# ---------------------------------------------------------------------------

_agent_path = str(Path(__file__).parent.parent / "php-fpm" / "agents" / "plugins" / "php_fpm_pools")
_loader = SourceFileLoader("php_fpm_pools_agent", _agent_path)
_spec = importlib.util.spec_from_loader("php_fpm_pools_agent", _loader)
agent = importlib.util.module_from_spec(_spec)
_loader.exec_module(agent)
sys.modules["php_fpm_pools_agent"] = agent

# ---------------------------------------------------------------------------
# Mock cmk.agent_based.v2 so check plugin tests run without a CheckMK install
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent.parent / "php-fpm" / "agent_based"))


class GetRateError(Exception):
    pass


check_levels = MagicMock(return_value=[])
get_rate = MagicMock(return_value=5.0)
get_value_store = MagicMock(return_value={})

_mock_v2 = ModuleType("cmk.agent_based.v2")
_mock_v2.AgentSection = MagicMock()
_mock_v2.CheckPlugin = MagicMock()
_mock_v2.check_levels = check_levels
_mock_v2.get_rate = get_rate
_mock_v2.get_value_store = get_value_store
_mock_v2.GetRateError = GetRateError
_mock_v2.render = SimpleNamespace(timespan=str, bytes=str)
_mock_v2.Service = MagicMock(side_effect=lambda item: item)
_mock_v2.StringTable = list
_mock_v2.CheckResult = object
_mock_v2.DiscoveryResult = object

sys.modules.setdefault("cmk", ModuleType("cmk"))
sys.modules.setdefault("cmk.agent_based", ModuleType("cmk.agent_based"))
sys.modules["cmk.agent_based.v2"] = _mock_v2

# ---------------------------------------------------------------------------
# Fake /proc helpers
# ---------------------------------------------------------------------------


def make_master(root, master_pid, config_path, worker_pids):
    """Create /proc entries for a PHP-FPM master process."""
    master_dir = root / "proc" / str(master_pid)
    master_dir.mkdir(parents=True)
    (master_dir / "cmdline").write_bytes(("php-fpm: master process (%s)\0" % config_path).encode())
    task_dir = master_dir / "task" / str(master_pid)
    task_dir.mkdir(parents=True)
    (task_dir / "children").write_text(" ".join(str(p) for p in worker_pids), encoding="utf-8")


def make_worker(root, pid, pool_name, vmrss_kb):
    """Create /proc entries for a PHP-FPM worker process."""
    worker_dir = root / "proc" / str(pid)
    worker_dir.mkdir(parents=True)
    (worker_dir / "cmdline").write_text("php-fpm: pool %s" % pool_name, encoding="utf-8")
    (worker_dir / "status").write_text("VmRSS:\t%d kB\n" % vmrss_kb, encoding="utf-8")


# ---------------------------------------------------------------------------
# Fake config helpers
# ---------------------------------------------------------------------------


def make_pool_config(root, config_path, pools, include_dir=None):
    """
    Write a PHP-FPM config file under root.
    pools: list of dicts with keys: name, listen, pm (default: dynamic),
           status_path (default: /status), optionally status_listen.
    include_dir: if given, write each pool to a separate file under include_dir
                 and add an include= line to the main config.
    """
    full_path = root / config_path.lstrip("/")
    full_path.parent.mkdir(parents=True, exist_ok=True)

    if include_dir:
        inc_dir = root / include_dir.lstrip("/")
        inc_dir.mkdir(parents=True, exist_ok=True)
        main_content = "include=%s\n" % (include_dir.rstrip("/") + "/*.conf")
        full_path.write_text(main_content, encoding="utf-8")
        for pool in pools:
            pool_file = inc_dir / ("%s.conf" % pool["name"])
            pool_file.write_text(_pool_section(pool), encoding="utf-8")
    else:
        content = "".join(_pool_section(p) for p in pools)
        full_path.write_text(content, encoding="utf-8")


def _pool_section(pool):
    lines = ["[%s]\n" % pool["name"]]
    lines.append("listen = %s\n" % pool["listen"])
    lines.append("pm = %s\n" % pool.get("pm", "dynamic"))
    lines.append("pm.status_path = %s\n" % pool.get("status_path", "/status"))
    if "status_listen" in pool:
        lines.append("pm.status_listen = %s\n" % pool["status_listen"])
    return "".join(lines)


# ---------------------------------------------------------------------------
# Fake FastCGI socket
# ---------------------------------------------------------------------------


def make_fcgi_response(status_dict):
    """Build FCGI-framed response bytes for the given PHP-FPM status dict."""
    FCGI_VERSION = 1
    FCGI_STDOUT = 6
    FCGI_END_REQUEST = 3
    request_id = 1

    body = b"Status: 200 OK\r\nContent-Type: application/json\r\n\r\n" + json.dumps(status_dict).encode()
    body_len = len(body)
    padding_len = (8 - (body_len % 8)) % 8

    stdout_header = struct.pack("!BBHHBx", FCGI_VERSION, FCGI_STDOUT, request_id, body_len, padding_len)
    stdout_record = stdout_header + body + b"\x00" * padding_len

    end_body = struct.pack("!IB3x", 0, 0)
    end_header = struct.pack("!BBHHBx", FCGI_VERSION, FCGI_END_REQUEST, request_id, len(end_body), 0)
    end_record = end_header + end_body

    return stdout_record + end_record


class FakeFCGISocket:
    """Minimal socket that replays a pre-built FCGI response on connect()."""

    def __init__(self, responses):
        self._responses = responses  # {socket_path: bytes}
        self._data = b""
        self._pos = 0

    def connect(self, path):
        self._data = self._responses[path]
        self._pos = 0

    def settimeout(self, t):
        pass

    def send(self, data):
        pass

    def recv(self, n):
        chunk = self._data[self._pos : self._pos + n]
        self._pos += len(chunk)
        return chunk

    def close(self):
        pass


@contextmanager
def patch_sockets(responses):
    """
    Context manager that patches socket.socket in the agent module.
    responses: {socket_path: status_dict}
    """
    response_bytes = {path: make_fcgi_response(data) for path, data in responses.items()}

    def socket_factory(*args, **kwargs):
        return FakeFCGISocket(response_bytes)

    with patch("php_fpm_pools_agent.socket.socket", side_effect=socket_factory):
        yield
