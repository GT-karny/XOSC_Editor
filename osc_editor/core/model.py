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
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


@dataclass
class RoutePosition:
    """RoutePosition（ルート座標）"""
    route_ref: Optional[CatalogReference] = None  # RouteRef内のCatalogReference
    route: Optional[Route] = None  # RouteRef内のRoute要素
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）
    in_route_position: Optional[dict] = None  # InRoutePosition（FromLaneCoordinates等）


@dataclass
class RelativeWorldPosition:
    """RelativeWorldPosition（相対ワールド座標）"""
    entity_ref: str
    dx: Union[str, float]
    dy: Union[str, float]
    dz: Union[str, float] = 0.0
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


@dataclass
class RelativeLanePosition:
    """RelativeLanePosition（相対レーン座標）"""
    entity_ref: str
    d_lane: Union[str, int]  # dLane属性（Int型）
    ds: Optional[Union[str, float]] = None
    offset: Optional[Union[str, float]] = None
    ds_lane: Optional[Union[str, float]] = None
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


@dataclass
class RelativeRoadPosition:
    """RelativeRoadPosition（相対道路座標）"""
    entity_ref: str
    ds: Union[str, float]
    dt: Union[str, float]
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


@dataclass
class RelativeObjectPosition:
    """RelativeObjectPosition（相対オブジェクト座標）"""
    entity_ref: str
    dx: Union[str, float]
    dy: Union[str, float]
    dz: Optional[Union[str, float]] = None
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


@dataclass
class RoadPosition:
    """RoadPosition（道路座標）"""
    road_id: str
    s: Union[str, float]
    t: Union[str, float]
    orientation: Optional[dict] = None  # Orientation要素（type, h, p, r）


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
class Waypoint:
    """Waypoint（ウェイポイント）"""
    position: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition, 
                    RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    route_strategy: str  # fastest, leastIntersections, random, shortest


@dataclass
class Route:
    """Route（ルート）"""
    name: str
    closed: bool
    waypoints: List[Waypoint] = field(default_factory=list)
    parameter_declarations: Optional[ParameterDeclarations] = None


@dataclass
class AssignRouteAction:
    """AssignRouteAction（ルート割り当て）"""
    route_ref: Optional[CatalogReference] = None  # CatalogReference
    route: Optional[Route] = None  # Route要素


@dataclass
class TeleportAction:
    """TeleportAction（瞬間移動）"""
    position: Optional[WorldPosition] = None
    lane_position: Optional[LanePosition] = None
    route_position: Optional[RoutePosition] = None
    relative_world_position: Optional[RelativeWorldPosition] = None
    relative_lane_position: Optional[RelativeLanePosition] = None
    relative_road_position: Optional[RelativeRoadPosition] = None
    relative_object_position: Optional[RelativeObjectPosition] = None
    road_position: Optional[RoadPosition] = None


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
    target_lane: Optional[int] = None  # RelativeTargetLaneまたはAbsoluteTargetLaneのvalue
    target_entity_ref: Optional[str] = None  # RelativeTargetLaneのentityRef属性
    target_lane_absolute: Optional[int] = None  # AbsoluteTargetLaneのvalue（entityRefなしの場合）
    dynamics: Optional[Dynamics] = None
    target_lane_offset: Optional[float] = None


@dataclass
class LaneOffsetActionDynamics:
    """LaneOffsetActionDynamics（レーンオフセット動作の動的特性）"""
    dynamics_shape: DynamicsShape = DynamicsShape.LINEAR
    max_lateral_acc: Optional[float] = None  # maxLateralAcc属性


@dataclass
class LaneOffsetAction:
    """LaneOffsetAction（レーンオフセット）"""
    target_offset: Union[str, float]  # AbsoluteTargetLaneOffsetのvalue
    dynamics: Optional[LaneOffsetActionDynamics] = None
    continuous: bool = True  # continuous属性


@dataclass
class Vertex:
    """Vertex（頂点）"""
    position: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                    RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    time: Optional[Union[str, float]] = None  # time属性（オプション）


