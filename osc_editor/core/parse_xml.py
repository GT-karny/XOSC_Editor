"""XML → モデルへの変換"""

import xml.etree.ElementTree as ET
from typing import Optional, Union
from osc_editor.core.model import (
    ScenarioDefinition,
    FileHeader,
    ParameterDeclarations,
    ParameterDeclaration,
    VariableDeclarations,
    VariableDeclaration,
    RoadNetwork,
    CatalogLocations,
    Entities,
    ScenarioObject,
    Vehicle,
    Pedestrian,
    CatalogReference,
    ParameterAssignment,
    ParameterAssignments,
    Storyboard,
    Init,
    Story,
    Act,
    ManeuverGroup,
    Maneuver,
    Event,
    Action,
    Private,
    PrivateAction,
    TeleportAction,
    AssignRouteAction,
    AcquirePositionAction,
    RoutingAction,
    FollowTrajectoryAction,
    Trajectory,
    TrajectoryRef,
    Polyline,
    Clothoid,
    Nurbs,
    Vertex,
    ControlPoint,
    TimeReference,
    ActivateControllerAction,
    AssignControllerAction,
    OverrideControllerValueAction,
    ControllerAction,
    Controller,
    SpeedAction,
    SpeedProfileEntry,
    SpeedProfileAction,
    LongitudinalDistanceAction,
    LateralDistanceAction,
    DynamicConstraints,
    RelativeTargetSpeed,
    LaneChangeAction,
    LaneOffsetAction,
    LaneOffsetActionDynamics,
    VisibilityAction,
    SynchronizeAction,
    TargetDistanceSteadyState,
    TargetTimeSteadyState,
    AppearanceAction,
    WorldPosition,
    LanePosition,
    RoutePosition,
    RelativeWorldPosition,
    RelativeLanePosition,
    RelativeRoadPosition,
    RelativeObjectPosition,
    RoadPosition,
    Dynamics,
    DynamicsDimension,
    DynamicsShape,
    StartTrigger,
    ConditionGroup,
    Condition,
    SimulationTimeCondition,
    ByEntityCondition,
    TimeHeadwayCondition,
    OffroadCondition,
    TraveledDistanceCondition,
    TimeToCollisionCondition,
    ReachPositionCondition,
    EndOfRoadCondition,
    CollisionCondition,
    ParameterCondition,
    StoryboardElementStateCondition,
    TimeOfDayCondition,
    UserDefinedValueCondition,
    TrafficSignalCondition,
    TrafficSignalControllerCondition,
    VariableCondition,
    AccelerationCondition,
    StandStillCondition,
    SpeedCondition,
    RelativeSpeedCondition,
    DistanceCondition,
    RelativeDistanceCondition,
    RelativeClearanceCondition,
    RelativeLaneRange,
    GlobalAction,
    ParameterAction,
    VariableAction,
    VariableSetAction,
    VariableModifyAction,
    VariableModifyRule,
    VariableAddValueRule,
    VariableMultiplyByValueRule,
    ObjectController,
    Controller,
    Properties,
    Property,
    Rule,
    BoundingBox,
    Center,
    Dimensions,
    Performance,
    Axles,
    Axle,
    Route,
    Waypoint,
)


# OpenSCENARIO名前空間
OSC_NS = "{http://www.asam.net/xml}"
OSC_NS_MAP = {"osc": "http://www.asam.net/xml"}


def _detect_namespace(element: ET.Element) -> str:
    """要素から名前空間を検出（グローバル変数を変更しない）"""
    if element is None:
        return ""
    if element.tag.startswith("{"):
        return element.tag[:element.tag.index("}") + 1]
    return ""


# ============================================================================
# 属性取得用ヘルパー関数（XSD準拠）
# ============================================================================

def _get_attr(element: ET.Element, attr_name: str, default: str = "") -> str:
    """要素の属性から文字列を取得"""
    if element is None:
        return default
    return element.get(attr_name, default)


def _get_attr_float(element: ET.Element, attr_name: str, default: float = 0.0) -> Union[str, float]:
    """要素の属性から浮動小数点数を取得（パラメータ参照の場合は文字列を返す）"""
    if element is None:
        return default
    attr_value = element.get(attr_name)
    if attr_value is None:
        return default
    # パラメータ参照（$で始まる）または式（${...}を含む）の場合は文字列として返す
    if attr_value.startswith('$') or '${' in attr_value:
        return attr_value
    try:
        return float(attr_value)
    except (ValueError, TypeError):
        return default


def _get_attr_int(element: ET.Element, attr_name: str, default: int = 0) -> int:
    """要素の属性から整数を取得"""
    if element is None:
        return default
    attr_value = element.get(attr_name)
    if attr_value is None:
        return default
    try:
        return int(attr_value)
    except (ValueError, TypeError):
        return default


def _get_attr_bool(element: ET.Element, attr_name: str, default: bool = False) -> Union[str, bool]:
    """要素の属性から真偽値を取得（パラメータ参照の場合は文字列を返す）"""
    if element is None:
        return default
    attr_value = element.get(attr_name)
    if attr_value is None:
        return default
    # パラメータ参照（$で始まる）または式（${...}を含む）の場合は文字列として返す
    if isinstance(attr_value, str) and (attr_value.startswith('$') or '${' in attr_value):
        return attr_value
    if isinstance(attr_value, bool):
        return attr_value
    if isinstance(attr_value, str):
        return attr_value.lower() in ("true", "1", "yes")
    return default


# ============================================================================
# 子要素取得用ヘルパー関数（後方互換性のため残す）
# ============================================================================

def _get_text(element: ET.Element, tag: str, default: str = "") -> str:
    """要素からテキストを取得（名前空間付き）"""
    if element is None:
        return default
    child = element.find(f"./{OSC_NS}{tag}")
    if child is not None and child.text:
        return child.text
    return default


def _get_float(element: ET.Element, tag: str, default: float = 0.0) -> float:
    """要素から浮動小数点数を取得"""
    text = _get_text(element, tag)
    if text:
        try:
            return float(text)
        except ValueError:
            return default
    return default


def _get_int(element: ET.Element, tag: str, default: int = 0) -> int:
    """要素から整数を取得"""
    text = _get_text(element, tag)
    if text:
        try:
            return int(text)
        except ValueError:
            return default
    return default


def parse_file_header(element: ET.Element) -> FileHeader:
    """FileHeaderをパース（XSD準拠：属性から取得）"""
    if element is None:
        return FileHeader()
    return FileHeader(
        rev_major=_get_attr_int(element, "revMajor", 1),
        rev_minor=_get_attr_int(element, "revMinor", 2),
        date=_get_attr(element, "date", ""),
        description=_get_attr(element, "description", ""),
        author=_get_attr(element, "author", ""),
    )


def parse_parameter_declarations(element: ET.Element) -> ParameterDeclarations:
    """ParameterDeclarationsをパース"""
    if element is None:
        return ParameterDeclarations(parameters=[])
    ns = _detect_namespace(element)
    params = []
    for param_elem in element.findall(f"./{ns}ParameterDeclaration"):
        params.append(
            ParameterDeclaration(
                name=param_elem.get("name", ""),
                parameter_type=param_elem.get("parameterType", "double"),
                value=param_elem.get("value", ""),
            )
        )
    return ParameterDeclarations(parameters=params)


def parse_variable_declarations(element: ET.Element) -> VariableDeclarations:
    """VariableDeclarationsをパース"""
    if element is None:
        return VariableDeclarations(variables=[])
    ns = _detect_namespace(element)
    variables = []
    for var_elem in element.findall(f"./{ns}VariableDeclaration"):
        variables.append(
            VariableDeclaration(
                name=var_elem.get("name", ""),
                variable_type=var_elem.get("variableType", "double"),
                value=var_elem.get("value", ""),
            )
        )
    return VariableDeclarations(variables=variables)


def parse_road_network(element: ET.Element) -> RoadNetwork:
    """RoadNetworkをパース"""
    if element is None:
        return RoadNetwork()
    ns = _detect_namespace(element)
    logic_file_elem = element.find(f"./{ns}LogicFile")
    scene_graph_elem = element.find(f"./{ns}SceneGraphFile")
    
    return RoadNetwork(
        logic_file=logic_file_elem.get("filepath") if logic_file_elem is not None else None,
        scene_graph_file=scene_graph_elem.get("filepath") if scene_graph_elem is not None else None,
    )


def parse_catalog_locations(element: ET.Element) -> CatalogLocations:
    """CatalogLocationsをパース"""
    if element is None:
        return CatalogLocations()
    ns = _detect_namespace(element)
    vehicle_catalog_elem = element.find(f"./{ns}VehicleCatalog/{ns}Directory")
    vehicle_catalog = vehicle_catalog_elem.get("path") if vehicle_catalog_elem is not None else None
    
    route_catalog_elem = element.find(f"./{ns}RouteCatalog/{ns}Directory")
    route_catalog = route_catalog_elem.get("path") if route_catalog_elem is not None else None
    
    controller_catalog_elem = element.find(f"./{ns}ControllerCatalog/{ns}Directory")
    controller_catalog = controller_catalog_elem.get("path") if controller_catalog_elem is not None else None
    
    pedestrian_catalog_elem = element.find(f"./{ns}PedestrianCatalog/{ns}Directory")
    pedestrian_catalog = pedestrian_catalog_elem.get("path") if pedestrian_catalog_elem is not None else None
    
    misc_object_catalog_elem = element.find(f"./{ns}MiscObjectCatalog/{ns}Directory")
    misc_object_catalog = misc_object_catalog_elem.get("path") if misc_object_catalog_elem is not None else None
    
    environment_catalog_elem = element.find(f"./{ns}EnvironmentCatalog/{ns}Directory")
    environment_catalog = environment_catalog_elem.get("path") if environment_catalog_elem is not None else None
    
    maneuver_catalog_elem = element.find(f"./{ns}ManeuverCatalog/{ns}Directory")
    maneuver_catalog = maneuver_catalog_elem.get("path") if maneuver_catalog_elem is not None else None
    
    trajectory_catalog_elem = element.find(f"./{ns}TrajectoryCatalog/{ns}Directory")
    trajectory_catalog = trajectory_catalog_elem.get("path") if trajectory_catalog_elem is not None else None
    
    return CatalogLocations(
        vehicle_catalog=vehicle_catalog,
        route_catalog=route_catalog,
        controller_catalog=controller_catalog,
        pedestrian_catalog=pedestrian_catalog,
        misc_object_catalog=misc_object_catalog,
        environment_catalog=environment_catalog,
        maneuver_catalog=maneuver_catalog,
        trajectory_catalog=trajectory_catalog
    )


def parse_world_position(element: ET.Element) -> WorldPosition:
    """WorldPositionをパース（XSD準拠：属性から取得）"""
    if element is None:
        return WorldPosition(x=0.0, y=0.0)
    return WorldPosition(
        x=_get_attr_float(element, "x", 0.0),
        y=_get_attr_float(element, "y", 0.0),
        z=_get_attr_float(element, "z", 0.0),
        h=_get_attr_float(element, "h", 0.0),
        p=_get_attr_float(element, "p", 0.0),
        r=_get_attr_float(element, "r", 0.0),
    )


def parse_lane_position(element: ET.Element) -> LanePosition:
    """LanePositionをパース（XSD準拠：属性から取得、laneIdはString型）"""
    if element is None:
        return LanePosition(road_id="", lane_id="")
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return LanePosition(
        road_id=_get_attr(element, "roadId", ""),
        lane_id=_get_attr(element, "laneId", ""),  # XSDではString型
        s=_get_attr_float(element, "s", 0.0),
        offset=_get_attr_float(element, "offset", 0.0),
        orientation=orientation,
    )


def parse_route_position(element: ET.Element) -> Optional[RoutePosition]:
    """RoutePositionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    route_ref_elem = element.find(f"./{ns}RouteRef")
    route_ref = None
    route = None
    if route_ref_elem is not None:
        catalog_ref_elem = route_ref_elem.find(f"./{ns}CatalogReference")
        if catalog_ref_elem is not None:
            route_ref = parse_catalog_reference(catalog_ref_elem)
        route_elem = route_ref_elem.find(f"./{ns}Route")
        if route_elem is not None:
            route = parse_route(route_elem)
    
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    in_route_position_elem = element.find(f"./{ns}InRoutePosition")
    in_route_position = None
    if in_route_position_elem is not None:
        # FromCurrentEntity
        from_current_entity_elem = in_route_position_elem.find(f"./{ns}FromCurrentEntity")
        if from_current_entity_elem is not None:
            in_route_position = {
                "type": "FromCurrentEntity",
                "entityRef": _get_attr(from_current_entity_elem, "entityRef", ""),
            }
        # FromRoadCoordinates
        elif in_route_position_elem.find(f"./{ns}FromRoadCoordinates") is not None:
            from_road_coords_elem = in_route_position_elem.find(f"./{ns}FromRoadCoordinates")
            in_route_position = {
                "type": "FromRoadCoordinates",
                "pathS": _get_attr_float(from_road_coords_elem, "pathS", 0.0),
                "t": _get_attr_float(from_road_coords_elem, "t", 0.0),
            }
        # FromLaneCoordinates
        else:
            from_lane_elem = in_route_position_elem.find(f"./{ns}FromLaneCoordinates")
            if from_lane_elem is not None:
                in_route_position = {
                    "type": "FromLaneCoordinates",
                    "pathS": _get_attr_float(from_lane_elem, "pathS", 0.0),
                    "laneId": _get_attr(from_lane_elem, "laneId", ""),
                    "laneOffset": _get_attr_float(from_lane_elem, "laneOffset", 0.0),
                }
    
    if route_ref is None and route is None and in_route_position is None:
        return None
    
    return RoutePosition(route_ref=route_ref, route=route, orientation=orientation, in_route_position=in_route_position)


def parse_relative_world_position(element: ET.Element) -> Optional[RelativeWorldPosition]:
    """RelativeWorldPositionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    if not entity_ref:
        return None
    
    dx = _get_attr_float(element, "dx", 0.0)
    dy = _get_attr_float(element, "dy", 0.0)
    dz = _get_attr_float(element, "dz", 0.0)
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return RelativeWorldPosition(
        entity_ref=entity_ref,
        dx=dx,
        dy=dy,
        dz=dz,
        orientation=orientation,
    )


