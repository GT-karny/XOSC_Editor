# OpenSCENARIOエディタUI対応要素まとめ

## 概要

このドキュメントは、XOSC EditorのUI上から操作可能なOpenSCENARIO要素をまとめたものです。
OpenSCENARIO.xsdで定義されている要素と、エディタでの操作状況を対応させています。

## 凡例

- ✅ 完全対応：ツリー表示・選択・プロパティ編集が可能
- ⚠️ 一部対応：ツリー表示・選択のみ可能（プロパティ編集は未対応）
- ❌ 未対応：UI上で操作不可

## サマリー

| カテゴリ | 完全対応 | 一部対応 | 未対応 | 合計 |
|---------|---------|---------|--------|------|
| トップレベル要素 | 0 | 2 | 4 | 6 |
| Entities関連 | 1 | 0 | 11 | 12 |
| Storyboard階層 | 9 | 0 | 0 | 9 |
| Action関連 | 3 | 0 | 20 | 23 |
| Position関連 | 2 | 0 | 7 | 9 |
| Condition関連 | 1 | 0 | 21 | 22 |
| Dynamics関連 | 1 | 0 | 2 | 3 |
| Trajectory関連 | 0 | 0 | 8 | 8 |
| Route関連 | 0 | 0 | 4 | 4 |
| Controller関連 | 0 | 0 | 8 | 8 |
| Environment関連 | 0 | 0 | 9 | 9 |
| Traffic関連 | 0 | 0 | 12 | 12 |
| ParameterValueDistribution関連 | 0 | 0 | 15 | 15 |
| その他 | 0 | 0 | 20 | 20 |
| **合計** | **17** | **2** | **141** | **160** |

## 1. 全要素対応状況一覧

### 1.1 トップレベル要素

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| OpenScenario | `OpenScenario` | ❌ | ルート要素、UI上では操作不可 |
| FileHeader | `FileHeader` | ❌ | ファイルヘッダー、UI上では操作不可 |
| ParameterDeclarations | `ParameterDeclarations` | ❌ | パラメータ宣言、UI上では操作不可 |
| VariableDeclarations | `VariableDeclarations` | ❌ | 変数宣言、UI上では操作不可 |
| CatalogLocations | `CatalogLocations` | ❌ | カタログ位置、UI上では操作不可 |
| RoadNetwork | `RoadNetwork` | ❌ | 道路ネットワーク、UI上では操作不可 |
| Entities | `Entities` | ⚠️ | ツリーに「エンティティ」として表示、プロパティ編集不可 |
| Storyboard | `Storyboard` | ⚠️ | ツリーに「ストーリーボード」として表示、プロパティ編集不可 |

### 1.2 Entities関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| ScenarioObject | `ScenarioObject` | ✅ | ツリー表示・選択・プロパティ編集可能（name属性） |
| Vehicle | `Vehicle` | ❌ | 車両定義、UI上では操作不可 |
| Pedestrian | `Pedestrian` | ❌ | 歩行者定義、UI上では操作不可 |
| MiscObject | `MiscObject` | ❌ | その他オブジェクト定義、UI上では操作不可 |
| CatalogReference | `CatalogReference` | ❌ | カタログ参照、UI上では操作不可 |
| ObjectController | `ObjectController` | ❌ | オブジェクトコントローラー、UI上では操作不可 |
| EntitySelection | `EntitySelection` | ❌ | エンティティ選択、UI上では操作不可 |
| SelectedEntities | `SelectedEntities` | ❌ | 選択されたエンティティ、UI上では操作不可 |
| ByType | `ByType` | ❌ | タイプによる選択、UI上では操作不可 |
| ByObjectType | `ByObjectType` | ❌ | オブジェクトタイプによる選択、UI上では操作不可 |
| EntityRef | `EntityRef` | ❌ | エンティティ参照、UI上では操作不可 |
| ExternalObjectReference | `ExternalObjectReference` | ❌ | 外部オブジェクト参照、UI上では操作不可 |

### 1.3 Storyboard階層

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Init | `Init` | ⚠️ | ツリーに「Init」として表示、プロパティ編集不可 |
| InitActions | `InitActions` | ❌ | 初期化アクション、UI上では操作不可 |
| Private | `Private` | ⚠️ | ツリーに「Private: {entityRef}」として表示、プロパティ編集不可 |
| Story | `Story` | ⚠️ | ツリーに「Story: {name}」として表示、プロパティ編集不可 |
| Act | `Act` | ⚠️ | ツリーに「Act: {name}」として表示、プロパティ編集不可 |
| ManeuverGroup | `ManeuverGroup` | ⚠️ | ツリーに「ManeuverGroup: {name}」として表示、プロパティ編集不可 |
| Maneuver | `Maneuver` | ⚠️ | ツリーに「Maneuver: {name}」として表示、プロパティ編集不可 |
| Event | `Event` | ✅ | ツリー表示・選択・プロパティ編集可能（name, priority） |
| Action | `Action` | ⚠️ | ツリーに「Action {i+1}」として表示、プロパティ編集不可 |
| PrivateAction | `PrivateAction` | ✅ | ツリー表示・選択・プロパティ編集可能（TeleportAction, SpeedAction, LaneChangeAction） |