@dataclass
class ControlPoint:
    """ControlPoint（制御点、Nurbs用）"""
    position: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                    RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    time: Optional[Union[str, float]] = None  # time属性（オプション）
    weight: Optional[Union[str, float]] = None  # weight属性（オプション）


@dataclass
class Polyline:
    """Polyline（ポリライン）"""
    vertices: List[Vertex] = field(default_factory=list)


@dataclass
class Clothoid:
    """Clothoid（クロソイド曲線）"""
    curvature: Union[str, float]  # required
    length: Union[str, float]  # required
    position: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                   RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    curvature_prime: Optional[Union[str, float]] = None  # optional
    start_time: Optional[Union[str, float]] = None  # optional
    stop_time: Optional[Union[str, float]] = None  # optional


@dataclass
class Nurbs:
    """Nurbs（NURBS曲線）"""
    order: int  # required, UnsignedInt
    control_points: List[ControlPoint] = field(default_factory=list)  # 2以上 required
    knots: List[dict] = field(default_factory=list)  # 2以上 required, value属性を持つ


@dataclass
class Trajectory:
    """Trajectory（軌跡）"""
    name: str
    closed: bool = False
    shape: Optional[Union[Polyline, Clothoid, Nurbs]] = None  # Shape内のPolyline, Clothoid, Nurbs（choice）
    parameter_declarations: Optional[ParameterDeclarations] = None


@dataclass
class TimeReference:
    """TimeReference（時間参照）"""
    timing: Optional[dict] = None  # Timing要素（domainAbsoluteRelative, offset, scale）またはNone


@dataclass
class TrajectoryRef:
    """TrajectoryRef（軌跡参照）"""
    trajectory: Optional[Trajectory] = None
    catalog_reference: Optional[CatalogReference] = None


@dataclass
class FollowTrajectoryAction:
    """FollowTrajectoryAction（軌跡追従アクション）"""
    trajectory: Optional[Trajectory] = None  # deprecatedだが互換性のため残す
    trajectory_ref: Optional[TrajectoryRef] = None
    time_reference: Optional[TimeReference] = None
    following_mode: str = "follow"  # TrajectoryFollowingModeのfollowingMode属性
    initial_distance_offset: Optional[Union[str, float]] = None


@dataclass
class RoutingAction:
    """RoutingAction（ルーティングアクション）"""
    assign_route_action: Optional[AssignRouteAction] = None
    follow_trajectory_action: Optional[FollowTrajectoryAction] = None


@dataclass
class ActivateControllerAction:
    """ActivateControllerAction（コントローラー有効化アクション）"""
    longitudinal: bool = True
    lateral: bool = True


@dataclass
class VisibilityAction:
    """VisibilityAction（可視性アクション）"""
    graphics: Union[str, bool]  # Boolean型, required
    sensors: Union[str, bool]  # Boolean型, required
    traffic: Union[str, bool]  # Boolean型, required
    sensor_reference_set: Optional[dict] = None  # SensorReferenceSet要素（将来の拡張用）


@dataclass
class SynchronizeAction:
    """SynchronizeAction（同期アクション）"""
    master_entity_ref: str  # required
    target_position_master: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                                   RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    target_position: Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                           RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]
    target_tolerance_master: Optional[Union[str, float]] = None  # optional
    target_tolerance: Optional[Union[str, float]] = None  # optional
    final_speed: Optional[dict] = None  # FinalSpeed要素（AbsoluteSpeedまたはRelativeSpeedToMaster）


@dataclass
class AppearanceAction:
    """AppearanceAction（外観アクション）"""
    light_state_action: Optional[dict] = None  # LightStateAction要素（optional）
    animation_action: Optional[dict] = None  # AnimationAction要素（optional）


@dataclass
class PrivateAction:
    """PrivateAction（エンティティ固有のアクション）"""
    teleport_action: Optional[TeleportAction] = None
    speed_action: Optional[SpeedAction] = None
    lane_change_action: Optional[LaneChangeAction] = None
    lane_offset_action: Optional[LaneOffsetAction] = None
    routing_action: Optional[RoutingAction] = None
    activate_controller_action: Optional[ActivateControllerAction] = None
    visibility_action: Optional[VisibilityAction] = None
    synchronize_action: Optional[SynchronizeAction] = None
    appearance_action: Optional[AppearanceAction] = None


