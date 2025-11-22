# ASAM OpenSCENARIO 1.2 構造まとめ（完全版・教育用）

本書は ASAM OpenSCENARIO 1.2 の User Guide および Modeling Guidelines に基づき、  
シナリオ構造を体系的・厳密に整理した教育用ドキュメントである。  
初めて学ぶ読者が混乱しないよう、必要な概念を一貫した表現でまとめる。

---

# 1. ファイル構造とルート要素

OpenSCENARIO のシナリオファイル（`.xosc`）は次のルート要素を持つ。

```xml
<OpenSCENARIO>
    <FileHeader .../>
    <ParameterDeclarations>...</ParameterDeclarations>
    <VariableDeclarations>...</VariableDeclarations>     <!-- 1.2 で追加 -->
    <CatalogLocations>...</CatalogLocations>
    <RoadNetwork>...</RoadNetwork>
    <Entities>...</Entities>
    <Storyboard>...</Storyboard>
</OpenSCENARIO>
```

OpenSCENARIO 1.2 では以下の 3 種の用途別ファイルを作成できる：

- シナリオ（.xosc）
- カタログ（車両・歩行者・コントローラ等）
- パラメータ分布設定ファイル

ただし、いずれも `<OpenSCENARIO>` をルートに持つ点は共通である。

---

# 2. 各トップレベル要素の役割

## 2.1 FileHeader
ファイルの作成者、バージョン、タイムスタンプなどのメタ情報。

## 2.2 ParameterDeclarations
`${speed}` など、型付きのパラメータを宣言する。

## 2.3 VariableDeclarations（1.2）
条件式や計算に利用される変数を定義する。  
後述の VariableAction と組み合わせて実行中に値を書き換えられる。

## 2.4 CatalogLocations
VehicleCatalog など外部カタログファイルへのパスを指定する。

## 2.5 RoadNetwork
OpenDRIVE などの論理道路ネットワークを参照する。  
道路形状やレーン構造は外部ファイルで管理し、OpenSCENARIO から読み込む。

## 2.6 Entities
シナリオ内で登場する動的／静的エンティティを定義する。

要素：
- **ScenarioObject**  
  - Vehicle / Pedestrian / MiscObject を内包する。
- **EntitySelection**  
  - エンティティ集合（手動・ランダム選択）の表現。

## 2.7 Storyboard
シナリオ中の「行動の流れ」を管理する中心的構造。  
Init から始まり、Story → Act → ManeuverGroup → Maneuver → Event → Action の階層を形成する。

---

# 3. Storyboard 階層構造

```
Storyboard
├─ Init
│   └─ Action*
├─ Story*
│  └─ Act*
│     ├─ ManeuverGroup*
│     │  ├─ Actors
│     │  └─ Maneuver*
│     │     └─ Event*
│     │        ├─ Action*
│     │        └─ StartTrigger
│     ├─ StartTrigger
│     └─ StopTrigger?
└─ StopTrigger
```

## 3.1 Init
シミュレーション開始時に 1 回だけ実行される初期設定。  
例：Teleport（瞬間移動）、Controller の割り当てなど。

## 3.2 Story
1 つまたは複数の Act を束ねる物語単位。

## 3.3 Act
開始・終了が Trigger で定義されるフェーズ単位。

## 3.4 ManeuverGroup
指定された Actors（ScenarioObject または EntitySelection）に対して  
どの Maneuver を適用するかを定義する。

`maximumExecutionCount` によりループ実行が可能。

## 3.5 Maneuver
1 つ以上の Event を持つ行動のまとまり。  
カタログ化して再利用できる。

## 3.6 Event
StartTrigger により開始され、1 つ以上の Action を実行する。

Event は Maneuver 内で次の優先度制御を持つ：

- **override**：開始すると他 Event を停止する  
- **parallel**：他 Event と併行実行  
- **skip**：実行されない  

Event のランタイムインスタンスは常に 1 つであり、  
同じ Event が同時に複数実行されることはない。

---

# 4. Action の分類（1.2 正式構造）

OpenSCENARIO 1.2 の Action は 3 分類：

```
Action
 ├─ GlobalAction
 ├─ UserDefinedAction
 └─ PrivateAction
```

## 4.1 GlobalAction  
環境・道路条件・信号など、システム全体に作用するアクション。