### 1.4 Action関連（PrivateAction内）

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| TeleportAction | `TeleportAction` | ✅ | ツリー表示・選択・プロパティ編集可能（WorldPosition, LanePosition） |
| SpeedAction | `SpeedAction` | ✅ | ツリー表示・選択・プロパティ編集可能（AbsoluteTargetSpeed, RelativeTargetSpeed, Dynamics） |
| LaneChangeAction | `LaneChangeAction` | ✅ | ツリー表示・選択・プロパティ編集可能（RelativeTargetLane, Dynamics） |
| LaneOffsetAction | `LaneOffsetAction` | ❌ | レーンオフセットアクション、UI上では操作不可 |
| LongitudinalAction | `LongitudinalAction` | ❌ | 縦方向アクション、UI上では操作不可 |
| LongitudinalDistanceAction | `LongitudinalDistanceAction` | ❌ | 縦方向距離アクション、UI上では操作不可 |
| LateralAction | `LateralAction` | ❌ | 横方向アクション、UI上では操作不可 |
| LateralDistanceAction | `LateralDistanceAction` | ❌ | 横方向距離アクション、UI上では操作不可 |
| SpeedProfileAction | `SpeedProfileAction` | ❌ | 速度プロファイルアクション、UI上では操作不可 |
| RoutingAction | `RoutingAction` | ❌ | ルーティングアクション、UI上では操作不可 |
| AssignRouteAction | `AssignRouteAction` | ❌ | ルート割り当てアクション、UI上では操作不可 |
| FollowTrajectoryAction | `FollowTrajectoryAction` | ❌ | 軌跡追従アクション、UI上では操作不可 |
| AcquirePositionAction | `AcquirePositionAction` | ❌ | 位置取得アクション、UI上では操作不可 |
| ControllerAction | `ControllerAction` | ❌ | コントローラーアクション、UI上では操作不可 |
| AssignControllerAction | `AssignControllerAction` | ❌ | コントローラー割り当てアクション、UI上では操作不可 |
| ActivateControllerAction | `ActivateControllerAction` | ❌ | コントローラー有効化アクション、UI上では操作不可 |
| OverrideControllerValueAction | `OverrideControllerValueAction` | ❌ | コントローラー値上書きアクション、UI上では操作不可 |
| VisibilityAction | `VisibilityAction` | ❌ | 可視性アクション、UI上では操作不可 |
| SynchronizeAction | `SynchronizeAction` | ❌ | 同期アクション、UI上では操作不可 |
| AppearanceAction | `AppearanceAction` | ❌ | 外観アクション、UI上では操作不可 |
| GlobalAction | `GlobalAction` | ❌ | グローバルアクション、UI上では操作不可 |
| UserDefinedAction | `UserDefinedAction` | ❌ | ユーザー定義アクション、UI上では操作不可 |

### 1.5 Position関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Position | `Position` | ❌ | 位置要素（choice）、UI上では操作不可 |
| WorldPosition | `WorldPosition` | ✅ | ワールド座標、TeleportAction内で編集可能 |
| LanePosition | `LanePosition` | ✅ | レーン座標、TeleportAction内で編集可能 |
| RoadPosition | `RoadPosition` | ❌ | 道路座標、UI上では操作不可 |
| RoutePosition | `RoutePosition` | ❌ | ルート座標、UI上では操作不可 |
| RelativeWorldPosition | `RelativeWorldPosition` | ❌ | 相対ワールド座標、UI上では操作不可 |
| RelativeLanePosition | `RelativeLanePosition` | ❌ | 相対レーン座標、UI上では操作不可 |
| RelativeRoadPosition | `RelativeRoadPosition` | ❌ | 相対道路座標、UI上では操作不可 |
| RelativeObjectPosition | `RelativeObjectPosition` | ❌ | 相対オブジェクト座標、UI上では操作不可 |
| GeoPosition | `GeoPosition` | ❌ | 地理座標、UI上では操作不可 |
| TrajectoryPosition | `TrajectoryPosition` | ❌ | 軌跡座標、UI上では操作不可 |
| Orientation | `Orientation` | ❌ | 方向、UI上では操作不可 |
| InRoutePosition | `InRoutePosition` | ❌ | ルート内位置、UI上では操作不可 |
| PositionInLaneCoordinates | `PositionInLaneCoordinates` | ❌ | レーン座標内位置、UI上では操作不可 |
| PositionInRoadCoordinates | `PositionInRoadCoordinates` | ❌ | 道路座標内位置、UI上では操作不可 |
| PositionOfCurrentEntity | `PositionOfCurrentEntity` | ❌ | 現在エンティティ位置、UI上では操作不可 |

