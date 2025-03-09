"""レーダーチャートダイアログ - 段階別スキル目標値の可視化"""
import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ダミーのDebugLogger（循環インポートを避けるため）
#class DebugLogger:
#    @staticmethod
#    def get_logger():
#        import logging
#        logging.basicConfig(level=logging.DEBUG)
#        return logging.getLogger(__name__)

# ロガー取得
#logger = DebugLogger.get_logger()
import logging
logger = logging.getLogger(__name__)

class RadarChartDialog(QDialog):
    """レーダーチャートを表示するダイアログ"""

    def __init__(self, parent, stages_data):
        super().__init__(parent)
        try:
            logger.info(f"RadarChartDialog初期化: {len(stages_data) if stages_data else 0}個のステージデータ")
            self.stages_data = stages_data

            self.setWindowTitle("スキルギャップ分析 - レーダーチャート")
            self.setMinimumSize(800, 600)
            self.setup_ui()
        except Exception as e:
            logger.error(f"RadarChartDialog の初期化中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc() # スタックトレースを表示
            # 例外を再発生させることで、上位の例外ハンドラで処理できるようにします。
            raise

    def setup_ui(self):
        """UIの初期設定"""
        layout = QVBoxLayout(self)

        # タイトル
        title_layout = QHBoxLayout()
        title_label = QLabel("段階別スキルギャップ レーダーチャート")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        layout.addLayout(title_layout)

        # MatplotlibのFigureとCanvas
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        # 説明テキスト
        desc_label = QLabel("各段階でのスキル目標値をレーダーチャートで表示しています。")
        desc_label.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(desc_label)

        # 閉じるボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        close_btn = QPushButton("閉じる")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("padding: 8px 16px;")
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # チャートを描画
        self.draw_radar_chart()

    def draw_radar_chart(self):
        """レーダーチャートを描画"""
        # 図をクリア
        self.figure.clear()

        if not self.stages_data:
            # データがない場合
            logger.warning("表示可能なデータがありません")
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "表示可能なデータがありません",
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            self.canvas.draw()
            return

        # スキル名のセットを作成
        all_skills = set()
        for stage in self.stages_data:
            all_skills.update(stage.get("targets", {}).keys())

        if not all_skills:
            # スキルがない場合
            logger.warning("スキルデータがありません")
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "スキルデータがありません",
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
            self.canvas.draw()
            return

        # スキル名のリスト
        skills = sorted(list(all_skills))
        logger.info(f"レーダーチャート描画: {len(skills)}個のスキル, {len(self.stages_data)}個のステージ")

        # レーダーチャートの描画
        ax = self.figure.add_subplot(111, polar=True)

        # 角度の設定
        angles = np.linspace(0, 2*np.pi, len(skills), endpoint=False).tolist()

        # チャートを閉じるために最初の点を最後にも追加
        angles.append(angles[0])

        # モダンな配色
        colors = [
            "#FF6B6B",  # 赤
            "#4ECDC4",  # ターコイズ
            "#FFD166",  # 黄色
            "#6A0572",  # 紫
            "#1A535C",  # 深緑
            "#F0C808",  # 金色
            "#5C80BC",  # 青
            "#C16200",  # オレンジ
        ]

        # 各段階のデータをプロット
        for i, stage in enumerate(self.stages_data):
            targets = stage.get("targets", {})

            # 全てのスキルのデータを準備（ない場合は1）
            values = [targets.get(skill, 1) for skill in skills]

            # チャートを閉じるためにリストの最初の要素を最後に追加
            values.append(values[0])

            color = colors[i % len(colors)]

            # ラベル名の設定
            if "name" in stage:
                label = stage["name"]
            elif "time" in stage and "unit" in stage:
                label = f"{stage['time']}{stage['unit']}後"
            else:
                label = f"段階 {i+1}"

            logger.info(f"プロット: {label}, {len(values)-1}個の値")

            # プロット
            ax.plot(angles, values, 'o-', linewidth=2, color=color, label=label)
            ax.fill(angles, values, color=color, alpha=0.25)

        # 軸設定
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(skills)

        # y軸の設定
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_ylim(0, 5)

        # グリッド
        ax.grid(True, linestyle='-', alpha=0.5)

        # 凡例
        legend = ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

        # チャートタイトル
        if self.stages_data and len(self.stages_data) > 0:
            if "unit" in self.stages_data[0]:
                unit = self.stages_data[0]["unit"]
                ax.set_title(f"スキル目標レベル (期間: {unit}単位)", pad=20, fontsize=14)
            else:
                ax.set_title("段階別スキル目標レベル", pad=20, fontsize=14)

        self.figure.tight_layout()
        self.canvas.draw()