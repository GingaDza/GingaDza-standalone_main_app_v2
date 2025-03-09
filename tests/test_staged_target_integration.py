# tests/test_staged_target_integration.py
import pytest
from PyQt5.QtWidgets import QApplication
from unittest.mock import MagicMock
from standalone_main_app.plugins.staged_target.staged_target_plugin import StagedTargetPlugin # import文を修正

def test_staged_target_plugin_name(plugin_manager):
    for name, plugin in plugin_manager.plugins.items():
        if isinstance(plugin,StagedTargetPlugin):
            assert plugin.name == "段階的目標設定"
            return
    assert False #プラグインが見つからない場合はテスト失敗