### 1.6 Condition関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Trigger | `Trigger` | ❌ | トリガー、UI上では操作不可 |
| StartTrigger | `StartTrigger` | ⚠️ | 開始トリガー、ツリー表示可能、SimulationTimeConditionのみ編集可能 |
| ConditionGroup | `ConditionGroup` | ❌ | 条件グループ、UI上では操作不可 |
| Condition | `Condition` | ❌ | 条件、UI上では操作不可 |
| ByValueCondition | `ByValueCondition` | ❌ | 値による条件、UI上では操作不可 |
| SimulationTimeCondition | `SimulationTimeCondition` | ✅ | シミュレーション時間条件、StartTrigger内で編集可能 |
| ParameterCondition | `ParameterCondition` | ❌ | パラメータ条件、UI上では操作不可 |
| TimeOfDayCondition | `TimeOfDayCondition` | ❌ | 時刻条件、UI上では操作不可 |
| StoryboardElementStateCondition | `StoryboardElementStateCondition` | ❌ | ストーリーボード要素状態条件、UI上では操作不可 |
| UserDefinedValueCondition | `UserDefinedValueCondition` | ❌ | ユーザー定義値条件、UI上では操作不可 |
| TrafficSignalCondition | `TrafficSignalCondition` | ❌ | 交通信号条件、UI上では操作不可 |
| TrafficSignalControllerCondition | `TrafficSignalControllerCondition` | ❌ | 交通信号制御器条件、UI上では操作不可 |
| VariableCondition | `VariableCondition` | ❌ | 変数条件、UI上では操作不可 |
| ByEntityCondition | `ByEntityCondition` | ❌ | エンティティによる条件、UI上では操作不可 |
| EntityCondition | `EntityCondition` | ❌ | エンティティ条件、UI上では操作不可 |
| EndOfRoadCondition | `EndOfRoadCondition` | ❌ | 道路終端条件、UI上では操作不可 |
| CollisionCondition | `CollisionCondition` | ❌ | 衝突条件、UI上では操作不可 |
| OffroadCondition | `OffroadCondition` | ❌ | オフロード条件、UI上では操作不可 |
| TimeHeadwayCondition | `TimeHeadwayCondition` | ❌ | 時間ヘッドウェイ条件、UI上では操作不可 |
| TimeToCollisionCondition | `TimeToCollisionCondition` | ❌ | 衝突までの時間条件、UI上では操作不可 |
| AccelerationCondition | `AccelerationCondition` | ❌ | 加速度条件、UI上では操作不可 |
| StandStillCondition | `StandStillCondition` | ❌ | 停止条件、UI上では操作不可 |
| SpeedCondition | `SpeedCondition` | ❌ | 速度条件、UI上では操作不可 |
| RelativeSpeedCondition | `RelativeSpeedCondition` | ❌ | 相対速度条件、UI上では操作不可 |
| TraveledDistanceCondition | `TraveledDistanceCondition` | ❌ | 走行距離条件、UI上では操作不可 |
| ReachPositionCondition | `ReachPositionCondition` | ❌ | 位置到達条件、UI上では操作不可 |
| DistanceCondition | `DistanceCondition` | ❌ | 距離条件、UI上では操作不可 |
| RelativeDistanceCondition | `RelativeDistanceCondition` | ❌ | 相対距離条件、UI上では操作不可 |
| RelativeClearanceCondition | `RelativeClearanceCondition` | ❌ | 相対クリアランス条件、UI上では操作不可 |
| TriggeringEntities | `TriggeringEntities` | ❌ | トリガーエンティティ、UI上では操作不可 |
| Actors | `Actors` | ❌ | アクター、UI上では操作不可 |

### 1.7 Dynamics関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| TransitionDynamics | `TransitionDynamics` | ✅ | 遷移動力学、SpeedAction/LaneChangeAction内で編集可能 |
| LaneOffsetActionDynamics | `LaneOffsetActionDynamics` | ❌ | レーンオフセット動作の動的特性、UI上では操作不可 |
| DynamicConstraints | `DynamicConstraints` | ❌ | 動的制約、UI上では操作不可 |

### 1.8 Speed/Target関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| SpeedActionTarget | `SpeedActionTarget` | ❌ | 速度アクションターゲット、UI上では操作不可 |
| AbsoluteTargetSpeed | `AbsoluteTargetSpeed` | ✅ | 絶対速度ターゲット、SpeedAction内で編集可能 |
| RelativeTargetSpeed | `RelativeTargetSpeed` | ✅ | 相対速度ターゲット、SpeedAction内で編集可能 |
| AbsoluteSpeed | `AbsoluteSpeed` | ❌ | 絶対速度、UI上では操作不可 |
| RelativeSpeedToMaster | `RelativeSpeedToMaster` | ❌ | マスターへの相対速度、UI上では操作不可 |
| LaneChangeTarget | `LaneChangeTarget` | ❌ | レーン変更ターゲット、UI上では操作不可 |
| AbsoluteTargetLane | `AbsoluteTargetLane` | ❌ | 絶対レーンターゲット、UI上では操作不可 |
| RelativeTargetLane | `RelativeTargetLane` | ✅ | 相対レーンターゲット、LaneChangeAction内で編集可能 |
| LaneOffsetTarget | `LaneOffsetTarget` | ❌ | レーンオフセットターゲット、UI上では操作不可 |
| AbsoluteTargetLaneOffset | `AbsoluteTargetLaneOffset` | ❌ | 絶対レーンオフセットターゲット、UI上では操作不可 |
| RelativeTargetLaneOffset | `RelativeTargetLaneOffset` | ❌ | 相対レーンオフセットターゲット、UI上では操作不可 |
| FinalSpeed | `FinalSpeed` | ❌ | 最終速度、UI上では操作不可 |
| SteadyState | `SteadyState` | ❌ | 定常状態、UI上では操作不可 |
| TargetDistanceSteadyState | `TargetDistanceSteadyState` | ❌ | 目標距離定常状態、UI上では操作不可 |
| TargetTimeSteadyState | `TargetTimeSteadyState` | ❌ | 目標時間定常状態、UI上では操作不可 |

### 1.9 Trajectory関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Trajectory | `Trajectory` | ❌ | 軌跡、UI上では操作不可 |
| TrajectoryRef | `TrajectoryRef` | ❌ | 軌跡参照、UI上では操作不可 |
| Shape | `Shape` | ❌ | 形状、UI上では操作不可 |
| Polyline | `Polyline` | ❌ | ポリライン、UI上では操作不可 |
| Clothoid | `Clothoid` | ❌ | クロソイド曲線、UI上では操作不可 |
| Nurbs | `Nurbs` | ❌ | NURBS曲線、UI上では操作不可 |
| Vertex | `Vertex` | ❌ | 頂点、UI上では操作不可 |
| ControlPoint | `ControlPoint` | ❌ | 制御点、UI上では操作不可 |
| Knot | `Knot` | ❌ | ノット、UI上では操作不可 |
| TrajectoryFollowingMode | `TrajectoryFollowingMode` | ❌ | 軌跡追従モード、UI上では操作不可 |
| TimeReference | `TimeReference` | ❌ | 時間参照、UI上では操作不可 |
| Timing | `Timing` | ❌ | タイミング、UI上では操作不可 |
| None | `None` | ❌ | なし、UI上では操作不可 |

