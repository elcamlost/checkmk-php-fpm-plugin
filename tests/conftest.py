"""
Mock cmk.agent_based.v2 so tests can run without a Checkmk installation.
"""

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

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
_mock_v2.render = SimpleNamespace(timespan=str)
_mock_v2.Service = MagicMock(side_effect=lambda item: item)
_mock_v2.StringTable = list
_mock_v2.CheckResult = object
_mock_v2.DiscoveryResult = object

sys.modules.setdefault("cmk", ModuleType("cmk"))
sys.modules.setdefault("cmk.agent_based", ModuleType("cmk.agent_based"))
sys.modules["cmk.agent_based.v2"] = _mock_v2