def parse_relative_lane_position(element: ET.Element) -> Optional[RelativeLanePosition]:
    """RelativeLanePositionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    d_lane_attr = element.get("dLane")
    if not entity_ref or d_lane_attr is None:
        return None
    
    # dLaneはInt型
    try:
        d_lane = int(d_lane_attr)
    except (ValueError, TypeError):
        d_lane = d_lane_attr  # パラメータ参照の場合は文字列として保持
    
    ds = _get_attr_float(element, "ds", None)
    if isinstance(ds, str):
        ds = None
    
    offset = _get_attr_float(element, "offset", None)
    if isinstance(offset, str):
        offset = None
    
    ds_lane = _get_attr_float(element, "dsLane", None)
    if isinstance(ds_lane, str):
        ds_lane = None
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return RelativeLanePosition(
        entity_ref=entity_ref,
        d_lane=d_lane,
        ds=ds,
        offset=offset,
        ds_lane=ds_lane,
        orientation=orientation,
    )


def parse_relative_road_position(element: ET.Element) -> Optional[RelativeRoadPosition]:
    """RelativeRoadPositionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    if not entity_ref:
        return None
    
    ds = _get_attr_float(element, "ds", 0.0)
    dt = _get_attr_float(element, "dt", 0.0)
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return RelativeRoadPosition(
        entity_ref=entity_ref,
        ds=ds,
        dt=dt,
        orientation=orientation,
    )


def parse_relative_object_position(element: ET.Element) -> Optional[RelativeObjectPosition]:
    """RelativeObjectPositionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    if not entity_ref:
        return None
    
    dx = _get_attr_float(element, "dx", 0.0)
    dy = _get_attr_float(element, "dy", 0.0)
    dz = _get_attr_float(element, "dz", 0.0)
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return RelativeObjectPosition(
        entity_ref=entity_ref,
        dx=dx,
        dy=dy,
        dz=dz,
        orientation=orientation,
    )


def parse_road_position(element: ET.Element) -> Optional[RoadPosition]:
    """RoadPositionをパース"""
    if element is None:
        return None
    
    road_id = _get_attr(element, "roadId", "")
    if not road_id:
        return None
    
    s = _get_attr_float(element, "s", 0.0)
    t = _get_attr_float(element, "t", 0.0)
    
    ns = _detect_namespace(element)
    orientation_elem = element.find(f"./{ns}Orientation")
    orientation = None
    if orientation_elem is not None:
        orientation = {
            "type": _get_attr(orientation_elem, "type", "absolute"),
            "h": _get_attr_float(orientation_elem, "h", 0.0),
            "p": _get_attr_float(orientation_elem, "p", 0.0),
            "r": _get_attr_float(orientation_elem, "r", 0.0),
        }
    
    return RoadPosition(
        road_id=road_id,
        s=s,
        t=t,
        orientation=orientation,
    )


def parse_transition_dynamics(element: ET.Element) -> Optional[Dynamics]:
    """TransitionDynamicsをパース（XSD準拠：属性から取得）"""
    if element is None:
        return None
    
    dim_str = _get_attr(element, "dynamicsDimension", "time")
    shape_str = _get_attr(element, "dynamicsShape", "linear")
    
    # value属性の取得（必須属性、パラメータ式も対応）
    # _get_attr_floatはパラメータ式（$で始まる、または${...}を含む）の場合は文字列として返す
    value = _get_attr_float(element, "value", None)
    
    try:
        dim = DynamicsDimension(dim_str)
    except ValueError:
        dim = DynamicsDimension.TIME
    
    try:
        shape = DynamicsShape(shape_str)
    except ValueError:
        shape = DynamicsShape.LINEAR
    
    return Dynamics(
        dynamics_dimension=dim,
        dynamics_shape=shape,
        value=value,
    )


def parse_position(element: ET.Element):
    """Position要素をパース（全タイプに対応）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    
    # 各Positionタイプを順にチェック
    world_pos_elem = element.find(f"./{ns}WorldPosition")
    if world_pos_elem is not None:
        return parse_world_position(world_pos_elem)
    
    relative_world_pos_elem = element.find(f"./{ns}RelativeWorldPosition")
    if relative_world_pos_elem is not None:
        return parse_relative_world_position(relative_world_pos_elem)
    
    relative_object_pos_elem = element.find(f"./{ns}RelativeObjectPosition")
    if relative_object_pos_elem is not None:
        return parse_relative_object_position(relative_object_pos_elem)
    
    road_pos_elem = element.find(f"./{ns}RoadPosition")
    if road_pos_elem is not None:
        return parse_road_position(road_pos_elem)
    
    relative_road_pos_elem = element.find(f"./{ns}RelativeRoadPosition")
    if relative_road_pos_elem is not None:
        return parse_relative_road_position(relative_road_pos_elem)
    
    lane_pos_elem = element.find(f"./{ns}LanePosition")
    if lane_pos_elem is not None:
        return parse_lane_position(lane_pos_elem)
    
    relative_lane_pos_elem = element.find(f"./{ns}RelativeLanePosition")
    if relative_lane_pos_elem is not None:
        return parse_relative_lane_position(relative_lane_pos_elem)
    
    route_pos_elem = element.find(f"./{ns}RoutePosition")
    if route_pos_elem is not None:
        return parse_route_position(route_pos_elem)
    
    return None


def parse_teleport_action(element: ET.Element) -> Optional[TeleportAction]:
    """TeleportActionをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    position_container = element.find(f"./{ns}Position")
    if position_container is None:
        return None
    
    position = parse_position(position_container)
    if position is None:
        return None
    
    # Positionタイプに応じてTeleportActionの属性を設定
    if isinstance(position, WorldPosition):
        return TeleportAction(position=position)
    elif isinstance(position, LanePosition):
        return TeleportAction(lane_position=position)
    elif isinstance(position, RoutePosition):
        return TeleportAction(route_position=position)
    elif isinstance(position, RelativeWorldPosition):
        return TeleportAction(relative_world_position=position)
    elif isinstance(position, RelativeLanePosition):
        return TeleportAction(relative_lane_position=position)
    elif isinstance(position, RelativeRoadPosition):
        return TeleportAction(relative_road_position=position)
    elif isinstance(position, RelativeObjectPosition):
        return TeleportAction(relative_object_position=position)
    elif isinstance(position, RoadPosition):
        return TeleportAction(road_position=position)
    
    return None


def parse_relative_target_speed(element: ET.Element) -> Optional[RelativeTargetSpeed]:
    """RelativeTargetSpeedをパース"""
    if element is None:
        return None
    entity_ref = _get_attr(element, "entityRef", "")
    value = _get_attr(element, "value", "")
    speed_target_value_type = _get_attr(element, "speedTargetValueType", "delta")
    continuous = _get_attr_bool(element, "continuous", True)
    if not entity_ref or not value:
        return None
    return RelativeTargetSpeed(
        entity_ref=entity_ref,
        value=value,
        speed_target_value_type=speed_target_value_type,
        continuous=continuous
    )


def parse_speed_action(element: ET.Element) -> Optional[SpeedAction]:
    """SpeedActionをパース（XSD準拠）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    # SpeedActionDynamicsはTransitionDynamics型（属性から取得）
    dynamics_elem = element.find(f"./{ns}SpeedActionDynamics")
    dynamics = parse_transition_dynamics(dynamics_elem) if dynamics_elem is not None else None
    
    # SpeedActionTargetからAbsoluteTargetSpeedまたはRelativeTargetSpeedを取得
    speed_target_elem = element.find(f"./{ns}SpeedActionTarget")
    if speed_target_elem is None:
        return None
    
    absolute_elem = speed_target_elem.find(f"./{ns}AbsoluteTargetSpeed")
    relative_elem = speed_target_elem.find(f"./{ns}RelativeTargetSpeed")
    
    speed_target = None
    speed_target_str = None
    relative_target_speed = None
    
    if absolute_elem is not None:
        value_str = _get_attr(absolute_elem, "value", "")
        # パラメータ式かどうかを判定（${で始まる、または$を含む）
        if value_str.startswith("${") or "$" in value_str:
            speed_target_str = value_str
            speed_target = None
        else:
            try:
                speed_target = _get_attr_float(absolute_elem, "value", 0.0)
                speed_target_str = None
            except (ValueError, TypeError):
                # 変換に失敗した場合は文字列として扱う
                speed_target_str = value_str
                speed_target = None
    elif relative_elem is not None:
        relative_target_speed = parse_relative_target_speed(relative_elem)
    
    if speed_target is None and speed_target_str is None and relative_target_speed is None:
        return None
    
    return SpeedAction(
        speed_target=speed_target,
        speed_target_str=speed_target_str,
        relative_target_speed=relative_target_speed,
        dynamics=dynamics
    )


def parse_dynamic_constraints(element: ET.Element) -> Optional[DynamicConstraints]:
    """DynamicConstraintsをパース"""
    if element is None:
        return None
    
    return DynamicConstraints(
        max_acceleration=_get_attr_float(element, "maxAcceleration", None),
        max_acceleration_rate=_get_attr_float(element, "maxAccelerationRate", None),
        max_deceleration=_get_attr_float(element, "maxDeceleration", None),
        max_deceleration_rate=_get_attr_float(element, "maxDecelerationRate", None),
        max_speed=_get_attr_float(element, "maxSpeed", None),
    )


def parse_speed_profile_entry(element: ET.Element) -> Optional[SpeedProfileEntry]:
    """SpeedProfileEntryをパース"""
    if element is None:
        return None
    
    speed = _get_attr_float(element, "speed", 0.0)
    time = _get_attr_float(element, "time", None)
    
    return SpeedProfileEntry(speed=speed, time=time)


def parse_speed_profile_action(element: ET.Element) -> Optional[SpeedProfileAction]:
    """SpeedProfileActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    following_mode = _get_attr(element, "followingMode", "follow")
    entity_ref = _get_attr(element, "entityRef", None)
    
    # DynamicConstraints要素（optional）
    dynamic_constraints_elem = element.find(f"./{ns}DynamicConstraints")
    dynamic_constraints = parse_dynamic_constraints(dynamic_constraints_elem) if dynamic_constraints_elem is not None else None
    
    # SpeedProfileEntry要素（required, maxOccurs="unbounded"）
    entry_elems = element.findall(f"./{ns}SpeedProfileEntry")
    entries = []
    for entry_elem in entry_elems:
        entry = parse_speed_profile_entry(entry_elem)
        if entry is not None:
            entries.append(entry)
    
    if not entries:
        return None  # SpeedProfileEntryは必須
    
    return SpeedProfileAction(
        following_mode=following_mode,
        entity_ref=entity_ref if entity_ref else None,
        dynamic_constraints=dynamic_constraints,
        entries=entries,
    )


def parse_longitudinal_distance_action(element: ET.Element) -> Optional[LongitudinalDistanceAction]:
    """LongitudinalDistanceActionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    continuous = _get_attr_bool(element, "continuous", True)
    freespace = _get_attr_bool(element, "freespace", True)
    
    if not entity_ref:
        return None
    
    ns = _detect_namespace(element)
    dynamic_constraints_elem = element.find(f"./{ns}DynamicConstraints")
    dynamic_constraints = parse_dynamic_constraints(dynamic_constraints_elem) if dynamic_constraints_elem is not None else None
    
    return LongitudinalDistanceAction(
        entity_ref=entity_ref,
        continuous=continuous,
        freespace=freespace,
        distance=_get_attr_float(element, "distance", None),
        time_gap=_get_attr_float(element, "timeGap", None),
        displacement=_get_attr(element, "displacement", None),
        coordinate_system=_get_attr(element, "coordinateSystem", None),
        dynamic_constraints=dynamic_constraints,
    )