### 1.10 Route関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Route | `Route` | ❌ | ルート、UI上では操作不可 |
| RouteRef | `RouteRef` | ❌ | ルート参照、UI上では操作不可 |
| Waypoint | `Waypoint` | ❌ | ウェイポイント、UI上では操作不可 |

### 1.11 Controller関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Controller | `Controller` | ❌ | コントローラー、UI上では操作不可 |
| OverrideThrottleAction | `OverrideThrottleAction` | ❌ | スロットル上書きアクション、UI上では操作不可 |
| OverrideBrakeAction | `OverrideBrakeAction` | ❌ | ブレーキ上書きアクション、UI上では操作不可 |
| OverrideClutchAction | `OverrideClutchAction` | ❌ | クラッチ上書きアクション、UI上では操作不可 |
| OverrideParkingBrakeAction | `OverrideParkingBrakeAction` | ❌ | パーキングブレーキ上書きアクション、UI上では操作不可 |
| OverrideSteeringWheelAction | `OverrideSteeringWheelAction` | ❌ | ステアリングホイール上書きアクション、UI上では操作不可 |
| OverrideGearAction | `OverrideGearAction` | ❌ | ギア上書きアクション、UI上では操作不可 |
| Brake | `Brake` | ❌ | ブレーキ、UI上では操作不可 |
| BrakeInput | `BrakeInput` | ❌ | ブレーキ入力、UI上では操作不可 |
| ManualGear | `ManualGear` | ❌ | マニュアルギア、UI上では操作不可 |
| AutomaticGear | `AutomaticGear` | ❌ | オートマチックギア、UI上では操作不可 |
| Gear | `Gear` | ❌ | ギア、UI上では操作不可 |

### 1.12 Visibility/Appearance関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| SensorReferenceSet | `SensorReferenceSet` | ❌ | センサー参照セット、UI上では操作不可 |
| SensorReference | `SensorReference` | ❌ | センサー参照、UI上では操作不可 |
| LightStateAction | `LightStateAction` | ❌ | ライト状態アクション、UI上では操作不可 |
| AnimationAction | `AnimationAction` | ❌ | アニメーションアクション、UI上では操作不可 |
| LightType | `LightType` | ❌ | ライトタイプ、UI上では操作不可 |
| VehicleLight | `VehicleLight` | ❌ | 車両ライト、UI上では操作不可 |
| UserDefinedLight | `UserDefinedLight` | ❌ | ユーザー定義ライト、UI上では操作不可 |
| LightState | `LightState` | ❌ | ライト状態、UI上では操作不可 |
| Color | `Color` | ❌ | 色、UI上では操作不可 |
| ColorRgb | `ColorRgb` | ❌ | RGB色、UI上では操作不可 |
| ColorCmyk | `ColorCmyk` | ❌ | CMYK色、UI上では操作不可 |
| AnimationType | `AnimationType` | ❌ | アニメーションタイプ、UI上では操作不可 |
| ComponentAnimation | `ComponentAnimation` | ❌ | コンポーネントアニメーション、UI上では操作不可 |
| PedestrianAnimation | `PedestrianAnimation` | ❌ | 歩行者アニメーション、UI上では操作不可 |
| AnimationFile | `AnimationFile` | ❌ | アニメーションファイル、UI上では操作不可 |
| UserDefinedAnimation | `UserDefinedAnimation` | ❌ | ユーザー定義アニメーション、UI上では操作不可 |
| VehicleComponent | `VehicleComponent` | ❌ | 車両コンポーネント、UI上では操作不可 |
| UserDefinedComponent | `UserDefinedComponent` | ❌ | ユーザー定義コンポーネント、UI上では操作不可 |
| PedestrianGesture | `PedestrianGesture` | ❌ | 歩行者ジェスチャー、UI上では操作不可 |
| AnimationState | `AnimationState` | ❌ | アニメーション状態、UI上では操作不可 |

### 1.13 Environment関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| EnvironmentAction | `EnvironmentAction` | ❌ | 環境アクション、UI上では操作不可 |
| Environment | `Environment` | ❌ | 環境、UI上では操作不可 |
| TimeOfDay | `TimeOfDay` | ❌ | 時刻、UI上では操作不可 |
| Weather | `Weather` | ❌ | 天候、UI上では操作不可 |
| Sun | `Sun` | ❌ | 太陽、UI上では操作不可 |
| Fog | `Fog` | ❌ | 霧、UI上では操作不可 |
| Precipitation | `Precipitation` | ❌ | 降水、UI上では操作不可 |
| Wind | `Wind` | ❌ | 風、UI上では操作不可 |
| DomeImage | `DomeImage` | ❌ | ドーム画像、UI上では操作不可 |
| RoadCondition | `RoadCondition` | ❌ | 道路条件、UI上では操作不可 |
| Wetness | `Wetness` | ❌ | 湿り度、UI上では操作不可 |

### 1.14 EntityAction関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| EntityAction | `EntityAction` | ❌ | エンティティアクション、UI上では操作不可 |
| AddEntityAction | `AddEntityAction` | ❌ | エンティティ追加アクション、UI上では操作不可 |
| DeleteEntityAction | `DeleteEntityAction` | ❌ | エンティティ削除アクション、UI上では操作不可 |

