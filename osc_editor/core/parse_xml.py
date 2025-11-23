"""XML → モデルへの変換"""

import xml.etree.ElementTree as ET
from typing import Optional, Union
from osc_editor.core.model import (
    ScenarioDefinition,
    FileHeader,
    ParameterDeclarations,
    ParameterDeclaration,
    RoadNetwork,
    CatalogLocations,
    Entities,
    ScenarioObject,
    Vehicle,
    Pedestrian,
    CatalogReference,
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
    RoutingAction,
    FollowTrajectoryAction,
    Trajectory,
    Polyline,
    Clothoid,
    Nurbs,
    Vertex,
    ControlPoint,
    TimeReference,
    ActivateControllerAction,
    SpeedAction,
    RelativeTargetSpeed,
    LaneChangeAction,
    LaneOffsetAction,
    LaneOffsetActionDynamics,
    VisibilityAction,
    SynchronizeAction,
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
    GlobalAction,
    ParameterAction,
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
    
    return CatalogLocations(
        vehicle_catalog=vehicle_catalog,
        route_catalog=route_catalog,
        controller_catalog=controller_catalog
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
        from_lane_elem = in_route_position_elem.find(f"./{ns}FromLaneCoordinates")
        if from_lane_elem is not None:
            in_route_position = {
                "pathS": _get_attr_float(from_lane_elem, "pathS", 0.0),
                "laneId": _get_attr(from_lane_elem, "laneId", ""),
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
    
    # value属性の取得（必須属性だが、存在しない場合はNoneとする）
    value_attr = element.get("value")
    if value_attr is None:
        value = None
    else:
        try:
            value = float(value_attr)
        except (ValueError, TypeError):
            value = None
    
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
            target_lane_absolute = _get_attr_int(absolute_target_elem, "value", 0)
    
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
    
    # LaneOffsetTargetからAbsoluteTargetLaneOffsetのvalue属性を取得
    target_elem = element.find(f"./{ns}LaneOffsetTarget/{ns}AbsoluteTargetLaneOffset")
    if target_elem is None:
        return None
    
    target_offset = _get_attr_float(target_elem, "value", 0.0)
    
    return LaneOffsetAction(
        target_offset=target_offset,
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


def parse_follow_trajectory_action(element: ET.Element) -> Optional[FollowTrajectoryAction]:
    """FollowTrajectoryActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    trajectory_elem = element.find(f"./{ns}Trajectory")
    trajectory = parse_trajectory(trajectory_elem) if trajectory_elem is not None else None
    
    if trajectory is None:
        return None
    
    time_ref_elem = element.find(f"./{ns}TimeReference")
    time_reference = parse_time_reference(time_ref_elem) if time_ref_elem is not None else None
    
    following_mode_elem = element.find(f"./{ns}TrajectoryFollowingMode")
    following_mode = _get_attr(following_mode_elem, "followingMode", "follow") if following_mode_elem is not None else "follow"
    
    return FollowTrajectoryAction(
        trajectory=trajectory,
        time_reference=time_reference,
        following_mode=following_mode,
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


def parse_routing_action(element: ET.Element) -> Optional[RoutingAction]:
    """RoutingActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    assign_route_elem = element.find(f"./{ns}AssignRouteAction")
    follow_trajectory_elem = element.find(f"./{ns}FollowTrajectoryAction")
    
    assign_route_action = parse_assign_route_action(assign_route_elem) if assign_route_elem is not None else None
    follow_trajectory_action = parse_follow_trajectory_action(follow_trajectory_elem) if follow_trajectory_elem is not None else None
    
    if assign_route_action is None and follow_trajectory_action is None:
        return None
    
    return RoutingAction(
        assign_route_action=assign_route_action,
        follow_trajectory_action=follow_trajectory_action,
    )


def parse_activate_controller_action(element: ET.Element) -> Optional[ActivateControllerAction]:
    """ActivateControllerActionをパース"""
    if element is None:
        return None
    
    longitudinal = _get_attr_bool(element, "longitudinal", True)
    lateral = _get_attr_bool(element, "lateral", True)
    
    return ActivateControllerAction(longitudinal=longitudinal, lateral=lateral)


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
            final_speed = {"type": "AbsoluteSpeed", "value": abs_speed_value}
        else:
            rel_speed_elem = final_speed_elem.find(f"./{ns}RelativeSpeedToMaster")
            if rel_speed_elem is not None:
                speed_target_value_type = _get_attr(rel_speed_elem, "speedTargetValueType", "delta")
                value = _get_attr_float(rel_speed_elem, "value", None)
                final_speed = {
                    "type": "RelativeSpeedToMaster",
                    "speedTargetValueType": speed_target_value_type,
                    "value": value,
                }
    
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
    speed_elem = element.find(f"./{ns}LongitudinalAction/{ns}SpeedAction")
    lane_change_elem = element.find(f"./{ns}LateralAction/{ns}LaneChangeAction")
    lane_offset_elem = element.find(f"./{ns}LateralAction/{ns}LaneOffsetAction")
    routing_elem = element.find(f"./{ns}RoutingAction")
    activate_controller_elem = element.find(f"./{ns}ActivateControllerAction")
    visibility_elem = element.find(f"./{ns}VisibilityAction")
    synchronize_elem = element.find(f"./{ns}SynchronizeAction")
    appearance_elem = element.find(f"./{ns}AppearanceAction")
    
    teleport_action = parse_teleport_action(teleport_elem) if teleport_elem is not None else None
    speed_action = parse_speed_action(speed_elem) if speed_elem is not None else None
    lane_change_action = parse_lane_change_action(lane_change_elem) if lane_change_elem is not None else None
    lane_offset_action = parse_lane_offset_action(lane_offset_elem) if lane_offset_elem is not None else None
    routing_action = parse_routing_action(routing_elem) if routing_elem is not None else None
    activate_controller_action = parse_activate_controller_action(activate_controller_elem) if activate_controller_elem is not None else None
    visibility_action = parse_visibility_action(visibility_elem) if visibility_elem is not None else None
    synchronize_action = parse_synchronize_action(synchronize_elem) if synchronize_elem is not None else None
    appearance_action = parse_appearance_action(appearance_elem) if appearance_elem is not None else None
    
    if (teleport_action is None and speed_action is None and lane_change_action is None and 
        lane_offset_action is None and routing_action is None and activate_controller_action is None and
        visibility_action is None and synchronize_action is None and appearance_action is None):
        return None
    
    return PrivateAction(
        teleport_action=teleport_action,
        speed_action=speed_action,
        lane_change_action=lane_change_action,
        lane_offset_action=lane_offset_action,
        routing_action=routing_action,
        activate_controller_action=activate_controller_action,
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


def parse_global_action(element: ET.Element) -> Optional[GlobalAction]:
    """GlobalActionをパース"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    parameter_action_elem = element.find(f"./{ns}ParameterAction")
    parameter_action = parse_parameter_action(parameter_action_elem) if parameter_action_elem is not None else None
    
    if parameter_action is None:
        return None
    
    return GlobalAction(parameter_action=parameter_action)


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
    
    if (not triggering_entities and entity_condition is None and offroad_condition is None and
        traveled_distance_condition is None and time_to_collision_condition is None and
        reach_position_condition is None and end_of_road_condition is None and
        collision_condition is None):
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
    
    if by_value_elem is not None:
        sim_time_elem = by_value_elem.find(f"./{ns}SimulationTimeCondition")
        sim_time_condition = parse_simulation_time_condition(sim_time_elem) if sim_time_elem is not None else None
        
        param_cond_elem = by_value_elem.find(f"./{ns}ParameterCondition")
        parameter_condition = parse_parameter_condition(param_cond_elem) if param_cond_elem is not None else None
        
        storyboard_elem = by_value_elem.find(f"./{ns}StoryboardElementStateCondition")
        storyboard_element_state_condition = parse_storyboard_element_state_condition(storyboard_elem) if storyboard_elem is not None else None
    
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
    select_triggering_entities = None
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


def parse_catalog_reference(element: ET.Element) -> Optional[CatalogReference]:
    """CatalogReferenceをパース"""
    if element is None:
        return None
    catalog_name = _get_attr(element, "catalogName", "")
    entry_name = _get_attr(element, "entryName", "")
    if not catalog_name or not entry_name:
        return None
    return CatalogReference(catalog_name=catalog_name, entry_name=entry_name)


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
    
    catalog_locs_elem = root.find(f"./{local_osc_ns}CatalogLocations")
    catalog_locs = parse_catalog_locations(catalog_locs_elem) if catalog_locs_elem is not None else None
    
    road_network_elem = root.find(f"./{local_osc_ns}RoadNetwork")
    road_network = parse_road_network(road_network_elem) if road_network_elem is not None else None
    
    entities_elem = root.find(f"./{local_osc_ns}Entities")
    entities = parse_entities(entities_elem) if entities_elem is not None else None
    
    storyboard_elem = root.find(f"./{local_osc_ns}Storyboard")
    storyboard = parse_storyboard(storyboard_elem) if storyboard_elem is not None else None
    
    return ScenarioDefinition(
        file_header=file_header,
        parameter_declarations=param_decls,
        catalog_locations=catalog_locs,
        road_network=road_network,
        entities=entities,
        storyboard=storyboard,
    )