@dataclass
class ParameterAction:
    """ParameterAction（パラメータアクション）"""
    parameter_ref: str
    set_action_value: Union[str, float]  # SetActionのvalue


@dataclass
class GlobalAction:
    """GlobalAction（グローバルアクション）"""
    parameter_action: Optional[ParameterAction] = None


@dataclass
class Action:
    """Action（アクション、XSDではname属性が必須）"""
    name: str
    private_action: Optional[PrivateAction] = None
    global_action: Optional[GlobalAction] = None
    # 将来の拡張: user_defined_action


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
class OffroadCondition:
    """OffroadCondition（オフロード条件）"""
    duration: Union[str, float]  # パラメータ参照を含む可能性があるため


@dataclass
class TraveledDistanceCondition:
    """TraveledDistanceCondition（走行距離条件）"""
    value: Union[str, float]  # パラメータ参照を含む可能性があるため


@dataclass
class TimeToCollisionCondition:
    """TimeToCollisionCondition（衝突までの時間条件）"""
    value: Union[str, float]
    freespace: bool = True
    coordinate_system: str = "entity"
    relative_distance_type: str = "longitudinal"
    rule: str = "lessThan"
    target_entity_ref: Optional[str] = None  # TimeToCollisionConditionTarget内のEntityRef


@dataclass
class ReachPositionCondition:
    """ReachPositionCondition（位置到達条件）"""
    tolerance: Union[str, float] = 0.0
    position: Optional[Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                             RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]] = None


@dataclass
class EndOfRoadCondition:
    """EndOfRoadCondition（道路終端条件）"""
    duration: Union[str, float]  # required


@dataclass
class CollisionCondition:
    """CollisionCondition（衝突条件）"""
    entity_ref: Optional[str] = None  # EntityRef要素（choice）
    by_object_type: Optional[dict] = None  # ByType要素（ByObjectTypeのtype属性）


@dataclass
class ParameterCondition:
    """ParameterCondition（パラメータ条件）"""
    parameter_ref: str
    value: Union[str, float]  # パラメータ参照を含む可能性があるため
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class StoryboardElementStateCondition:
    """StoryboardElementStateCondition（ストーリーボード要素状態条件）"""
    storyboard_element_type: str  # act, action, event, maneuver, maneuverGroup, story
    storyboard_element_ref: str
    state: str  # startTransition, endTransition, stopTransition, skipTransition, completeState


@dataclass
class TimeOfDayCondition:
    """TimeOfDayCondition（時刻条件）"""
    date_time: Union[str, float]  # DateTime型、パラメータ参照を含む可能性があるため
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class UserDefinedValueCondition:
    """UserDefinedValueCondition（ユーザー定義値条件）"""
    name: str
    value: str  # String型（required）
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class TrafficSignalCondition:
    """TrafficSignalCondition（交通信号条件）"""
    name: str
    state: str


@dataclass
class TrafficSignalControllerCondition:
    """TrafficSignalControllerCondition（交通信号制御器条件）"""
    traffic_signal_controller_ref: str
    phase: str


@dataclass
class VariableCondition:
    """VariableCondition（変数条件）"""
    variable_ref: str
    value: str  # String型（required）
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo


@dataclass
class AccelerationCondition:
    """AccelerationCondition（加速度条件）"""
    value: Union[str, float]  # パラメータ参照を含む可能性があるため（required）
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo
    direction: Optional[str] = None  # longitudinal, lateral, vertical


@dataclass
class StandStillCondition:
    """StandStillCondition（停止条件）"""
    duration: Union[str, float]  # パラメータ参照を含む可能性があるため


@dataclass
class SpeedCondition:
    """SpeedCondition（速度条件）"""
    value: Union[str, float]  # パラメータ参照を含む可能性があるため（required）
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo
    direction: Optional[str] = None  # longitudinal, lateral, vertical


@dataclass
class RelativeSpeedCondition:
    """RelativeSpeedCondition（相対速度条件）"""
    entity_ref: str
    value: Union[str, float]  # パラメータ参照を含む可能性があるため（required）
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo
    direction: Optional[str] = None  # longitudinal, lateral, vertical


