"""実装された要素が正しく書き出されているか確認するスクリプト"""

import xml.etree.ElementTree as ET
import os

def check_elements_in_file(file_path: str):
    """ファイル内に特定の要素が存在するか確認"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return {}
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 名前空間を検出
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag[:root.tag.index("}") + 1]
    
    results = {
        'file': os.path.basename(file_path),
        'elements': {}
    }
    
    # チェックする要素
    elements_to_check = {
        'FollowTrajectoryAction': f".//{ns}FollowTrajectoryAction",
        'Trajectory': f".//{ns}Trajectory",
        'Polyline': f".//{ns}Polyline",
        'Vertex': f".//{ns}Vertex",
        'RoutePosition': f".//{ns}RoutePosition",
        'AssignRouteAction': f".//{ns}AssignRouteAction",
        'TraveledDistanceCondition': f".//{ns}TraveledDistanceCondition",
        'TimeToCollisionCondition': f".//{ns}TimeToCollisionCondition",
        'ReachPositionCondition': f".//{ns}ReachPositionCondition",
        'ActivateControllerAction': f".//{ns}ActivateControllerAction",
        'ObjectController': f".//{ns}ObjectController",
        'Controller': f".//{ns}Controller",
        'Properties': f".//{ns}Properties",
        'Pedestrian': f".//{ns}Pedestrian",
        'LaneOffsetAction': f".//{ns}LaneOffsetAction",
        'AbsoluteTargetLane': f".//{ns}AbsoluteTargetLane",
        'OffroadCondition': f".//{ns}OffroadCondition",
        'ParameterCondition': f".//{ns}ParameterCondition",
        'GlobalAction': f".//{ns}GlobalAction",
        'ParameterAction': f".//{ns}ParameterAction",
    }
    
    for elem_name, xpath in elements_to_check.items():
        found = root.findall(xpath)
        results['elements'][elem_name] = len(found) > 0
    
    return results

def main():
    """メイン関数"""
    output_files = [
        "out/cut-in.xosc",
        "out/lane_change.xosc",
        "out/pedestrian.xosc",
        "out/bicycle_fall_over.xosc",
        "out/acc-test.xosc",
    ]
    
    print("実装要素の確認結果")
    print("=" * 60)
    
    for file_path in output_files:
        if not os.path.exists(file_path):
            continue
        
        results = check_elements_in_file(file_path)
        print(f"\n{results['file']}:")
        for elem_name, found in results['elements'].items():
            status = "[OK]" if found else "[ ]"
            print(f"  {status} {elem_name}")

if __name__ == "__main__":
    main()

