# XOSC読み込み・書き出しテスト結果サマリー

## テスト概要

- **テスト日時**: 2025-11-23 12:54:24
- **テスト対象**: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/` 内の全40ファイル
- **テスト内容**: 
  1. XOSCファイルの読み込み（parse_xml）
  2. XOSCファイルの書き出し（write_xml）
  - **esmini実行はスキップ**

## テスト結果サマリー

- **総ファイル数**: 40
- **読み込み成功**: 40 (100%) ✅
- **書き出し成功**: 34 (85%) ⚠️
- **書き出しエラー**: 6 (15%)

## エラー詳細

### 1. ActにStartTriggerがない（3件）

**エラー内容**:
```
ValueError: Act 'Act_DistTest' must have a StartTrigger element
ValueError: Act 'SpeedProfileAct' must have a StartTrigger element
ValueError: Act 'act' must have a StartTrigger element
```

**影響ファイル**:
1. `distance_test.xosc` (Act: Act_DistTest)
2. `speed-profile.xosc` (Act: SpeedProfileAct)
3. `swarm.xosc` (Act: act)

**原因**:
- `write_xml.py`の`write_act`関数で、ActにStartTriggerが必須としてチェックしている
- しかし、元のXOSCファイルではStartTriggerが省略されている可能性がある
- OpenSCENARIO仕様では、ActのStartTriggerは必須ではない場合もある

**対応方針**:
- `write_act`関数のバリデーションを緩和する
- StartTriggerがNoneの場合は、デフォルトのStartTriggerを生成するか、エラーではなく警告として扱う

### 2. ManeuverGroupにActorがない（3件）

**エラー内容**:
```
ValueError: ManeuverGroup 'DummyManueverGroup' must have at least one Actor
ValueError: ManeuverGroup 'empty' must have at least one Actor
```

**影響ファイル**:
1. `parking_lot.xosc` (ManeuverGroup: DummyManueverGroup)
2. `trailers.xosc` (ManeuverGroup: empty)
3. `truck_with_rotating_axle.xosc` (ManeuverGroup: DummyManueverGroup)

**原因**:
- `write_xml.py`の`write_maneuver_group`関数で、ManeuverGroupにActorが必須としてチェックしている
- しかし、元のXOSCファイルでは空のManeuverGroupが存在している可能性がある
- これらはダミーのManeuverGroupで、実際には使用されていない可能性がある

**対応方針**:
- `write_maneuver_group`関数のバリデーションを緩和する
- Actorが空の場合は、エラーではなく警告として扱うか、スキップする

## 成功したファイル（34件）

以下のファイルは読み込み・書き出しともに成功しました：

1. acc-test.xosc
2. alks-test.xosc
3. alks_r157_cut_in_quick_brake.xosc
4. bicycle_fall_over.xosc
5. controller_test.xosc
6. cut-in.xosc
7. cut-in_interactive.xosc
8. cut-in_parameter_set.xosc
9. cut-in_simple.xosc
10. cut-in_sumo.xosc
11. cut-in_visibility.xosc
12. drop-bike.xosc
13. follow_ghost.xosc
14. follow_reference.xosc
15. highway_merge.xosc
16. highway_merge_advanced.xosc
17. lane-change_clothoid_based_trajectory.xosc
18. lane_change.xosc
19. lane_change_crest.xosc
20. lane_change_simple.xosc
21. left-hand-traffic_by_heading.xosc
22. left-hand-traffic_using_road_rule.xosc
23. ltap-od.xosc
24. pedestrian.xosc
25. pedestrian_collision.xosc
26. routing-test.xosc
27. slow-lead-vehicle.xosc
28. sumo-test.xosc
29. synchronize.xosc
30. synch_with_steady_state.xosc
31. trailer_connect.xosc
32. trajectory-test.xosc
33. tunnels.xosc
34. two_plus_one_road.xosc

## 結論

- **読み込み機能**: 100%成功 - すべてのXOSCファイルを正常に読み込めています ✅
- **書き出し機能**: 85%成功 - 6ファイルでバリデーションエラーが発生しています ⚠️

書き出しエラーは、バリデーションが厳しすぎることが原因です。元のXOSCファイルの構造を確認し、バリデーションを緩和することで解決できる見込みです。

## 推奨される対応

1. **`write_act`関数の修正**
   - StartTriggerがNoneの場合の処理を追加
   - デフォルトのStartTriggerを生成するか、警告として扱う

2. **`write_maneuver_group`関数の修正**
   - Actorが空の場合の処理を追加
   - 警告として扱うか、スキップする

3. **元のXOSCファイルの確認**
   - エラーが発生した6ファイルの元の構造を確認
   - StartTriggerやActorが本当に必要かどうかを判断

## 参考情報

- エラーレポート: `out/xosc/error_report_20251123_125424.txt`
- バッチ処理スクリプト: `scripts/batch_test_xosc.py`
- テスト対象ディレクトリ: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/`

