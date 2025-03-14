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
print(f"Python path: {sys.path}")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton

    # 直接クラスをインポートする前にコンポーネントのディレクトリをPythonパスに追加
    standalone_app_dir = os.path.join(current_dir, "standalone_main_app")
    sys.path.append(standalone_app_dir)
    plugins_dir = os.path.join(standalone_app_dir, "plugins")
    sys.path.append(plugins_dir)
    staged_dir = os.path.join(plugins_dir, "staged_target")
    sys.path.append(staged_dir)
    components_dir = os.path.join(staged_dir, "components")
    sys.path.append(components_dir)

    print("Python パス:")
    for p in sys.path:
        print(f" - {p}")
    
    print("\nディレクトリ内容:")
    if os.path.exists(staged_dir):
        print(f"{staged_dir}:")
        print(os.listdir(staged_dir))
    
    if os.path.exists(components_dir):
        print(f"{components_dir}:")
        print(os.listdir(components_dir))
    
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
            
        def register_event_listener(self, event_name, callback):
            print(f"イベント登録: {event_name}")
            return True
    
    # アプリケーション作成
    app = QApplication(sys.argv)
    
    # メインウィンドウ作成
    main_window = QMainWindow()
    main_window.setWindowTitle("段階的目標設定テスト")
    
    # 中央ウィジェット
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # レイアウト
    layout = QVBoxLayout(central_widget)
    
    # ヘッダー（可視化のため）
    header = QLabel("===== 段階的目標設定タブ テスト =====")
    header.setStyleSheet("font-size: 16px; font-weight: bold; color: blue; background-color: #f0f0f0; padding: 5px;")
    layout.addWidget(header)
    
    try:
        print("\nStagedTargetTab をインポートします...")
        # まず相対パスでインポートを試みる
        sys.path.append(os.path.abspath(os.path.join(staged_dir)))
        
        # インポート方法を試す
        try:
            # 方法1: 直接インポート
            print("方法1: 直接インポート")
            from staged_target_tab import StagedTargetTab
            print("インポート成功 (方法1)")
        except ImportError as e1:
            print(f"インポートエラー (方法1): {e1}")
            
            try:
                # 方法2: フルパスでのインポート
                print("方法2: フルパスでのインポート")
                from standalone_main_app.plugins.staged_target.staged_target_tab import StagedTargetTab
                print("インポート成功 (方法2)")
            except ImportError as e2:
                print(f"インポートエラー (方法2): {e2}")
                
                try:
                    # 方法3: sys.pathにファイルのディレクトリを追加
                    print("方法3: ファイルディレクトリをsys.pathに追加")
                    tab_file_path = os.path.join(staged_dir, "staged_target_tab.py")
                    if os.path.exists(tab_file_path):
                        print(f"ファイルは存在します: {tab_file_path}")
                        
                        # ファイルを直接実行してモジュールをロード
                        print("直接ファイルを実行してクラスを読み込みます")
                        tab_namespace = {}
                        with open(tab_file_path, 'r', encoding='utf-8') as f:
                            tab_code = f.read()
                        
                        exec(tab_code, tab_namespace)
                        if 'StagedTargetTab' in tab_namespace:
                            StagedTargetTab = tab_namespace['StagedTargetTab']
                            print("クラスを直接読み込みました")
                        else:
                            raise ImportError("クラスが見つかりませんでした")
                    else:
                        print(f"ファイルが存在しません: {tab_file_path}")
                        raise FileNotFoundError(f"ファイルが存在しません: {tab_file_path}")
                except Exception as e3:
                    print(f"すべてのインポート方法が失敗しました: {e3}")
                    raise
        
        print("タブを作成します...")
        main_app_mock = MainAppMock()
        tab = StagedTargetTab(main_app=main_app_mock)
        print("タブの作成に成功しました")
        
        # タブをレイアウトに追加
        layout.addWidget(tab)
        
    except Exception as e:
        error_label = QLabel(f"エラーが発生しました: {str(e)}")
        error_label.setStyleSheet("color: red; font-weight: bold; padding: 20px;")
        layout.addWidget(error_label)
        
        # エラー情報を詳細表示
        import traceback
        error_details = QLabel(traceback.format_exc())
        error_details.setWordWrap(True)
        error_details.setStyleSheet("color: #880000; font-family: monospace; background-color: #ffe0e0; padding: 10px;")
        layout.addWidget(error_details)
        
        print(f"エラーが発生しました: {e}")
        traceback.print_exc()
    
    # フッター（可視化のため）
    footer = QLabel("===== テスト終了 =====")
    footer.setStyleSheet("color: green; font-weight: bold; background-color: #f0f0f0; padding: 5px;")
    layout.addWidget(footer)
    
    # 閉じるボタン
    close_btn = QPushButton("閉じる")
    close_btn.clicked.connect(app.quit)
    layout.addWidget(close_btn)
    
    # ウィンドウ表示
    main_window.resize(1000, 700)
    main_window.show()
    print("ウィンドウを表示しました")
    
    sys.exit(app.exec_())

except Exception as e:
    print(f"全体エラー: {e}")
    import traceback
    traceback.print_exc()