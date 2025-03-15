# test_staged_target_tab.py
import pytest
from PyQt5.QtWidgets import QApplication
from standalone_main_app.plugins.staged_target.staged_target_tab import StagedTargetTab
from standalone_main_app.plugins.staged_target.components.skill_selector import SkillSelector # 追加

import logging # 追加

# ロガー設定 (必要であれば)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # ロガー取得

# QApplicationのインスタンスはテストスイート全体で一つだけ必要
@pytest.fixture(scope="session")
def qapp():
    app = QApplication([])
    yield app
    app.quit()

# モックオブジェクト (簡略化)
class MockEventManager:
    def subscribe(self, event, callback):
        pass  # テストでは何もしない

    def publish(self, event, data=None):
        pass  # テストでは何もしない

class MockMainApp:
    def __init__(self):
        self.event_manager = MockEventManager()
        self.user_settings = {
            "selected_category": "プログラミング言語",
            "skills": {
                "プログラミング言語": ["Python", "JavaScript", "Java"]
            }
        }
        self.shared_data = {
            'hierarchy': {
                "プログラミング": {
                    "name": "プログラミング",
                    "categories": {
                        "言語": {
                            "name": "プログラミング言語",
                            "skills": {
                                "python": {"name": "Python", "level": 3},
                                "javascript": {"name": "JavaScript", "level": 4},
                                "java": {"name": "Java", "level": 2}
                            }
                        },
                        "フレームワーク": {
                            "name": "フレームワーク",
                            "skills": {
                                "django": {"name": "Django", "level": 3},
                                "react": {"name": "React", "level": 2}
                            }
                        }
                    }
                }
            }
        }

@pytest.fixture
def staged_target_tab(qapp):
    """StagedTargetTabのインスタンスを作成するフィクスチャ"""
    main_app = MockMainApp()
    tab = StagedTargetTab(main_app=main_app)
    return tab

def test_staged_target_tab_creation(staged_target_tab):
    """StagedTargetTabのインスタンスが正常に作成されることをテスト"""
    assert staged_target_tab is not None

def test_set_hierarchy_data(staged_target_tab):
    """set_hierarchy_data メソッドが正しく動作することをテスト"""
    hierarchy_data = {
        "group1": {
            "name": "Group 1",
            "categories": {
                "category1": {
                    "name": "Category 1",
                    "skills": {
                        "skill1": {"name": "Skill 1"},
                        "skill2": {"name": "Skill 2"}
                    }
                }
            }
        }
    }
    assert staged_target_tab.set_hierarchy_data(hierarchy_data) == True
    assert staged_target_tab.hierarchy_data == hierarchy_data

def test_show_radar_chart_no_skills(staged_target_tab):
    """選択されたスキルがない場合に show_radar_chart がエラーなく動作することをテスト"""
    # スキルが選択されていない状態をシミュレート
    staged_target_tab.selected_skills = {}
    # show_radar_chart を呼び出しても例外が発生しないことを確認
    try:
        staged_target_tab.show_radar_chart()
    except Exception as e:
        pytest.fail(f"show_radar_chart raised an exception with no skills selected: {e}")

def test_show_radar_chart_with_skills(staged_target_tab):
    """スキルが選択されている場合に show_radar_chart がエラーなく動作することをテスト"""
    # テスト用の階層データを設定
    staged_target_tab.set_hierarchy_data({
        "プログラミング": {
            "name": "プログラミング",
            "categories": {
                "プログラミング言語": {
                    "name": "プログラミング言語",
                    "skills": {
                        "python": {"name": "Python"},
                        "javascript": {"name": "JavaScript"},
                        "java": {"name": "Java"}
                    }
                }
            }
        }
    })
    # スキルを選択
    staged_target_tab.on_skills_updated({"python": "Python"})

    # show_radar_chart を呼び出しても例外が発生しないことを確認
    try:
        staged_target_tab.show_radar_chart()
    except Exception as e:
        pytest.fail(f"show_radar_chart raised an exception with skills selected: {e}")

# 他のテストケースも同様に追加