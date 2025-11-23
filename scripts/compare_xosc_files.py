"""XOSCファイルの差分確認スクリプト"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def normalize_xml(content: str) -> str:
    """XMLを正規化（比較用）"""
    try:
        root = ET.fromstring(content)
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding="unicode")
    except Exception as e:
        return content


def compare_files(original_file: Path, output_file: Path) -> Dict:
    """2つのXOSCファイルを比較"""
    result = {
        "original_file": str(original_file),
        "output_file": str(output_file),
        "original_exists": original_file.exists(),
        "output_exists": output_file.exists(),
        "size_diff": None,
        "content_diff": None,
        "structure_diff": None,
        "errors": []
    }
    
    if not original_file.exists():
        result["errors"].append("元ファイルが存在しません")
        return result
    
    if not output_file.exists():
        result["errors"].append("書き出しファイルが存在しません")
        return result
    
    # ファイルサイズ比較
    original_size = original_file.stat().st_size
    output_size = output_file.stat().st_size
    result["size_diff"] = {
        "original": original_size,
        "output": output_size,
        "diff": output_size - original_size,
        "diff_percent": ((output_size - original_size) / original_size * 100) if original_size > 0 else 0
    }
    
    # 内容比較
    try:
        original_content = original_file.read_text(encoding="utf-8")
        output_content = output_file.read_text(encoding="utf-8")
        
        # XML構造比較
        try:
            original_root = ET.fromstring(original_content)
            output_root = ET.fromstring(output_content)
            
            # 主要要素の比較
            structure_diff = compare_structure(original_root, output_root)
            result["structure_diff"] = structure_diff
            
        except ET.ParseError as e:
            result["errors"].append(f"XML解析エラー: {e}")
        
        # 内容の差分（簡易版）
        if original_content != output_content:
            result["content_diff"] = {
                "identical": False,
                "original_lines": len(original_content.splitlines()),
                "output_lines": len(output_content.splitlines())
            }
        else:
            result["content_diff"] = {"identical": True}
            
    except Exception as e:
        result["errors"].append(f"ファイル読み込みエラー: {e}")
    
    return result


def compare_structure(original_root: ET.Element, output_root: ET.Element) -> Dict:
    """XML構造を比較"""
    diff = {
        "root_tag_match": original_root.tag == output_root.tag,
        "missing_elements": [],
        "extra_elements": [],
        "attribute_diffs": []
    }
    
    # 主要要素の存在確認
    key_elements = [
        "FileHeader",
        "ParameterDeclarations",
        "CatalogLocations",
        "RoadNetwork",
        "Entities",
        "Storyboard"
    ]
    
    original_children = {child.tag: child for child in original_root}
    output_children = {child.tag: child for child in output_root}
    
    for key in key_elements:
        if key in original_children and key not in output_children:
            diff["missing_elements"].append(key)
        elif key not in original_children and key in output_children:
            diff["extra_elements"].append(key)
        elif key in original_children and key in output_children:
            # 属性の比較
            orig_attrs = original_children[key].attrib
            out_attrs = output_children[key].attrib
            for attr in orig_attrs:
                if attr not in out_attrs:
                    diff["attribute_diffs"].append(f"{key}.{attr}: 元ファイルにのみ存在")
                elif orig_attrs[attr] != out_attrs[attr]:
                    diff["attribute_diffs"].append(f"{key}.{attr}: '{orig_attrs[attr]}' -> '{out_attrs[attr]}'")
            for attr in out_attrs:
                if attr not in orig_attrs:
                    diff["attribute_diffs"].append(f"{key}.{attr}: 書き出しファイルにのみ存在")
    
    return diff


def main():
    """メイン処理"""
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "thirdparty" / "esmini-demo_Windows" / "esmini-demo" / "resources" / "xosc"
    output_dir = project_root / "out" / "xosc"
    
    # 成功したファイルリスト（エラーレポートから取得）
    success_files = [
        "acc-test.xosc", "alks-test.xosc", "alks_r157_cut_in_quick_brake.xosc",
        "bicycle_fall_over.xosc", "controller_test.xosc", "cut-in.xosc",
        "cut-in_interactive.xosc", "cut-in_parameter_set.xosc", "cut-in_simple.xosc",
        "cut-in_sumo.xosc", "cut-in_visibility.xosc", "drop-bike.xosc",
        "follow_ghost.xosc", "follow_reference.xosc", "highway_merge.xosc",
        "highway_merge_advanced.xosc", "lane-change_clothoid_based_trajectory.xosc",
        "lane_change.xosc", "lane_change_crest.xosc", "lane_change_simple.xosc",
        "left-hand-traffic_by_heading.xosc", "left-hand-traffic_using_road_rule.xosc",
        "ltap-od.xosc", "pedestrian.xosc", "pedestrian_collision.xosc",
        "routing-test.xosc", "slow-lead-vehicle.xosc", "sumo-test.xosc",
        "synchronize.xosc", "synch_with_steady_state.xosc", "trailer_connect.xosc",
        "trajectory-test.xosc", "tunnels.xosc", "two_plus_one_road.xosc"
    ]
    
    print(f"\n{'='*80}")
    print(f"XOSCファイル差分確認")
    print(f"{'='*80}\n")
    print(f"比較対象: {len(success_files)}ファイル\n")
    
    results = []
    issues = []
    
    for filename in success_files:
        original_file = input_dir / filename
        output_file = output_dir / filename
        
        print(f"比較中: {filename}")
        result = compare_files(original_file, output_file)
        results.append(result)
        
        # 問題点の検出
        if result["errors"]:
            issues.append({
                "file": filename,
                "type": "error",
                "message": "; ".join(result["errors"])
            })
        elif result["size_diff"] and abs(result["size_diff"]["diff_percent"]) > 50:
            issues.append({
                "file": filename,
                "type": "size_diff",
                "message": f"ファイルサイズの差が大きい: {result['size_diff']['diff_percent']:.1f}%"
            })
        elif result["structure_diff"]:
            struct_diff = result["structure_diff"]
            if struct_diff["missing_elements"] or struct_diff["extra_elements"] or struct_diff["attribute_diffs"]:
                issues.append({
                    "file": filename,
                    "type": "structure_diff",
                    "message": f"構造の違い: 欠落={struct_diff['missing_elements']}, 追加={struct_diff['extra_elements']}, 属性={len(struct_diff['attribute_diffs'])}件"
                })
        elif result["content_diff"] and not result["content_diff"]["identical"]:
            issues.append({
                "file": filename,
                "type": "content_diff",
                "message": f"内容が異なる: 元={result['content_diff']['original_lines']}行, 出力={result['content_diff']['output_lines']}行"
            })
        else:
            print(f"  [OK] 差分なし")
    
    # 結果をファイルに保存
    report_file = output_dir / f"diff_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("XOSCファイル差分確認レポート\n")
        f.write(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"比較対象ファイル数: {len(success_files)}\n")
        f.write(f"問題検出数: {len(issues)}\n\n")
        
        if issues:
            f.write("=" * 80 + "\n")
            f.write("問題点一覧\n")
            f.write("=" * 80 + "\n\n")
            
            for i, issue in enumerate(issues, 1):
                f.write(f"[{i}] {issue['file']}\n")
                f.write(f"  タイプ: {issue['type']}\n")
                f.write(f"  内容: {issue['message']}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("詳細比較結果\n")
        f.write("=" * 80 + "\n\n")
        
        for result in results:
            f.write(f"\n{'='*80}\n")
            f.write(f"ファイル: {Path(result['original_file']).name}\n")
            f.write(f"{'='*80}\n")
            
            if result["errors"]:
                f.write(f"エラー: {', '.join(result['errors'])}\n")
            else:
                if result["size_diff"]:
                    f.write(f"ファイルサイズ:\n")
                    f.write(f"  元ファイル: {result['size_diff']['original']:,} bytes\n")
                    f.write(f"  書き出し: {result['size_diff']['output']:,} bytes\n")
                    f.write(f"  差分: {result['size_diff']['diff']:+,} bytes ({result['size_diff']['diff_percent']:+.1f}%)\n")
                
                if result["content_diff"]:
                    f.write(f"内容比較:\n")
                    if result["content_diff"]["identical"]:
                        f.write(f"  完全一致\n")
                    else:
                        f.write(f"  元ファイル: {result['content_diff']['original_lines']}行\n")
                        f.write(f"  書き出し: {result['content_diff']['output_lines']}行\n")
                
                if result["structure_diff"]:
                    f.write(f"構造比較:\n")
                    struct = result["structure_diff"]
                    f.write(f"  ルートタグ一致: {struct['root_tag_match']}\n")
                    if struct["missing_elements"]:
                        f.write(f"  欠落要素: {', '.join(struct['missing_elements'])}\n")
                    if struct["extra_elements"]:
                        f.write(f"  追加要素: {', '.join(struct['extra_elements'])}\n")
                    if struct["attribute_diffs"]:
                        f.write(f"  属性の違い ({len(struct['attribute_diffs'])}件):\n")
                        for attr_diff in struct["attribute_diffs"][:10]:  # 最初の10件のみ
                            f.write(f"    - {attr_diff}\n")
                        if len(struct["attribute_diffs"]) > 10:
                            f.write(f"    ... 他 {len(struct['attribute_diffs']) - 10}件\n")
    
    print(f"\n{'='*80}")
    print("差分確認完了")
    print(f"{'='*80}")
    print(f"問題検出数: {len(issues)}")
    print(f"レポート保存先: {report_file}")
    
    if issues:
        print("\n問題点:")
        for issue in issues:
            print(f"  - {issue['file']}: {issue['message']}")


if __name__ == "__main__":
    main()

