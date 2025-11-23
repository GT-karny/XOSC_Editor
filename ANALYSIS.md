# xoscファイルの差分分析結果

## 概要
5つのxoscファイルの読み込み・書き出し・差分確認を実施した結果、以下の問題が見つかりました。

## 発見された問題

### 1. フォーマットの問題
- **問題**: XMLが1行にまとまって書き出されている（改行・インデントがない）
- **影響**: 機能的には問題ないが、可読性が低く、元ファイルとの差分が大きい
- **優先度**: 低（後で対応可能）

### 2. 未実装要素による情報損失

#### `lane_change.xosc`
以下の要素が未実装で、パース・書き出しされていない：

1. **LaneOffsetAction** (行649-667)
   - `EgoGoOffRoadEvent`のActionが空になる
   - パーサー・ライター未実装

2. **AbsoluteTargetLane** (行709)
   - `EgoGoOnRoadEvent`で使用
   - 現在はRelativeTargetLaneのみサポート

3. **OffroadCondition** (行737)
   - `EgoGoOnRoadCondition`が空になる
   - パーサー・ライター未実装

4. **ParameterCondition** (行799)
   - `Lane change Target condition`が空になり、バリデーションエラー
   - パーサー・ライター未実装

5. **ParameterAction (GlobalAction)** (行815-822)
   - `Dummy parameter event`のActionが空になる
   - GlobalAction未実装

#### `pedestrian.xosc`
以下の要素が未実装で、パース・書き出しされていない：

1. **Pedestrian** (行972)
   - `pedestrian_adult`が空のScenarioObjectになる
   - パーサー・ライター未実装

2. **RouteCatalog** (行940-943)
   - CatalogLocationsに未実装
   - 現在はVehicleCatalogのみサポート

3. **RoutePosition** (行1026-1040)
   - TeleportActionで使用
   - 現在はWorldPosition/LanePositionのみサポート

4. **AssignRouteAction** (行1010-1014)
   - RoutingActionとして使用
   - パーサー・ライター未実装

5. **FollowTrajectoryAction** (行1148-1256)
   - `walk_route`のActionが空になる
   - Trajectory, Polyline, Vertex等も未実装

6. **TraveledDistanceCondition** (行1280)
   - `ped_walk_event`のConditionが空になる
   - パーサー・ライター未実装

7. **TimeToCollisionCondition** (行1350-1366)
   - `brake_Condition`が空になる
   - パーサー・ライター未実装

8. **ReachPositionCondition** (行1422-1429)
   - `QuitCondition`が空になる
   - パーサー・ライター未実装

#### `bicycle_fall_over.xosc`
以下の要素が未実装で、パース・書き出しされていない：

1. **FollowTrajectoryAction** (行1526-1620)
   - Init内のRoutingActionが失われる
   - Storyがなくなるため、バリデーションエラー

#### `acc-test.xosc`
以下の要素が未実装で、パース・書き出しされていない：

1. **ControllerCatalog** (行1725-1729)
   - CatalogLocationsに未実装

2. **ObjectController** (行1747-1763)
   - ScenarioObject内のControllerが失われる

3. **ActivateControllerAction** (行1824, 1848)
   - Init内のPrivateActionが失われる
   - パーサー・ライター未実装

### 3. バリデーションエラー

1. **lane_change.xosc**
   - `Lane change Target condition`が空のConditionになり、バリデーションエラー

2. **bicycle_fall_over.xosc**
   - Storyが書き出されないため、「At least one Story is required」エラー

## 修正の優先順位

### 優先度: 高
1. **LaneOffsetAction** - lane_change.xoscで必須
2. **AbsoluteTargetLane** - lane_change.xoscで必須
3. **OffroadCondition** - lane_change.xoscで必須
4. **ParameterCondition** - lane_change.xoscでバリデーションエラー
5. **FollowTrajectoryAction** - pedestrian.xosc, bicycle_fall_over.xoscで必須

### 優先度: 中
6. **Pedestrian** - pedestrian.xoscで必須
7. **RoutePosition** - pedestrian.xoscで必須
8. **AssignRouteAction** - pedestrian.xoscで必須
9. **TraveledDistanceCondition** - pedestrian.xoscで必須
10. **TimeToCollisionCondition** - pedestrian.xoscで必須
11. **ReachPositionCondition** - pedestrian.xoscで必須

### 優先度: 低
12. **ParameterAction (GlobalAction)** - lane_change.xoscで使用
13. **ObjectController** - acc-test.xoscで使用
14. **ActivateControllerAction** - acc-test.xoscで使用
15. **ControllerCatalog** - acc-test.xoscで使用
16. **RouteCatalog** - pedestrian.xoscで使用

## 次のステップ

1. モデル定義の追加 (`osc_editor/core/model.py`)
2. パーサーの追加 (`osc_editor/core/parse_xml.py`)
3. ライターの追加 (`osc_editor/core/write_xml.py`)
4. バリデーションルールの追加 (`osc_editor/core/validate.py`)

