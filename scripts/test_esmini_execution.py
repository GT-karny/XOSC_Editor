"""esminiでの実行テストスクリプト"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from osc_editor.esmini.runner import EsminiRunner

def test_esmini_file(file_path: str, esmini_path: str = None) -> Dict[str, Any]:
    """1つのxoscファイルをesminiで実行してテスト"""
    print(f"\n{'='*60}")
    print(f"Testing with esmini: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    results = {
        'file': file_path,
        'esmini_found': False,
        'execution_success': False,
        'return_code': None,
        'error': None,
        'output': [],
    }
    
    # esmini実行ファイルのパスを設定
    if esmini_path:
        runner = EsminiRunner(esmini_path=esmini_path)
    else:
        # 標準的なパスから検索
        possible_paths = [
            "thirdparty/esmini/bin/esmini.exe",
            "thirdparty/esmini-demo_Windows/esmini-demo/bin/esmini.exe",
        ]
        runner = None
        for path in possible_paths:
            full_path = Path(path).resolve()
            if full_path.exists():
                runner = EsminiRunner(esmini_path=str(full_path))
                break
        
        if runner is None:
            runner = EsminiRunner()  # 環境変数から検索
    
    if runner.esmini_path is None:
        results['error'] = "esmini executable not found"
        print("[ERROR] esmini executable not found")
        return results
    
    results['esmini_found'] = True
    print(f"[OK] Found esmini: {runner.esmini_path}")
    
    # XMLファイルを読み込んでesminiで実行
    try:
        from osc_editor.core.parse_xml import parse_xml
        
        scenario = parse_xml(file_path)
        
        # 出力コールバック
        output_lines = []
        def output_callback(line: str):
            output_lines.append(line)
            # エラーメッセージをチェック
            if "error" in line.lower() or "exception" in line.lower() or "failed" in line.lower():
                print(f"  [ESMINI] {line}")
        
        # esminiで実行（タイムアウト付き）
        try:
            completed = runner.run(
                scenario,
                output_callback=output_callback
            )
            
            results['return_code'] = completed.returncode
            results['output'] = output_lines[:20]  # 最初の20行だけ保存
            
            if completed.returncode == 0:
                results['execution_success'] = True
                print("[OK] esmini execution completed successfully")
            else:
                print(f"[WARNING] esmini returned code: {completed.returncode}")
                # エラー出力を表示
                for line in output_lines[:10]:
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'warning']):
                        print(f"  {line}")
        
        except subprocess.TimeoutExpired:
            results['error'] = "Execution timeout"
            print("[WARNING] esmini execution timeout")
        except Exception as e:
            results['error'] = str(e)
            print(f"[ERROR] esmini execution error: {e}")
        
        finally:
            runner.cleanup()
    
    except Exception as e:
        results['error'] = str(e)
        print(f"[ERROR] Failed to parse or run: {e}")
    
    return results


def main():
    """メイン関数"""
    # テスト対象ファイル（出力ファイル）
    test_files = [
        "out/cut-in.xosc",
        "out/lane_change.xosc",
        "out/pedestrian.xosc",
        "out/bicycle_fall_over.xosc",
        "out/acc-test.xosc",
    ]
    
    # esminiパスの確認
    esmini_paths = [
        "thirdparty/esmini/bin/esmini.exe",
        "thirdparty/esmini-demo_Windows/esmini-demo/bin/esmini.exe",
    ]
    
    esmini_path = None
    for path in esmini_paths:
        if os.path.exists(path):
            esmini_path = os.path.abspath(path)
            print(f"Using esmini: {esmini_path}")
            break
    
    if esmini_path is None:
        print("WARNING: esmini executable not found in standard paths")
        print("Set ESMINI_PATH environment variable or specify path")
        print("Skipping esmini tests...")
        return
    
    all_results = []
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"[WARNING] File not found: {test_file}")
            continue
        
        results = test_esmini_file(test_file, esmini_path)
        all_results.append(results)
    
    # サマリー
    print(f"\n{'='*60}")
    print("ESMINI EXECUTION SUMMARY")
    print(f"{'='*60}")
    
    esmini_found = sum(1 for r in all_results if r['esmini_found'])
    execution_success = sum(1 for r in all_results if r['execution_success'])
    
    print(f"Files tested: {len(all_results)}")
    print(f"esmini found: {esmini_found}/{len(all_results)}")
    print(f"Execution successful: {execution_success}/{len(all_results)}")
    
    # 詳細な結果を表示
    for results in all_results:
        print(f"\n{os.path.basename(results['file'])}:")
        print(f"  esmini found: {results['esmini_found']}")
        print(f"  execution success: {results['execution_success']}")
        if results['return_code'] is not None:
            print(f"  return code: {results['return_code']}")
        if results['error']:
            print(f"  error: {results['error']}")
        if results['output']:
            error_lines = [line for line in results['output'] if any(k in line.lower() for k in ['error', 'exception', 'failed'])]
            if error_lines:
                print(f"  error output (first 3):")
                for line in error_lines[:3]:
                    print(f"    {line}")


if __name__ == "__main__":
    main()