### 1.15 Parameter/Variable関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| ParameterAction | `ParameterAction` | ❌ | パラメータアクション、UI上では操作不可 |
| ParameterSetAction | `ParameterSetAction` | ❌ | パラメータ設定アクション、UI上では操作不可 |
| ParameterModifyAction | `ParameterModifyAction` | ❌ | パラメータ変更アクション、UI上では操作不可 |
| ModifyRule | `ModifyRule` | ❌ | 変更ルール、UI上では操作不可 |
| ParameterAddValueRule | `ParameterAddValueRule` | ❌ | パラメータ加算値ルール、UI上では操作不可 |
| ParameterMultiplyByValueRule | `ParameterMultiplyByValueRule` | ❌ | パラメータ乗算値ルール、UI上では操作不可 |
| ParameterDeclaration | `ParameterDeclaration` | ❌ | パラメータ宣言、UI上では操作不可 |
| ParameterAssignment | `ParameterAssignment` | ❌ | パラメータ割り当て、UI上では操作不可 |
| ParameterAssignments | `ParameterAssignments` | ❌ | パラメータ割り当てリスト、UI上では操作不可 |
| VariableAction | `VariableAction` | ❌ | 変数アクション、UI上では操作不可 |
| VariableSetAction | `VariableSetAction` | ❌ | 変数設定アクション、UI上では操作不可 |
| VariableModifyAction | `VariableModifyAction` | ❌ | 変数変更アクション、UI上では操作不可 |
| VariableModifyRule | `VariableModifyRule` | ❌ | 変数変更ルール、UI上では操作不可 |
| VariableAddValueRule | `VariableAddValueRule` | ❌ | 変数加算値ルール、UI上では操作不可 |
| VariableMultiplyByValueRule | `VariableMultiplyByValueRule` | ❌ | 変数乗算値ルール、UI上では操作不可 |
| VariableDeclaration | `VariableDeclaration` | ❌ | 変数宣言、UI上では操作不可 |

### 1.16 Traffic関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| TrafficAction | `TrafficAction` | ❌ | 交通アクション、UI上では操作不可 |
| TrafficSourceAction | `TrafficSourceAction` | ❌ | 交通ソースアクション、UI上では操作不可 |
| TrafficSinkAction | `TrafficSinkAction` | ❌ | 交通シンクアクション、UI上では操作不可 |
| TrafficSwarmAction | `TrafficSwarmAction` | ❌ | 交通群アクション、UI上では操作不可 |
| TrafficStopAction | `TrafficStopAction` | ❌ | 交通停止アクション、UI上では操作不可 |
| TrafficDefinition | `TrafficDefinition` | ❌ | 交通定義、UI上では操作不可 |
| VehicleCategoryDistribution | `VehicleCategoryDistribution` | ❌ | 車両カテゴリ分布、UI上では操作不可 |
| VehicleCategoryDistributionEntry | `VehicleCategoryDistributionEntry` | ❌ | 車両カテゴリ分布エントリ、UI上では操作不可 |
| VehicleRoleDistribution | `VehicleRoleDistribution` | ❌ | 車両役割分布、UI上では操作不可 |
| VehicleRoleDistributionEntry | `VehicleRoleDistributionEntry` | ❌ | 車両役割分布エントリ、UI上では操作不可 |
| ControllerDistribution | `ControllerDistribution` | ❌ | コントローラー分布、UI上では操作不可 |
| ControllerDistributionEntry | `ControllerDistributionEntry` | ❌ | コントローラー分布エントリ、UI上では操作不可 |
| DirectionOfTravelDistribution | `DirectionOfTravelDistribution` | ❌ | 走行方向分布、UI上では操作不可 |
| CentralSwarmObject | `CentralSwarmObject` | ❌ | 中央群オブジェクト、UI上では操作不可 |

### 1.17 Infrastructure関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| InfrastructureAction | `InfrastructureAction` | ❌ | インフラアクション、UI上では操作不可 |
| TrafficSignalAction | `TrafficSignalAction` | ❌ | 交通信号アクション、UI上では操作不可 |
| TrafficSignalControllerAction | `TrafficSignalControllerAction` | ❌ | 交通信号制御器アクション、UI上では操作不可 |
| TrafficSignalStateAction | `TrafficSignalStateAction` | ❌ | 交通信号状態アクション、UI上では操作不可 |
| TrafficSignals | `TrafficSignals` | ❌ | 交通信号、UI上では操作不可 |
| TrafficSignalController | `TrafficSignalController` | ❌ | 交通信号制御器、UI上では操作不可 |
| Phase | `Phase` | ❌ | フェーズ、UI上では操作不可 |
| TrafficSignalState | `TrafficSignalState` | ❌ | 交通信号状態、UI上では操作不可 |
| TrafficSignalGroupState | `TrafficSignalGroupState` | ❌ | 交通信号グループ状態、UI上では操作不可 |

### 1.18 Vehicle/Pedestrian/MiscObject関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| BoundingBox | `BoundingBox` | ❌ | 境界ボックス、UI上では操作不可 |
| Center | `Center` | ❌ | 中心点、UI上では操作不可 |
| Dimensions | `Dimensions` | ❌ | 寸法、UI上では操作不可 |
| Performance | `Performance` | ❌ | 性能、UI上では操作不可 |
| Axles | `Axles` | ❌ | 車軸集合、UI上では操作不可 |
| Axle | `Axle` | ❌ | 車軸、UI上では操作不可 |
| Properties | `Properties` | ❌ | プロパティ集合、UI上では操作不可 |
| Property | `Property` | ❌ | プロパティ、UI上では操作不可 |
| File | `File` | ❌ | ファイル、UI上では操作不可 |
| CustomContent | `CustomContent` | ❌ | カスタムコンテンツ、UI上では操作不可 |