@dataclass
class RelativeLaneRange:
    """RelativeLaneRange（相対レーン範囲）"""
    from_lane: Optional[Union[str, int]] = None  # Int型、パラメータ参照を含む可能性があるため
    to_lane: Optional[Union[str, int]] = None  # Int型、パラメータ参照を含む可能性があるため


@dataclass
class DistanceCondition:
    """DistanceCondition（距離条件）"""
    value: Union[str, float]  # パラメータ参照を含む可能性があるため（required）
    position: Optional[Union[WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition,
                             RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition]] = None
    freespace: bool = True
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo
    coordinate_system: Optional[str] = None  # entity, lane, road, trajectory
    relative_distance_type: Optional[str] = None  # longitudinal, lateral, cartesianDistance, euclidianDistance
    routing_algorithm: Optional[str] = None  # assignedRoute, fastest, leastIntersections, shortest, undefined
    along_route: Optional[bool] = None  # deprecated


@dataclass
class RelativeDistanceCondition:
    """RelativeDistanceCondition（相対距離条件）"""
    entity_ref: str
    value: Union[str, float]  # パラメータ参照を含む可能性があるため（required）
    freespace: bool = True
    relative_distance_type: str = "longitudinal"  # longitudinal, lateral, cartesianDistance, euclidianDistance
    rule: str = "greaterThan"  # greaterThan, lessThan, equalTo
    coordinate_system: Optional[str] = None  # entity, lane, road, trajectory
    routing_algorithm: Optional[str] = None  # assignedRoute, fastest, leastIntersections, shortest, undefined


@dataclass
class RelativeClearanceCondition:
    """RelativeClearanceCondition（相対クリアランス条件）"""
    relative_lane_ranges: List[RelativeLaneRange] = field(default_factory=list)
    entity_refs: List[str] = field(default_factory=list)
    opposite_lanes: bool = False
    distance_forward: Optional[Union[str, float]] = None
    distance_backward: Optional[Union[str, float]] = None
    free_space: bool = True


@dataclass
class ByEntityCondition:
    """ByEntityCondition（エンティティによる条件）"""
    triggering_entities: List[str] = field(default_factory=list)  # Entity名のリスト
    triggering_entities_rule: str = "any"  # any, all
    entity_condition: Optional[TimeHeadwayCondition] = None
    offroad_condition: Optional[OffroadCondition] = None
    traveled_distance_condition: Optional[TraveledDistanceCondition] = None
    time_to_collision_condition: Optional[TimeToCollisionCondition] = None
    reach_position_condition: Optional[ReachPositionCondition] = None
    end_of_road_condition: Optional[EndOfRoadCondition] = None
    collision_condition: Optional[CollisionCondition] = None
    acceleration_condition: Optional[AccelerationCondition] = None
    stand_still_condition: Optional[StandStillCondition] = None
    speed_condition: Optional[SpeedCondition] = None
    relative_speed_condition: Optional[RelativeSpeedCondition] = None
    distance_condition: Optional[DistanceCondition] = None
    relative_distance_condition: Optional[RelativeDistanceCondition] = None
    relative_clearance_condition: Optional[RelativeClearanceCondition] = None


@dataclass
class Condition:
    """Condition（条件）"""
    name: str = ""
    delay: Union[str, float] = 0.0  # パラメータ参照を含む可能性があるため
    condition_edge: str = "rising"  # rising, falling, none, risingOrFalling
    simulation_time_condition: Optional[SimulationTimeCondition] = None
    by_entity_condition: Optional[ByEntityCondition] = None
    storyboard_element_state_condition: Optional[StoryboardElementStateCondition] = None
    parameter_condition: Optional[ParameterCondition] = None
    time_of_day_condition: Optional[TimeOfDayCondition] = None
    user_defined_value_condition: Optional[UserDefinedValueCondition] = None
    traffic_signal_condition: Optional[TrafficSignalCondition] = None
    traffic_signal_controller_condition: Optional[TrafficSignalControllerCondition] = None
    variable_condition: Optional[VariableCondition] = None


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
class Center:
    """Center（中心点）"""
    x: Union[str, float]
    y: Union[str, float]
    z: Union[str, float]