例：
- EnvironmentAction（天候・時刻）
- TrafficSignalAction
- InfrastructureAction

## 4.2 UserDefinedAction  
標準にない動作を独自に拡張するためのアクション。

## 4.3 PrivateAction  
特定エンティティに作用する。下位分類は以下。

```
PrivateAction
 ├─ LongitudinalAction
 │    ├─ SpeedAction
 │    └─ LongitudinalDistanceAction
 ├─ LateralAction
 │    ├─ LaneChangeAction
 │    ├─ LaneOffsetAction
 │    └─ LateralDistanceAction
 ├─ VisibilityAction
 ├─ SynchronizeAction
 ├─ ControllerAction
 │    ├─ AssignControllerAction
 │    └─ ActivateControllerAction
 ├─ TeleportAction
 ├─ RoutingAction
 └─ AppearanceAction
```

---

# 5. 追加アクションカテゴリ（1.2 仕様）

## 5.1 VariableAction
VariableDeclarations で定義した変数を操作する。
- VariableSetAction
- VariableModifyAction

## 5.2 TrafficAction
交通流を生成・制御する。
- TrafficSourceAction
- TrafficSwarmAction

---

# 6. Trigger と Condition

Trigger は Condition の論理的集合で構成される。

```
Trigger
 ├─ ConditionGroup+
      └─ Condition+
```

## 主な Condition 種類

- SimulationTimeCondition  
- TimeHeadwayCondition  
- TimeToCollisionCondition  
- SpeedCondition / RelativeSpeedCondition  
- DistanceCondition / RelativeDistanceCondition  
- AccelerationCondition  
- StandStillCondition  
- CollisionCondition  
- OffroadCondition  
- TraveledDistanceCondition  
- StoryboardElementStateCondition  
- ParameterCondition  
- VariableCondition（1.2）  
- ByValueCondition（1.2）

---

# 7. Position（位置指定モデル）

OpenSCENARIO の Positioning は多体系をサポートする。

- **WorldPosition**  
  地球楕円体の接平面を基準とした XYZ。
- **GeographicPosition**  
  緯度・経度。
- **RoadPosition**  
  OpenDRIVE の s, t。
- **LanePosition**  
  laneId, s, offset。
- **RelativeWorldPosition**
- **RelativeLanePosition**
- **RelativeRoadPosition**
- **RelativeObjectPosition**
- **TrajectoryPosition**
- **RoutePosition**

### 距離の定義
- 非負実数  
- ワールド座標／局所座標の両方で定義  
- エンティティのバウンディングボックスに基づく測定ルールを持つ

---

# 8. Parameters / Variables / Evaluation

## Parameters
- `${param}` として参照  
- 階層スコープ（Storyboard → Act → Maneuver）によりシャドウイング

## Variables（1.2）
- VariableAction により動的変更が可能  

## Evaluation
- Condition の評価サイクルに従い実行時に更新される。

---

# 9. Catalog の分類

- VehicleCatalog  
- PedestrianCatalog  
- MiscObjectCatalog  
- ControllerCatalog  
- ManeuverCatalog  
- TrajectoryCatalog  
- EnvironmentCatalog

Catalog はパラメトリックに再利用可能である。

---

# 10. 全体構造まとめ図

```
OpenSCENARIO
├─ FileHeader
├─ ParameterDeclarations
├─ VariableDeclarations
├─ CatalogLocations
├─ RoadNetwork
├─ Entities
│   ├─ ScenarioObject*
│   └─ EntitySelection*
└─ Storyboard
    ├─ Init
    │   └─ Action*
    ├─ Story*
    │   └─ Act*
    │       ├─ ManeuverGroup*
    │       │   ├─ Actors
    │       │   └─ Maneuver*
    │       │       └─ Event*
    │       │           ├─ Action*
    │       │           └─ StartTrigger
    │       ├─ StartTrigger
    │       └─ StopTrigger?
    └─ StopTrigger
```

---

# 11. エディタ構築の参考モデル

- 左ペイン：OpenSCENARIO の階層構造ツリー  
- 中央：Storyboard（各階層のノード／タイムライン）  
- 右ペイン：選択ノードの属性（Action / Trigger / Position / Dynamics 等）

Action と Trigger/Condition の階層構造をそのまま UI に投影すると、  
仕様との整合性が取りやすい。

