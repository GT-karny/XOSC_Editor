"""OpenSCENARIO 1.2 データモデル（dataclass）"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Union
from enum import Enum


# ============================================================================
# 基本型・列挙型
# ============================================================================

class DynamicsDimension(Enum):
    """Dynamicsの次元"""
    TIME = "time"
    DISTANCE = "distance"
    RATE = "rate"


class DynamicsShape(Enum):
    """Dynamicsの形状"""
    LINEAR = "linear"
    STEP = "step"
    CUBIC = "cubic"
    SINUSOIDAL = "sinusoidal"


class Rule(Enum):
    """優先度ルール"""
    OVERRIDE = "override"
    OVERWRITE = "overwrite"  # OpenSCENARIO 1.0/1.1の旧形式に対応
    PARALLEL = "parallel"
    SKIP = "skip"


# ============================================================================
# Position関連
# ============================================================================

@dataclass
class WorldPosition:
    """WorldPosition（ワールド座標）"""
    x: Union[str, float]  # パラメータ参照を含む可能性があるため
    y: Union[str, float]
    z: Union[str, float] = 0.0
    h: Union[str, float] = 0.0  # heading
    p: Union[str, float] = 0.0  # pitch
    r: Union[str, float] = 0.0  # roll


@dataclass
class LanePosition:
    """LanePosition（レーン座標）"""
    road_id: str
    lane_id: str  # XSDではString型
    s: Union[str, float] = 0.0  # パラメータ参照を含む可能性があるため
    offset: Union[str, float] = 0.0


# ============================================================================
# Dynamics関連
# ============================================================================

@dataclass
class Dynamics:
    """Dynamics（動作の動的特性）"""
    dynamics_dimension: DynamicsDimension = DynamicsDimension.TIME
    dynamics_shape: DynamicsShape = DynamicsShape.LINEAR
    value: Optional[float] = None
    constraint: Optional[str] = None  # 将来の拡張用


# ============================================================================
# Action関連
# ============================================================================

@dataclass
class TeleportAction:
    """TeleportAction（瞬間移動）"""
    position: Optional[WorldPosition] = None
    lane_position: Optional[LanePosition] = None


@dataclass
class RelativeTargetSpeed:
    """RelativeTargetSpeed（相対速度ターゲット）"""
    entity_ref: str
    value: str  # パラメータ式を含む可能性があるため文字列
    speed_target_value_type: str = "delta"  # delta, factor
    continuous: bool = True


@dataclass
class SpeedAction:
    """SpeedAction（速度制御）"""
    speed_target: Optional[float] = None  # AbsoluteTargetSpeed用（数値）
    speed_target_str: Optional[str] = None  # AbsoluteTargetSpeed用（パラメータ式）
    relative_target_speed: Optional[RelativeTargetSpeed] = None  # RelativeTargetSpeed用
    dynamics: Optional[Dynamics] = None


@dataclass
class LaneChangeAction:
    """LaneChangeAction（レーン変更）"""
    target_lane: int
    target_entity_ref: Optional[str] = None  # RelativeTargetLaneのentityRef属性
    dynamics: Optional[Dynamics] = None
    target_lane_offset: Optional[float] = None


@dataclass
class PrivateAction:
    """PrivateAction（エンティティ固有のアクション）"""
    teleport_action: Optional[TeleportAction] = None
    speed_action: Optional[SpeedAction] = None
    lane_change_action: Optional[LaneChangeAction] = None


@dataclass
class Action:
    """Action（アクション、XSDではname属性が必須）"""
    name: str
    private_action: Optional[PrivateAction] = None
    # 将来の拡張: global_action, user_defined_action


# ============================================================================
# Trigger / Condition関連
# ============================================================================

@dataclass
class SimulationTimeCondition:
    """SimulationTimeCondition（シミュレーション時間条件）"""
    value: Union[str, float]  # パラメータ参照を含む可能性があるため
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class TimeHeadwayCondition:
    """TimeHeadwayCondition（時間ヘッドウェイ条件）"""
    entity_ref: str
    value: str  # パラメータ式を含む可能性があるため文字列
    freespace: bool = False
    coordinate_system: str = "entity"  # entity, road
    relative_distance_type: str = "longitudinal"  # longitudinal, lateral
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class StoryboardElementStateCondition:
    """StoryboardElementStateCondition（ストーリーボード要素状態条件）"""
    storyboard_element_type: str  # act, action, event, maneuver, maneuverGroup, story
    storyboard_element_ref: str
    state: str  # startTransition, endTransition, stopTransition, skipTransition, completeState


@dataclass
class ByEntityCondition:
    """ByEntityCondition（エンティティによる条件）"""
    triggering_entities: List[str] = field(default_factory=list)  # Entity名のリスト
    triggering_entities_rule: str = "any"  # any, all
    entity_condition: Optional[TimeHeadwayCondition] = None


@dataclass
class Condition:
    """Condition（条件）"""
    name: str = ""
    delay: Union[str, float] = 0.0  # パラメータ参照を含む可能性があるため
    condition_edge: str = "rising"  # rising, falling, none
    simulation_time_condition: Optional[SimulationTimeCondition] = None
    by_entity_condition: Optional[ByEntityCondition] = None
    storyboard_element_state_condition: Optional[StoryboardElementStateCondition] = None


@dataclass
class ConditionGroup:
    """ConditionGroup（条件グループ、AND結合）"""
    conditions: List[Condition] = field(default_factory=list)


@dataclass
class StartTrigger:
    """StartTrigger（開始トリガー）"""
    condition_groups: List[ConditionGroup] = field(default_factory=list)


# ============================================================================
# Storyboard階層
# ============================================================================

@dataclass
class Event:
    """Event（イベント）"""
    name: str
    priority: Rule = Rule.OVERRIDE
    actions: List[Action] = field(default_factory=list)
    start_trigger: Optional[StartTrigger] = None


@dataclass
class Maneuver:
    """Maneuver（マニューバー）"""
    name: str
    events: List[Event] = field(default_factory=list)


@dataclass
class ManeuverGroup:
    """ManeuverGroup（マニューバーグループ）"""
    name: str
    maximum_execution_count: int = 1
    actors: List[str] = field(default_factory=list)  # Entity名のリスト
    select_triggering_entities: Optional[bool] = None  # ActorsのselectTriggeringEntities属性
    maneuvers: List[Maneuver] = field(default_factory=list)


@dataclass
class Act:
    """Act（アクト）"""
    name: str
    maneuver_groups: List[ManeuverGroup] = field(default_factory=list)
    start_trigger: Optional[StartTrigger] = None
    stop_trigger: Optional[StartTrigger] = None


@dataclass
class Story:
    """Story（ストーリー）"""
    name: str
    parameter_declarations: Optional[ParameterDeclarations] = None
    acts: List[Act] = field(default_factory=list)


@dataclass
class Private:
    """Private（プライベートアクション、XSDではentityRef属性が必須）"""
    entity_ref: str
    actions: List[PrivateAction] = field(default_factory=list)


@dataclass
class Init:
    """Init（初期化）"""
    actions: List[Private] = field(default_factory=list)


@dataclass
class Storyboard:
    """Storyboard（ストーリーボード）"""
    init: Optional[Init] = None
    stories: List[Story] = field(default_factory=list)
    stop_trigger: Optional[StartTrigger] = None


# ============================================================================
# Entities関連
# ============================================================================

@dataclass
class Vehicle:
    """Vehicle（車両）"""
    name: str
    vehicle_category: str = "car"  # car, van, truck, trailer, semitrailer, bus, motorbike, bicycle, train, tram
    # 将来の拡張: 物理パラメータなど


@dataclass
class CatalogReference:
    """CatalogReference（カタログ参照）"""
    catalog_name: str
    entry_name: str


@dataclass
class ScenarioObject:
    """ScenarioObject（シナリオオブジェクト）"""
    name: str
    vehicle: Optional[Vehicle] = None
    catalog_reference: Optional[CatalogReference] = None
    # 将来の拡張: pedestrian, misc_object


@dataclass
class Entities:
    """Entities（エンティティ集合）"""
    scenario_objects: List[ScenarioObject] = field(default_factory=list)


# ============================================================================
# トップレベル要素
# ============================================================================

@dataclass
class FileHeader:
    """FileHeader（ファイルヘッダー）"""
    rev_major: int = 1
    rev_minor: int = 2
    date: str = ""
    description: str = ""
    author: str = ""


@dataclass
class ParameterDeclaration:
    """ParameterDeclaration（パラメータ宣言）"""
    name: str
    parameter_type: str  # double, int, bool, string
    value: str = ""


@dataclass
class ParameterDeclarations:
    """ParameterDeclarations（パラメータ宣言集合）"""
    parameters: List[ParameterDeclaration] = field(default_factory=list)


@dataclass
class RoadNetwork:
    """RoadNetwork（道路ネットワーク）"""
    logic_file: Optional[str] = None  # OpenDRIVEファイルのパス
    scene_graph_file: Optional[str] = None


@dataclass
class CatalogLocations:
    """CatalogLocations（カタログ位置）"""
    vehicle_catalog: Optional[str] = None  # VehicleCatalogのDirectoryパス


# ============================================================================
# ルート要素
# ============================================================================

@dataclass
class ScenarioDefinition:
    """ScenarioDefinition（シナリオ定義）"""
    file_header: Optional[FileHeader] = None
    parameter_declarations: Optional[ParameterDeclarations] = None
    catalog_locations: Optional[CatalogLocations] = None
    road_network: Optional[RoadNetwork] = None
    entities: Optional[Entities] = None
    storyboard: Optional[Storyboard] = None


