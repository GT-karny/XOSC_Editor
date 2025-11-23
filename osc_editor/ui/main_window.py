"""メインウィンドウ"""

from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QMenu,
    QStatusBar,
    QDockWidget,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from osc_editor.ui.scenario_tree import ScenarioTreeWidget
from osc_editor.ui.properties_panel import PropertiesPanel
from osc_editor.ui.menu_actions import MenuActions
from osc_editor.ui.settings_dialog import SettingsDialog
from osc_editor.core.model import ScenarioDefinition


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("XOSC Editor - OpenSCENARIO 1.2 Editor")
        self.setMinimumSize(800, 600)
        
        # メニューアクション
        self.menu_actions = MenuActions(self)
        self.menu_actions.scenario_changed.connect(self._on_scenario_changed)
        self.menu_actions.scenario_modified.connect(self._on_scenario_modified)
        
        # UIコンポーネント
        self.scenario_tree: ScenarioTreeWidget = None
        self.properties_panel: PropertiesPanel = None
        
        self._create_menu_bar()
        self._create_status_bar()
        self._create_dock_widgets()
        
        # 中央ウィジェット（将来のストーリーボードビュー用）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 初期状態で新規ファイルを作成
        self.menu_actions.new_file()

    def _create_menu_bar(self):
        """メニューバーの作成"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")
        file_menu.addAction("新規(&N)", self._new_file, "Ctrl+N")
        file_menu.addAction("開く(&O)...", self._open_file, "Ctrl+O")
        file_menu.addAction("保存(&S)", self._save_file, "Ctrl+S")
        file_menu.addAction("名前を付けて保存(&A)...", self._save_as_file, "Ctrl+Shift+S")
        file_menu.addSeparator()
        file_menu.addAction("終了(&X)", self.close, "Ctrl+Q")
        
        # 編集メニュー
        edit_menu = menubar.addMenu("編集(&E)")
        edit_menu.addAction("元に戻す(&U)", self._undo, "Ctrl+Z")
        edit_menu.addAction("やり直し(&R)", self._redo, "Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("削除(&D)", self._delete, "Del")
        
        # 表示メニュー
        view_menu = menubar.addMenu("表示(&V)")
        view_menu.addAction("ストーリーボードツリー", self._toggle_scenario_tree)
        view_menu.addAction("プロパティパネル", self._toggle_properties_panel)
        
        # 実行メニュー
        run_menu = menubar.addMenu("実行(&R)")
        run_menu.addAction("esminiで再生(&P)", self._run_esmini, "F5")
        
        # 設定メニュー
        settings_menu = menubar.addMenu("設定(&S)")
        settings_menu.addAction("設定(&S)...", self._open_settings)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")
        help_menu.addAction("バージョン情報(&A)...", self._about)

    def _create_status_bar(self):
        """ステータスバーの作成"""
        self.statusBar().showMessage("準備完了")

    def _create_dock_widgets(self):
        """ドッキングウィジェットの作成"""
        # ストーリーボードツリー（左側）
        self.scenario_tree_dock = QDockWidget("ストーリーボード", self)
        self.scenario_tree_dock.setObjectName("ScenarioTreeDock")
        self.scenario_tree = ScenarioTreeWidget()
        self.scenario_tree.node_selected.connect(self._on_node_selected)
        self.scenario_tree_dock.setWidget(self.scenario_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.scenario_tree_dock)
        
        # プロパティパネル（右側）
        self.properties_dock = QDockWidget("プロパティ", self)
        self.properties_dock.setObjectName("PropertiesDock")
        self.properties_panel = PropertiesPanel()
        self.properties_panel.property_changed.connect(self._on_property_changed)
        self.properties_dock.setWidget(self.properties_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)

    # メニューアクション
    def _new_file(self):
        """新規ファイル作成"""
        if self.menu_actions.new_file():
            self.statusBar().showMessage("新規ファイルを作成しました", 2000)

    def _open_file(self):
        """ファイルを開く"""
        if self.menu_actions.open_file():
            self.statusBar().showMessage("ファイルを開きました", 2000)

    def _save_file(self):
        """ファイルを保存"""
        if self.menu_actions.save_file():
            self.statusBar().showMessage("ファイルを保存しました", 2000)

    def _save_as_file(self):
        """名前を付けて保存"""
        if self.menu_actions.save_file_as():
            self.statusBar().showMessage("ファイルを保存しました", 2000)

    def _undo(self):
        """元に戻す"""
        self.statusBar().showMessage("元に戻す（未実装）", 2000)

    def _redo(self):
        """やり直し"""
        self.statusBar().showMessage("やり直し（未実装）", 2000)

    def _delete(self):
        """削除"""
        self.statusBar().showMessage("削除（未実装）", 2000)

    def _toggle_scenario_tree(self):
        """ストーリーボードツリーの表示/非表示"""
        self.scenario_tree_dock.setVisible(not self.scenario_tree_dock.isVisible())

    def _toggle_properties_panel(self):
        """プロパティパネルの表示/非表示"""
        self.properties_dock.setVisible(not self.properties_dock.isVisible())

    def _run_esmini(self):
        """esminiで再生"""
        self.statusBar().showMessage("esminiを実行中...", 0)
        self.menu_actions.run_esmini()
        self.statusBar().showMessage("準備完了", 0)

    def _open_settings(self):
        """設定ダイアログを開く"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def _about(self):
        """バージョン情報"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "バージョン情報",
            "XOSC Editor\n\n"
            "ASAM OpenSCENARIO 1.2 対応シナリオエディタ\n\n"
            "Version 0.1.0"
        )
    
    def _on_scenario_changed(self, scenario: ScenarioDefinition):
        """シナリオ変更時のハンドラ"""
        if self.scenario_tree:
            self.scenario_tree.set_scenario(scenario)
        
        if self.properties_panel:
            self.properties_panel.set_scenario(scenario)
        
        # ウィンドウタイトルを更新
        file_path = self.menu_actions.current_file_path
        if file_path:
            self.setWindowTitle(f"XOSC Editor - {file_path}")
        else:
            self.setWindowTitle("XOSC Editor - 新規ファイル")
    
    def _on_scenario_modified(self, is_modified: bool):
        """シナリオ変更状態変更時のハンドラ"""
        title = self.windowTitle()
        if is_modified and not title.startswith("*"):
            self.setWindowTitle(f"*{title}")
        elif not is_modified and title.startswith("*"):
            self.setWindowTitle(title[1:])
    
    def _on_node_selected(self, node):
        """ノード選択時のハンドラ"""
        if self.properties_panel:
            self.properties_panel.set_node(node)
    
    def _on_property_changed(self):
        """プロパティ変更時のハンドラ"""
        self.menu_actions.mark_modified()
        # ツリーを更新（名前変更など）
        scenario = self.menu_actions.current_scenario
        if scenario and self.scenario_tree:
            self.scenario_tree.set_scenario(scenario)
    
    def closeEvent(self, event):
        """ウィンドウを閉じる際のイベント"""
        if self.menu_actions.is_modified:
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "未保存の変更",
                "未保存の変更があります。終了しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        event.accept()

