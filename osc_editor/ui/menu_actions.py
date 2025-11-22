"""メニューアクション（新規/開く/保存/esmini再生）"""

from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QObject, Signal
from pathlib import Path
from typing import Optional
from osc_editor.core.model import ScenarioDefinition, FileHeader, RoadNetwork, Entities, Storyboard, Init
from osc_editor.core.parse_xml import parse_xml
from osc_editor.core.write_xml import write_xml
from osc_editor.core.validate import validate_and_get_errors
from osc_editor.core.settings import Settings
from osc_editor.esmini.runner import EsminiRunner


class MenuActions(QObject):
    """メニューアクションを管理するクラス"""
    
    # シナリオ変更時のシグナル
    scenario_changed = Signal(ScenarioDefinition)
    scenario_modified = Signal(bool)  # 未保存変更の有無
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_scenario: Optional[ScenarioDefinition] = None
        self._current_file_path: Optional[str] = None
        self._is_modified = False
        self._esmini_runner: Optional[EsminiRunner] = None
        self._settings = Settings()
    
    @property
    def current_scenario(self) -> Optional[ScenarioDefinition]:
        """現在のシナリオを取得"""
        return self._current_scenario
    
    @property
    def current_file_path(self) -> Optional[str]:
        """現在のファイルパスを取得"""
        return self._current_file_path
    
    @property
    def is_modified(self) -> bool:
        """未保存変更があるか"""
        return self._is_modified
    
    def new_file(self) -> bool:
        """新規ファイル作成"""
        if self._check_save_changes():
            self._create_new_scenario()
            return True
        return False
    
    def open_file(self) -> bool:
        """ファイルを開く"""
        if not self._check_save_changes():
            return False
        
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "OpenSCENARIOファイルを開く",
            "",
            "OpenSCENARIO Files (*.xosc);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        try:
            scenario = parse_xml(file_path)
            self._current_scenario = scenario
            self._current_file_path = file_path
            self._is_modified = False
            self.scenario_changed.emit(scenario)
            self.scenario_modified.emit(False)
            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                "エラー",
                f"ファイルを開けませんでした:\n{str(e)}"
            )
            return False
    
    def save_file(self) -> bool:
        """ファイルを保存"""
        if not self._current_scenario:
            return False
        
        if not self._current_file_path:
            return self.save_file_as()
        
        return self._save_to_file(self._current_file_path)
    
    def save_file_as(self) -> bool:
        """名前を付けて保存"""
        if not self._current_scenario:
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "OpenSCENARIOファイルを保存",
            "",
            "OpenSCENARIO Files (*.xosc);;All Files (*)"
        )
        
        if not file_path:
            return False
        
        return self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str) -> bool:
        """指定パスにファイルを保存"""
        try:
            # バリデーション
            is_valid, errors = validate_and_get_errors(self._current_scenario)
            if not is_valid:
                reply = QMessageBox.warning(
                    None,
                    "バリデーション警告",
                    f"シナリオに{len(errors)}個のエラーがあります。\n"
                    "保存しますか？\n\n" +
                    "\n".join(str(e) for e in errors[:5]),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return False
            
            write_xml(self._current_scenario, file_path)
            self._current_file_path = file_path
            self._is_modified = False
            self.scenario_modified.emit(False)
            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                "エラー",
                f"ファイルを保存できませんでした:\n{str(e)}"
            )
            return False
    
    def _check_save_changes(self) -> bool:
        """未保存変更がある場合、保存確認ダイアログを表示"""
        if not self._is_modified:
            return True
        
        reply = QMessageBox.question(
            None,
            "未保存の変更",
            "未保存の変更があります。保存しますか？",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        
        if reply == QMessageBox.StandardButton.Yes:
            return self.save_file()
        
        return True
    
    def _create_new_scenario(self):
        """新規シナリオを作成"""
        self._current_scenario = ScenarioDefinition(
            file_header=FileHeader(
                rev_major=1,
                rev_minor=2,
                description="New scenario",
                author="",
            ),
            parameter_declarations=None,
            catalog_locations=None,
            road_network=RoadNetwork(),
            entities=Entities(),
            storyboard=Storyboard(init=Init()),
        )
        self._current_file_path = None
        self._is_modified = False
        self.scenario_changed.emit(self._current_scenario)
        self.scenario_modified.emit(False)
    
    def mark_modified(self):
        """変更をマーク"""
        if not self._is_modified:
            self._is_modified = True
            self.scenario_modified.emit(True)
    
    def run_esmini(self, output_callback=None):
        """esminiで再生"""
        if not self._current_scenario:
            QMessageBox.warning(
                None,
                "警告",
                "シナリオが読み込まれていません。"
            )
            return
        
        try:
            # 設定からesminiパスを取得
            esmini_path = self._settings.get_esmini_path()
            
            # EsminiRunnerを初期化（すべてのケースを処理）
            # ケース1: ランナーなし + パスなし -> 新規作成（デフォルト検索）
            # ケース2: ランナーなし + パスあり -> 新規作成（指定パス）
            # ケース3: ランナーあり + パスなし -> 再初期化（デフォルト検索）
            # ケース4: ランナーあり + パスあり -> 再初期化（指定パス）
            if self._esmini_runner is None:
                # ランナーがない場合：新規作成
                if esmini_path:
                    self._esmini_runner = EsminiRunner(esmini_path=esmini_path)
                else:
                    self._esmini_runner = EsminiRunner()
            else:
                # ランナーがある場合：設定が変更されている可能性があるため常に再初期化
                if esmini_path:
                    self._esmini_runner = EsminiRunner(esmini_path=esmini_path)
                else:
                    # パスがクリアされた場合も再初期化（デフォルト検索）
                    self._esmini_runner = EsminiRunner()
            
            road_file = None
            if self._current_scenario.road_network and self._current_scenario.road_network.logic_file:
                road_file = self._current_scenario.road_network.logic_file
            
            def default_callback(line: str):
                if output_callback:
                    output_callback(line)
                else:
                    print(line)
            
            process = self._esmini_runner.run(
                self._current_scenario,
                road_file=road_file,
                output_callback=default_callback
            )
            
            if process.returncode == 0:
                QMessageBox.information(
                    None,
                    "成功",
                    "esminiの実行が完了しました。"
                )
            else:
                QMessageBox.warning(
                    None,
                    "警告",
                    f"esminiの実行が終了しました（終了コード: {process.returncode}）。"
                )
        except Exception as e:
            QMessageBox.critical(
                None,
                "エラー",
                f"esminiの実行中にエラーが発生しました:\n{str(e)}"
            )


