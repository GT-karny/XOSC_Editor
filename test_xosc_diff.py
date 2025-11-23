"""xoscファイルの読み込み・書き出し・差分確認スクリプト"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import difflib
from osc_editor.core.parse_xml import parse_xml
from osc_editor.core.write_xml import write_xml
from osc_editor.core.validate import validate_scenario


def compare_xml_files(file1_path: str, file2_path: str) -> List[str]:
    """2つのXMLファイルを比較して差分を返す"""
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        with open(file2_path, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=os.path.basename(file1_path),
            tofile=os.path.basename(file2_path),
            lineterm=''
        ))
        return diff
    except Exception as e:
        print(f"  Error comparing files: {e}")
        return []


def test_xosc_file(input_path: str, output_dir: str = "out") -> Dict[str, Any]:
    """1つのxoscファイルをテストして結果を返す"""
    print(f"\n{'='*60}")
    print(f"Testing: {input_path}")
    print(f"{'='*60}")
    
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 出力ファイル名を決定
    input_filename = Path(input_path).name
    output_path = os.path.join(output_dir, input_filename)
    
    results = {
        'input_path': input_path,
        'output_path': output_path,
        'parse_success': False,
        'write_success': False,
        'validation_errors': [],
        'differences': [],
        'parse_error': None,
        'write_error': None,
    }
    
    # 1. パース
    try:
        scenario = parse_xml(input_path)
        results['parse_success'] = True
        print("[OK] Parse successful")
    except Exception as e:
        results['parse_error'] = str(e)
        print(f"[ERROR] Parse failed: {e}")
        return results
    
    # 2. バリデーション
    try:
        validation_errors = validate_scenario(scenario)
        results['validation_errors'] = validation_errors
        if validation_errors:
            print(f"⚠ Validation errors: {len(validation_errors)}")
            for error in validation_errors[:5]:  # 最初の5つだけ表示
                print(f"  - {error}")
            if len(validation_errors) > 5:
                print(f"  ... and {len(validation_errors) - 5} more")
        else:
            print("[OK] Validation passed")
    except Exception as e:
        print(f"[WARNING] Validation exception: {e}")
    
    # 3. 書き出し
    try:
        write_xml(scenario, output_path)
        results['write_success'] = True
        print("[OK] Write successful")
    except Exception as e:
        results['write_error'] = str(e)
        print(f"[ERROR] Write failed: {e}")
        return results
    
    # 4. 差分確認
    try:
        if os.path.exists(output_path):
            diff = compare_xml_files(input_path, output_path)
            results['differences'] = diff
            if diff:
                diff_lines = [d for d in diff if not d.startswith('---') and not d.startswith('+++') and (d.startswith('-') or d.startswith('+'))]
                print(f"⚠ Differences found: {len(diff_lines)} lines")
                # 最初の10行だけ表示
                for line in diff[:20]:
                    if line.startswith('+') or line.startswith('-'):
                        print(f"  {line}")
                if len(diff) > 20:
                    print(f"  ... and {len(diff) - 20} more lines")
            else:
                print("[OK] No differences")
    except Exception as e:
        print(f"[WARNING] Diff comparison failed: {e}")
    
    return results


def main():
    """メイン関数"""
    # テスト対象ファイル
    test_files = [
        "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/cut-in.xosc",
        "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/lane_change.xosc",
        "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/pedestrian.xosc",
        "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/bicycle_fall_over.xosc",
        "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/acc-test.xosc",
    ]
    
    all_results = []
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"[WARNING] File not found: {test_file}")
            continue
        
        results = test_xosc_file(test_file)
        all_results.append(results)
    
    # サマリー
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    parse_success = sum(1 for r in all_results if r['parse_success'])
    write_success = sum(1 for r in all_results if r['write_success'])
    validation_passed = sum(1 for r in all_results if not r['validation_errors'])
    no_diff = sum(1 for r in all_results if not r['differences'])
    
    print(f"Files tested: {len(all_results)}")
    print(f"Parse successful: {parse_success}/{len(all_results)}")
    print(f"Write successful: {write_success}/{len(all_results)}")
    print(f"Validation passed: {validation_passed}/{len(all_results)}")
    print(f"No differences: {no_diff}/{len(all_results)}")
    
    # 詳細な結果をファイルに保存
    summary_file = "xosc_diff_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("xosc File Diff Summary\n")
        f.write("="*60 + "\n\n")
        
        for results in all_results:
            f.write(f"File: {results['input_path']}\n")
            f.write(f"  Parse: {'OK' if results['parse_success'] else 'ERROR'}\n")
            if results['parse_error']:
                f.write(f"    Error: {results['parse_error']}\n")
            f.write(f"  Write: {'OK' if results['write_success'] else 'ERROR'}\n")
            if results['write_error']:
                f.write(f"    Error: {results['write_error']}\n")
            f.write(f"  Validation errors: {len(results['validation_errors'])}\n")
            for error in results['validation_errors']:
                f.write(f"    - {error}\n")
            f.write(f"  Differences: {len([d for d in results['differences'] if not d.startswith('---') and not d.startswith('+++') and (d.startswith('-') or d.startswith('+'))])} lines\n")
            if results['differences']:
                f.write("    Diff:\n")
                for line in results['differences']:
                    f.write(f"    {line}\n")
            f.write("\n")
    
    print(f"\nDetailed summary saved to: {summary_file}")


if __name__ == "__main__":
    main()

