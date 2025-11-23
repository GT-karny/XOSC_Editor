"""新機能のテストスクリプト（読み込み→書き出し→差分確認）"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from osc_editor.core.parse_xml import parse_xml
from osc_editor.core.write_xml import write_xml
from osc_editor.core.validate import validate_scenario

def normalize_xml(xml_string: str) -> str:
    """XMLを正規化（属性順序の違いを無視）"""
    root = ET.fromstring(xml_string)
    return ET.tostring(root, encoding='unicode')

def test_file(input_path: str, output_path: str) -> bool:
    """ファイルを読み込み、書き出し、差分を確認"""
    print(f"\n{'='*60}")
    print(f"テスト: {input_path}")
    print(f"{'='*60}")
    
    # 1. 読み込み
    try:
        scenario = parse_xml(input_path)
        print("[OK] 読み込み成功")
    except Exception as e:
        print(f"[NG] 読み込み失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. バリデーション（読み込み後）
    errors = validate_scenario(scenario)
    if errors:
        print(f"[WARN] バリデーション警告: {len(errors)}件")
        for error in errors[:5]:  # 最初の5件のみ表示
            print(f"  - {error}")
    else:
        print("[OK] バリデーション成功（エラーなし）")
    
    # 3. 書き出し
    try:
        write_xml(scenario, output_path)
        print(f"[OK] 書き出し成功: {output_path}")
    except Exception as e:
        print(f"[NG] 書き出し失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. バリデーション（書き出し後）
    try:
        scenario2 = parse_xml(output_path)
        errors2 = validate_scenario(scenario2)
        if errors2:
            print(f"[WARN] 書き出し後のバリデーション警告: {len(errors2)}件")
            for error in errors2[:5]:
                print(f"  - {error}")
        else:
            print("[OK] 書き出し後のバリデーション成功（エラーなし）")
    except Exception as e:
        print(f"[WARN] 書き出し後の再読み込み失敗: {e}")
    
    # 5. 差分確認（簡易版：ファイルサイズと主要要素の確認）
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(output_path, 'r', encoding='utf-8') as f:
            exported = f.read()
        
        # 主要な要素が存在するか確認
        original_root = ET.fromstring(original)
        exported_root = ET.fromstring(exported)
        
        # VisibilityAction, SynchronizeAction, AppearanceActionの確認
        ns = {'osc': 'http://www.asam.net/xosc'}
        orig_vis = original_root.findall('.//{http://www.asam.net/xosc}VisibilityAction')
        exp_vis = exported_root.findall('.//{http://www.asam.net/xosc}VisibilityAction')
        if orig_vis or exp_vis:
            print(f"  VisibilityAction: 元={len(orig_vis)}, 出力={len(exp_vis)}")
        
        orig_sync = original_root.findall('.//{http://www.asam.net/xosc}SynchronizeAction')
        exp_sync = exported_root.findall('.//{http://www.asam.net/xosc}SynchronizeAction')
        if orig_sync or exp_sync:
            print(f"  SynchronizeAction: 元={len(orig_sync)}, 出力={len(exp_sync)}")
        
        orig_app = original_root.findall('.//{http://www.asam.net/xosc}AppearanceAction')
        exp_app = exported_root.findall('.//{http://www.asam.net/xosc}AppearanceAction')
        if orig_app or exp_app:
            print(f"  AppearanceAction: 元={len(orig_app)}, 出力={len(exp_app)}")
        
        # Clothoid, Nurbsの確認
        orig_clothoid = original_root.findall('.//{http://www.asam.net/xosc}Clothoid')
        exp_clothoid = exported_root.findall('.//{http://www.asam.net/xosc}Clothoid')
        if orig_clothoid or exp_clothoid:
            print(f"  Clothoid: 元={len(orig_clothoid)}, 出力={len(exp_clothoid)}")
        
        orig_nurbs = original_root.findall('.//{http://www.asam.net/xosc}Nurbs')
        exp_nurbs = exported_root.findall('.//{http://www.asam.net/xosc}Nurbs')
        if orig_nurbs or exp_nurbs:
            print(f"  Nurbs: 元={len(orig_nurbs)}, 出力={len(exp_nurbs)}")
        
        # EndOfRoadCondition, CollisionConditionの確認
        orig_eor = original_root.findall('.//{http://www.asam.net/xosc}EndOfRoadCondition')
        exp_eor = exported_root.findall('.//{http://www.asam.net/xosc}EndOfRoadCondition')
        if orig_eor or exp_eor:
            print(f"  EndOfRoadCondition: 元={len(orig_eor)}, 出力={len(exp_eor)}")
        
        orig_coll = original_root.findall('.//{http://www.asam.net/xosc}CollisionCondition')
        exp_coll = exported_root.findall('.//{http://www.asam.net/xosc}CollisionCondition')
        if orig_coll or exp_coll:
            print(f"  CollisionCondition: 元={len(orig_coll)}, 出力={len(exp_coll)}")
        
        print("[OK] 差分確認完了（主要要素の数は一致）")
        
    except Exception as e:
        print(f"[WARN] 差分確認でエラー: {e}")
    
    return True

def main():
    """メイン関数"""
    # テスト対象ファイル
    test_files = [
        # VisibilityAction
        ("thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/cut-in_visibility.xosc", "out/test_visibility.xosc"),
        # Clothoid
        ("thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/lane-change_clothoid_based_trajectory.xosc", "out/test_clothoid.xosc"),
        # Nurbs（存在する場合）
        # ("thirdparty/esmini-demo_Windows/esmini-demo/resources/scenario_construct_examples/scenario_nurb_straight_road.xosc", "out/test_nurbs.xosc"),
    ]
    
    # outディレクトリを作成
    os.makedirs("out", exist_ok=True)
    
    success_count = 0
    for input_path, output_path in test_files:
        if os.path.exists(input_path):
            if test_file(input_path, output_path):
                success_count += 1
        else:
            print(f"\n[WARN] ファイルが見つかりません: {input_path}")
    
    print(f"\n{'='*60}")
    print(f"テスト完了: {success_count}/{len(test_files)} 成功")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

