import sys
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QGroupBox, QFormLayout, QDoubleSpinBox,
    QRadioButton, QButtonGroup, QScrollArea, QGridLayout, QApplication,
    QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication

# ダミーのDebugLogger
class DebugLogger:
    @staticmethod
    def get_logger():
        logging.basicConfig(level=logging.DEBUG)
        return logging.getLogger(__name__)

# RadarChartDialogをインポート
try:
    from standalone_main_app.plugins.staged_target.components.radar_chart_dialog import RadarChartDialog
except ImportError as e:
    print(f"Error: Could not import RadarChartDialog: {e}")
    RadarChartDialog = None

class StagedTargetTab(QWidget):
    """段階的な目標値設定タブ"""

    # データ変更通知用シグナル
    data_changed = pyqtSignal()

    def __init__(self, data_model=None, parent=None):
        super().__init__(parent)
        # ロガー設定
        self.logger = DebugLogger.get_logger()
        self.data_model = data_model or {}
        self.stage_rows = []
        self.staged_targets = {}
        self.hierarchy = self.data_model.get("hierarchy", {})
        self.logger.debug(f"data_modelの内容: {self.data_model}")
        self.logger.debug(f"hierarchyの内容: {self.hierarchy}")

        self.setup_ui()

    def setup_ui(self):
        """UIの初期設定"""
        main_layout = QVBoxLayout(self)

        # タイトル
        title_label = QLabel("段階的な目標値設定")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        # 説明
        desc_label = QLabel("各スキルの習得目標を複数の段階に分けて設定します。")
        desc_label.setStyleSheet("font-size: 10pt; margin-bottom: 10px;")
        main_layout.addWidget(desc_label)

        # 時間単位選択
        time_unit_group = QGroupBox("時間単位")
        time_unit_layout = QHBoxLayout(time_unit_group)

        self.time_unit_group = QButtonGroup(time_unit_group)
        units = ["時間", "日", "週", "月", "年"]

        for i, unit in enumerate(units):
            radio = QRadioButton(unit)
            if i == 3:  # デフォルトで「月」を選択
                radio.setChecked(True)
            self.time_unit_group.addButton(radio, i)
            time_unit_layout.addWidget(radio)

        main_layout.addWidget(time_unit_group)

        # スキル選択
        skill_selection_group = QGroupBox("スキル選択")
        skill_selection_layout = QVBoxLayout(skill_selection_group)

        # グループ・カテゴリ選択
        selection_form = QFormLayout()

        self.staged_group_combo = QComboBox()
        if self.hierarchy: #hierarchyが空でないことを確認
            for group_id, group_data in self.hierarchy.items():
                self.staged_group_combo.addItem(group_data["name"], group_id)
        else:
             self.logger.warning("hierarchyが空です。データが正しく読み込まれていません。")

        self.staged_category_combo = QComboBox()

        selection_form.addRow("グループ:", self.staged_group_combo)
        selection_form.addRow("カテゴリ:", self.staged_category_combo)
        skill_selection_layout.addLayout(selection_form)

        # スキル選択テーブル
        self.skill_selection_table = QTableWidget()
        self.skill_selection_table.setColumnCount(2)
        self.skill_selection_table.setHorizontalHeaderLabels(["スキル名", "選択"])
        self.skill_selection_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.skill_selection_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        skill_selection_layout.addWidget(self.skill_selection_table)

        # グループ選択時の処理を設定
        self.staged_group_combo.currentIndexChanged.connect(self.update_staged_category_combo)
        self.staged_category_combo.currentIndexChanged.connect(self.update_skill_selection_table)

        main_layout.addWidget(skill_selection_group)

        # 段階設定 - 各段階でのレベルを設定する
        self.stages_group = QGroupBox("段階的目標設定")
        self.stages_layout = QGridLayout(self.stages_group)

        # ヘッダー
        self.stages_layout.addWidget(QLabel("<b>段階</b>"), 0, 0)
        self.stages_layout.addWidget(QLabel("<b>時間</b>"), 0, 1)
        self.stages_layout.addWidget(QLabel("<b>目標レベル</b>"), 0, 2)
        self.stages_layout.addWidget(QLabel(""), 0, 3)  # 削除ボタン用の列

        # 段階の行を追加
        for i in range(1, 4):  # 初期段階は3つ
            self.add_stage_row(i)

        # 段階追加ボタン
        add_stage_btn = QPushButton("段階を追加")
        add_stage_btn.clicked.connect(self.add_stage)
        self.stages_layout.addWidget(add_stage_btn, len(self.stage_rows) + 1, 0, 1, 4)

        main_layout.addWidget(self.stages_group)

        # ボタンエリア
        button_layout = QHBoxLayout()

        # レーダーチャート確認ボタン
        self.chart_btn = QPushButton("レーダーチャートで確認")
        self.chart_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 15px;")
        self.chart_btn.clicked.connect(self.show_radar_chart)
        button_layout.addWidget(self.chart_btn)

        button_layout.addStretch(1)

        # 保存ボタン
        self.save_btn = QPushButton("目標値を保存")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 15px; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_targets)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

        # 段階的目標用のカテゴリコンボとスキル選択テーブルを初期化
        self.update_staged_category_combo()

    def add_stage_row(self, row_num):
        """段階的目標の行を追加"""
        # 段階ラベル
        stage_label = QLabel(f"段階 {row_num}")

        # 時間入力
        time_spin = QDoubleSpinBox()
        time_spin.setMinimum(1)
        time_spin.setMaximum(1000)
        time_spin.setValue(row_num * 3)  # デフォルト値 (3, 6, 9, 12...)
        time_spin.setSingleStep(1)

        # 目標レベル
        level_combo = QComboBox()
        for i in range(1, 6):
            level_combo.addItem(f"レベル {i}", i)

        # 最後の行の場合はレベル5をデフォルトに、それ以外は段階に合わせて設定
        default_level = min(row_num, 5)
        level_combo.setCurrentIndex(default_level - 1)

        # 削除ボタン
        delete_btn = QPushButton("削除")
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_stage_row(row_num))

        # 行にウィジェットを追加
        self.stages_layout.addWidget(stage_label, row_num, 0)
        self.stages_layout.addWidget(time_spin, row_num, 1)
        self.stages_layout.addWidget(level_combo, row_num, 2)
        self.stages_layout.addWidget(delete_btn, row_num, 3)

        # 管理用に行データを保存
        self.stage_rows.append({
            "label": stage_label,
            "time": time_spin,
            "level": level_combo,
            "delete": delete_btn
        })

    def add_stage(self):
        """新しい段階を追加"""
        # 追加ボタンの位置を取得
        btn_row = len(self.stage_rows) + 1

        # 新しい行を追加
        row_num = btn_row
        self.add_stage_row(row_num)

        # ボタンの位置を更新
        add_stage_btn = self.stages_layout.itemAtPosition(btn_row, 0).widget()
        if add_stage_btn:
            self.stages_layout.removeWidget(add_stage_btn)
            self.stages_layout.addWidget(add_stage_btn, btn_row + 1, 0, 1, 4)  # 削除ボタン列も含める

    def delete_stage_row(self, row_num):
        """段階行を削除"""
        # 少なくとも 1つの段階は残す
        if len(self.stage_rows) <= 1:
            QMessageBox.warning(self, "削除エラー", "少なくとも1つの段階が必要です。")
            return

        # 指定された行を削除
        actual_idx = row_num - 1  # インデックスは0から始まるため調整

        if 0 <= actual_idx < len(self.stage_rows):
            # 行のウィジェットを削除
            row_data = self.stage_rows[actual_idx]
            for key in ["label", "time", "level", "delete"]:
                widget = row_data[key]
                self.stages_layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

            # リストから削除
            self.stage_rows.pop(actual_idx)

            # 残りの行を再配置
            for i, row_data in enumerate(self.stage_rows, start=1):
                row_data["label"].setText(f"段階 {i}")
                self.stages_layout.addWidget(row_data["label"], i, 0)
                self.stages_layout.addWidget(row_data["time"], i, 1)
                self.stages_layout.addWidget(row_data["level"], i, 2)
                self.stages_layout.addWidget(row_data["delete"], i, 3)

            # 追加ボタンの位置を更新
            add_btn_row = len(self.stage_rows) + 1
            add_stage_btn = self.stages_layout.itemAtPosition(add_btn_row + 1, 0).widget()
            if add_stage_btn:
                self.stages_layout.removeWidget(add_stage_btn)
                self.stages_layout.addWidget(add_stage_btn, add_btn_row, 0, 1, 4)

    def update_staged_category_combo(self):
        """段階的目標タブ用のカテゴリコンボボックスを更新"""
        self.logger.debug("update_staged_category_combo が呼び出されました")
        self.staged_category_combo.clear()

        group_id = self.staged_group_combo.currentData()
        self.logger.debug(f"選択されたグループID: {group_id}")

        if group_id in self.hierarchy:
            group_data = self.hierarchy[group_id]
            self.logger.debug(f"選択されたグループデータ: {group_data}")

            for cat_id, cat_data in group_data["categories"].items():
                self.staged_category_combo.addItem(cat_data["name"], cat_id)
                self.logger.debug(f"カテゴリを追加: name={cat_data['name']}, id={cat_id}")
        else:
            self.logger.warning(f"グループID '{group_id}' に対応するデータが見つかりません")

        self.update_skill_selection_table()

    def update_skill_selection_table(self):
        """スキル選択テーブルを更新"""
        self.logger.debug("update_skill_selection_table が呼び出されました")
        self.skill_selection_table.setRowCount(0)

        group_id = self.staged_group_combo.currentData()
        cat_id = self.staged_category_combo.currentData()

        self.logger.debug(f"選択されたグループID: {group_id}, カテゴリID: {cat_id}")

        if group_id in self.hierarchy and cat_id and cat_id in self.hierarchy[group_id]["categories"]:
            skills = self.hierarchy[group_id]["categories"][cat_id]["skills"]
            self.logger.debug(f"スキルデータ: {skills}")

            self.skill_selection_table.setRowCount(len(skills))
            for row, (skill_id, skill_data) in enumerate(skills.items()):
                # スキル名
                self.skill_selection_table.setItem(row, 0, QTableWidgetItem(skill_data["name"]))

                # 選択チェックボックス
                checkbox = QCheckBox()
                checkbox.setProperty("skill_id", skill_id)
                checkbox.setChecked(True)  # デフォルトで「含める」を選択
                checkbox.stateChanged.connect(lambda state, check=checkbox: self.update_checkbox_property(check, state))
                self.skill_selection_table.setCellWidget(row, 1, checkbox)
                self.logger.debug(f"スキルを追加: name={skill_data['name']}, id={skill_id}")
        else:
            self.logger.warning(f"グループID '{group_id}' または カテゴリID '{cat_id}' に対応するデータが見つかりません")

    def update_checkbox_property(self, checkbox, state):
        """
        チェックボックスの状態に応じてプロパティを更新
        """
        skill_id = checkbox.property("skill_id")
        selected = (state == Qt.Checked)
        checkbox.setProperty("selected", selected)
        self.logger.debug(f"スキルID '{skill_id}' の選択状態が '{selected}' に変更されました")

    def get_staged_data(self):
        """段階的目標データを収集して返す"""
        # 選択されたグループとカテゴリ
        group_id = self.staged_group_combo.currentData()
        cat_id = self.staged_category_combo.currentData()

        self.logger.debug(f"get_staged_data() - 選択されたグループID: {group_id}, カテゴリID: {cat_id}")

        if not (group_id and cat_id):
            self.logger.debug("get_staged_data() - グループまたはカテゴリが選択されていません")
            return None

        # 時間単位
        time_unit_id = self.time_unit_group.checkedId()
        time_units = ["時間", "日", "週", "月", "年"]
        time_unit = time_units[time_unit_id] if 0 <= time_unit_id < len(time_units) else "月"

        # 選択されたスキル
        selected_skills = {}
        for row in range(self.skill_selection_table.rowCount()):
            checkbox = self.skill_selection_table.cellWidget(row, 1)
            if checkbox and isinstance(checkbox, QCheckBox) and checkbox.isChecked():  # 選択状態を isChecked から取得
                skill_id = checkbox.property("skill_id")
                skill_name = self.skill_selection_table.item(row, 0).text()
                selected_skills[skill_id] = skill_name
        self.logger.debug(f"get_staged_data() - 選択されたスキル: {selected_skills}")

        if not selected_skills:
            self.logger.debug("get_staged_data() - スキルが選択されていません")
            return None

        # 段階データの収集
        stages_data = []
        for i, row_data in enumerate(self.stage_rows):
            time_value = row_data["time"].value()
            level = row_data["level"].currentData()

            # 各スキルのターゲット設定
            targets = {}
            for skill_id, skill_name in selected_skills.items():
                targets[skill_name] = level

            stages_data.append({
                "time": time_value,
                "unit": time_unit,
                "targets": targets,
                "name": f"段階 {i+1}" # チャートで表示するために名前を追加
            })

        # 時間順にソート
        stages_data.sort(key=lambda x: x["time"])
        self.logger.debug(f"get_staged_data() が返すデータ: {stages_data}")  # ログ出力
        return stages_data

    def save_targets(self):
        """段階的な目標値を保存"""
        stages_data = self.get_staged_data()

        if not stages_data:
            QMessageBox.warning(self, "データエラー", "保存するデータがありません。\nグループ、カテゴリ、スキルを正しく選択してください。")
            return

        # 選択されたグループとカテゴリ
        group_id = self.staged_group_combo.currentData()
        cat_id = self.staged_category_combo.currentData()

        # データモデルに保存
        if group_id not in self.staged_targets:
            self.staged_targets[group_id] = {}

        self.staged_targets[group_id][cat_id] = stages_data

        # 保存成功メッセージ
        group_name = self.hierarchy[group_id]["name"]
        cat_name = self.hierarchy[group_id]["categories"][cat_id]["name"]
        time_unit = stages_data[0]["unit"]  # 全ての段階で同じ単位を使用

        message = f"以下の段階的目標を保存しました:\n\n"
        message += f"グループ: {group_name}\n"
        message += f"カテゴリ: {cat_name}\n"
        message += f"時間単位: {time_unit}\n\n"

        # 選択されたスキル名のリスト
        skill_names = list(stages_data[0]["targets"].keys())
        message += f"対象スキル: {', '.join(skill_names[:3])}"
        if len(skill_names) > 3:
            message += f" 他{len(skill_names) - 3}件"

        message += "\n\n段階設定:\n"
        for i, stage in enumerate(stages_data):
            message += f"段階 {i+1}: {stage['time']} {time_unit}後 → レベル {list(stage['targets'].values())[0]}\n"

        QMessageBox.information(self, "段階的目標保存", message)

        # 変更通知
        self.data_changed.emit()

    def show_radar_chart(self):
        """レーダーチャートを表示する"""
        self.logger.info("レーダーチャートを表示")
        try:
            stages_data = self.get_staged_data()  # 実際に設定したデータを使う
            if not stages_data:
                QMessageBox.warning(self, "データエラー", "レーダーチャートを表示するためのデータがありません。\nスキルを選択し、段階的目標を設定してください。")
                return

            from .components.radar_chart_dialog import RadarChartDialog

            dialog = RadarChartDialog(self, stages_data=stages_data)
            self.logger.debug(f"RadarChartDialog インスタンス作成: {dialog}")
            dialog.exec_()
            self.logger.debug("RadarChartDialog exec_() 呼び出し完了")

        except Exception as e:
            self.logger.error(f"レーダーチャート表示中にエラー発生: {e}")
            import traceback
            traceback.print_exc()