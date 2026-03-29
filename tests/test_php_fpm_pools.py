import pytest
from php_fpm_pools import check_php_fpm_pools, parse_php_fpm_pools

from tests.conftest import GetRateError, check_levels, get_rate

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TYPICAL_SECTION = {
    "www [dynamic]": {
        "active_processes": 1,
        "idle_processes": 2,
        "max_active_processes": 3,
        "max_children_reached": 0,
        "slow_requests": 0,
        "listen_queue": 0,
        "max_listen_queue": 5,
        "accepted_conn": 1000,
    }
}


@pytest.fixture(autouse=True)
def reset_mocks():
    check_levels.reset_mock()
    get_rate.reset_mock()
    get_rate.return_value = 5.0
    get_rate.side_effect = None


def run_check(item="www [dynamic]", params=None, section=None):
    return list(check_php_fpm_pools(item, params or {}, section or TYPICAL_SECTION))


def check_levels_calls_for(key):
    return [c for c in check_levels.call_args_list if c.kwargs.get("metric_name") == key]


# ---------------------------------------------------------------------------
# parse_php_fpm_pools
# ---------------------------------------------------------------------------


class TestParse:
    def test_empty_input(self):
        assert parse_php_fpm_pools([]) == {}

    def test_parses_item_key(self):
        result = parse_php_fpm_pools([["www", "dynamic", "active_processes", "1"]])
        assert "www [dynamic]" in result

    def test_values_cast_to_int(self):
        result = parse_php_fpm_pools([["www", "dynamic", "idle_processes", "5"]])
        value = result["www [dynamic]"]["idle_processes"]
        assert value == 5
        assert isinstance(value, int)

    def test_malformed_line_skipped(self):
        table = [
            ["www", "dynamic", "active_processes", "1"],
            ["bad_line"],
            ["www", "dynamic", "idle_processes", "2"],
        ]
        result = parse_php_fpm_pools(table)
        assert result["www [dynamic]"] == {"active_processes": 1, "idle_processes": 2}

    def test_multiple_pools(self):
        table = [
            ["www", "dynamic", "active_processes", "1"],
            ["api", "ondemand", "active_processes", "3"],
        ]
        result = parse_php_fpm_pools(table)
        assert set(result.keys()) == {"www [dynamic]", "api [ondemand]"}

    def test_multiple_metrics_same_pool(self):
        table = [
            ["www", "dynamic", "active_processes", "1"],
            ["www", "dynamic", "idle_processes", "4"],
        ]
        result = parse_php_fpm_pools(table)
        assert len(result["www [dynamic]"]) == 2


# ---------------------------------------------------------------------------
# check_php_fpm_pools — unknown item
# ---------------------------------------------------------------------------


class TestCheckUnknownItem:
    def test_unknown_item_yields_nothing(self):
        result = run_check(item="unknown [pm]")
        assert result == []
        check_levels.assert_not_called()


# ---------------------------------------------------------------------------
# check_php_fpm_pools — rate metrics
# ---------------------------------------------------------------------------


class TestRateMetrics:
    def test_get_rate_error_skips_per_sec_metrics(self):
        get_rate.side_effect = GetRateError
        run_check()
        keys_checked = [c.kwargs["metric_name"] for c in check_levels.call_args_list]
        assert "accepted_conn_per_sec" not in keys_checked
        assert "max_children_reached_per_sec" not in keys_checked
        assert "slow_requests_per_sec" not in keys_checked

    def test_rate_success_adds_per_sec_metrics(self):
        get_rate.return_value = 2.5
        run_check()
        keys_checked = [c.kwargs["metric_name"] for c in check_levels.call_args_list]
        assert "accepted_conn_per_sec" in keys_checked
        assert "max_children_reached_per_sec" in keys_checked
        assert "slow_requests_per_sec" in keys_checked

    def test_rate_value_passed_to_check_levels(self):
        get_rate.return_value = 7.3
        run_check()
        calls = check_levels_calls_for("accepted_conn_per_sec")
        assert calls
        assert calls[0].kwargs["value"] == pytest.approx(7.3)


