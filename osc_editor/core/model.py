"""OpenSCENARIO 1.2 データモデル（dataclass）"""

from dataclasses import dataclass, field
from typing import Optional, List
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
    PARALLEL = "parallel"
    SKIP = "skip"


# ============================================================================
# Position関連
# ============================================================================

@dataclass
class WorldPosition:
    """WorldPosition（ワールド座標）"""
    x: float
    y: float
    z: float = 0.0
    h: float = 0.0  # heading
    p: float = 0.0  # pitch
    r: float = 0.0  # roll


@dataclass
class LanePosition:
    """LanePosition（レーン座標）"""
    road_id: str
    lane_id: int
    s: float = 0.0
    offset: float = 0.0


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
class SpeedAction:
    """SpeedAction（速度制御）"""
    speed_target: float
    dynamics: Optional[Dynamics] = None


@dataclass
class LaneChangeAction:
    """LaneChangeAction（レーン変更）"""
    target_lane: int
    dynamics: Optional[Dynamics] = None
    target_lane_offset: Optional[float] = None


@dataclass
class PrivateAction:
    """PrivateAction（エンティティ固有のアクション）"""
    teleport_action: Optional[TeleportAction] = None
    speed_action: Optional[SpeedAction] = None
    lane_change_action: Optional[LaneChangeAction] = None


# ============================================================================
# Trigger / Condition関連
# ============================================================================

@dataclass
class SimulationTimeCondition:
    """SimulationTimeCondition（シミュレーション時間条件）"""
    value: float
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class Condition:
    """Condition（条件）"""
    name: str = ""
    delay: float = 0.0
    condition_edge: str = "rising"  # rising, falling, none
    simulation_time_condition: Optional[SimulationTimeCondition] = None


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
    actions: List[PrivateAction] = field(default_factory=list)
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
    acts: List[Act] = field(default_factory=list)


@dataclass
class Init:
    """Init（初期化）"""
    actions: List[PrivateAction] = field(default_factory=list)


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
class ScenarioObject:
    """ScenarioObject（シナリオオブジェクト）"""
    name: str
    vehicle: Optional[Vehicle] = None
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
    # MVPでは省略、将来の拡張用
    pass


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