@dataclass
class Dimensions:
    """Dimensions（寸法）"""
    height: Union[str, float]
    length: Union[str, float]
    width: Union[str, float]


@dataclass
class BoundingBox:
    """BoundingBox（境界ボックス）"""
    center: Center
    dimensions: Dimensions


@dataclass
class Performance:
    """Performance（性能）"""
    max_acceleration: Union[str, float]
    max_deceleration: Union[str, float]
    max_speed: Union[str, float]
    max_acceleration_rate: Optional[Union[str, float]] = None
    max_deceleration_rate: Optional[Union[str, float]] = None


@dataclass
class Axle:
    """Axle（車軸）"""
    max_steering: Union[str, float]
    position_x: Union[str, float]
    position_z: Union[str, float]
    track_width: Union[str, float]
    wheel_diameter: Union[str, float]


@dataclass
class Axles:
    """Axles（車軸集合）"""
    front_axle: Axle
    rear_axle: Axle
    additional_axles: List[Axle] = field(default_factory=list)


@dataclass
class Vehicle:
    """Vehicle（車両）"""
    name: str
    vehicle_category: str = "car"  # car, van, truck, trailer, semitrailer, bus, motorbike, bicycle, train, tram
    role: Optional[str] = None
    mass: Optional[Union[str, float]] = None
    model3d: Optional[str] = None
    parameter_declarations: Optional[ParameterDeclarations] = None
    bounding_box: Optional[BoundingBox] = None
    performance: Optional[Performance] = None
    axles: Optional[Axles] = None
    properties: Optional[Properties] = None


@dataclass
class ParameterAssignment:
    """ParameterAssignment（パラメータ割り当て）"""
    parameter_ref: str
    value: str


@dataclass
class ParameterAssignments:
    """ParameterAssignments（パラメータ割り当てリスト）"""
    assignments: List[ParameterAssignment]


@dataclass
class CatalogReference:
    """CatalogReference（カタログ参照）"""
    catalog_name: str
    entry_name: str
    parameter_assignments: Optional[ParameterAssignments] = None


@dataclass
class Pedestrian:
    """Pedestrian（歩行者）"""
    name: str
    mass: Union[str, float]  # XSDでは必須
    pedestrian_category: str = "pedestrian"
    model: Optional[str] = None  # deprecated
    model3d: Optional[str] = None
    role: Optional[str] = None
    parameter_declarations: Optional[ParameterDeclarations] = None
    bounding_box: Optional[BoundingBox] = None
    properties: Optional[Properties] = None


@dataclass
class Property:
    """Property（プロパティ）"""
    name: str
    value: str


@dataclass
class Properties:
    """Properties（プロパティ集合）"""
    properties: List[Property] = field(default_factory=list)


@dataclass
class Controller:
    """Controller（コントローラー）"""
    name: str
    properties: Optional[Properties] = None


@dataclass
class ObjectController:
    """ObjectController（オブジェクトコントローラー）"""
    controller: Optional[Controller] = None
    catalog_reference: Optional[CatalogReference] = None


@dataclass
class ScenarioObject:
    """ScenarioObject（シナリオオブジェクト）"""
    name: str
    vehicle: Optional[Vehicle] = None
    pedestrian: Optional[Pedestrian] = None
    catalog_reference: Optional[CatalogReference] = None
    object_controller: Optional[ObjectController] = None
    # 将来の拡張: misc_object


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
    route_catalog: Optional[str] = None  # RouteCatalogのDirectoryパス
    controller_catalog: Optional[str] = None  # ControllerCatalogのDirectoryパス
    pedestrian_catalog: Optional[str] = None  # PedestrianCatalogのDirectoryパス
    misc_object_catalog: Optional[str] = None  # MiscObjectCatalogのDirectoryパス
    environment_catalog: Optional[str] = None  # EnvironmentCatalogのDirectoryパス
    maneuver_catalog: Optional[str] = None  # ManeuverCatalogのDirectoryパス
    trajectory_catalog: Optional[str] = None  # TrajectoryCatalogのDirectoryパス


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


