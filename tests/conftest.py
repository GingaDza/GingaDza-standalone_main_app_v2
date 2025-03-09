# tests/conftest.py
import pytest
import sys
import os
from unittest.mock import MagicMock
from PyQt5.QtWidgets import QApplication
# from standalone_main_app.plugins.staged_target.staged_target_plugin import StagedTargetPlugin  # 使用しないのでコメントアウト
from standalone_main_app.plugin.plugin_interface import PluginInterface
from standalone_main_app.plugin.plugin_manager import PluginManager  # PluginManager をインポート

# プロジェクトルートディレクトリをsys.pathに追加
#sys.path.insert(0, "/Users/sanadatakeshi/Desktop/new_staged_target_project")
print(sys.path)  # sys.path の内容を表示

# ダミーのSamplePluginを作成
class SamplePlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "サンプルプラグイン"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "サンプル機能のデモ"
    
    def get_tab_widget(self):
        return None
    
    def initialize(self, app_context):
        pass
    
    def cleanup(self):
        pass
@pytest.fixture
def data_model():
    """サンプルデータモデルfixture"""
    return {
        "hierarchy": {
            "group1": {
                "name": "Group 1",
                "categories": {
                    "cat1": {
                        "name": "Category 1",
                            "skills": {
                            "skill1": {"name": "Skill 1"},
                            "skill2": {"name": "Skill 2"}
                        }
                    },
                    "cat2": {
                        "name": "Category 2",
                            "skills": {
                            "skill3": {"name": "Skill 3"},
                            "skill4": {"name": "Skill 4"}
                        }
                    }
                }
            }
        }
    }

from standalone_main_app.plugins.staged_target.staged_target_plugin import StagedTargetPlugin
@pytest.fixture
def plugin_manager(data_model):
    """PluginManager fixture"""
    main_window_mock = MagicMock()
    main_window_mock.data_model = data_model
    plugin_manager = PluginManager(main_window_mock)
    plugin_dir = os.path.join(os.path.dirname(__file__), "../standalone_main_app/plugins")
    plugin_manager.discover_plugins(plugin_dir=plugin_dir)
    return plugin_manager

@pytest.fixture
def staged_target_plugin(plugin_manager):
    """StagedTargetPlugin fixture"""
    for name, plugin in plugin_manager.plugins.items():
        if isinstance(plugin, StagedTargetPlugin):
            return plugin
    return None  # StagedTargetPlugin が見つからない場合

@pytest.fixture
def staged_target_tab(staged_target_plugin, data_model):
    """StagedTargetTab fixture"""
    if staged_target_plugin:
        app_context = {"main_window": MagicMock(data_model=data_model)}
        staged_target_plugin.initialize(app_context)
        return staged_target_plugin.tab
    else:
        return None

@pytest.fixture
def mock_qmessagebox(monkeypatch):
    """QMessageBoxをモックするfixture"""
    mock = MagicMock()
    monkeypatch.setattr("PyQt5.QtWidgets.QMessageBox", mock)
    return mock