### 1.19 Catalog関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| Catalog | `Catalog` | ❌ | カタログ、UI上では操作不可 |
| CatalogDefinition | `CatalogDefinition` | ❌ | カタログ定義、UI上では操作不可 |
| VehicleCatalogLocation | `VehicleCatalogLocation` | ❌ | 車両カタログ位置、UI上では操作不可 |
| ControllerCatalogLocation | `ControllerCatalogLocation` | ❌ | コントローラーカタログ位置、UI上では操作不可 |
| PedestrianCatalogLocation | `PedestrianCatalogLocation` | ❌ | 歩行者カタログ位置、UI上では操作不可 |
| MiscObjectCatalogLocation | `MiscObjectCatalogLocation` | ❌ | その他オブジェクトカタログ位置、UI上では操作不可 |
| EnvironmentCatalogLocation | `EnvironmentCatalogLocation` | ❌ | 環境カタログ位置、UI上では操作不可 |
| ManeuverCatalogLocation | `ManeuverCatalogLocation` | ❌ | マニューバーカタログ位置、UI上では操作不可 |
| TrajectoryCatalogLocation | `TrajectoryCatalogLocation` | ❌ | 軌跡カタログ位置、UI上では操作不可 |
| RouteCatalogLocation | `RouteCatalogLocation` | ❌ | ルートカタログ位置、UI上では操作不可 |
| Directory | `Directory` | ❌ | ディレクトリ、UI上では操作不可 |

### 1.20 ParameterValueDistribution関連

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| ParameterValueDistribution | `ParameterValueDistribution` | ❌ | パラメータ値分布、UI上では操作不可 |
| ParameterValueDistributionDefinition | `ParameterValueDistributionDefinition` | ❌ | パラメータ値分布定義、UI上では操作不可 |
| ScenarioFile | `ScenarioFile` | ❌ | シナリオファイル、UI上では操作不可 |
| DistributionDefinition | `DistributionDefinition` | ❌ | 分布定義、UI上では操作不可 |
| Deterministic | `Deterministic` | ❌ | 決定論的分布、UI上では操作不可 |
| Stochastic | `Stochastic` | ❌ | 確率的分布、UI上では操作不可 |
| DeterministicSingleParameterDistribution | `DeterministicSingleParameterDistribution` | ❌ | 決定論的単一パラメータ分布、UI上では操作不可 |
| DeterministicMultiParameterDistribution | `DeterministicMultiParameterDistribution` | ❌ | 決定論的多パラメータ分布、UI上では操作不可 |
| DistributionSet | `DistributionSet` | ❌ | 分布セット、UI上では操作不可 |
| DistributionSetElement | `DistributionSetElement` | ❌ | 分布セット要素、UI上では操作不可 |
| DistributionRange | `DistributionRange` | ❌ | 分布範囲、UI上では操作不可 |
| Range | `Range` | ❌ | 範囲、UI上では操作不可 |
| ValueSetDistribution | `ValueSetDistribution` | ❌ | 値セット分布、UI上では操作不可 |
| ParameterValueSet | `ParameterValueSet` | ❌ | パラメータ値セット、UI上では操作不可 |
| StochasticDistribution | `StochasticDistribution` | ❌ | 確率分布、UI上では操作不可 |
| ProbabilityDistributionSet | `ProbabilityDistributionSet` | ❌ | 確率分布セット、UI上では操作不可 |
| ProbabilityDistributionSetElement | `ProbabilityDistributionSetElement` | ❌ | 確率分布セット要素、UI上では操作不可 |
| NormalDistribution | `NormalDistribution` | ❌ | 正規分布、UI上では操作不可 |
| UniformDistribution | `UniformDistribution` | ❌ | 一様分布、UI上では操作不可 |
| PoissonDistribution | `PoissonDistribution` | ❌ | ポアソン分布、UI上では操作不可 |
| Histogram | `Histogram` | ❌ | ヒストグラム、UI上では操作不可 |
| HistogramBin | `HistogramBin` | ❌ | ヒストグラムビン、UI上では操作不可 |
| UserDefinedDistribution | `UserDefinedDistribution` | ❌ | ユーザー定義分布、UI上では操作不可 |
| ValueConstraintGroup | `ValueConstraintGroup` | ❌ | 値制約グループ、UI上では操作不可 |
| ValueConstraint | `ValueConstraint` | ❌ | 値制約、UI上では操作不可 |

### 1.21 その他

| 要素名 | XSD要素 | 対応状況 | 備考 |
|--------|---------|---------|------|
| License | `License` | ❌ | ライセンス、UI上では操作不可 |
| UsedArea | `UsedArea` | ❌ | 使用領域、UI上では操作不可 |
| CustomCommandAction | `CustomCommandAction` | ❌ | カスタムコマンドアクション、UI上では操作不可 |
| RelativeLaneRange | `RelativeLaneRange` | ❌ | 相対レーン範囲、UI上では操作不可 |
| TimeToCollisionConditionTarget | `TimeToCollisionConditionTarget` | ❌ | 衝突までの時間条件ターゲット、UI上では操作不可 |
| SpeedProfileEntry | `SpeedProfileEntry` | ❌ | 速度プロファイルエントリ、UI上では操作不可 |

## 2. プロパティ編集可能な要素の詳細

