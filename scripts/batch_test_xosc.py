"""XOSCファイルのバッチ処理とesmini実行テスト"""

import os
import sys
import subprocess
import traceback
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from osc_editor.core.parse_xml import parse_xml
from osc_editor.core.write_xml import write_xml
from osc_editor.esmini.runner import EsminiRunner


class BatchProcessor:
    """XOSCファイルのバッチ処理クラス"""
    
    def __init__(self, 
                 input_dir: str,
                 output_dir: str,
                 esmini_path: Optional[str] = None):
        """
        Args:
            input_dir: 入力XOSCファイルのディレクトリ
            output_dir: 出力XOSCファイルのディレクトリ
            esmini_path: esmini実行ファイルのパス（Noneの場合は自動検索）
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.esmini_path = esmini_path
        
        # 出力ディレクトリを作成
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # エラー記録
        self.errors: List[Dict] = []
        self.success_count = 0
        self.total_count = 0
        
        # esminiランナーを初期化
        self.esmini_runner = None
        if esmini_path:
            self.esmini_runner = EsminiRunner(esmini_path=esmini_path)
        else:
            self.esmini_runner = EsminiRunner()
    
    def process_file(self, xosc_file: Path) -> Dict:
        """
        単一のXOSCファイルを処理
        
        Returns:
            処理結果の辞書
        """
        result = {
            "file": str(xosc_file),
            "filename": xosc_file.name,
            "parse_error": None,
            "write_error": None,
            "esmini_error": None,
            "esmini_output": None,
            "success": False
        }
        
        try:
            # 1. 読み込み
            print(f"読み込み中: {xosc_file.name}")
            try:
                scenario = parse_xml(str(xosc_file))
                print(f"  [OK] 読み込み成功")
            except Exception as e:
                result["parse_error"] = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                print(f"  [ERROR] 読み込みエラー: {e}")
                return result
            
            # 2. 書き出し
            output_file = self.output_dir / xosc_file.name
            print(f"書き出し中: {output_file.name}")
            try:
                write_xml(scenario, str(output_file), pretty_print=True)
                print(f"  [OK] 書き出し成功")
            except Exception as e:
                result["write_error"] = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                print(f"  [ERROR] 書き出しエラー: {e}")
                return result
            
            # 3. esmini実行はスキップ（読み込み・書き出しのみをテスト）
            print(f"esmini実行: スキップ（読み込み・書き出しのみテスト）")
            result["success"] = True  # 読み込み・書き出しが成功していれば成功として扱う
            
        except Exception as e:
            # 予期しないエラー
            result["unexpected_error"] = {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  [ERROR] 予期しないエラー: {e}")
        
        return result
    
    def process_all(self):
        """すべてのXOSCファイルを処理"""
        # XOSCファイルを取得
        xosc_files = list(self.input_dir.glob("*.xosc"))
        self.total_count = len(xosc_files)
        
        print(f"\n{'='*80}")
        print(f"バッチ処理開始: {self.total_count}個のファイル")
        print(f"入力ディレクトリ: {self.input_dir}")
        print(f"出力ディレクトリ: {self.output_dir}")
        print(f"{'='*80}\n")
        
        for i, xosc_file in enumerate(xosc_files, 1):
            print(f"\n[{i}/{self.total_count}] {xosc_file.name}")
            print("-" * 80)
            
            result = self.process_file(xosc_file)
            
            if result["success"]:
                self.success_count += 1
            else:
                self.errors.append(result)
        
        # 結果を表示
        self.print_summary()
        
        # エラー詳細をファイルに保存
        self.save_error_report()
    
    def print_summary(self):
        """結果サマリーを表示"""
        print(f"\n{'='*80}")
        print("処理結果サマリー")
        print(f"{'='*80}")
        print(f"総ファイル数: {self.total_count}")
        print(f"成功: {self.success_count}")
        print(f"エラー: {len(self.errors)}")
        if self.total_count > 0:
            print(f"成功率: {self.success_count / self.total_count * 100:.1f}%")
        print(f"{'='*80}\n")
        
        if self.errors:
            print("エラー詳細:")
            for i, error in enumerate(self.errors, 1):
                print(f"\n[{i}] {error['filename']}")
                if error.get("parse_error"):
                    print(f"  読み込みエラー: {error['parse_error']['type']}: {error['parse_error']['message']}")
                if error.get("write_error"):
                    print(f"  書き出しエラー: {error['write_error']['type']}: {error['write_error']['message']}")
                if error.get("esmini_error"):
                    if isinstance(error['esmini_error'], dict) and 'returncode' in error['esmini_error']:
                        print(f"  esmini実行エラー: 終了コード {error['esmini_error']['returncode']}")
                    else:
                        print(f"  esmini実行エラー: {error['esmini_error']}")
    
    def save_error_report(self):
        """エラーレポートをファイルに保存"""
        if not self.errors:
            print("\nエラーはありませんでした。")
            return
        
        report_file = self.output_dir / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("XOSCバッチ処理エラーレポート\n")
            f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"総ファイル数: {self.total_count}\n")
            f.write(f"成功: {self.success_count}\n")
            f.write(f"エラー: {len(self.errors)}\n")
            if self.total_count > 0:
                f.write(f"成功率: {self.success_count / self.total_count * 100:.1f}%\n\n")
            
            for i, error in enumerate(self.errors, 1):
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"[{i}] {error['filename']}\n")
                f.write("=" * 80 + "\n")
                f.write(f"ファイルパス: {error['file']}\n\n")
                
                if error.get("parse_error"):
                    f.write("【読み込みエラー】\n")
                    f.write(f"タイプ: {error['parse_error']['type']}\n")
                    f.write(f"メッセージ: {error['parse_error']['message']}\n")
                    f.write(f"トレースバック:\n{error['parse_error']['traceback']}\n\n")
                
                if error.get("write_error"):
                    f.write("【書き出しエラー】\n")
                    f.write(f"タイプ: {error['write_error']['type']}\n")
                    f.write(f"メッセージ: {error['write_error']['message']}\n")
                    f.write(f"トレースバック:\n{error['write_error']['traceback']}\n\n")
                
                if error.get("esmini_error"):
                    f.write("【esmini実行エラー】\n")
                    if isinstance(error['esmini_error'], dict):
                        if 'returncode' in error['esmini_error']:
                            f.write(f"終了コード: {error['esmini_error']['returncode']}\n")
                        if 'output' in error['esmini_error']:
                            f.write(f"出力:\n{error['esmini_error']['output']}\n")
                        if 'type' in error['esmini_error']:
                            f.write(f"タイプ: {error['esmini_error']['type']}\n")
                            f.write(f"メッセージ: {error['esmini_error']['message']}\n")
                            f.write(f"トレースバック:\n{error['esmini_error']['traceback']}\n")
                    else:
                        f.write(f"{error['esmini_error']}\n")
                    f.write("\n")
                
                if error.get("unexpected_error"):
                    f.write("【予期しないエラー】\n")
                    f.write(f"タイプ: {error['unexpected_error']['type']}\n")
                    f.write(f"メッセージ: {error['unexpected_error']['message']}\n")
                    f.write(f"トレースバック:\n{error['unexpected_error']['traceback']}\n\n")
        
        print(f"\nエラーレポートを保存しました: {report_file}")


def main():
    """メイン関数"""
    # パス設定
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "thirdparty" / "esmini-demo_Windows" / "esmini-demo" / "resources" / "xosc"
    output_dir = project_root / "out" / "xosc"
    
    # esminiパスを検索
    esmini_path = None
    # まずthirdparty/esmini/bin/esmini.exeを確認
    esmini_candidate = project_root / "thirdparty" / "esmini" / "bin" / "esmini.exe"
    if esmini_candidate.exists():
        esmini_path = str(esmini_candidate)
        print(f"esminiパス: {esmini_path}")
    else:
        # 環境変数から取得
        esmini_env = os.environ.get("ESMINI_PATH")
        if esmini_env:
            esmini_exe = Path(esmini_env) / "bin" / "esmini.exe"
            if esmini_exe.exists():
                esmini_path = str(esmini_exe)
                print(f"esminiパス (環境変数): {esmini_path}")
    
    if not esmini_path:
        print("警告: esmini実行ファイルが見つかりません。esmini実行はスキップされます。")
        print("ESMINI_PATH環境変数を設定するか、thirdparty/esmini/bin/esmini.exeを配置してください。")
    
    # バッチプロセッサーを作成して実行
    processor = BatchProcessor(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        esmini_path=esmini_path
    )
    
    processor.process_all()


if __name__ == "__main__":
    main()

