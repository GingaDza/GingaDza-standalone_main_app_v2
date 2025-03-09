import pytest
from PyQt5.QtWidgets import QApplication
from unittest.mock import MagicMock
from standalone_main_app.plugins.staged_target.staged_target_plugin import StagedTargetPlugin

@pytest.fixture
def staged_target_plugin(data_model):
    try:
        plugin = StagedTargetPlugin()
        app_context = {"main_window": MagicMock(data_model=data_model)}
        plugin.initialize(app_context)
        return plugin
    except Exception as e:
        print(f"fixtureの初期化でエラーが発生しました: {e}")
        return None


def test_staged_target_tab_initialization(staged_target_plugin):
    # StagedTargetTabの初期化に関するテストを記述
    if staged_target_plugin:
        assert True
    else:
        assert False, "fixture 'staged_target_plugin' の初期化に失敗しました"