# ---------------------------------------------------------------------------
# check_php_fpm_pools — levels direction
# ---------------------------------------------------------------------------


class TestLevelsDirection:
    def test_idle_processes_uses_lower_levels(self):
        params = {"idle_processes": ("fixed", (3, 1))}
        run_check(params=params)
        calls = check_levels_calls_for("idle_processes")
        assert calls[0].kwargs["levels_lower"] == ("fixed", (3, 1))
        assert calls[0].kwargs["levels_upper"] is None

    def test_active_processes_uses_upper_levels(self):
        params = {"active_processes": ("fixed", (10, 20))}
        run_check(params=params)
        calls = check_levels_calls_for("active_processes")
        assert calls[0].kwargs["levels_upper"] == ("fixed", (10, 20))
        assert calls[0].kwargs["levels_lower"] is None

    def test_no_params_passes_none_levels(self):
        run_check(params={})
        calls = check_levels_calls_for("active_processes")
        assert calls[0].kwargs["levels_upper"] is None


# ---------------------------------------------------------------------------
# check_php_fpm_pools — notice_only
# ---------------------------------------------------------------------------


class TestMemoryMetrics:
    def _section_with_memory(self, total=104857600, avg=52428800):
        return {
            "www [dynamic]": {
                **TYPICAL_SECTION["www [dynamic]"],
                "memory_total_rss": total,
                "memory_avg_rss": avg,
            }
        }

    def test_memory_metrics_checked_when_present(self):
        run_check(section=self._section_with_memory())
        keys_checked = [c.kwargs["metric_name"] for c in check_levels.call_args_list]
        assert "memory_total_rss" in keys_checked
        assert "memory_avg_rss" in keys_checked

    def test_memory_metrics_skipped_when_absent(self):
        run_check()
        keys_checked = [c.kwargs["metric_name"] for c in check_levels.call_args_list]
        assert "memory_total_rss" not in keys_checked
        assert "memory_avg_rss" not in keys_checked

    def test_memory_uses_upper_levels(self):
        params = {"memory_total_rss": ("fixed", (512 * 1024 * 1024, 1024 * 1024 * 1024))}
        run_check(params=params, section=self._section_with_memory())
        calls = check_levels_calls_for("memory_total_rss")
        assert calls[0].kwargs["levels_upper"] is not None
        assert calls[0].kwargs["levels_lower"] is None

    def test_memory_total_rss_not_notice_only(self):
        run_check(section=self._section_with_memory())
        calls = check_levels_calls_for("memory_total_rss")
        assert calls[0].kwargs["notice_only"] is False

    def test_memory_avg_rss_not_notice_only(self):
        run_check(section=self._section_with_memory())
        calls = check_levels_calls_for("memory_avg_rss")
        assert calls[0].kwargs["notice_only"] is False


class TestNoticeOnly:
    def _notice_only_for(self, key):
        run_check()
        calls = check_levels_calls_for(key)
        assert calls, f"check_levels not called for {key!r}"
        return calls[0].kwargs["notice_only"]

    def test_active_processes_not_notice_only(self):
        assert self._notice_only_for("active_processes") is False

    def test_idle_processes_not_notice_only(self):
        assert self._notice_only_for("idle_processes") is False

    def test_listen_queue_not_notice_only(self):
        assert self._notice_only_for("listen_queue") is False

    def test_accepted_conn_per_sec_not_notice_only(self):
        assert self._notice_only_for("accepted_conn_per_sec") is False

    def test_max_children_reached_is_notice_only(self):
        assert self._notice_only_for("max_children_reached") is True

    def test_slow_requests_is_notice_only(self):
        assert self._notice_only_for("slow_requests") is True

    def test_max_listen_queue_is_notice_only(self):
        assert self._notice_only_for("max_listen_queue") is True
