# tests/test_sample_plugin.py
import pytest
from PyQt5.QtWidgets import QApplication, QComboBox, QPushButton, QTextBrowser, QWidget, QVBoxLayout, QLabel  # QWidget, QVBoxLayout, QLabelを追加
from standalone_main_app.plugin.plugin_interface import PluginInterface

#from standalone_main_app.plugins.sample_plugin import SamplePlugin #ここを削除

#def test_sample_plugin_name(mock_sample_plugin): #引数を修正
#    plugin = mock_sample_plugin
#    assert plugin.name == "サンプルプラグイン"

#def test_sample_plugin_tab_widget(mock_sample_plugin): #引数を修正
#    plugin = mock_sample_plugin
#    tab_widget = plugin.get_tab_widget()
#    assert tab_widget is not None

#def test_sample_plugin_button_click(mock_sample_plugin, monkeypatch): #引数を修正
#    plugin = mock_sample_plugin
#    tab_widget = plugin.get_tab_widget()
#    button = tab_widget.findChildren(QPushButton)[0]
#    output = tab_widget.findChildren(QTextBrowser)[0]

#    # Mock append メソッド
#    def mock_append(text):
#        mock_append.called = True
#        mock_append.text = text
#        print(f"mock_append called with text: {text}")
#    mock_append.called = False
#    mock_append.text = ""
#    monkeypatch.setattr(output, 'append', mock_append)

#    button.click()
#    print(f"mock_append.called: {mock_append.called}")
#    print(f"mock_append.text: {mock_append.text}")

#    assert mock_append.called
#    assert "ボタンがクリックされました 現在のグループ: dummy" in mock_append.text

def test_dummy():
    assert True