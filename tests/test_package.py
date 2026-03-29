import json
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import package as pkg


@pytest.fixture(scope="module")
def mkp_path(tmp_path_factory):
    output = tmp_path_factory.mktemp("mkp") / f"{pkg.PKG_NAME}.mkp"
    pkg.build_mkp(output)
    return output


@pytest.fixture(scope="module")
def mkp(mkp_path):
    return tarfile.open(mkp_path, "r:gz")


@pytest.fixture(scope="module")
def info_json(mkp):
    return json.loads(mkp.extractfile("info.json").read())


@pytest.fixture(scope="module")
def agents_tar(mkp, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("agents")
    mkp.extract("agents.tar", tmp)
    return tarfile.open(tmp / "agents.tar")


@pytest.fixture(scope="module")
def plugins_tar(mkp, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("plugins")
    mkp.extract("cmk_addons_plugins.tar", tmp)
    return tarfile.open(tmp / "cmk_addons_plugins.tar")


class TestMkpStructure:
    def test_mkp_contains_info(self, mkp):
        assert "info" in mkp.getnames()

    def test_mkp_contains_info_json(self, mkp):
        assert "info.json" in mkp.getnames()

    def test_mkp_contains_agents_tar(self, mkp):
        assert "agents.tar" in mkp.getnames()

    def test_mkp_contains_plugins_tar(self, mkp):
        assert "cmk_addons_plugins.tar" in mkp.getnames()


class TestInfoJson:
    def test_valid_json(self, info_json):
        assert isinstance(info_json, dict)

    def test_usable_until_is_null(self, info_json):
        assert info_json["version.usable_until"] is None

    def test_name(self, info_json):
        assert info_json["name"] == pkg.PKG_NAME

    def test_version(self, info_json):
        assert info_json["version"] == pkg.PLUGIN_VERSION

    def test_min_required(self, info_json):
        assert info_json["version.min_required"] == pkg.CHECKMK_MIN_VERSION

    def test_files_keys(self, info_json):
        assert set(info_json["files"].keys()) == {"agents", "cmk_addons_plugins"}

    def test_num_files_matches_files(self, info_json):
        total = sum(len(v) for v in info_json["files"].values())
        assert info_json["num_files"] == total


class TestAgentsTar:
    def test_contains_agent_plugin(self, agents_tar):
        assert "plugins/php_fpm_pools" in agents_tar.getnames()


class TestPluginsTar:
    def test_contains_agent_based(self, plugins_tar):
        assert f"{pkg.PKG_NAME}/agent_based/php_fpm_pools.py" in plugins_tar.getnames()

    def test_contains_graphing(self, plugins_tar):
        assert f"{pkg.PKG_NAME}/graphing/php_fpm_pools.py" in plugins_tar.getnames()

    def test_contains_rulesets(self, plugins_tar):
        assert f"{pkg.PKG_NAME}/rulesets/php_fpm_pools.py" in plugins_tar.getnames()

    def test_contains_checkman(self, plugins_tar):
        assert f"{pkg.PKG_NAME}/checkman/php_fpm_pools" in plugins_tar.getnames()
