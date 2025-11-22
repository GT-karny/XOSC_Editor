"""アプリケーション設定管理"""

from PySide6.QtCore import QSettings
from pathlib import Path
from typing import Optional


class Settings:
    """アプリケーション設定を管理するクラス"""
    
    def __init__(self):
        """設定オブジェクトを初期化"""
        self._settings = QSettings("XOSC Editor", "XOSC Editor")
    
    def get_esmini_path(self) -> Optional[str]:
        """
        esmini実行ファイルのパスを取得
        
        Returns:
            esmini実行ファイルのパス（未設定の場合はNone）
        """
        path = self._settings.value("esmini/path", None)
        if path and isinstance(path, str):
            # パスが存在するか確認
            if Path(path).exists():
                return path
            # 存在しない場合は設定をクリア
            self._settings.remove("esmini/path")
        return None
    
    def set_esmini_path(self, path: Optional[str]) -> bool:
        """
        esmini実行ファイルのパスを設定
        
        Args:
            path: esmini実行ファイルのパス（Noneの場合は設定を削除）
        
        Returns:
            設定が成功した場合True
        """
        if path is None:
            self._settings.remove("esmini/path")
            return True
        
        # パスの検証
        path_obj = Path(path)
        if not path_obj.exists():
            return False
        
        # ファイルが実行可能か確認（拡張子チェック）
        if path_obj.is_file():
            # Windowsの場合、.exeファイルを期待
            if path_obj.suffix.lower() in ('.exe', '') or path_obj.name.startswith('esmini'):
                self._settings.setValue("esmini/path", str(path_obj.absolute()))
                return True
        
        return False
    
    def get_esmini_directory(self) -> Optional[str]:
        """
        esminiのインストールディレクトリを取得（ESMINI_PATH相当）
        
        Returns:
            esminiのインストールディレクトリ（未設定の場合はNone）
        """
        path = self.get_esmini_path()
        if path:
            path_obj = Path(path)
            # bin/esmini.exe または bin/esmini の形式を想定
            if path_obj.parent.name == "bin":
                return str(path_obj.parent.parent.absolute())
        return None