以下は、プロパティパネルで編集可能な要素の詳細です。

### 2.1 ScenarioObject

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| name | `ScenarioObject/@name` (String, required) | ✅ | QLineEditで編集可能 |

### 2.2 PrivateAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| TeleportAction | `PrivateAction/TeleportAction` | ✅ | フォームで編集可能 |
| SpeedAction | `PrivateAction/SpeedAction` | ✅ | フォームで編集可能 |
| LaneChangeAction | `PrivateAction/LaneChangeAction` | ✅ | フォームで編集可能 |

### 2.3 TeleportAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| Position/WorldPosition | `TeleportAction/Position/WorldPosition` | ✅ | x, y, z, h (heading) を編集可能 |
| Position/LanePosition | `TeleportAction/Position/LanePosition` | ✅ | roadId, laneId, s, offset を編集可能 |

**WorldPositionの編集可能属性:**

- x (Double, required) - QDoubleSpinBoxで編集（範囲: -10000 ～ 10000）
- y (Double, required) - QDoubleSpinBoxで編集（範囲: -10000 ～ 10000）
- z (Double) - QDoubleSpinBoxで編集（範囲: -100 ～ 100）
- h (Double) - QDoubleSpinBoxで編集（heading、範囲: -360 ～ 360）

**LanePositionの編集可能属性:**

- roadId (String, required) - QLineEditで編集
- laneId (String, required) - QLineEditで編集
- s (Double, required) - QDoubleSpinBoxで編集（範囲: 0 ～ 100000）
- offset (Double) - QDoubleSpinBoxで編集（範囲: -10 ～ 10）

### 2.4 SpeedAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| SpeedActionTarget/AbsoluteTargetSpeed | `SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed` | ✅ | 数値またはパラメータ式で編集可能 |
| SpeedActionTarget/RelativeTargetSpeed | `SpeedAction/SpeedActionTarget/RelativeTargetSpeed` | ✅ | フォームで編集可能 |
| SpeedActionDynamics | `SpeedAction/SpeedActionDynamics` (TransitionDynamics) | ✅ | フォームで編集可能 |

**AbsoluteTargetSpeedの編集可能属性:**

- value (Double, required) - QDoubleSpinBoxまたはQLineEdit（パラメータ式）で編集
  - 数値入力: QDoubleSpinBox（範囲: 0 ～ 200 m/s）
  - パラメータ式入力: QLineEdit（例: `${$EgoSpeed / 3.6}`）

**RelativeTargetSpeedの編集可能属性:**

- entityRef (String, required) - QLineEditで編集
- value (String, required) - QLineEditで編集（パラメータ式対応、例: `$TargetSpeedFactor`）
- speedTargetValueType (SpeedTargetValueType, required) - QComboBoxで選択（delta, factor）
- continuous (Boolean, required) - QCheckBoxで編集

**TransitionDynamics (SpeedActionDynamics)の編集可能属性:**

- dynamicsDimension (DynamicsDimension, required) - QComboBoxで選択（time, distance, rate）
- dynamicsShape (DynamicsShape, required) - QComboBoxで選択（linear, step, cubic, sinusoidal）
- value (Double) - QDoubleSpinBoxで編集（範囲: 0 ～ 1000）

### 2.5 LaneChangeAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| LaneChangeTarget/RelativeTargetLane | `LaneChangeAction/LaneChangeTarget/RelativeTargetLane` | ✅ | target_lane (Int) を編集可能 |
| LaneChangeActionDynamics | `LaneChangeAction/LaneChangeActionDynamics` (TransitionDynamics) | ✅ | フォームで編集可能 |

**RelativeTargetLaneの編集可能属性:**

- value (Int, required) - QSpinBoxで編集（範囲: -10 ～ 10）

**TransitionDynamics (LaneChangeActionDynamics)の編集可能属性:**

- dynamicsDimension (DynamicsDimension, required) - QComboBoxで選択（time, distance, rate）
- dynamicsShape (DynamicsShape, required) - QComboBoxで選択（linear, step, cubic, sinusoidal）
- value (Double) - QDoubleSpinBoxで編集（範囲: 0 ～ 1000）

### 2.6 Event

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| name | `Event/@name` (String, required) | ✅ | QLineEditで編集可能 |
| priority | `Event/@priority` (Priority, required) | ✅ | QComboBoxで選択（override, overwrite, parallel, skip） |

### 2.7 StartTrigger

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| ConditionGroup/Condition/SimulationTimeCondition | `StartTrigger/ConditionGroup/Condition/ByValueCondition/SimulationTimeCondition` | ✅ | フォームで編集可能 |

**SimulationTimeConditionの編集可能属性:**

- value (Double, required) - QDoubleSpinBoxで編集（範囲: 0 ～ 10000 s）
- rule (Rule, required) - QComboBoxで選択（greaterThan, lessThan, equalTo）

## 3. 完全対応要素の詳細説明

### 3.1 ScenarioObject

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| name | `ScenarioObject/@name` (String, required) | ✅ | QLineEditで編集可能 |

### 3.2 PrivateAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| TeleportAction | `PrivateAction/TeleportAction` | ✅ | フォームで編集可能 |
| SpeedAction | `PrivateAction/SpeedAction` | ✅ | フォームで編集可能 |
| LaneChangeAction | `PrivateAction/LaneChangeAction` | ✅ | フォームで編集可能 |

### 3.3 TeleportAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| Position/WorldPosition | `TeleportAction/Position/WorldPosition` | ✅ | x, y, z, h (heading) を編集可能 |
| Position/LanePosition | `TeleportAction/Position/LanePosition` | ✅ | roadId, laneId, s, offset を編集可能 |