def parse_lane_change_action(element: ET.Element) -> Optional[LaneChangeAction]:
    """LaneChangeActionをパース（XSD準拠：RelativeTargetLaneまたはAbsoluteTargetLane）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    # LaneChangeActionDynamicsはTransitionDynamics型（属性から取得）
    dynamics_elem = element.find(f"./{ns}LaneChangeActionDynamics")
    dynamics = parse_transition_dynamics(dynamics_elem) if dynamics_elem is not None else None
    
    # LaneChangeTargetからRelativeTargetLaneまたはAbsoluteTargetLaneを取得
    target_elem = element.find(f"./{ns}LaneChangeTarget")
    if target_elem is None:
        return None
    
    target_lane = None
    target_lane_absolute = None
    target_entity_ref = None
    
    # RelativeTargetLaneをチェック
    relative_target_elem = target_elem.find(f"./{ns}RelativeTargetLane")
    if relative_target_elem is not None:
        target_lane = _get_attr_int(relative_target_elem, "value", 0)
        target_entity_ref = _get_attr(relative_target_elem, "entityRef", "")
        if not target_entity_ref:
            target_entity_ref = None
    else:
        # AbsoluteTargetLaneをチェック
        absolute_target_elem = target_elem.find(f"./{ns}AbsoluteTargetLane")
        if absolute_target_elem is not None:
            target_lane_absolute = _get_attr(absolute_target_elem, "value", "")
    
    if target_lane is None and target_lane_absolute is None:
        return None
    
    # targetLaneOffset属性（オプション）
    target_lane_offset_attr = element.get("targetLaneOffset")
    if target_lane_offset_attr is None:
        target_lane_offset = None
    else:
        try:
            target_lane_offset = float(target_lane_offset_attr)
        except (ValueError, TypeError):
            target_lane_offset = None
    
    return LaneChangeAction(
        target_lane=target_lane,
        target_lane_absolute=target_lane_absolute,
        target_entity_ref=target_entity_ref,
        dynamics=dynamics,
        target_lane_offset=target_lane_offset,
    )


def parse_lateral_distance_action(element: ET.Element) -> Optional[LateralDistanceAction]:
    """LateralDistanceActionをパース"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    continuous = _get_attr_bool(element, "continuous", True)
    freespace = _get_attr_bool(element, "freespace", True)
    
    if not entity_ref:
        return None
    
    ns = _detect_namespace(element)
    dynamic_constraints_elem = element.find(f"./{ns}DynamicConstraints")
    dynamic_constraints = parse_dynamic_constraints(dynamic_constraints_elem) if dynamic_constraints_elem is not None else None
    
    return LateralDistanceAction(
        entity_ref=entity_ref,
        continuous=continuous,
        freespace=freespace,
        distance=_get_attr_float(element, "distance", None),
        displacement=_get_attr(element, "displacement", None),
        coordinate_system=_get_attr(element, "coordinateSystem", None),
        dynamic_constraints=dynamic_constraints,
    )


def parse_lane_offset_action_dynamics(element: ET.Element) -> Optional[LaneOffsetActionDynamics]:
    """LaneOffsetActionDynamicsをパース"""
    if element is None:
        return None
    
    shape_str = _get_attr(element, "dynamicsShape", "linear")
    try:
        shape = DynamicsShape(shape_str)
    except ValueError:
        shape = DynamicsShape.LINEAR
    
    max_lateral_acc = _get_attr_float(element, "maxLateralAcc", None)
    if isinstance(max_lateral_acc, str):
        max_lateral_acc = None
    
    return LaneOffsetActionDynamics(
        dynamics_shape=shape,
        max_lateral_acc=max_lateral_acc if isinstance(max_lateral_acc, float) else None,
    )


def parse_lane_offset_action(element: ET.Element) -> Optional[LaneOffsetAction]:
    """LaneOffsetActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    continuous = _get_attr_bool(element, "continuous", True)
    
    # LaneOffsetActionDynamics
    dynamics_elem = element.find(f"./{ns}LaneOffsetActionDynamics")
    dynamics = parse_lane_offset_action_dynamics(dynamics_elem) if dynamics_elem is not None else None
    
    # LaneOffsetTargetからAbsoluteTargetLaneOffsetまたはRelativeTargetLaneOffsetを取得
    target_elem = element.find(f"./{ns}LaneOffsetTarget")
    if target_elem is None:
        return None
    
    target_offset = None
    target_offset_relative = None
    target_offset_entity_ref = None
    
    # AbsoluteTargetLaneOffsetをチェック
    absolute_target_elem = target_elem.find(f"./{ns}AbsoluteTargetLaneOffset")
    if absolute_target_elem is not None:
        target_offset = _get_attr_float(absolute_target_elem, "value", 0.0)
    else:
        # RelativeTargetLaneOffsetをチェック
        relative_target_elem = target_elem.find(f"./{ns}RelativeTargetLaneOffset")
        if relative_target_elem is not None:
            target_offset_entity_ref = _get_attr(relative_target_elem, "entityRef", "")
            target_offset_relative = _get_attr_float(relative_target_elem, "value", 0.0)
    
    if target_offset is None and target_offset_relative is None:
        return None
    
    return LaneOffsetAction(
        target_offset=target_offset,
        target_offset_relative=target_offset_relative,
        target_offset_entity_ref=target_offset_entity_ref,
        dynamics=dynamics,
        continuous=continuous,
    )


def parse_vertex(element: ET.Element) -> Optional[Vertex]:
    """Vertexをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position")
    if position_elem is None:
        return None
    
    position = parse_position(position_elem)
    if position is None:
        return None
    
    time = _get_attr_float(element, "time", None)
    if isinstance(time, str):
        time = None
    
    return Vertex(position=position, time=time)


def parse_control_point(element: ET.Element) -> Optional[ControlPoint]:
    """ControlPointをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position")
    if position_elem is None:
        return None
    
    position = parse_position(position_elem)
    if position is None:
        return None
    
    time = _get_attr_float(element, "time", None)
    if isinstance(time, str):
        time = None
    
    weight = _get_attr_float(element, "weight", None)
    if isinstance(weight, str):
        weight = None
    
    return ControlPoint(position=position, time=time, weight=weight)


def parse_polyline(element: ET.Element) -> Optional[Polyline]:
    """Polylineをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    vertices = []
    for vertex_elem in element.findall(f"./{ns}Vertex"):
        vertex = parse_vertex(vertex_elem)
        if vertex is not None:
            vertices.append(vertex)
    
    if not vertices:
        return None
    
    return Polyline(vertices=vertices)


def parse_clothoid(element: ET.Element) -> Optional[Clothoid]:
    """Clothoidをパース"""
    if element is None:
        return None
    
    curvature = _get_attr_float(element, "curvature", None)
    if curvature is None:
        return None
    
    length = _get_attr_float(element, "length", None)
    if length is None:
        return None
    
    curvature_prime = _get_attr_float(element, "curvaturePrime", None)
    if isinstance(curvature_prime, str):
        curvature_prime = None
    
    start_time = _get_attr_float(element, "startTime", None)
    if isinstance(start_time, str):
        start_time = None
    
    stop_time = _get_attr_float(element, "stopTime", None)
    if isinstance(stop_time, str):
        stop_time = None
    
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position")
    if position_elem is None:
        return None
    
    position = parse_position(position_elem)
    if position is None:
        return None
    
    return Clothoid(
        curvature=curvature,
        length=length,
        position=position,
        curvature_prime=curvature_prime,
        start_time=start_time,
        stop_time=stop_time,
    )


def parse_nurbs(element: ET.Element) -> Optional[Nurbs]:
    """Nurbsをパース"""
    if element is None:
        return None
    
    order_attr = _get_attr(element, "order", None)
    if order_attr is None:
        return None
    
    try:
        order = int(order_attr)
    except (ValueError, TypeError):
        return None
    
    ns = _detect_namespace(element)
    
    # ControlPointリスト（2以上）
    control_points = []
    for cp_elem in element.findall(f"./{ns}ControlPoint"):
        cp = parse_control_point(cp_elem)
        if cp is not None:
            control_points.append(cp)
    
    if len(control_points) < 2:
        return None
    
    # Knotリスト（2以上）
    knots = []
    for knot_elem in element.findall(f"./{ns}Knot"):
        value = _get_attr_float(knot_elem, "value", None)
        if value is not None:
            knots.append({"value": value})
    
    if len(knots) < 2:
        return None
    
    return Nurbs(
        order=order,
        control_points=control_points,
        knots=knots,
    )


