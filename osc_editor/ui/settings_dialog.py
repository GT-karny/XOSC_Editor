"""設定ダイアログ"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from pathlib import Path
from osc_editor.core.settings import Settings


class SettingsDialog(QDialog):
    """設定ダイアログクラス"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumWidth(500)
        
        self.settings = Settings()
        
        self._create_ui()
        self._load_settings()
    
    def _create_ui(self):
        """UIを作成"""
        layout = QVBoxLayout(self)
        
        # esminiパス設定セクション
        esmini_group_layout = QVBoxLayout()
        esmini_label = QLabel("esmini実行ファイルのパス:")
        esmini_group_layout.addWidget(esmini_label)
        
        # パス入力とファイル選択ボタン
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("esmini.exeのパスを選択してください")
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("参照...")
        browse_button.clicked.connect(self._browse_esmini_path)
        path_layout.addWidget(browse_button)
        
        esmini_group_layout.addLayout(path_layout)
        layout.addLayout(esmini_group_layout)
        
        # 説明ラベル
        info_label = QLabel(
            "esminiの実行ファイル（esmini.exe）を選択してください。\n"
            "または、esminiのインストールディレクトリのbinフォルダ内のesmini.exeを指定してください。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """設定を読み込んでUIに反映"""
        path = self.settings.get_esmini_path()
        if path:
            self.path_edit.setText(path)
    
    def _browse_esmini_path(self):
        """esmini実行ファイルを選択"""
        # 現在のパスから初期ディレクトリを決定
        current_path = self.path_edit.text()
        initial_dir = None
        if current_path:
            path_obj = Path(current_path)
            if path_obj.exists():
                initial_dir = str(path_obj.parent)
        
        # ファイル選択ダイアログ
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "esmini実行ファイルを選択",
            initial_dir or "",
            "実行ファイル (*.exe);;すべてのファイル (*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def _on_ok_clicked(self):
        """OKボタンがクリックされたときの処理"""
        path = self.path_edit.text().strip()
        
        # 空の場合は設定を削除
        if not path:
            self.settings.set_esmini_path(None)
            self.accept()
            return
        
        # パスの検証
        path_obj = Path(path)
        if not path_obj.exists():
            QMessageBox.warning(
                self,
                "エラー",
                f"指定されたパスが存在しません:\n{path}"
            )
            return
        
        if not path_obj.is_file():
            QMessageBox.warning(
                self,
                "エラー",
                f"指定されたパスはファイルではありません:\n{path}"
            )
            return
        
        # 設定を保存
        if self.settings.set_esmini_path(path):
            QMessageBox.information(
                self,
                "設定を保存しました",
                f"esminiパスを設定しました:\n{path}"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "エラー",
                "設定の保存に失敗しました。"
            )

