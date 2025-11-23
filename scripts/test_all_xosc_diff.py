"""全xoscファイルの読み込み・書き出し・差分確認スクリプト"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import difflib
import xml.etree.ElementTree as ET

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# XML正規化用の関数
def normalize_xml(xml_string: str) -> str:
    """XMLを正規化して比較しやすくする"""
    try:
        # XMLをパースして正規化
        root = ET.fromstring(xml_string)
        # 文字列に戻す（整形）
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    except Exception:
        # パースに失敗した場合は元の文字列を返す
        return xml_string

def compare_xml_files(file1_path: str, file2_path: str) -> List[str]:
    """2つのXMLファイルを比較して差分を返す"""
    try:
        with open(file1_path, 'r', encoding='utf-8', errors='replace') as f1:
            xml1 = f1.read()
        with open(file2_path, 'r', encoding='utf-8', errors='replace') as f2:
            xml2 = f2.read()
        
        # XMLを正規化
        normalized1 = normalize_xml(xml1)
        normalized2 = normalize_xml(xml2)
        
        lines1 = normalized1.splitlines(keepends=True)
        lines2 = normalized2.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=os.path.basename(file1_path),
            tofile=os.path.basename(file2_path),
            lineterm=''
        ))
        return diff
    except Exception as e:
        # エラーメッセージを安全に表示
        try:
            error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"  Error comparing files: {error_msg}")
        except:
            print(f"  Error comparing files")
        return []


def test_xosc_file(input_path: str, output_dir: str = "out") -> Dict[str, Any]:
    """1つのxoscファイルをテストして結果を返す"""
    print(f"Testing: {input_path}", end=' ... ')
    
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
        from osc_editor.core.parse_xml import parse_xml
        scenario = parse_xml(input_path)
        results['parse_success'] = True
    except Exception as e:
        results['parse_error'] = str(e)
        print(f"PARSE ERROR: {e}")
        return results
    
    # 2. バリデーション
    try:
        from osc_editor.core.validate import validate_scenario
        validation_errors = validate_scenario(scenario)
        results['validation_errors'] = validation_errors
    except Exception as e:
        pass  # バリデーションエラーは無視
    
    # 3. 書き出し
    try:
        from osc_editor.core.write_xml import write_xml
        write_xml(scenario, output_path)
        results['write_success'] = True
    except Exception as e:
        results['write_error'] = str(e)
        print(f"WRITE ERROR: {e}")
        return results
    
    # 4. 差分確認
    try:
        if os.path.exists(output_path):
            diff = compare_xml_files(input_path, output_path)
            results['differences'] = diff
            if diff:
                diff_lines = [d for d in diff if not d.startswith('---') and not d.startswith('+++') and (d.startswith('-') or d.startswith('+'))]
                if diff_lines:
                    print(f"DIFF ({len(diff_lines)} lines)")
                else:
                    print("OK (no significant diff)")
            else:
                print("OK (no diff)")
    except Exception as e:
        pass
    
    return results


def main():
    """メイン関数"""
    # テスト対象ディレクトリ
    xosc_dir = "thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc"
    
    if not os.path.exists(xosc_dir):
        print(f"Error: Directory not found: {xosc_dir}")
        return
    
    # すべての.xoscファイルを取得（Catalogsディレクトリは除外）
    xosc_files = []
    for root, dirs, files in os.walk(xosc_dir):
        # Catalogsディレクトリはスキップ
        if 'Catalogs' in root:
            continue
        for file in files:
            if file.endswith('.xosc'):
                xosc_files.append(os.path.join(root, file))
    
    xosc_files.sort()
    
    print(f"Found {len(xosc_files)} xosc files")
    print("="*60)
    
    all_results = []
    
    for xosc_file in xosc_files:
        results = test_xosc_file(xosc_file)
        all_results.append(results)
    
    # サマリー
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    parse_success = sum(1 for r in all_results if r['parse_success'])
    write_success = sum(1 for r in all_results if r['write_success'])
    validation_passed = sum(1 for r in all_results if not r['validation_errors'])
    no_diff = sum(1 for r in all_results if not r['differences'])
    
    print(f"Files tested: {len(all_results)}")
    print(f"Parse successful: {parse_success}/{len(all_results)}")
    print(f"Write successful: {write_success}/{len(all_results)}")
    print(f"Validation passed: {validation_passed}/{len(all_results)}")
    print(f"No differences: {no_diff}/{len(all_results)}")
    
    # 差分があるファイルをリスト
    files_with_diff = [r for r in all_results if r['differences']]
    if files_with_diff:
        print(f"\nFiles with differences ({len(files_with_diff)}):")
        for r in files_with_diff:
            diff_lines = [d for d in r['differences'] if not d.startswith('---') and not d.startswith('+++') and (d.startswith('-') or d.startswith('+'))]
            print(f"  - {os.path.basename(r['input_path'])}: {len(diff_lines)} lines")
    
    # エラーがあるファイルをリスト
    files_with_errors = [r for r in all_results if not r['parse_success'] or not r['write_success']]
    if files_with_errors:
        print(f"\nFiles with errors ({len(files_with_errors)}):")
        for r in files_with_errors:
            print(f"  - {os.path.basename(r['input_path'])}")
            if r['parse_error']:
                print(f"    Parse error: {r['parse_error']}")
            if r['write_error']:
                print(f"    Write error: {r['write_error']}")
    
    # 詳細な結果をファイルに保存
    summary_file = "xosc_diff_summary_all.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("xosc File Diff Summary (All Files)\n")
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
            diff_lines = [d for d in results['differences'] if not d.startswith('---') and not d.startswith('+++') and (d.startswith('-') or d.startswith('+'))]
            f.write(f"  Differences: {len(diff_lines)} lines\n")
            if results['differences']:
                f.write("    Diff (first 50 lines):\n")
                for line in results['differences'][:50]:
                    f.write(f"    {line}\n")
            f.write("\n")
    
    print(f"\nDetailed summary saved to: {summary_file}")


if __name__ == "__main__":
    main()

