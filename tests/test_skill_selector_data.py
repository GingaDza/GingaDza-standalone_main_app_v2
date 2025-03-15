# tests/test_skill_selector_data.py
import pytest
from PyQt5.QtWidgets import QApplication
from standalone_main_app.plugins.staged_target.components.skill_selector import SkillSelector

@pytest.fixture
def skill_selector(qtbot):
    """SkillSelectorのインスタンスを作成するフィクスチャ"""
    selector = SkillSelector()
    qtbot.addWidget(selector)
    return selector

def test_skill_selector_invalid_data(skill_selector):
    """無効データの処理をテスト"""

    # 無効なデータ形式を設定 - エラーを発生させない
    try:
        skill_selector.set_hierarchy_data("無効なデータ文字列")
    except Exception as e:
        pytest.fail(f"無効なデータ設定でエラーが発生: {e}")

    # エラーなく処理できているか確認
    assert skill_selector.group_combo.count() == 0

    # 不完全なデータ構造
    incomplete_data = {
        1: {
            'name': '不完全グループ'
            # categories キーが欠けている
        }
    }
    try:
        skill_selector.set_hierarchy_data(incomplete_data)
    except Exception as e:
        pytest.fail(f"不完全なデータ設定でエラーが発生: {e}")

    # グループは表示されるがカテゴリは空か
    assert skill_selector.group_combo.count() == 1
    skill_selector.group_combo.setCurrentIndex(0)
    assert skill_selector.category_combo.count() == 0