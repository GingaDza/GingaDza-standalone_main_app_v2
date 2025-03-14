#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging

# ログ設定
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
print(f"現在の作業ディレクトリ: {current_dir}")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel

    # メインアプリケーションのモック
    class MainAppMock:
        def __init__(self):
            self.event_manager = None
            self.shared_data = {}
            
        def get_setting(self, key, default=None):
            return default
            
        def save_setting(self, key, value):
            print(f"設定保存: {key}")
            return True
            
        def show_message(self, message, title="情報", message_type="info"):
            print(f"メッセージ: {title} - {message}")
            return True
    
    # アプリケーション作成
    app = QApplication(sys.argv)
    
    # メインウィンドウ作成
    main_window = QMainWindow()
    main_window.setWindowTitle("簡易テスト")
    
    # 中央ウィジェット
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # レイアウト
    layout = QVBoxLayout(central_widget)
    
    # テスト用ラベル
    label = QLabel("テストウィンドウ")
    label.setStyleSheet("font-size: 24px; color: blue;")
    layout.addWidget(label)
    
    # 本来のインポートはここで行う
    print("StagedTargetTabをインポートします...")
    try:
        sys.path.append(os.path.join(current_dir, "plugins", "staged_target"))
        from staged_target_tab import StagedTargetTab
        
        # タブ作成
        print("タブを作成します...")
        main_app_mock = MainAppMock()
        tab = StagedTargetTab(main_app=main_app_mock)
        
        # レイアウトに追加
        layout.addWidget(tab)
        print("タブを追加しました")
    except Exception as e:
        error_label = QLabel(f"エラー: {str(e)}")
        error_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(error_label)
        print(f"エラーが発生しました: {e}")
    
    # ウィンドウ表示
    main_window.resize(1000, 700)
    main_window.show()
    print("ウィンドウを表示しました")
    
    sys.exit(app.exec_())

except Exception as e:
    print(f"全体エラー: {e}")
    import traceback
    traceback.print_exc()