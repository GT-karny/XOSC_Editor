"""esmini実行ラッパー"""

import subprocess
import tempfile
import os
import shutil
from pathlib import Path
from typing import Optional, List, Callable
from osc_editor.core.model import ScenarioDefinition
from osc_editor.core.write_xml import write_xml


class EsminiRunner:
    """esmini実行クラス"""
    
    def __init__(self, esmini_path: Optional[str] = None):
        """
        Args:
            esmini_path: esmini実行ファイルのパス（Noneの場合は環境変数から検索）
        """
        self.esmini_path = esmini_path or self._find_esmini()
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
    
    def _find_esmini(self) -> Optional[str]:
        """環境変数や標準的なパスからesminiを検索"""
        # 環境変数から検索
        esmini_env = os.environ.get("ESMINI_PATH")
        if esmini_env:
            esmini_exe = Path(esmini_env) / "bin" / "esmini.exe"
            if esmini_exe.exists():
                return str(esmini_exe)
            esmini_exe = Path(esmini_env) / "bin" / "esmini"
            if esmini_exe.exists():
                return str(esmini_exe)
        
        # 標準的なパスを検索
        common_paths = [
            Path("C:/Program Files/esmini/bin/esmini.exe"),
            Path("/usr/local/bin/esmini"),
            Path("/usr/bin/esmini"),
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def _create_temp_scenario(self, scenario: ScenarioDefinition) -> str:
        """一時ファイルにシナリオを書き込み、パスを返す"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.TemporaryDirectory(prefix="xosc_editor_")
        
        temp_file = os.path.join(self.temp_dir.name, "scenario.xosc")
        write_xml(scenario, temp_file)
        return temp_file
    
    def run(
        self,
        scenario: ScenarioDefinition,
        road_file: Optional[str] = None,
        output_callback: Optional[Callable[[str], None]] = None,
    ) -> subprocess.CompletedProcess:
        """
        esminiを実行
        
        Args:
            scenario: 実行するシナリオ
            road_file: OpenDRIVEファイルのパス（オプション）
            output_callback: 標準出力の各行を呼び出すコールバック
        
        Returns:
            subprocess.CompletedProcess
        """
        if self.esmini_path is None:
            raise RuntimeError(
                "esmini実行ファイルが見つかりません。"
                "ESMINI_PATH環境変数を設定するか、esmini_pathを指定してください。"
            )
        
        # 一時ファイルにシナリオを書き込み
        scenario_file = self._create_temp_scenario(scenario)
        
        # コマンドライン引数を構築
        cmd = [self.esmini_path, "--osc", scenario_file]
        
        if road_file:
            cmd.extend(["--road", road_file])
        
        # esminiを実行
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            
            # 標準出力をリアルタイムで処理
            if output_callback:
                for line in process.stdout:
                    output_callback(line.rstrip())
            
            process.wait()
            
            return subprocess.CompletedProcess(
                cmd,
                process.returncode,
                stdout="",  # 既にコールバックで処理済み
                stderr="",
            )
        except FileNotFoundError:
            raise RuntimeError(f"esmini実行ファイルが見つかりません: {self.esmini_path}")
        except Exception as e:
            raise RuntimeError(f"esmini実行中にエラーが発生しました: {e}")
    
    def cleanup(self):
        """一時ファイルをクリーンアップ"""
        if self.temp_dir is not None:
            self.temp_dir.cleanup()
            self.temp_dir = None
    
    def __del__(self):
        """デストラクタでクリーンアップ"""
        self.cleanup()