def parse_trajectory(element: ET.Element) -> Optional[Trajectory]:
    """Trajectoryをパース"""
    if element is None:
        return None
    
    name = _get_attr(element, "name", "")
    if not name:
        return None
    
    closed = _get_attr_bool(element, "closed", False)
    if isinstance(closed, str):
        closed = False  # パラメータ参照の場合はデフォルト値を使用
    
    ns = _detect_namespace(element)
    param_decls_elem = element.find(f"./{ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    # Shape内のPolyline, Clothoid, Nurbsをチェック（choice）
    shape_elem = element.find(f"./{ns}Shape")
    shape = None
    if shape_elem is not None:
        polyline_elem = shape_elem.find(f"./{ns}Polyline")
        if polyline_elem is not None:
            shape = parse_polyline(polyline_elem)
        else:
            clothoid_elem = shape_elem.find(f"./{ns}Clothoid")
            if clothoid_elem is not None:
                shape = parse_clothoid(clothoid_elem)
            else:
                nurbs_elem = shape_elem.find(f"./{ns}Nurbs")
                if nurbs_elem is not None:
                    shape = parse_nurbs(nurbs_elem)
    
    return Trajectory(
        name=name,
        closed=closed if isinstance(closed, bool) else False,
        shape=shape,
        parameter_declarations=param_decls,
    )


def parse_time_reference(element: ET.Element) -> Optional[TimeReference]:
    """TimeReferenceをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    none_elem = element.find(f"./{ns}None")
    if none_elem is not None:
        return TimeReference(timing=None)
    
    timing_elem = element.find(f"./{ns}Timing")
    if timing_elem is not None:
        timing = {
            "domainAbsoluteRelative": _get_attr(timing_elem, "domainAbsoluteRelative", "absolute"),
            "offset": _get_attr_float(timing_elem, "offset", 0.0),
            "scale": _get_attr_float(timing_elem, "scale", 1.0),
        }
        return TimeReference(timing=timing)
    
    return TimeReference(timing=None)


def parse_trajectory_ref(element: ET.Element) -> Optional[TrajectoryRef]:
    """TrajectoryRefをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    trajectory_elem = element.find(f"./{ns}Trajectory")
    trajectory = parse_trajectory(trajectory_elem) if trajectory_elem is not None else None
    
    catalog_ref_elem = element.find(f"./{ns}CatalogReference")
    catalog_reference = parse_catalog_reference(catalog_ref_elem) if catalog_ref_elem is not None else None
    
    if trajectory is None and catalog_reference is None:
        return None
    
    return TrajectoryRef(trajectory=trajectory, catalog_reference=catalog_reference)


def parse_follow_trajectory_action(element: ET.Element) -> Optional[FollowTrajectoryAction]:
    """FollowTrajectoryActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    
    # deprecatedだが互換性のためTrajectoryもサポート
    trajectory_elem = element.find(f"./{ns}Trajectory")
    trajectory = parse_trajectory(trajectory_elem) if trajectory_elem is not None else None
    
    # TrajectoryRef要素をパース（推奨）
    trajectory_ref_elem = element.find(f"./{ns}TrajectoryRef")
    trajectory_ref = parse_trajectory_ref(trajectory_ref_elem) if trajectory_ref_elem is not None else None
    
    # どちらもない場合はNoneを返す（後方互換性のためtrajectoryがない場合も許容）
    
    time_ref_elem = element.find(f"./{ns}TimeReference")
    time_reference = parse_time_reference(time_ref_elem) if time_ref_elem is not None else None
    
    following_mode_elem = element.find(f"./{ns}TrajectoryFollowingMode")
    following_mode = _get_attr(following_mode_elem, "followingMode", "follow") if following_mode_elem is not None else "follow"
    
    initial_distance_offset = _get_attr_float(element, "initialDistanceOffset", None)
    if isinstance(initial_distance_offset, str):
        initial_distance_offset = None
    
    return FollowTrajectoryAction(
        trajectory=trajectory,
        trajectory_ref=trajectory_ref,
        time_reference=time_reference,
        following_mode=following_mode,
        initial_distance_offset=initial_distance_offset,
    )


def parse_waypoint(element: ET.Element) -> Optional[Waypoint]:
    """Waypointをパース"""
    if element is None:
        return None
    
    route_strategy = _get_attr(element, "routeStrategy", "fastest")
    
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position")
    if position_elem is None:
        return None
    
    position = parse_position(position_elem)
    if position is None:
        return None
    
    return Waypoint(position=position, route_strategy=route_strategy)


def parse_route(element: ET.Element) -> Optional[Route]:
    """Routeをパース"""
    if element is None:
        return None
    
    name = _get_attr(element, "name", "")
    if not name:
        return None
    
    closed = _get_attr_bool(element, "closed", False)
    
    ns = _detect_namespace(element)
    param_decls_elem = element.find(f"./{ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    waypoints = []
    for waypoint_elem in element.findall(f"./{ns}Waypoint"):
        waypoint = parse_waypoint(waypoint_elem)
        if waypoint is not None:
            waypoints.append(waypoint)
    
    if len(waypoints) < 2:
        return None  # XSDではWaypointは2つ以上必要
    
    return Route(
        name=name,
        closed=closed,
        waypoints=waypoints,
        parameter_declarations=param_decls,
    )


def parse_assign_route_action(element: ET.Element) -> Optional[AssignRouteAction]:
    """AssignRouteActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    catalog_ref_elem = element.find(f"./{ns}CatalogReference")
    route_ref = parse_catalog_reference(catalog_ref_elem) if catalog_ref_elem is not None else None
    
    route_elem = element.find(f"./{ns}Route")
    route = parse_route(route_elem) if route_elem is not None else None
    
    if route_ref is None and route is None:
        return None
    
    return AssignRouteAction(route_ref=route_ref, route=route)


def parse_acquire_position_action(element: ET.Element) -> Optional[AcquirePositionAction]:
    """AcquirePositionActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position")
    if position_elem is None:
        return None
    
    position = parse_position(position_elem)
    if position is None:
        return None
    
    return AcquirePositionAction(position=position)


def parse_routing_action(element: ET.Element) -> Optional[RoutingAction]:
    """RoutingActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    assign_route_elem = element.find(f"./{ns}AssignRouteAction")
    follow_trajectory_elem = element.find(f"./{ns}FollowTrajectoryAction")
    acquire_position_elem = element.find(f"./{ns}AcquirePositionAction")
    
    assign_route_action = parse_assign_route_action(assign_route_elem) if assign_route_elem is not None else None
    follow_trajectory_action = parse_follow_trajectory_action(follow_trajectory_elem) if follow_trajectory_elem is not None else None
    acquire_position_action = parse_acquire_position_action(acquire_position_elem) if acquire_position_elem is not None else None
    
    if assign_route_action is None and follow_trajectory_action is None and acquire_position_action is None:
        return None
    
    return RoutingAction(
        assign_route_action=assign_route_action,
        follow_trajectory_action=follow_trajectory_action,
        acquire_position_action=acquire_position_action,
    )


def parse_assign_controller_action(element: ET.Element) -> Optional[AssignControllerAction]:
    """AssignControllerActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    controller_elem = element.find(f"./{ns}Controller")
    catalog_ref_elem = element.find(f"./{ns}CatalogReference")
    
    controller = parse_controller(controller_elem) if controller_elem is not None else None
    catalog_reference = parse_catalog_reference(catalog_ref_elem) if catalog_ref_elem is not None else None
    
    if controller is None and catalog_reference is None:
        return None
    
    return AssignControllerAction(
        controller=controller,
        catalog_reference=catalog_reference,
        activate_lateral=_get_attr_bool(element, "activateLateral", None),
        activate_longitudinal=_get_attr_bool(element, "activateLongitudinal", None),
        activate_animation=_get_attr_bool(element, "activateAnimation", None),
        activate_lighting=_get_attr_bool(element, "activateLighting", None),
    )


def parse_override_controller_value_action(element: ET.Element) -> Optional[OverrideControllerValueAction]:
    """OverrideControllerValueActionをパース（基本的な構造のみ）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    # 将来的な拡張として辞書型で保存
    throttle_elem = element.find(f"./{ns}Throttle")
    brake_elem = element.find(f"./{ns}Brake")
    clutch_elem = element.find(f"./{ns}Clutch")
    parking_brake_elem = element.find(f"./{ns}ParkingBrake")
    steering_wheel_elem = element.find(f"./{ns}SteeringWheel")
    gear_elem = element.find(f"./{ns}Gear")
    
    throttle = None
    if throttle_elem is not None:
        throttle = {"active": _get_attr_bool(throttle_elem, "active", True), "value": _get_attr_float(throttle_elem, "value", 0.0)}
    
    brake = None
    if brake_elem is not None:
        brake = {"active": _get_attr_bool(brake_elem, "active", True)}
    
    clutch = None
    if clutch_elem is not None:
        clutch = {"active": _get_attr_bool(clutch_elem, "active", True), "value": _get_attr_float(clutch_elem, "value", 0.0)}
    
    parking_brake = None
    if parking_brake_elem is not None:
        parking_brake = {"active": _get_attr_bool(parking_brake_elem, "active", True)}
    
    steering_wheel = None
    if steering_wheel_elem is not None:
        steering_wheel = {"active": _get_attr_bool(steering_wheel_elem, "active", True), "value": _get_attr_float(steering_wheel_elem, "value", 0.0)}
    
    gear = None
    if gear_elem is not None:
        gear = {"active": _get_attr_bool(gear_elem, "active", True)}
    
    if throttle is None and brake is None and clutch is None and parking_brake is None and steering_wheel is None and gear is None:
        return None
    
    return OverrideControllerValueAction(
        throttle=throttle,
        brake=brake,
        clutch=clutch,
        parking_brake=parking_brake,
        steering_wheel=steering_wheel,
        gear=gear,
    )


def parse_controller_action(element: ET.Element) -> Optional[ControllerAction]:
    """ControllerActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    assign_controller_elem = element.find(f"./{ns}AssignControllerAction")
    override_controller_value_elem = element.find(f"./{ns}OverrideControllerValueAction")
    activate_controller_elem = element.find(f"./{ns}ActivateControllerAction")
    
    assign_controller_action = parse_assign_controller_action(assign_controller_elem) if assign_controller_elem is not None else None
    override_controller_value_action = parse_override_controller_value_action(override_controller_value_elem) if override_controller_value_elem is not None else None
    activate_controller_action = parse_activate_controller_action(activate_controller_elem) if activate_controller_elem is not None else None
    
    if assign_controller_action is None and override_controller_value_action is None and activate_controller_action is None:
        return None
    
    return ControllerAction(
        assign_controller_action=assign_controller_action,
        override_controller_value_action=override_controller_value_action,
        activate_controller_action=activate_controller_action,
    )


def parse_activate_controller_action(element: ET.Element) -> Optional[ActivateControllerAction]:
    """ActivateControllerActionをパース"""
    if element is None:
        return None
    
    controller_ref = _get_attr(element, "controllerRef", None)
    longitudinal = _get_attr_bool(element, "longitudinal", None)
    lateral = _get_attr_bool(element, "lateral", None)
    animation = _get_attr_bool(element, "animation", None)
    lighting = _get_attr_bool(element, "lighting", None)
    return ActivateControllerAction(
        controller_ref=controller_ref if controller_ref else None,
        longitudinal=longitudinal,
        lateral=lateral,
        animation=animation,
        lighting=lighting,
    )


def parse_visibility_action(element: ET.Element) -> Optional[VisibilityAction]:
    """VisibilityActionをパース"""
    if element is None:
        return None
    
    graphics = _get_attr_bool(element, "graphics", True)
    sensors = _get_attr_bool(element, "sensors", True)
    traffic = _get_attr_bool(element, "traffic", True)
    
    # SensorReferenceSet要素は将来対応（現時点では省略）
    
    return VisibilityAction(
        graphics=graphics,
        sensors=sensors,
        traffic=traffic,
    )


def parse_synchronize_action(element: ET.Element) -> Optional[SynchronizeAction]:
    """SynchronizeActionをパース"""
    if element is None:
        return None
    
    master_entity_ref = _get_attr(element, "masterEntityRef", "")
    if not master_entity_ref:
        return None
    
    ns = _detect_namespace(element)
    
    # TargetPositionMaster要素（required）
    target_position_master_elem = element.find(f"./{ns}TargetPositionMaster")
    if target_position_master_elem is None:
        return None
    target_position_master = parse_position(target_position_master_elem)
    if target_position_master is None:
        return None
    
    # TargetPosition要素（required）
    target_position_elem = element.find(f"./{ns}TargetPosition")
    if target_position_elem is None:
        return None
    target_position = parse_position(target_position_elem)
    if target_position is None:
        return None
    
    # targetToleranceMaster, targetTolerance属性（optional）
    target_tolerance_master = _get_attr_float(element, "targetToleranceMaster", None)
    if isinstance(target_tolerance_master, str):
        target_tolerance_master = None
    
    target_tolerance = _get_attr_float(element, "targetTolerance", None)
    if isinstance(target_tolerance, str):
        target_tolerance = None
    
    # FinalSpeed要素（optional）
    final_speed_elem = element.find(f"./{ns}FinalSpeed")
    final_speed = None
    if final_speed_elem is not None:
        # AbsoluteSpeedまたはRelativeSpeedToMaster（choice）
        abs_speed_elem = final_speed_elem.find(f"./{ns}AbsoluteSpeed")
        if abs_speed_elem is not None:
            abs_speed_value = _get_attr_float(abs_speed_elem, "value", None)
            steady_state = None
            # SteadyState要素をチェック（TargetDistanceSteadyStateまたはTargetTimeSteadyState）
            target_distance_elem = abs_speed_elem.find(f"./{ns}TargetDistanceSteadyState")
            if target_distance_elem is not None:
                distance = _get_attr_float(target_distance_elem, "distance", None)
                if distance is not None:
                    steady_state = {"type": "TargetDistanceSteadyState", "distance": distance}
            else:
                target_time_elem = abs_speed_elem.find(f"./{ns}TargetTimeSteadyState")
                if target_time_elem is not None:
                    time = _get_attr_float(target_time_elem, "time", None)
                    if time is not None:
                        steady_state = {"type": "TargetTimeSteadyState", "time": time}
            final_speed = {"type": "AbsoluteSpeed", "value": abs_speed_value}
            if steady_state is not None:
                final_speed["steadyState"] = steady_state
        else:
            rel_speed_elem = final_speed_elem.find(f"./{ns}RelativeSpeedToMaster")
            if rel_speed_elem is not None:
                speed_target_value_type = _get_attr(rel_speed_elem, "speedTargetValueType", "delta")
                value = _get_attr_float(rel_speed_elem, "value", None)
                steady_state = None
                # SteadyState要素をチェック（TargetDistanceSteadyStateまたはTargetTimeSteadyState）
                target_distance_elem = rel_speed_elem.find(f"./{ns}TargetDistanceSteadyState")
                if target_distance_elem is not None:
                    distance = _get_attr_float(target_distance_elem, "distance", None)
                    if distance is not None:
                        steady_state = {"type": "TargetDistanceSteadyState", "distance": distance}
                else:
                    target_time_elem = rel_speed_elem.find(f"./{ns}TargetTimeSteadyState")
                    if target_time_elem is not None:
                        time = _get_attr_float(target_time_elem, "time", None)
                        if time is not None:
                            steady_state = {"type": "TargetTimeSteadyState", "time": time}
                final_speed = {
                    "type": "RelativeSpeedToMaster",
                    "speedTargetValueType": speed_target_value_type,
                    "value": value,
                }
                if steady_state is not None:
                    final_speed["steadyState"] = steady_state
    
    return SynchronizeAction(
        master_entity_ref=master_entity_ref,
        target_position_master=target_position_master,
        target_position=target_position,
        target_tolerance_master=target_tolerance_master,
        target_tolerance=target_tolerance,
        final_speed=final_speed,
    )


def parse_appearance_action(element: ET.Element) -> Optional[AppearanceAction]:
    """AppearanceActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    
    # LightStateAction要素（optional）
    light_state_elem = element.find(f"./{ns}LightStateAction")
    light_state_action = None
    if light_state_elem is not None:
        # 簡易実装：dictとして保存（将来の拡張用）
        transition_time = _get_attr_float(light_state_elem, "transitionTime", None)
        light_state_action = {"transitionTime": transition_time}
        # LightType, LightState要素は将来対応
    
    # AnimationAction要素（optional）
    animation_elem = element.find(f"./{ns}AnimationAction")
    animation_action = None
    if animation_elem is not None:
        # 簡易実装：dictとして保存（将来の拡張用）
        loop = _get_attr_bool(animation_elem, "loop", False)
        animation_duration = _get_attr_float(animation_elem, "animationDuration", None)
        animation_action = {"loop": loop, "animationDuration": animation_duration}
        # AnimationType, AnimationState要素は将来対応
    
    if light_state_action is None and animation_action is None:
        return None
    
    return AppearanceAction(
        light_state_action=light_state_action,
        animation_action=animation_action,
    )


def parse_private_action(element: ET.Element) -> Optional[PrivateAction]:
    """PrivateActionをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    teleport_elem = element.find(f"./{ns}TeleportAction")
    
    # LongitudinalActionのchoice要素
    longitudinal_action_elem = element.find(f"./{ns}LongitudinalAction")
    speed_elem = None
    speed_profile_elem = None
    longitudinal_distance_elem = None
    if longitudinal_action_elem is not None:
        speed_elem = longitudinal_action_elem.find(f"./{ns}SpeedAction")
        speed_profile_elem = longitudinal_action_elem.find(f"./{ns}SpeedProfileAction")
        longitudinal_distance_elem = longitudinal_action_elem.find(f"./{ns}LongitudinalDistanceAction")
    
    # LateralActionのchoice要素
    lateral_action_elem = element.find(f"./{ns}LateralAction")
    lane_change_elem = None
    lane_offset_elem = None
    lateral_distance_elem = None
    if lateral_action_elem is not None:
        lane_change_elem = lateral_action_elem.find(f"./{ns}LaneChangeAction")
        lane_offset_elem = lateral_action_elem.find(f"./{ns}LaneOffsetAction")
        lateral_distance_elem = lateral_action_elem.find(f"./{ns}LateralDistanceAction")
    
    routing_elem = element.find(f"./{ns}RoutingAction")
    activate_controller_elem = element.find(f"./{ns}ActivateControllerAction")
    controller_action_elem = element.find(f"./{ns}ControllerAction")
    visibility_elem = element.find(f"./{ns}VisibilityAction")
    synchronize_elem = element.find(f"./{ns}SynchronizeAction")
    appearance_elem = element.find(f"./{ns}AppearanceAction")
    
    teleport_action = parse_teleport_action(teleport_elem) if teleport_elem is not None else None
    speed_action = parse_speed_action(speed_elem) if speed_elem is not None else None
    speed_profile_action = parse_speed_profile_action(speed_profile_elem) if speed_profile_elem is not None else None
    longitudinal_distance_action = parse_longitudinal_distance_action(longitudinal_distance_elem) if longitudinal_distance_elem is not None else None
    lane_change_action = parse_lane_change_action(lane_change_elem) if lane_change_elem is not None else None
    lane_offset_action = parse_lane_offset_action(lane_offset_elem) if lane_offset_elem is not None else None
    lateral_distance_action = parse_lateral_distance_action(lateral_distance_elem) if lateral_distance_elem is not None else None
    routing_action = parse_routing_action(routing_elem) if routing_elem is not None else None
    activate_controller_action = parse_activate_controller_action(activate_controller_elem) if activate_controller_elem is not None else None
    controller_action = parse_controller_action(controller_action_elem) if controller_action_elem is not None else None
    visibility_action = parse_visibility_action(visibility_elem) if visibility_elem is not None else None
    synchronize_action = parse_synchronize_action(synchronize_elem) if synchronize_elem is not None else None
    appearance_action = parse_appearance_action(appearance_elem) if appearance_elem is not None else None
    
    if (teleport_action is None and speed_action is None and speed_profile_action is None and 
        longitudinal_distance_action is None and lane_change_action is None and 
        lane_offset_action is None and lateral_distance_action is None and
        routing_action is None and activate_controller_action is None and controller_action is None and
        visibility_action is None and synchronize_action is None and appearance_action is None):
        return None
    
    return PrivateAction(
        teleport_action=teleport_action,
        speed_action=speed_action,
        speed_profile_action=speed_profile_action,
        longitudinal_distance_action=longitudinal_distance_action,
        lane_change_action=lane_change_action,
        lane_offset_action=lane_offset_action,
        routing_action=routing_action,
        activate_controller_action=activate_controller_action,
        controller_action=controller_action,
        visibility_action=visibility_action,
        synchronize_action=synchronize_action,
        appearance_action=appearance_action,
    )


def parse_parameter_action(element: ET.Element) -> Optional[ParameterAction]:
    """ParameterActionをパース"""
    if element is None:
        return None
    parameter_ref = _get_attr(element, "parameterRef", "")
    if not parameter_ref:
        return None
    
    ns = _detect_namespace(element)
    set_action_elem = element.find(f"./{ns}SetAction")
    if set_action_elem is None:
        return None
    
    set_value = _get_attr_float(set_action_elem, "value", 0.0)
    
    return ParameterAction(
        parameter_ref=parameter_ref,
        set_action_value=set_value
    )


def parse_variable_add_value_rule(element: ET.Element) -> Optional[VariableAddValueRule]:
    """VariableAddValueRuleをパース"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    return VariableAddValueRule(value=value)


def parse_variable_multiply_by_value_rule(element: ET.Element) -> Optional[VariableMultiplyByValueRule]:
    """VariableMultiplyByValueRuleをパース"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    return VariableMultiplyByValueRule(value=value)


def parse_variable_modify_rule(element: ET.Element) -> Optional[VariableModifyRule]:
    """VariableModifyRuleをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    add_value_elem = element.find(f"./{ns}AddValue")
    multiply_by_value_elem = element.find(f"./{ns}MultiplyByValue")
    
    add_value_rule = parse_variable_add_value_rule(add_value_elem) if add_value_elem is not None else None
    multiply_by_value_rule = parse_variable_multiply_by_value_rule(multiply_by_value_elem) if multiply_by_value_elem is not None else None
    
    if add_value_rule is None and multiply_by_value_rule is None:
        return None
    
    return VariableModifyRule(
        add_value_rule=add_value_rule,
        multiply_by_value_rule=multiply_by_value_rule
    )


def parse_variable_modify_action(element: ET.Element) -> Optional[VariableModifyAction]:
    """VariableModifyActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    rule_elem = element.find(f"./{ns}Rule")
    modify_rule = parse_variable_modify_rule(rule_elem) if rule_elem is not None else None
    
    if modify_rule is None:
        return None
    
    return VariableModifyAction(modify_rule=modify_rule)


def parse_variable_set_action(element: ET.Element) -> Optional[VariableSetAction]:
    """VariableSetActionをパース"""
    if element is None:
        return None
    value = _get_attr(element, "value", "")
    if not value:
        return None
    return VariableSetAction(value=value)


def parse_variable_action(element: ET.Element) -> Optional[VariableAction]:
    """VariableActionをパース"""
    if element is None:
        return None
    variable_ref = _get_attr(element, "variableRef", "")
    if not variable_ref:
        return None
    
    ns = _detect_namespace(element)
    set_action_elem = element.find(f"./{ns}SetAction")
    modify_action_elem = element.find(f"./{ns}ModifyAction")
    
    set_action = parse_variable_set_action(set_action_elem) if set_action_elem is not None else None
    modify_action = parse_variable_modify_action(modify_action_elem) if modify_action_elem is not None else None
    
    if set_action is None and modify_action is None:
        return None
    
    return VariableAction(
        variable_ref=variable_ref,
        set_action=set_action,
        modify_action=modify_action
    )


def parse_global_action(element: ET.Element) -> Optional[GlobalAction]:
    """GlobalActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    parameter_action_elem = element.find(f"./{ns}ParameterAction")
    parameter_action = parse_parameter_action(parameter_action_elem) if parameter_action_elem is not None else None
    
    variable_action_elem = element.find(f"./{ns}VariableAction")
    variable_action = parse_variable_action(variable_action_elem) if variable_action_elem is not None else None
    
    if parameter_action is None and variable_action is None:
        return None
    
    return GlobalAction(
        parameter_action=parameter_action,
        variable_action=variable_action
    )


def parse_action(element: ET.Element) -> Optional[Action]:
    """Actionをパース（XSD準拠：name属性が必須）"""
    if element is None:
        return None
    
    name = _get_attr(element, "name", "")
    if not name:
        return None
    
    ns = _detect_namespace(element)
    # PrivateActionを取得
    private_action_elem = element.find(f"./{ns}PrivateAction")
    private_action = parse_private_action(private_action_elem) if private_action_elem is not None else None
    
    # GlobalActionを取得
    global_action_elem = element.find(f"./{ns}GlobalAction")
    global_action = parse_global_action(global_action_elem) if global_action_elem is not None else None
    
    # 将来の拡張: UserDefinedAction
    
    return Action(
        name=name,
        private_action=private_action,
        global_action=global_action,
    )


def parse_private(element: ET.Element) -> Optional[Private]:
    """Privateをパース（XSD準拠：entityRef属性が必須）"""
    if element is None:
        return None
    
    entity_ref = _get_attr(element, "entityRef", "")
    if not entity_ref:
        return None
    
    ns = _detect_namespace(element)
    actions = []
    for action_elem in element.findall(f"./{ns}PrivateAction"):
        action = parse_private_action(action_elem)
        if action is not None:
            actions.append(action)
    
    return Private(
        entity_ref=entity_ref,
        actions=actions,
    )


def parse_simulation_time_condition(element: ET.Element) -> Optional[SimulationTimeCondition]:
    """SimulationTimeConditionをパース（XSD準拠：属性から取得）"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    rule = _get_attr(element, "rule", "greaterThan")
    return SimulationTimeCondition(value=value, rule=rule)


def parse_time_headway_condition(element: ET.Element) -> Optional[TimeHeadwayCondition]:
    """TimeHeadwayConditionをパース"""
    if element is None:
        return None
    entity_ref = _get_attr(element, "entityRef", "")
    value = _get_attr(element, "value", "")
    freespace = _get_attr_bool(element, "freespace", False)
    coordinate_system = _get_attr(element, "coordinateSystem", "entity")
    relative_distance_type = _get_attr(element, "relativeDistanceType", "longitudinal")
    rule = _get_attr(element, "rule", "greaterThan")
    if not entity_ref or not value:
        return None
    return TimeHeadwayCondition(
        entity_ref=entity_ref,
        value=value,
        freespace=freespace,
        coordinate_system=coordinate_system,
        relative_distance_type=relative_distance_type,
        rule=rule
    )


def parse_offroad_condition(element: ET.Element) -> Optional[OffroadCondition]:
    """OffroadConditionをパース"""
    if element is None:
        return None
    duration = _get_attr_float(element, "duration", 0.0)
    return OffroadCondition(duration=duration)


def parse_traveled_distance_condition(element: ET.Element) -> Optional[TraveledDistanceCondition]:
    """TraveledDistanceConditionをパース"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    return TraveledDistanceCondition(value=value)


def parse_time_to_collision_condition(element: ET.Element) -> Optional[TimeToCollisionCondition]:
    """TimeToCollisionConditionをパース"""
    if element is None:
        return None
    
    value = _get_attr_float(element, "value", 0.0)
    freespace = _get_attr_bool(element, "freespace", True)
    coordinate_system = _get_attr(element, "coordinateSystem", "entity")
    relative_distance_type = _get_attr(element, "relativeDistanceType", "longitudinal")
    rule = _get_attr(element, "rule", "lessThan")
    
    ns = _detect_namespace(element)
    target_elem = element.find(f"./{ns}TimeToCollisionConditionTarget/{ns}EntityRef")
    target_entity_ref = _get_attr(target_elem, "entityRef", "") if target_elem is not None else None
    
    return TimeToCollisionCondition(
        value=value,
        freespace=freespace,
        coordinate_system=coordinate_system,
        relative_distance_type=relative_distance_type,
        rule=rule,
        target_entity_ref=target_entity_ref,
    )


def parse_end_of_road_condition(element: ET.Element) -> Optional[EndOfRoadCondition]:
    """EndOfRoadConditionをパース"""
    if element is None:
        return None
    
    duration = _get_attr_float(element, "duration", 0.0)
    return EndOfRoadCondition(duration=duration)


def parse_collision_condition(element: ET.Element) -> Optional[CollisionCondition]:
    """CollisionConditionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    
    # EntityRef要素またはByType要素（choice）
    entity_ref = None
    by_object_type = None
    
    entity_ref_elem = element.find(f"./{ns}EntityRef")
    if entity_ref_elem is not None:
        entity_ref = _get_attr(entity_ref_elem, "entityRef", "")
        if not entity_ref:
            entity_ref = None
    
    by_type_elem = element.find(f"./{ns}ByType")
    if by_type_elem is not None:
        obj_type = _get_attr(by_type_elem, "type", "")
        if obj_type:
            by_object_type = {"type": obj_type}
    
    if entity_ref is None and by_object_type is None:
        return None
    
    return CollisionCondition(
        entity_ref=entity_ref,
        by_object_type=by_object_type,
    )


def parse_reach_position_condition(element: ET.Element) -> Optional[ReachPositionCondition]:
    """ReachPositionConditionをパース"""
    if element is None:
        return None
    
    tolerance = _get_attr_float(element, "tolerance", 0.0)
    
    ns = _detect_namespace(element)
    position_container = element.find(f"./{ns}Position")
    position = parse_position(position_container) if position_container is not None else None
    
    return ReachPositionCondition(tolerance=tolerance, position=position)


def parse_parameter_condition(element: ET.Element) -> Optional[ParameterCondition]:
    """ParameterConditionをパース"""
    if element is None:
        return None
    parameter_ref = _get_attr(element, "parameterRef", "")
    value = _get_attr_float(element, "value", 0.0)
    rule = _get_attr(element, "rule", "greaterThan")
    if not parameter_ref:
        return None
    return ParameterCondition(
        parameter_ref=parameter_ref,
        value=value,
        rule=rule
    )


def parse_storyboard_element_state_condition(element: ET.Element) -> Optional[StoryboardElementStateCondition]:
    """StoryboardElementStateConditionをパース"""
    if element is None:
        return None
    storyboard_element_type = _get_attr(element, "storyboardElementType", "")
    storyboard_element_ref = _get_attr(element, "storyboardElementRef", "")
    state = _get_attr(element, "state", "")
    if not storyboard_element_type or not storyboard_element_ref or not state:
        return None
    return StoryboardElementStateCondition(
        storyboard_element_type=storyboard_element_type,
        storyboard_element_ref=storyboard_element_ref,
        state=state
    )


def parse_time_of_day_condition(element: ET.Element) -> Optional[TimeOfDayCondition]:
    """TimeOfDayConditionをパース"""
    if element is None:
        return None
    date_time = _get_attr(element, "dateTime", "")
    rule = _get_attr(element, "rule", "greaterThan")
    if not date_time:
        return None
    return TimeOfDayCondition(date_time=date_time, rule=rule)


def parse_user_defined_value_condition(element: ET.Element) -> Optional[UserDefinedValueCondition]:
    """UserDefinedValueConditionをパース"""
    if element is None:
        return None
    name = _get_attr(element, "name", "")
    value = _get_attr(element, "value", "")
    rule = _get_attr(element, "rule", "greaterThan")
    if not name or not value:
        return None
    return UserDefinedValueCondition(name=name, value=value, rule=rule)


def parse_traffic_signal_condition(element: ET.Element) -> Optional[TrafficSignalCondition]:
    """TrafficSignalConditionをパース"""
    if element is None:
        return None
    name = _get_attr(element, "name", "")
    state = _get_attr(element, "state", "")
    if not name or not state:
        return None
    return TrafficSignalCondition(name=name, state=state)


def parse_traffic_signal_controller_condition(element: ET.Element) -> Optional[TrafficSignalControllerCondition]:
    """TrafficSignalControllerConditionをパース"""
    if element is None:
        return None
    traffic_signal_controller_ref = _get_attr(element, "trafficSignalControllerRef", "")
    phase = _get_attr(element, "phase", "")
    if not traffic_signal_controller_ref or not phase:
        return None
    return TrafficSignalControllerCondition(
        traffic_signal_controller_ref=traffic_signal_controller_ref,
        phase=phase
    )


def parse_variable_condition(element: ET.Element) -> Optional[VariableCondition]:
    """VariableConditionをパース"""
    if element is None:
        return None
    variable_ref = _get_attr(element, "variableRef", "")
    value = _get_attr(element, "value", "")
    rule = _get_attr(element, "rule", "greaterThan")
    if not variable_ref or not value:
        return None
    return VariableCondition(variable_ref=variable_ref, value=value, rule=rule)


def parse_acceleration_condition(element: ET.Element) -> Optional[AccelerationCondition]:
    """AccelerationConditionをパース"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    rule = _get_attr(element, "rule", "greaterThan")
    direction = _get_attr(element, "direction", None)
    return AccelerationCondition(value=value, rule=rule, direction=direction)


def parse_stand_still_condition(element: ET.Element) -> Optional[StandStillCondition]:
    """StandStillConditionをパース"""
    if element is None:
        return None
    duration = _get_attr_float(element, "duration", 0.0)
    return StandStillCondition(duration=duration)


def parse_speed_condition(element: ET.Element) -> Optional[SpeedCondition]:
    """SpeedConditionをパース"""
    if element is None:
        return None
    value = _get_attr_float(element, "value", 0.0)
    rule = _get_attr(element, "rule", "greaterThan")
    direction = _get_attr(element, "direction", None)
    return SpeedCondition(value=value, rule=rule, direction=direction)


def parse_relative_speed_condition(element: ET.Element) -> Optional[RelativeSpeedCondition]:
    """RelativeSpeedConditionをパース"""
    if element is None:
        return None
    entity_ref = _get_attr(element, "entityRef", "")
    value = _get_attr_float(element, "value", 0.0)
    rule = _get_attr(element, "rule", "greaterThan")
    direction = _get_attr(element, "direction", None)
    if not entity_ref:
        return None
    return RelativeSpeedCondition(
        entity_ref=entity_ref,
        value=value,
        rule=rule,
        direction=direction
    )


def parse_relative_lane_range(element: ET.Element) -> Optional[RelativeLaneRange]:
    """RelativeLaneRangeをパース"""
    if element is None:
        return None
    from_lane = _get_attr(element, "from", None)
    to_lane = _get_attr(element, "to", None)
    if from_lane is not None:
        try:
            from_lane = int(from_lane)
        except (ValueError, TypeError):
            pass  # パラメータ参照の可能性があるため文字列のまま
    if to_lane is not None:
        try:
            to_lane = int(to_lane)
        except (ValueError, TypeError):
            pass  # パラメータ参照の可能性があるため文字列のまま
    return RelativeLaneRange(from_lane=from_lane, to_lane=to_lane)


def parse_distance_condition(element: ET.Element) -> Optional[DistanceCondition]:
    """DistanceConditionをパース"""
    if element is None:
        return None
    
    value = _get_attr_float(element, "value", 0.0)
    freespace = _get_attr_bool(element, "freespace", True)
    rule = _get_attr(element, "rule", "greaterThan")
    coordinate_system = _get_attr(element, "coordinateSystem", None)
    relative_distance_type = _get_attr(element, "relativeDistanceType", None)
    routing_algorithm = _get_attr(element, "routingAlgorithm", None)
    along_route = _get_attr_bool(element, "alongRoute", None)  # deprecated
    
    ns = _detect_namespace(element)
    position_container = element.find(f"./{ns}Position")
    position = parse_position(position_container) if position_container is not None else None
    
    return DistanceCondition(
        value=value,
        position=position,
        freespace=freespace,
        rule=rule,
        coordinate_system=coordinate_system,
        relative_distance_type=relative_distance_type,
        routing_algorithm=routing_algorithm,
        along_route=along_route
    )


def parse_relative_distance_condition(element: ET.Element) -> Optional[RelativeDistanceCondition]:
    """RelativeDistanceConditionをパース"""
    if element is None:
        return None
    entity_ref = _get_attr(element, "entityRef", "")
    value = _get_attr_float(element, "value", 0.0)
    freespace = _get_attr_bool(element, "freespace", True)
    relative_distance_type = _get_attr(element, "relativeDistanceType", "longitudinal")
    rule = _get_attr(element, "rule", "greaterThan")
    coordinate_system = _get_attr(element, "coordinateSystem", None)
    routing_algorithm = _get_attr(element, "routingAlgorithm", None)
    if not entity_ref:
        return None
    return RelativeDistanceCondition(
        entity_ref=entity_ref,
        value=value,
        freespace=freespace,
        relative_distance_type=relative_distance_type,
        rule=rule,
        coordinate_system=coordinate_system,
        routing_algorithm=routing_algorithm
    )


def parse_relative_clearance_condition(element: ET.Element) -> Optional[RelativeClearanceCondition]:
    """RelativeClearanceConditionをパース"""
    if element is None:
        return None
    
    opposite_lanes = _get_attr_bool(element, "oppositeLanes", False)
    distance_forward = _get_attr_float(element, "distanceForward", None)
    distance_backward = _get_attr_float(element, "distanceBackward", None)
    free_space = _get_attr_bool(element, "freeSpace", True)
    
    ns = _detect_namespace(element)
    relative_lane_ranges = []
    for lane_range_elem in element.findall(f"./{ns}RelativeLaneRange"):
        lane_range = parse_relative_lane_range(lane_range_elem)
        if lane_range is not None:
            relative_lane_ranges.append(lane_range)
    
    entity_refs = []
    for entity_ref_elem in element.findall(f"./{ns}EntityRef"):
        entity_ref = _get_attr(entity_ref_elem, "entityRef", "")
        if entity_ref:
            entity_refs.append(entity_ref)
    
    return RelativeClearanceCondition(
        relative_lane_ranges=relative_lane_ranges,
        entity_refs=entity_refs,
        opposite_lanes=opposite_lanes,
        distance_forward=distance_forward,
        distance_backward=distance_backward,
        free_space=free_space
    )


def parse_by_entity_condition(element: ET.Element) -> Optional[ByEntityCondition]:
    """ByEntityConditionをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    
    triggering_entities = []
    triggering_entities_rule = "any"
    triggering_entities_elem = element.find(f"./{ns}TriggeringEntities")
    if triggering_entities_elem is not None:
        triggering_entities_rule = _get_attr(triggering_entities_elem, "triggeringEntitiesRule", "any")
        for entity_ref_elem in triggering_entities_elem.findall(f"./{ns}EntityRef"):
            entity_ref = _get_attr(entity_ref_elem, "entityRef", "")
            if entity_ref:
                triggering_entities.append(entity_ref)
    
    entity_condition = None
    offroad_condition = None
    traveled_distance_condition = None
    time_to_collision_condition = None
    reach_position_condition = None
    end_of_road_condition = None
    collision_condition = None
    acceleration_condition = None
    stand_still_condition = None
    speed_condition = None
    relative_speed_condition = None
    distance_condition = None
    relative_distance_condition = None
    relative_clearance_condition = None
    
    entity_condition_elem = element.find(f"./{ns}EntityCondition")
    if entity_condition_elem is not None:
        time_headway_elem = entity_condition_elem.find(f"./{ns}TimeHeadwayCondition")
        if time_headway_elem is not None:
            entity_condition = parse_time_headway_condition(time_headway_elem)
        else:
            offroad_elem = entity_condition_elem.find(f"./{ns}OffroadCondition")
            if offroad_elem is not None:
                offroad_condition = parse_offroad_condition(offroad_elem)
            else:
                traveled_elem = entity_condition_elem.find(f"./{ns}TraveledDistanceCondition")
                if traveled_elem is not None:
                    traveled_distance_condition = parse_traveled_distance_condition(traveled_elem)
                else:
                    ttc_elem = entity_condition_elem.find(f"./{ns}TimeToCollisionCondition")
                    if ttc_elem is not None:
                        time_to_collision_condition = parse_time_to_collision_condition(ttc_elem)
                    else:
                        reach_elem = entity_condition_elem.find(f"./{ns}ReachPositionCondition")
                        if reach_elem is not None:
                            reach_position_condition = parse_reach_position_condition(reach_elem)
                        else:
                            end_of_road_elem = entity_condition_elem.find(f"./{ns}EndOfRoadCondition")
                            if end_of_road_elem is not None:
                                end_of_road_condition = parse_end_of_road_condition(end_of_road_elem)
                            else:
                                collision_elem = entity_condition_elem.find(f"./{ns}CollisionCondition")
                                if collision_elem is not None:
                                    collision_condition = parse_collision_condition(collision_elem)
                                else:
                                    acceleration_elem = entity_condition_elem.find(f"./{ns}AccelerationCondition")
                                    if acceleration_elem is not None:
                                        acceleration_condition = parse_acceleration_condition(acceleration_elem)
                                    else:
                                        stand_still_elem = entity_condition_elem.find(f"./{ns}StandStillCondition")
                                        if stand_still_elem is not None:
                                            stand_still_condition = parse_stand_still_condition(stand_still_elem)
                                        else:
                                            speed_elem = entity_condition_elem.find(f"./{ns}SpeedCondition")
                                            if speed_elem is not None:
                                                speed_condition = parse_speed_condition(speed_elem)
                                            else:
                                                relative_speed_elem = entity_condition_elem.find(f"./{ns}RelativeSpeedCondition")
                                                if relative_speed_elem is not None:
                                                    relative_speed_condition = parse_relative_speed_condition(relative_speed_elem)
                                                else:
                                                    distance_elem = entity_condition_elem.find(f"./{ns}DistanceCondition")
                                                    if distance_elem is not None:
                                                        distance_condition = parse_distance_condition(distance_elem)
                                                    else:
                                                        relative_distance_elem = entity_condition_elem.find(f"./{ns}RelativeDistanceCondition")
                                                        if relative_distance_elem is not None:
                                                            relative_distance_condition = parse_relative_distance_condition(relative_distance_elem)
                                                        else:
                                                            relative_clearance_elem = entity_condition_elem.find(f"./{ns}RelativeClearanceCondition")
                                                            if relative_clearance_elem is not None:
                                                                relative_clearance_condition = parse_relative_clearance_condition(relative_clearance_elem)
    
    if (not triggering_entities and entity_condition is None and offroad_condition is None and
        traveled_distance_condition is None and time_to_collision_condition is None and
        reach_position_condition is None and end_of_road_condition is None and
        collision_condition is None and acceleration_condition is None and
        stand_still_condition is None and speed_condition is None and
        relative_speed_condition is None and distance_condition is None and
        relative_distance_condition is None and relative_clearance_condition is None):
        return None
    
    return ByEntityCondition(
        triggering_entities=triggering_entities,
        triggering_entities_rule=triggering_entities_rule,
        entity_condition=entity_condition,
        offroad_condition=offroad_condition,
        traveled_distance_condition=traveled_distance_condition,
        time_to_collision_condition=time_to_collision_condition,
        reach_position_condition=reach_position_condition,
        end_of_road_condition=end_of_road_condition,
        collision_condition=collision_condition,
        acceleration_condition=acceleration_condition,
        stand_still_condition=stand_still_condition,
        speed_condition=speed_condition,
        relative_speed_condition=relative_speed_condition,
        distance_condition=distance_condition,
        relative_distance_condition=relative_distance_condition,
        relative_clearance_condition=relative_clearance_condition,
    )


def parse_condition(element: ET.Element) -> Condition:
    """Conditionをパース（XSD準拠：属性から取得）"""
    if element is None:
        return Condition()
    name = _get_attr(element, "name", "")
    delay = _get_attr_float(element, "delay", 0.0)
    condition_edge = _get_attr(element, "conditionEdge", "rising")
    
    ns = _detect_namespace(element)
    by_value_elem = element.find(f"./{ns}ByValueCondition")
    
    sim_time_condition = None
    parameter_condition = None
    storyboard_element_state_condition = None
    time_of_day_condition = None
    user_defined_value_condition = None
    traffic_signal_condition = None
    traffic_signal_controller_condition = None
    variable_condition = None
    
    if by_value_elem is not None:
        sim_time_elem = by_value_elem.find(f"./{ns}SimulationTimeCondition")
        sim_time_condition = parse_simulation_time_condition(sim_time_elem) if sim_time_elem is not None else None
        
        param_cond_elem = by_value_elem.find(f"./{ns}ParameterCondition")
        parameter_condition = parse_parameter_condition(param_cond_elem) if param_cond_elem is not None else None
        
        storyboard_elem = by_value_elem.find(f"./{ns}StoryboardElementStateCondition")
        storyboard_element_state_condition = parse_storyboard_element_state_condition(storyboard_elem) if storyboard_elem is not None else None
        
        time_of_day_elem = by_value_elem.find(f"./{ns}TimeOfDayCondition")
        time_of_day_condition = parse_time_of_day_condition(time_of_day_elem) if time_of_day_elem is not None else None
        
        user_defined_value_elem = by_value_elem.find(f"./{ns}UserDefinedValueCondition")
        user_defined_value_condition = parse_user_defined_value_condition(user_defined_value_elem) if user_defined_value_elem is not None else None
        
        traffic_signal_elem = by_value_elem.find(f"./{ns}TrafficSignalCondition")
        traffic_signal_condition = parse_traffic_signal_condition(traffic_signal_elem) if traffic_signal_elem is not None else None
        
        traffic_signal_controller_elem = by_value_elem.find(f"./{ns}TrafficSignalControllerCondition")
        traffic_signal_controller_condition = parse_traffic_signal_controller_condition(traffic_signal_controller_elem) if traffic_signal_controller_elem is not None else None
        
        variable_elem = by_value_elem.find(f"./{ns}VariableCondition")
        variable_condition = parse_variable_condition(variable_elem) if variable_elem is not None else None
    
    by_entity_elem = element.find(f"./{ns}ByEntityCondition")
    by_entity_condition = parse_by_entity_condition(by_entity_elem) if by_entity_elem is not None else None
    
    return Condition(
        name=name,
        delay=delay,
        condition_edge=condition_edge,
        simulation_time_condition=sim_time_condition,
        by_entity_condition=by_entity_condition,
        storyboard_element_state_condition=storyboard_element_state_condition,
        parameter_condition=parameter_condition,
        time_of_day_condition=time_of_day_condition,
        user_defined_value_condition=user_defined_value_condition,
        traffic_signal_condition=traffic_signal_condition,
        traffic_signal_controller_condition=traffic_signal_controller_condition,
        variable_condition=variable_condition,
    )


def parse_condition_group(element: ET.Element) -> ConditionGroup:
    """ConditionGroupをパース"""
    if element is None:
        return ConditionGroup(conditions=[])
    ns = _detect_namespace(element)
    conditions = []
    for cond_elem in element.findall(f"./{ns}Condition"):
        conditions.append(parse_condition(cond_elem))
    return ConditionGroup(conditions=conditions)


def parse_start_trigger(element: ET.Element) -> Optional[StartTrigger]:
    """StartTriggerをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    condition_groups = []
    for cg_elem in element.findall(f"./{ns}ConditionGroup"):
        condition_groups.append(parse_condition_group(cg_elem))
    
    if not condition_groups:
        return None
    
    return StartTrigger(condition_groups=condition_groups)


def parse_event(element: ET.Element) -> Event:
    """Eventをパース（XSD準拠：Action要素を正しくパース）"""
    if element is None:
        return Event(name="", priority=Rule.OVERRIDE, actions=[], start_trigger=None)
    name = element.get("name", "")
    priority_str = element.get("priority", "override").lower()
    # "overwrite"も保持（OpenSCENARIO 1.0/1.1の旧形式だが、元の値を保持する）
    try:
        priority = Rule(priority_str)
    except ValueError:
        # デフォルトはoverride
        priority = Rule.OVERRIDE
    
    ns = _detect_namespace(element)
    actions = []
    for action_elem in element.findall(f"./{ns}Action"):
        action = parse_action(action_elem)
        if action is not None:
            actions.append(action)
    
    start_trigger_elem = element.find(f"./{ns}StartTrigger")
    start_trigger = parse_start_trigger(start_trigger_elem)
    
    return Event(
        name=name,
        priority=priority,
        actions=actions,
        start_trigger=start_trigger,
    )


def parse_maneuver(element: ET.Element) -> Maneuver:
    """Maneuverをパース"""
    if element is None:
        return Maneuver(name="", events=[])
    name = element.get("name", "")
    ns = _detect_namespace(element)
    events = []
    for event_elem in element.findall(f"./{ns}Event"):
        events.append(parse_event(event_elem))
    
    return Maneuver(name=name, events=events)


def parse_maneuver_group(element: ET.Element) -> ManeuverGroup:
    """ManeuverGroupをパース（XSD準拠：属性から取得）"""
    if element is None:
        return ManeuverGroup(name="")
    name = _get_attr(element, "name", "")
    max_exec = _get_attr_int(element, "maximumExecutionCount", 1)
    
    ns = _detect_namespace(element)
    actors = []
    select_triggering_entities = False  # デフォルト値（XSD準拠）
    actors_elem = element.find(f"./{ns}Actors")
    if actors_elem is not None:
        select_triggering_entities_attr = actors_elem.get("selectTriggeringEntities")
        if select_triggering_entities_attr is not None:
            select_triggering_entities = _get_attr_bool(actors_elem, "selectTriggeringEntities", False)
        for entity_elem in actors_elem.findall(f"./{ns}EntityRef"):
            entity_ref = entity_elem.get("entityRef", "")
            if entity_ref:
                actors.append(entity_ref)
    
    maneuvers = []
    for maneuver_elem in element.findall(f"./{ns}Maneuver"):
        maneuvers.append(parse_maneuver(maneuver_elem))
    
    return ManeuverGroup(
        name=name,
        maximum_execution_count=max_exec,
        actors=actors,
        select_triggering_entities=select_triggering_entities,
        maneuvers=maneuvers,
    )


def parse_act(element: ET.Element) -> Act:
    """Actをパース"""
    if element is None:
        return Act(name="", maneuver_groups=[], start_trigger=None, stop_trigger=None)
    name = element.get("name", "")
    
    ns = _detect_namespace(element)
    maneuver_groups = []
    for mg_elem in element.findall(f"./{ns}ManeuverGroup"):
        maneuver_groups.append(parse_maneuver_group(mg_elem))
    
    start_trigger_elem = element.find(f"./{ns}StartTrigger")
    start_trigger = parse_start_trigger(start_trigger_elem)
    
    stop_trigger_elem = element.find(f"./{ns}StopTrigger")
    stop_trigger = parse_start_trigger(stop_trigger_elem)  # StopTriggerもStartTriggerと同じ構造
    
    return Act(
        name=name,
        maneuver_groups=maneuver_groups,
        start_trigger=start_trigger,
        stop_trigger=stop_trigger,
    )


def parse_story(element: ET.Element) -> Story:
    """Storyをパース"""
    if element is None:
        return Story(name="", acts=[])
    name = element.get("name", "")
    ns = _detect_namespace(element)
    
    param_decls_elem = element.find(f"./{ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    acts = []
    for act_elem in element.findall(f"./{ns}Act"):
        acts.append(parse_act(act_elem))
    
    return Story(name=name, parameter_declarations=param_decls, acts=acts)


def parse_init(element: ET.Element) -> Init:
    """Initをパース（XSD準拠：Private要素を正しくパース）"""
    if element is None:
        return Init(actions=[])
    ns = _detect_namespace(element)
    privates = []
    for private_elem in element.findall(f"./{ns}Actions/{ns}Private"):
        private = parse_private(private_elem)
        if private is not None:
            privates.append(private)
    
    return Init(actions=privates)


def parse_storyboard(element: ET.Element) -> Storyboard:
    """Storyboardをパース"""
    if element is None:
        return Storyboard()
    ns = _detect_namespace(element)
    init_elem = element.find(f"./{ns}Init")
    init = parse_init(init_elem) if init_elem is not None else None
    
    stories = []
    for story_elem in element.findall(f"./{ns}Story"):
        stories.append(parse_story(story_elem))
    
    stop_trigger_elem = element.find(f"./{ns}StopTrigger")
    stop_trigger = parse_start_trigger(stop_trigger_elem)
    
    return Storyboard(
        init=init,
        stories=stories,
        stop_trigger=stop_trigger,
    )


def parse_center(element: ET.Element) -> Optional[Center]:
    """Centerをパース"""
    if element is None:
        return None
    return Center(
        x=_get_attr_float(element, "x", 0.0),
        y=_get_attr_float(element, "y", 0.0),
        z=_get_attr_float(element, "z", 0.0),
    )


def parse_dimensions(element: ET.Element) -> Optional[Dimensions]:
    """Dimensionsをパース"""
    if element is None:
        return None
    return Dimensions(
        height=_get_attr_float(element, "height", 0.0),
        length=_get_attr_float(element, "length", 0.0),
        width=_get_attr_float(element, "width", 0.0),
    )


def parse_bounding_box(element: ET.Element) -> Optional[BoundingBox]:
    """BoundingBoxをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    center_elem = element.find(f"./{ns}Center")
    dimensions_elem = element.find(f"./{ns}Dimensions")
    
    center = parse_center(center_elem) if center_elem is not None else None
    dimensions = parse_dimensions(dimensions_elem) if dimensions_elem is not None else None
    
    if center is None or dimensions is None:
        return None
    
    return BoundingBox(center=center, dimensions=dimensions)


def parse_performance(element: ET.Element) -> Optional[Performance]:
    """Performanceをパース"""
    if element is None:
        return None
    return Performance(
        max_acceleration=_get_attr_float(element, "maxAcceleration", 0.0),
        max_deceleration=_get_attr_float(element, "maxDeceleration", 0.0),
        max_speed=_get_attr_float(element, "maxSpeed", 0.0),
        max_acceleration_rate=_get_attr_float(element, "maxAccelerationRate", None),
        max_deceleration_rate=_get_attr_float(element, "maxDecelerationRate", None),
    )


def parse_axle(element: ET.Element) -> Optional[Axle]:
    """Axleをパース"""
    if element is None:
        return None
    return Axle(
        max_steering=_get_attr_float(element, "maxSteering", 0.0),
        position_x=_get_attr_float(element, "positionX", 0.0),
        position_z=_get_attr_float(element, "positionZ", 0.0),
        track_width=_get_attr_float(element, "trackWidth", 0.0),
        wheel_diameter=_get_attr_float(element, "wheelDiameter", 0.0),
    )


def parse_axles(element: ET.Element) -> Optional[Axles]:
    """Axlesをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    front_axle_elem = element.find(f"./{ns}FrontAxle")
    rear_axle_elem = element.find(f"./{ns}RearAxle")
    
    front_axle = parse_axle(front_axle_elem) if front_axle_elem is not None else None
    rear_axle = parse_axle(rear_axle_elem) if rear_axle_elem is not None else None
    
    if front_axle is None or rear_axle is None:
        return None
    
    additional_axles = []
    for additional_elem in element.findall(f"./{ns}AdditionalAxle"):
        axle = parse_axle(additional_elem)
        if axle is not None:
            additional_axles.append(axle)
    
    return Axles(
        front_axle=front_axle,
        rear_axle=rear_axle,
        additional_axles=additional_axles,
    )


def parse_vehicle(element: ET.Element) -> Vehicle:
    """Vehicleをパース"""
    if element is None:
        return Vehicle(name="", vehicle_category="car")
    
    name = element.get("name", "")
    category = element.get("vehicleCategory", "car")
    role = element.get("role")
    mass_attr = element.get("mass")
    mass = None
    if mass_attr is not None:
        try:
            mass = float(mass_attr)
        except (ValueError, TypeError):
            mass = mass_attr  # パラメータ参照の場合は文字列として保持
    model3d = element.get("model3d")
    
    ns = _detect_namespace(element)
    param_decls_elem = element.find(f"./{ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    bounding_box_elem = element.find(f"./{ns}BoundingBox")
    bounding_box = parse_bounding_box(bounding_box_elem) if bounding_box_elem is not None else None
    
    performance_elem = element.find(f"./{ns}Performance")
    performance = parse_performance(performance_elem) if performance_elem is not None else None
    
    axles_elem = element.find(f"./{ns}Axles")
    axles = parse_axles(axles_elem) if axles_elem is not None else None
    
    properties_elem = element.find(f"./{ns}Properties")
    properties = parse_properties(properties_elem) if properties_elem is not None else None
    
    return Vehicle(
        name=name,
        vehicle_category=category,
        role=role,
        mass=mass,
        model3d=model3d,
        parameter_declarations=param_decls,
        bounding_box=bounding_box,
        performance=performance,
        axles=axles,
        properties=properties,
    )


def parse_parameter_assignment(element: ET.Element) -> Optional[ParameterAssignment]:
    """ParameterAssignmentをパース"""
    if element is None:
        return None
    parameter_ref = _get_attr(element, "parameterRef", "")
    value = _get_attr(element, "value", "")
    if not parameter_ref or not value:
        return None
    return ParameterAssignment(parameter_ref=parameter_ref, value=value)


def parse_parameter_assignments(element: ET.Element) -> Optional[ParameterAssignments]:
    """ParameterAssignmentsをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    assignment_elems = element.findall(f"./{ns}ParameterAssignment")
    assignments = []
    for assignment_elem in assignment_elems:
        assignment = parse_parameter_assignment(assignment_elem)
        if assignment is not None:
            assignments.append(assignment)
    if not assignments:
        return None
    return ParameterAssignments(assignments=assignments)


def parse_catalog_reference(element: ET.Element) -> Optional[CatalogReference]:
    """CatalogReferenceをパース"""
    if element is None:
        return None
    catalog_name = _get_attr(element, "catalogName", "")
    entry_name = _get_attr(element, "entryName", "")
    if not catalog_name or not entry_name:
        return None
    
    ns = _detect_namespace(element)
    param_assignments_elem = element.find(f"./{ns}ParameterAssignments")
    parameter_assignments = parse_parameter_assignments(param_assignments_elem) if param_assignments_elem is not None else None
    
    return CatalogReference(catalog_name=catalog_name, entry_name=entry_name, parameter_assignments=parameter_assignments)


def parse_pedestrian(element: ET.Element) -> Optional[Pedestrian]:
    """Pedestrianをパース"""
    if element is None:
        return None
    name = _get_attr(element, "name", "")
    if not name:
        return None
    
    mass_attr = element.get("mass")
    if mass_attr is None:
        return None  # massは必須属性
    try:
        mass = float(mass_attr)
    except (ValueError, TypeError):
        mass = mass_attr  # パラメータ参照の場合は文字列として保持
    
    model = _get_attr(element, "model", None)
    pedestrian_category = _get_attr(element, "pedestrianCategory", "pedestrian")
    model3d = _get_attr(element, "model3d", None)
    role = _get_attr(element, "role", None)
    
    ns = _detect_namespace(element)
    param_decls_elem = element.find(f"./{ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    bounding_box_elem = element.find(f"./{ns}BoundingBox")
    bounding_box = parse_bounding_box(bounding_box_elem) if bounding_box_elem is not None else None
    
    properties_elem = element.find(f"./{ns}Properties")
    properties = parse_properties(properties_elem) if properties_elem is not None else None
    
    return Pedestrian(
        name=name,
        mass=mass,
        model=model,
        pedestrian_category=pedestrian_category,
        model3d=model3d,
        role=role,
        parameter_declarations=param_decls,
        bounding_box=bounding_box,
        properties=properties,
    )


def parse_properties(element: ET.Element) -> Optional[Properties]:
    """Propertiesをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    properties_list = []
    for prop_elem in element.findall(f"./{ns}Property"):
        name = _get_attr(prop_elem, "name", "")
        value = _get_attr(prop_elem, "value", "")
        if name:
            properties_list.append(Property(name=name, value=value))
    
    # Properties要素が存在する場合は、空のリストでもPropertiesオブジェクトを返す
    # （XSDではProperties要素は必須だが、中身は空でもOK）
    return Properties(properties=properties_list)


def parse_controller(element: ET.Element) -> Optional[Controller]:
    """Controllerをパース"""
    if element is None:
        return None
    
    name = _get_attr(element, "name", "")
    if not name:
        return None
    
    ns = _detect_namespace(element)
    properties_elem = element.find(f"./{ns}Properties")
    properties = parse_properties(properties_elem) if properties_elem is not None else None
    
    return Controller(name=name, properties=properties)


def parse_object_controller(element: ET.Element) -> Optional[ObjectController]:
    """ObjectControllerをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    controller_elem = element.find(f"./{ns}Controller")
    catalog_ref_elem = element.find(f"./{ns}CatalogReference")
    
    controller = parse_controller(controller_elem) if controller_elem is not None else None
    catalog_reference = parse_catalog_reference(catalog_ref_elem) if catalog_ref_elem is not None else None
    
    if controller is None and catalog_reference is None:
        return None
    
    return ObjectController(controller=controller, catalog_reference=catalog_reference)


def parse_scenario_object(element: ET.Element) -> ScenarioObject:
    """ScenarioObjectをパース"""
    if element is None:
        return ScenarioObject(name="")
    name = element.get("name", "")
    ns = _detect_namespace(element)
    vehicle_elem = element.find(f"./{ns}Vehicle")
    vehicle = parse_vehicle(vehicle_elem) if vehicle_elem is not None else None
    
    pedestrian_elem = element.find(f"./{ns}Pedestrian")
    pedestrian = parse_pedestrian(pedestrian_elem) if pedestrian_elem is not None else None
    
    catalog_ref_elem = element.find(f"./{ns}CatalogReference")
    catalog_reference = parse_catalog_reference(catalog_ref_elem) if catalog_ref_elem is not None else None
    
    object_controller_elem = element.find(f"./{ns}ObjectController")
    object_controller = parse_object_controller(object_controller_elem) if object_controller_elem is not None else None
    
    return ScenarioObject(
        name=name,
        vehicle=vehicle,
        pedestrian=pedestrian,
        catalog_reference=catalog_reference,
        object_controller=object_controller
    )


def parse_entities(element: ET.Element) -> Entities:
    """Entitiesをパース"""
    if element is None:
        return Entities(scenario_objects=[])
    ns = _detect_namespace(element)
    scenario_objects = []
    for obj_elem in element.findall(f"./{ns}ScenarioObject"):
        scenario_objects.append(parse_scenario_object(obj_elem))
    
    return Entities(scenario_objects=scenario_objects)


def parse_xml(file_path: str) -> ScenarioDefinition:
    """XMLファイルをパースしてScenarioDefinitionを返す（グローバル変数を変更しない）"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 名前空間の処理（ローカル変数として保持、グローバル変数は変更しない）
    local_osc_ns = _detect_namespace(root)
    
    # 名前空間を使用して要素を検索（ローカル変数を使用）
    file_header_elem = root.find(f"./{local_osc_ns}FileHeader")
    file_header = parse_file_header(file_header_elem) if file_header_elem is not None else None
    
    param_decls_elem = root.find(f"./{local_osc_ns}ParameterDeclarations")
    param_decls = parse_parameter_declarations(param_decls_elem) if param_decls_elem is not None else None
    
    variable_decls_elem = root.find(f"./{local_osc_ns}VariableDeclarations")
    variable_decls = parse_variable_declarations(variable_decls_elem) if variable_decls_elem is not None else None
    
    catalog_locs_elem = root.find(f"./{local_osc_ns}CatalogLocations")
    catalog_locs = parse_catalog_locations(catalog_locs_elem) if catalog_locs_elem is not None else None
    
    road_network_elem = root.find(f"./{local_osc_ns}RoadNetwork")
    road_network = parse_road_network(road_network_elem) if road_network_elem is not None else None
    
    entities_elem = root.find(f"./{local_osc_ns}Entities")
    entities = parse_entities(entities_elem) if entities_elem is not None else None
    
    storyboard_elem = root.find(f"./{local_osc_ns}Storyboard")
    storyboard = parse_storyboard(storyboard_elem) if storyboard_elem is not None else None
    
    param_value_dist_elem = root.find(f"./{local_osc_ns}ParameterValueDistribution")
    param_value_dist = parse_parameter_value_distribution(param_value_dist_elem) if param_value_dist_elem is not None else None
    
    return ScenarioDefinition(
        file_header=file_header,
        parameter_declarations=param_decls,
        variable_declarations=variable_decls,
        catalog_locations=catalog_locs,
        road_network=road_network,
        entities=entities,
        storyboard=storyboard,
        parameter_value_distribution=param_value_dist,
    )


def parse_scenario_file(element: ET.Element) -> Optional['ScenarioFile']:
    """ScenarioFileをパース"""
    if element is None:
        return None
    from osc_editor.core.model import ScenarioFile
    filepath = _get_attr(element, "filepath", "")
    if not filepath:
        return None
    return ScenarioFile(filepath=filepath)


def parse_parameter_value_set(element: ET.Element) -> Optional['ParameterValueSet']:
    """ParameterValueSetをパース"""
    if element is None:
        return None
    from osc_editor.core.model import ParameterValueSet, ParameterAssignment
    ns = _detect_namespace(element)
    param_assignments = []
    for assignment_elem in element.findall(f"./{ns}ParameterAssignment"):
        param_assignments.append(parse_parameter_assignment(assignment_elem))
    return ParameterValueSet(parameter_assignments=param_assignments)


def parse_value_set_distribution(element: ET.Element) -> Optional['ValueSetDistribution']:
    """ValueSetDistributionをパース"""
    if element is None:
        return None
    from osc_editor.core.model import ValueSetDistribution
    ns = _detect_namespace(element)
    param_value_sets = []
    for value_set_elem in element.findall(f"./{ns}ParameterValueSet"):
        value_set = parse_parameter_value_set(value_set_elem)
        if value_set:
            param_value_sets.append(value_set)
    return ValueSetDistribution(parameter_value_sets=param_value_sets)


def parse_deterministic_multi_parameter_distribution(element: ET.Element) -> Optional['DeterministicMultiParameterDistribution']:
    """DeterministicMultiParameterDistributionをパース"""
    if element is None:
        return None
    from osc_editor.core.model import DeterministicMultiParameterDistribution
    ns = _detect_namespace(element)
    value_set_dist_elem = element.find(f"./{ns}ValueSetDistribution")
    value_set_dist = parse_value_set_distribution(value_set_dist_elem) if value_set_dist_elem is not None else None
    return DeterministicMultiParameterDistribution(value_set_distribution=value_set_dist)


def parse_distribution_set(element: ET.Element) -> Optional['DistributionSet']:
    """DistributionSetをパース"""
    if element is None:
        return None
    from osc_editor.core.model import DistributionSet
    ns = _detect_namespace(element)
    elements = []
    for elem in element.findall(f"./{ns}Element"):
        value = _get_attr(elem, "value", "")
        if value:
            elements.append({"value": value})
    return DistributionSet(elements=elements)


def parse_distribution_range(element: ET.Element) -> Optional['DistributionRange']:
    """DistributionRangeをパース"""
    if element is None:
        return None
    from osc_editor.core.model import DistributionRange, Range
    step_width = _get_attr_float(element, "stepWidth", 0.0)
    range_elem = element.find(f"./{_detect_namespace(element)}Range")
    range_obj = None
    if range_elem is not None:
        lower_limit = _get_attr_float(range_elem, "lowerLimit", 0.0)
        upper_limit = _get_attr_float(range_elem, "upperLimit", 0.0)
        range_obj = Range(lower_limit=lower_limit, upper_limit=upper_limit)
    return DistributionRange(step_width=step_width, range=range_obj)


def parse_deterministic_single_parameter_distribution(element: ET.Element) -> Optional['DeterministicSingleParameterDistribution']:
    """DeterministicSingleParameterDistributionをパース"""
    if element is None:
        return None
    from osc_editor.core.model import DeterministicSingleParameterDistribution
    parameter_name = _get_attr(element, "parameterName", "")
    if not parameter_name:
        return None
    ns = _detect_namespace(element)
    dist_set_elem = element.find(f"./{ns}DistributionSet")
    dist_set = parse_distribution_set(dist_set_elem) if dist_set_elem is not None else None
    dist_range_elem = element.find(f"./{ns}DistributionRange")
    dist_range = parse_distribution_range(dist_range_elem) if dist_range_elem is not None else None
    return DeterministicSingleParameterDistribution(
        parameter_name=parameter_name,
        distribution_set=dist_set,
        distribution_range=dist_range
    )


def parse_deterministic(element: ET.Element) -> Optional['Deterministic']:
    """Deterministicをパース"""
    if element is None:
        return None
    from osc_editor.core.model import Deterministic
    ns = _detect_namespace(element)
    multi_dist_elem = element.find(f"./{ns}DeterministicMultiParameterDistribution")
    multi_dist = parse_deterministic_multi_parameter_distribution(multi_dist_elem) if multi_dist_elem is not None else None
    single_dists = []
    for single_dist_elem in element.findall(f"./{ns}DeterministicSingleParameterDistribution"):
        single_dist = parse_deterministic_single_parameter_distribution(single_dist_elem)
        if single_dist:
            single_dists.append(single_dist)
    return Deterministic(
        deterministic_multi_parameter_distribution=multi_dist,
        deterministic_single_parameter_distributions=single_dists
    )


def parse_parameter_value_distribution(element: ET.Element) -> Optional['ParameterValueDistribution']:
    """ParameterValueDistributionをパース"""
    if element is None:
        return None
    from osc_editor.core.model import ParameterValueDistribution
    ns = _detect_namespace(element)
    scenario_file_elem = element.find(f"./{ns}ScenarioFile")
    scenario_file = parse_scenario_file(scenario_file_elem) if scenario_file_elem is not None else None
    deterministic_elem = element.find(f"./{ns}Deterministic")
    deterministic = parse_deterministic(deterministic_elem) if deterministic_elem is not None else None
    return ParameterValueDistribution(
        scenario_file=scenario_file,
        deterministic=deterministic
    )


