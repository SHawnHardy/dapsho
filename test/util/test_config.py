"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import tempfile

import yaml

from dapsho.util.config import (
    config_context,
    get_config,
    load_config_from_files,
    reset_config,
    set_config,
)


class TestConfig:

    def create_temp_yaml_file(self, content: dict) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_file:
            with open(temp_file.name, "w", encoding="utf-8") as f:
                yaml.dump(content, f)
        return temp_file.name

    def setup_method(self):
        reset_config(reset_default=True)

    def teardown_method(self):
        reset_config(reset_default=True)

    def test_get_config(self):
        assert get_config("hash_method") == "sha256"
        assert get_config("ignore_home_config") is True

    def test_config_context(self):
        assert get_config("hash_method") == "sha256"
        with config_context({"hash_method": "md5"}):
            assert get_config("hash_method") == "md5"
        assert get_config("hash_method") == "sha256"

    def test_set_config(self):
        with config_context():
            set_config(hash_method="md5")
            assert get_config("hash_method") == "md5"

    def test_load_config_from_files_pkg_default(self, monkeypatch):
        pkg_default_content = {"hash_method": "md5"}
        pkg_default_path = self.create_temp_yaml_file(pkg_default_content)
        monkeypatch.setattr("dapsho.util.config.PKG_CONFIG_PATH", pkg_default_path)

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "md5"

    def test_load_config_from_files_home(self, monkeypatch):
        home_content = {"hash_method": "md5"}
        home_path = self.create_temp_yaml_file(home_content)
        monkeypatch.setattr("dapsho.util.config.HOME_CONFIG_PATH", home_path)
        monkeypatch.setenv("DAPSHO_IGNORE_HOME_CONFIG", "FALSE")

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "md5"

    def test_load_config_from_files_project(self, monkeypatch):
        project_content = {"hash_method": "sha1"}
        project_path = self.create_temp_yaml_file(project_content)
        monkeypatch.setattr(
            "dapsho.util.config.DEFAULT_PROJECT_CONFIG_PATH", project_path
        )
        monkeypatch.setenv("DAPSHO_IGNORE_PROJECT_CONFIG", "FALSE")

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "sha1"

    def test_load_config_from_files_ignore_home(self, monkeypatch):
        home_content = {"hash_method": "md5"}
        home_path = self.create_temp_yaml_file(home_content)
        monkeypatch.setattr("dapsho.util.config.HOME_CONFIG_PATH", home_path)
        monkeypatch.setenv("DAPSHO_IGNORE_HOME_CONFIG", "TRUE")

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "sha256"

    def test_load_config_from_files_ignore_project(self, monkeypatch):
        project_content = {"hash_method": "sha1"}
        project_path = self.create_temp_yaml_file(project_content)
        monkeypatch.setattr(
            "dapsho.util.config.DEFAULT_PROJECT_CONFIG_PATH", project_path
        )
        monkeypatch.setenv("DAPSHO_IGNORE_PROJECT_CONFIG", "TRUE")

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "sha256"

    def test_load_config_from_files_merge(self, monkeypatch):
        pkg_default_content = {"hash_method": "sha256", "timeout": 30}
        home_content = {"hash_method": "md5"}
        project_content = {"timeout": 60}

        pkg_default_path = self.create_temp_yaml_file(pkg_default_content)
        home_path = self.create_temp_yaml_file(home_content)
        project_path = self.create_temp_yaml_file(project_content)

        monkeypatch.setattr("dapsho.util.config.PKG_CONFIG_PATH", pkg_default_path)
        monkeypatch.setattr("dapsho.util.config.HOME_CONFIG_PATH", home_path)
        monkeypatch.setattr(
            "dapsho.util.config.DEFAULT_PROJECT_CONFIG_PATH", project_path
        )

        monkeypatch.setenv("DAPSHO_IGNORE_HOME_CONFIG", "FALSE")
        monkeypatch.setenv("DAPSHO_IGNORE_PROJECT_CONFIG", "FALSE")

        reset_config(reset_default=True)
        config = load_config_from_files()
        assert config["hash_method"] == "md5"
        assert config["timeout"] == 60