**WorldPositionの編集可能属性:**

- x (Double, required) - QDoubleSpinBoxで編集（範囲: -10000 ～ 10000）
- y (Double, required) - QDoubleSpinBoxで編集（範囲: -10000 ～ 10000）
- z (Double) - QDoubleSpinBoxで編集（範囲: -100 ～ 100）
- h (Double) - QDoubleSpinBoxで編集（heading、範囲: -360 ～ 360）

**LanePositionの編集可能属性:**

- roadId (String, required) - QLineEditで編集
- laneId (String, required) - QLineEditで編集
- s (Double, required) - QDoubleSpinBoxで編集（範囲: 0 ～ 100000）
- offset (Double) - QDoubleSpinBoxで編集（範囲: -10 ～ 10）

### 3.4 SpeedAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| SpeedActionTarget/AbsoluteTargetSpeed | `SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed` | ✅ | 数値またはパラメータ式で編集可能 |
| SpeedActionTarget/RelativeTargetSpeed | `SpeedAction/SpeedActionTarget/RelativeTargetSpeed` | ✅ | フォームで編集可能 |
| SpeedActionDynamics | `SpeedAction/SpeedActionDynamics` (TransitionDynamics) | ✅ | フォームで編集可能 |

**AbsoluteTargetSpeedの編集可能属性:**

- value (Double, required) - QDoubleSpinBoxまたはQLineEdit（パラメータ式）で編集
  - 数値入力: QDoubleSpinBox（範囲: 0 ～ 200 m/s）
  - パラメータ式入力: QLineEdit（例: `${$EgoSpeed / 3.6}`）

**RelativeTargetSpeedの編集可能属性:**

- entityRef (String, required) - QLineEditで編集
- value (String, required) - QLineEditで編集（パラメータ式対応、例: `$TargetSpeedFactor`）
- speedTargetValueType (SpeedTargetValueType, required) - QComboBoxで選択（delta, factor）
- continuous (Boolean, required) - QCheckBoxで編集

**TransitionDynamics (SpeedActionDynamics)の編集可能属性:**

- dynamicsDimension (DynamicsDimension, required) - QComboBoxで選択（time, distance, rate）
- dynamicsShape (DynamicsShape, required) - QComboBoxで選択（linear, step, cubic, sinusoidal）
- value (Double) - QDoubleSpinBoxで編集（範囲: 0 ～ 1000）

### 3.5 LaneChangeAction

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| LaneChangeTarget/RelativeTargetLane | `LaneChangeAction/LaneChangeTarget/RelativeTargetLane` | ✅ | target_lane (Int) を編集可能 |
| LaneChangeActionDynamics | `LaneChangeAction/LaneChangeActionDynamics` (TransitionDynamics) | ✅ | フォームで編集可能 |

**RelativeTargetLaneの編集可能属性:**

- value (Int, required) - QSpinBoxで編集（範囲: -10 ～ 10）

**TransitionDynamics (LaneChangeActionDynamics)の編集可能属性:**

- dynamicsDimension (DynamicsDimension, required) - QComboBoxで選択（time, distance, rate）
- dynamicsShape (DynamicsShape, required) - QComboBoxで選択（linear, step, cubic, sinusoidal）
- value (Double) - QDoubleSpinBoxで編集（範囲: 0 ～ 1000）

### 3.6 Event

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| name | `Event/@name` (String, required) | ✅ | QLineEditで編集可能 |
| priority | `Event/@priority` (Priority, required) | ✅ | QComboBoxで選択（override, overwrite, parallel, skip） |

### 3.7 StartTrigger

| 属性/要素 | XSD定義 | 対応状況 | 備考 |
|----------|---------|---------|------|
| ConditionGroup/Condition/SimulationTimeCondition | `StartTrigger/ConditionGroup/Condition/ByValueCondition/SimulationTimeCondition` | ✅ | フォームで編集可能 |

**SimulationTimeConditionの編集可能属性:**

- value (Double, required) - QDoubleSpinBoxで編集（範囲: 0 ～ 10000 s）
- rule (Rule, required) - QComboBoxで選択（greaterThan, lessThan, equalTo）

## 4. 一部対応要素（ツリー表示のみ、プロパティ編集不可）

以下の要素はツリーに表示されますが、プロパティパネルでの編集は未対応です：

- Entities（親要素）
- Storyboard（親要素）
- Init（親要素）
- Private（親要素）
- Story（親要素）
- Act（親要素）
- ManeuverGroup（親要素）
- Maneuver（親要素）
- Action（親要素、PrivateAction以外のアクション）
- StartTrigger（SimulationTimeCondition以外の条件は未対応）

## 5. 実装ファイル

- ツリー表示: `osc_editor/ui/scenario_tree.py`
- プロパティ編集: `osc_editor/ui/properties_panel.py`
- データモデル: `osc_editor/core/model.py`

## 6. 今後の拡張予定

現在、以下の機能は未実装です：

- 要素の追加・削除
- 要素の並び替え
- その他のPrivateAction（RoutingAction, ControllerAction, VisibilityAction, SynchronizeAction, AppearanceAction等）
- その他のCondition（ByEntityCondition, ParameterCondition, TimeOfDayCondition等）
- その他のPositionタイプ（RoutePosition, RelativeWorldPosition, RelativeLanePosition等）
- Vehicle, Pedestrian, MiscObjectの詳細編集
- Trajectory関連要素の編集
- Route関連要素の編集
- Environment関連要素の編集
- Traffic関連要素の編集

