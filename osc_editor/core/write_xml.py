"""モデル → XMLへの変換"""

import xml.etree.ElementTree as ET
from typing import Optional
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
    DynamicsShape,
    StartTrigger,
    ConditionGroup,
    Condition,
    SimulationTimeCondition,
    ByEntityCondition,
    TimeHeadwayCondition,
    BoundingBox,
    Center,
    Dimensions,
    Performance,
    Axles,
    Axle,
    Route,
    Waypoint,
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
)


# OpenSCENARIO名前空間
OSC_NS = "http://www.asam.net/xml"
OSC_NS_MAP = {"osc": OSC_NS}


def _create_element(tag: str, parent: Optional[ET.Element] = None) -> ET.Element:
    """要素を作成（名前空間なし）"""
    if parent is None:
        elem = ET.Element(tag)
    else:
        elem = ET.SubElement(parent, tag)
    return elem


def _set_text(elem: ET.Element, tag: str, value: str):
    """子要素にテキストを設定"""
    child = _create_element(tag, elem)
    child.text = str(value)


def _set_float(elem: ET.Element, tag: str, value: float):
    """子要素に浮動小数点数を設定"""
    _set_text(elem, tag, value)


def _set_int(elem: ET.Element, tag: str, value: int):
    """子要素に整数を設定"""
    _set_text(elem, tag, value)


def write_file_header(parent: ET.Element, file_header: FileHeader):
    """FileHeaderをXMLに書き込み"""
    elem = _create_element("FileHeader", parent)
    # revMajorとrevMinorは属性として設定（必須）
    elem.set("revMajor", str(file_header.rev_major))
    elem.set("revMinor", str(file_header.rev_minor))
    # author、date、descriptionも属性として設定
    if file_header.author:
        elem.set("author", file_header.author)
    if file_header.date:
        elem.set("date", file_header.date)
    if file_header.description:
        elem.set("description", file_header.description)


def write_parameter_declarations(parent: ET.Element, param_decls: ParameterDeclarations):
    """ParameterDeclarationsをXMLに書き込み"""
    if not param_decls.parameters:
        return
    
    elem = _create_element("ParameterDeclarations", parent)
    for param in param_decls.parameters:
        param_elem = _create_element("ParameterDeclaration", elem)
        param_elem.set("name", param.name)
        param_elem.set("parameterType", param.parameter_type)
        # value属性は必須（XSD準拠）
        if not param.value:
            raise ValueError(f"ParameterDeclaration '{param.name}' must have a value attribute")
        param_elem.set("value", param.value)


def write_road_network(parent: ET.Element, road_network: RoadNetwork):
    """RoadNetworkをXMLに書き込み"""
    elem = _create_element("RoadNetwork", parent)
    
    if road_network.logic_file:
        logic_elem = _create_element("LogicFile", elem)
        logic_elem.set("filepath", road_network.logic_file)
    
    if road_network.scene_graph_file:
        scene_elem = _create_element("SceneGraphFile", elem)
        scene_elem.set("filepath", road_network.scene_graph_file)


def write_catalog_locations(parent: ET.Element, catalog_locs: CatalogLocations):
    """CatalogLocationsをXMLに書き込み"""
    elem = _create_element("CatalogLocations", parent)
    if catalog_locs.vehicle_catalog:
        vehicle_catalog_elem = _create_element("VehicleCatalog", elem)
        directory_elem = _create_element("Directory", vehicle_catalog_elem)
        directory_elem.set("path", catalog_locs.vehicle_catalog)
    
    if catalog_locs.route_catalog:
        route_catalog_elem = _create_element("RouteCatalog", elem)
        directory_elem = _create_element("Directory", route_catalog_elem)
        directory_elem.set("path", catalog_locs.route_catalog)
    
    if catalog_locs.controller_catalog:
        controller_catalog_elem = _create_element("ControllerCatalog", elem)
        directory_elem = _create_element("Directory", controller_catalog_elem)
        directory_elem.set("path", catalog_locs.controller_catalog)
    
    if catalog_locs.pedestrian_catalog:
        pedestrian_catalog_elem = _create_element("PedestrianCatalog", elem)
        directory_elem = _create_element("Directory", pedestrian_catalog_elem)
        directory_elem.set("path", catalog_locs.pedestrian_catalog)
    
    if catalog_locs.misc_object_catalog:
        misc_object_catalog_elem = _create_element("MiscObjectCatalog", elem)
        directory_elem = _create_element("Directory", misc_object_catalog_elem)
        directory_elem.set("path", catalog_locs.misc_object_catalog)
    
    if catalog_locs.environment_catalog:
        environment_catalog_elem = _create_element("EnvironmentCatalog", elem)
        directory_elem = _create_element("Directory", environment_catalog_elem)
        directory_elem.set("path", catalog_locs.environment_catalog)
    
    if catalog_locs.maneuver_catalog:
        maneuver_catalog_elem = _create_element("ManeuverCatalog", elem)
        directory_elem = _create_element("Directory", maneuver_catalog_elem)
        directory_elem.set("path", catalog_locs.maneuver_catalog)
    
    if catalog_locs.trajectory_catalog:
        trajectory_catalog_elem = _create_element("TrajectoryCatalog", elem)
        directory_elem = _create_element("Directory", trajectory_catalog_elem)
        directory_elem.set("path", catalog_locs.trajectory_catalog)


def write_world_position(parent: ET.Element, position: WorldPosition):
    """WorldPositionをXMLに書き込み（XSD準拠：属性として書き込み）"""
    elem = _create_element("WorldPosition", parent)
    # XSDでは属性として定義されている
    elem.set("x", str(position.x))
    elem.set("y", str(position.y))
    # パラメータ参照の可能性があるため、常に書き出す
    z_val = position.z
    if isinstance(z_val, str) or z_val != 0.0:
        elem.set("z", str(z_val))
    h_val = position.h
    if isinstance(h_val, str) or h_val != 0.0:
        elem.set("h", str(h_val))
    p_val = position.p
    if isinstance(p_val, str) or p_val != 0.0:
        elem.set("p", str(p_val))
    r_val = position.r
    if isinstance(r_val, str) or r_val != 0.0:
        elem.set("r", str(r_val))


def write_lane_position(parent: ET.Element, lane_position: LanePosition):
    """LanePositionをXMLに書き込み（XSD準拠：属性として書き込み）"""
    elem = _create_element("LanePosition", parent)
    # XSDでは属性として定義されている
    elem.set("roadId", lane_position.road_id)
    elem.set("laneId", str(lane_position.lane_id))  # lane_idは文字列型
    # s属性は常に書き出す（パラメータ式の場合も考慮）
    elem.set("s", str(lane_position.s))
    # offset属性も常に書き出す（元のXMLではデフォルト値でも明示的に書かれている場合がある）
    elem.set("offset", str(lane_position.offset))
    
    # Orientation要素
    if lane_position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in lane_position.orientation:
            orientation_elem.set("type", lane_position.orientation["type"])
        if "h" in lane_position.orientation:
            h_val = lane_position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in lane_position.orientation:
            p_val = lane_position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in lane_position.orientation:
            r_val = lane_position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_route_position(parent: ET.Element, route_position: RoutePosition):
    """RoutePositionをXMLに書き込み"""
    elem = _create_element("RoutePosition", parent)
    
    # RouteRef
    route_ref_elem = _create_element("RouteRef", elem)
    if route_position.route_ref:
        write_catalog_reference(route_ref_elem, route_position.route_ref)
    elif route_position.route:
        write_route(route_ref_elem, route_position.route)
    
    # Orientation
    if route_position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in route_position.orientation:
            orientation_elem.set("type", route_position.orientation["type"])
        if "h" in route_position.orientation:
            h_val = route_position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in route_position.orientation:
            p_val = route_position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in route_position.orientation:
            r_val = route_position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))
    
    # InRoutePosition
    if route_position.in_route_position:
        in_route_elem = _create_element("InRoutePosition", elem)
        from_lane_elem = _create_element("FromLaneCoordinates", in_route_elem)
        if "pathS" in route_position.in_route_position:
            from_lane_elem.set("pathS", str(route_position.in_route_position["pathS"]))
        if "laneId" in route_position.in_route_position:
            from_lane_elem.set("laneId", str(route_position.in_route_position["laneId"]))


def write_relative_world_position(parent: ET.Element, position: RelativeWorldPosition):
    """RelativeWorldPositionをXMLに書き込み"""
    elem = _create_element("RelativeWorldPosition", parent)
    elem.set("entityRef", position.entity_ref)
    elem.set("dx", str(position.dx))
    elem.set("dy", str(position.dy))
    if isinstance(position.dz, str) or position.dz != 0.0:
        elem.set("dz", str(position.dz))
    
    if position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in position.orientation:
            orientation_elem.set("type", position.orientation["type"])
        if "h" in position.orientation:
            h_val = position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in position.orientation:
            p_val = position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in position.orientation:
            r_val = position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_relative_lane_position(parent: ET.Element, position: RelativeLanePosition):
    """RelativeLanePositionをXMLに書き込み"""
    elem = _create_element("RelativeLanePosition", parent)
    elem.set("entityRef", position.entity_ref)
    elem.set("dLane", str(position.d_lane))
    if position.ds is not None:
        elem.set("ds", str(position.ds))
    if position.offset is not None:
        elem.set("offset", str(position.offset))
    if position.ds_lane is not None:
        elem.set("dsLane", str(position.ds_lane))
    
    if position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in position.orientation:
            orientation_elem.set("type", position.orientation["type"])
        if "h" in position.orientation:
            h_val = position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in position.orientation:
            p_val = position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in position.orientation:
            r_val = position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_relative_road_position(parent: ET.Element, position: RelativeRoadPosition):
    """RelativeRoadPositionをXMLに書き込み"""
    elem = _create_element("RelativeRoadPosition", parent)
    elem.set("entityRef", position.entity_ref)
    elem.set("ds", str(position.ds))
    elem.set("dt", str(position.dt))
    
    if position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in position.orientation:
            orientation_elem.set("type", position.orientation["type"])
        if "h" in position.orientation:
            h_val = position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in position.orientation:
            p_val = position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in position.orientation:
            r_val = position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_relative_object_position(parent: ET.Element, position: RelativeObjectPosition):
    """RelativeObjectPositionをXMLに書き込み"""
    elem = _create_element("RelativeObjectPosition", parent)
    elem.set("entityRef", position.entity_ref)
    elem.set("dx", str(position.dx))
    elem.set("dy", str(position.dy))
    if position.dz is not None and (isinstance(position.dz, str) or position.dz != 0.0):
        elem.set("dz", str(position.dz))
    
    if position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in position.orientation:
            orientation_elem.set("type", position.orientation["type"])
        if "h" in position.orientation:
            h_val = position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in position.orientation:
            p_val = position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in position.orientation:
            r_val = position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_road_position(parent: ET.Element, position: RoadPosition):
    """RoadPositionをXMLに書き込み"""
    elem = _create_element("RoadPosition", parent)
    elem.set("roadId", position.road_id)
    elem.set("s", str(position.s))
    elem.set("t", str(position.t))
    
    if position.orientation:
        orientation_elem = _create_element("Orientation", elem)
        if "type" in position.orientation:
            orientation_elem.set("type", position.orientation["type"])
        if "h" in position.orientation:
            h_val = position.orientation["h"]
            if isinstance(h_val, str) or h_val != 0.0:
                orientation_elem.set("h", str(h_val))
        if "p" in position.orientation:
            p_val = position.orientation["p"]
            if isinstance(p_val, str) or p_val != 0.0:
                orientation_elem.set("p", str(p_val))
        if "r" in position.orientation:
            r_val = position.orientation["r"]
            if isinstance(r_val, str) or r_val != 0.0:
                orientation_elem.set("r", str(r_val))


def write_position(parent: ET.Element, position):
    """Position要素をXMLに書き込み（全タイプに対応）"""
    if position is None:
        return
    
    if isinstance(position, WorldPosition):
        write_world_position(parent, position)
    elif isinstance(position, LanePosition):
        write_lane_position(parent, position)
    elif isinstance(position, RoutePosition):
        write_route_position(parent, position)
    elif isinstance(position, RelativeWorldPosition):
        write_relative_world_position(parent, position)
    elif isinstance(position, RelativeLanePosition):
        write_relative_lane_position(parent, position)
    elif isinstance(position, RelativeRoadPosition):
        write_relative_road_position(parent, position)
    elif isinstance(position, RelativeObjectPosition):
        write_relative_object_position(parent, position)
    elif isinstance(position, RoadPosition):
        write_road_position(parent, position)


def write_dynamics(parent: ET.Element, dynamics: Dynamics, tag_name: str = "Dynamics"):
    """DynamicsをXMLに書き込み（XSD準拠：属性として書き込み）"""
    elem = _create_element(tag_name, parent)
    elem.set("dynamicsDimension", dynamics.dynamics_dimension.value)
    elem.set("dynamicsShape", dynamics.dynamics_shape.value)
    
    # XSDではvalueは必須属性
    if dynamics.value is not None:
        elem.set("value", str(dynamics.value))


def write_teleport_action(parent: ET.Element, teleport_action: TeleportAction):
    """TeleportActionをXMLに書き込み"""
    elem = _create_element("TeleportAction", parent)
    position_elem = _create_element("Position", elem)
    
    if teleport_action.position is not None:
        write_world_position(position_elem, teleport_action.position)
    elif teleport_action.lane_position is not None:
        write_lane_position(position_elem, teleport_action.lane_position)
    elif teleport_action.route_position is not None:
        write_route_position(position_elem, teleport_action.route_position)
    elif teleport_action.relative_world_position is not None:
        write_relative_world_position(position_elem, teleport_action.relative_world_position)
    elif teleport_action.relative_lane_position is not None:
        write_relative_lane_position(position_elem, teleport_action.relative_lane_position)
    elif teleport_action.relative_road_position is not None:
        write_relative_road_position(position_elem, teleport_action.relative_road_position)
    elif teleport_action.relative_object_position is not None:
        write_relative_object_position(position_elem, teleport_action.relative_object_position)
    elif teleport_action.road_position is not None:
        write_road_position(position_elem, teleport_action.road_position)


def write_relative_target_speed(parent: ET.Element, relative_target_speed: RelativeTargetSpeed):
    """RelativeTargetSpeedをXMLに書き込み"""
    elem = _create_element("RelativeTargetSpeed", parent)
    elem.set("entityRef", relative_target_speed.entity_ref)
    elem.set("value", relative_target_speed.value)
    elem.set("speedTargetValueType", relative_target_speed.speed_target_value_type)
    # continuousは常に書き出す（デフォルト値でも）
    elem.set("continuous", "true" if relative_target_speed.continuous else "false")


def write_speed_action(parent: ET.Element, speed_action: SpeedAction):
    """SpeedActionをXMLに書き込み（XSD準拠：属性として書き込み）"""
    elem = _create_element("SpeedAction", parent)
    
    # SpeedActionTarget
    target_elem = _create_element("SpeedActionTarget", elem)
    if speed_action.speed_target is not None:
        abs_target_elem = _create_element("AbsoluteTargetSpeed", target_elem)
        # XSDではvalueは属性として定義されている
        abs_target_elem.set("value", str(speed_action.speed_target))
    elif speed_action.speed_target_str is not None:
        abs_target_elem = _create_element("AbsoluteTargetSpeed", target_elem)
        # パラメータ式の場合はそのまま文字列として書き込み
        abs_target_elem.set("value", speed_action.speed_target_str)
    elif speed_action.relative_target_speed is not None:
        write_relative_target_speed(target_elem, speed_action.relative_target_speed)
    
    # SpeedActionDynamics
    if speed_action.dynamics is not None:
        write_dynamics(elem, speed_action.dynamics, "SpeedActionDynamics")


def write_lane_change_action(parent: ET.Element, lane_change_action: LaneChangeAction):
    """LaneChangeActionをXMLに書き込み（XSD準拠：RelativeTargetLaneまたはAbsoluteTargetLane）"""
    elem = _create_element("LaneChangeAction", parent)
    
    # targetLaneOffset属性（オプション）
    if lane_change_action.target_lane_offset is not None:
        elem.set("targetLaneOffset", str(lane_change_action.target_lane_offset))
    
    # LaneChangeTarget
    target_elem = _create_element("LaneChangeTarget", elem)
    
    # RelativeTargetLaneまたはAbsoluteTargetLaneを選択
    if lane_change_action.target_lane is not None:
        rel_target_elem = _create_element("RelativeTargetLane", target_elem)
        rel_target_elem.set("value", str(lane_change_action.target_lane))
        if lane_change_action.target_entity_ref:
            rel_target_elem.set("entityRef", lane_change_action.target_entity_ref)
    elif lane_change_action.target_lane_absolute is not None:
        abs_target_elem = _create_element("AbsoluteTargetLane", target_elem)
        abs_target_elem.set("value", str(lane_change_action.target_lane_absolute))
    
    # LaneChangeActionDynamics
    if lane_change_action.dynamics is not None:
        write_dynamics(elem, lane_change_action.dynamics, "LaneChangeActionDynamics")


def write_lane_offset_action_dynamics(parent: ET.Element, dynamics: LaneOffsetActionDynamics):
    """LaneOffsetActionDynamicsをXMLに書き込み"""
    elem = _create_element("LaneOffsetActionDynamics", parent)
    elem.set("dynamicsShape", dynamics.dynamics_shape.value)
    if dynamics.max_lateral_acc is not None:
        elem.set("maxLateralAcc", str(dynamics.max_lateral_acc))


def write_lane_offset_action(parent: ET.Element, lane_offset_action: LaneOffsetAction):
    """LaneOffsetActionをXMLに書き込み"""
    elem = _create_element("LaneOffsetAction", parent)
    elem.set("continuous", "true" if lane_offset_action.continuous else "false")
    
    if lane_offset_action.dynamics is not None:
        write_lane_offset_action_dynamics(elem, lane_offset_action.dynamics)
    
    target_elem = _create_element("LaneOffsetTarget", elem)
    abs_target_elem = _create_element("AbsoluteTargetLaneOffset", target_elem)
    abs_target_elem.set("value", str(lane_offset_action.target_offset))


def write_vertex(parent: ET.Element, vertex: Vertex):
    """VertexをXMLに書き込み"""
    elem = _create_element("Vertex", parent)
    if vertex.time is not None:
        elem.set("time", str(vertex.time))
    
    position_elem = _create_element("Position", elem)
    write_position(position_elem, vertex.position)


def write_control_point(parent: ET.Element, control_point: ControlPoint):
    """ControlPointをXMLに書き込み"""
    elem = _create_element("ControlPoint", parent)
    if control_point.time is not None:
        elem.set("time", str(control_point.time))
    if control_point.weight is not None:
        elem.set("weight", str(control_point.weight))
    
    position_elem = _create_element("Position", elem)
    write_position(position_elem, control_point.position)


def write_polyline(parent: ET.Element, polyline: Polyline):
    """PolylineをXMLに書き込み"""
    elem = _create_element("Polyline", parent)
    for vertex in polyline.vertices:
        write_vertex(elem, vertex)


def write_clothoid(parent: ET.Element, clothoid: Clothoid):
    """ClothoidをXMLに書き込み"""
    elem = _create_element("Clothoid", parent)
    elem.set("curvature", str(clothoid.curvature))
    elem.set("length", str(clothoid.length))
    
    if clothoid.curvature_prime is not None:
        elem.set("curvaturePrime", str(clothoid.curvature_prime))
    if clothoid.start_time is not None:
        elem.set("startTime", str(clothoid.start_time))
    if clothoid.stop_time is not None:
        elem.set("stopTime", str(clothoid.stop_time))
    
    position_elem = _create_element("Position", elem)
    write_position(position_elem, clothoid.position)


def write_nurbs(parent: ET.Element, nurbs: Nurbs):
    """NurbsをXMLに書き込み"""
    elem = _create_element("Nurbs", parent)
    elem.set("order", str(nurbs.order))
    
    for control_point in nurbs.control_points:
        write_control_point(elem, control_point)
    
    for knot in nurbs.knots:
        knot_elem = _create_element("Knot", elem)
        knot_elem.set("value", str(knot["value"]))


def write_shape(parent: ET.Element, shape):
    """Shape要素を書き込み（Polyline, Clothoid, Nurbsのいずれか）"""
    shape_elem = _create_element("Shape", parent)
    
    if isinstance(shape, Polyline):
        write_polyline(shape_elem, shape)
    elif isinstance(shape, Clothoid):
        write_clothoid(shape_elem, shape)
    elif isinstance(shape, Nurbs):
        write_nurbs(shape_elem, shape)


def write_trajectory(parent: ET.Element, trajectory: Trajectory):
    """TrajectoryをXMLに書き込み"""
    elem = _create_element("Trajectory", parent)
    elem.set("name", trajectory.name)
    elem.set("closed", "true" if trajectory.closed else "false")
    
    if trajectory.parameter_declarations and trajectory.parameter_declarations.parameters:
        write_parameter_declarations(elem, trajectory.parameter_declarations)
    
    if trajectory.shape:
        write_shape(elem, trajectory.shape)


def write_time_reference(parent: ET.Element, time_reference: TimeReference):
    """TimeReferenceをXMLに書き込み"""
    elem = _create_element("TimeReference", parent)
    
    if time_reference.timing is None:
        _create_element("None", elem)
    else:
        timing_elem = _create_element("Timing", elem)
        timing = time_reference.timing
        if "domainAbsoluteRelative" in timing:
            timing_elem.set("domainAbsoluteRelative", timing["domainAbsoluteRelative"])
        if "offset" in timing:
            timing_elem.set("offset", str(timing["offset"]))
        if "scale" in timing:
            timing_elem.set("scale", str(timing["scale"]))


def write_follow_trajectory_action(parent: ET.Element, follow_trajectory: FollowTrajectoryAction):
    """FollowTrajectoryActionをXMLに書き込み"""
    elem = _create_element("FollowTrajectoryAction", parent)
    
    write_trajectory(elem, follow_trajectory.trajectory)
    
    if follow_trajectory.time_reference:
        write_time_reference(elem, follow_trajectory.time_reference)
    else:
        time_ref_elem = _create_element("TimeReference", elem)
        _create_element("None", time_ref_elem)
    
    following_mode_elem = _create_element("TrajectoryFollowingMode", elem)
    following_mode_elem.set("followingMode", follow_trajectory.following_mode)


def write_waypoint(parent: ET.Element, waypoint: Waypoint):
    """WaypointをXMLに書き込み"""
    elem = _create_element("Waypoint", parent)
    elem.set("routeStrategy", waypoint.route_strategy)
    
    position_elem = _create_element("Position", elem)
    write_position(position_elem, waypoint.position)


def write_route(parent: ET.Element, route: Route):
    """RouteをXMLに書き込み"""
    elem = _create_element("Route", parent)
    elem.set("name", route.name)
    elem.set("closed", "true" if route.closed else "false")
    
    if route.parameter_declarations and route.parameter_declarations.parameters:
        write_parameter_declarations(elem, route.parameter_declarations)
    
    # Waypointは2つ以上必須（XSD準拠）
    if len(route.waypoints) < 2:
        raise ValueError(f"Route '{route.name}' must have at least 2 Waypoints")
    
    for waypoint in route.waypoints:
        write_waypoint(elem, waypoint)


def write_assign_route_action(parent: ET.Element, assign_route: AssignRouteAction):
    """AssignRouteActionをXMLに書き込み"""
    elem = _create_element("AssignRouteAction", parent)
    
    # RouteまたはCatalogReferenceのいずれかが必須（XSD準拠）
    if assign_route.route_ref is None and assign_route.route is None:
        raise ValueError("AssignRouteAction must have either Route or CatalogReference element")
    
    if assign_route.route_ref is not None:
        write_catalog_reference(elem, assign_route.route_ref)
    elif assign_route.route is not None:
        write_route(elem, assign_route.route)


def write_routing_action(parent: ET.Element, routing_action: RoutingAction):
    """RoutingActionをXMLに書き込み"""
    elem = _create_element("RoutingAction", parent)
    
    if routing_action.assign_route_action is not None:
        write_assign_route_action(elem, routing_action.assign_route_action)
    elif routing_action.follow_trajectory_action is not None:
        write_follow_trajectory_action(elem, routing_action.follow_trajectory_action)


def write_activate_controller_action(parent: ET.Element, activate_controller: ActivateControllerAction):
    """ActivateControllerActionをXMLに書き込み"""
    elem = _create_element("ActivateControllerAction", parent)
    elem.set("longitudinal", "true" if activate_controller.longitudinal else "false")
    elem.set("lateral", "true" if activate_controller.lateral else "false")


def write_visibility_action(parent: ET.Element, visibility_action: VisibilityAction):
    """VisibilityActionをXMLに書き込み"""
    elem = _create_element("VisibilityAction", parent)
    # Boolean型属性を文字列として出力（パラメータ参照の場合はそのまま）
    if isinstance(visibility_action.graphics, bool):
        elem.set("graphics", "true" if visibility_action.graphics else "false")
    else:
        elem.set("graphics", str(visibility_action.graphics))
    
    if isinstance(visibility_action.sensors, bool):
        elem.set("sensors", "true" if visibility_action.sensors else "false")
    else:
        elem.set("sensors", str(visibility_action.sensors))
    
    if isinstance(visibility_action.traffic, bool):
        elem.set("traffic", "true" if visibility_action.traffic else "false")
    else:
        elem.set("traffic", str(visibility_action.traffic))
    
    # SensorReferenceSet要素は現時点では省略


def write_synchronize_action(parent: ET.Element, synchronize_action: SynchronizeAction):
    """SynchronizeActionをXMLに書き込み"""
    elem = _create_element("SynchronizeAction", parent)
    elem.set("masterEntityRef", synchronize_action.master_entity_ref)
    
    if synchronize_action.target_tolerance_master is not None:
        elem.set("targetToleranceMaster", str(synchronize_action.target_tolerance_master))
    if synchronize_action.target_tolerance is not None:
        elem.set("targetTolerance", str(synchronize_action.target_tolerance))
    
    # TargetPositionMaster要素（required）
    target_pos_master_elem = _create_element("TargetPositionMaster", elem)
    write_position(target_pos_master_elem, synchronize_action.target_position_master)
    
    # TargetPosition要素（required）
    target_pos_elem = _create_element("TargetPosition", elem)
    write_position(target_pos_elem, synchronize_action.target_position)
    
    # FinalSpeed要素（optional）
    if synchronize_action.final_speed is not None:
        final_speed_elem = _create_element("FinalSpeed", elem)
        if synchronize_action.final_speed.get("type") == "AbsoluteSpeed":
            abs_speed_elem = _create_element("AbsoluteSpeed", final_speed_elem)
            abs_speed_elem.set("value", str(synchronize_action.final_speed.get("value", "")))
        elif synchronize_action.final_speed.get("type") == "RelativeSpeedToMaster":
            rel_speed_elem = _create_element("RelativeSpeedToMaster", final_speed_elem)
            rel_speed_elem.set("speedTargetValueType", synchronize_action.final_speed.get("speedTargetValueType", "delta"))
            rel_speed_elem.set("value", str(synchronize_action.final_speed.get("value", "")))


def write_appearance_action(parent: ET.Element, appearance_action: AppearanceAction):
    """AppearanceActionをXMLに書き込み"""
    elem = _create_element("AppearanceAction", parent)
    
    # LightStateAction要素（optional）
    if appearance_action.light_state_action is not None:
        light_state_elem = _create_element("LightStateAction", elem)
        if "transitionTime" in appearance_action.light_state_action:
            light_state_elem.set("transitionTime", str(appearance_action.light_state_action["transitionTime"]))
        # LightType, LightState要素は将来対応
    
    # AnimationAction要素（optional）
    if appearance_action.animation_action is not None:
        animation_elem = _create_element("AnimationAction", elem)
        if "loop" in appearance_action.animation_action:
            animation_elem.set("loop", "true" if appearance_action.animation_action["loop"] else "false")
        if "animationDuration" in appearance_action.animation_action:
            animation_elem.set("animationDuration", str(appearance_action.animation_action["animationDuration"]))
        # AnimationType, AnimationState要素は将来対応


def write_private_action(parent: ET.Element, private_action: PrivateAction):
    """PrivateActionをXMLに書き込み"""
    elem = _create_element("PrivateAction", parent)
    
    if private_action.teleport_action is not None:
        write_teleport_action(elem, private_action.teleport_action)
    
    if private_action.speed_action is not None:
        long_elem = _create_element("LongitudinalAction", elem)
        write_speed_action(long_elem, private_action.speed_action)
    
    if private_action.lane_change_action is not None:
        lat_elem = _create_element("LateralAction", elem)
        write_lane_change_action(lat_elem, private_action.lane_change_action)
    
    if private_action.lane_offset_action is not None:
        lat_elem = _create_element("LateralAction", elem)
        write_lane_offset_action(lat_elem, private_action.lane_offset_action)
    
    if private_action.routing_action is not None:
        write_routing_action(elem, private_action.routing_action)
    
    if private_action.activate_controller_action is not None:
        write_activate_controller_action(elem, private_action.activate_controller_action)
    
    if private_action.visibility_action is not None:
        write_visibility_action(elem, private_action.visibility_action)
    
    if private_action.synchronize_action is not None:
        write_synchronize_action(elem, private_action.synchronize_action)
    
    if private_action.appearance_action is not None:
        write_appearance_action(elem, private_action.appearance_action)


def write_parameter_action(parent: ET.Element, parameter_action: ParameterAction):
    """ParameterActionをXMLに書き込み"""
    elem = _create_element("ParameterAction", parent)
    elem.set("parameterRef", parameter_action.parameter_ref)
    set_action_elem = _create_element("SetAction", elem)
    set_action_elem.set("value", str(parameter_action.set_action_value))


def write_global_action(parent: ET.Element, global_action: GlobalAction):
    """GlobalActionをXMLに書き込み"""
    elem = _create_element("GlobalAction", parent)
    
    if global_action.parameter_action is not None:
        write_parameter_action(elem, global_action.parameter_action)


def write_action(parent: ET.Element, action: Action):
    """ActionをXMLに書き込み（XSD準拠：name属性が必須）"""
    elem = _create_element("Action", parent)
    elem.set("name", action.name)
    
    if action.private_action is not None:
        write_private_action(elem, action.private_action)
    
    if action.global_action is not None:
        write_global_action(elem, action.global_action)
    
    # 将来の拡張: UserDefinedAction


def write_private(parent: ET.Element, private: Private):
    """PrivateをXMLに書き込み（XSD準拠：entityRef属性が必須）"""
    elem = _create_element("Private", parent)
    elem.set("entityRef", private.entity_ref)
    
    for action in private.actions:
        write_private_action(elem, action)


def write_simulation_time_condition(parent: ET.Element, condition: SimulationTimeCondition):
    """SimulationTimeConditionをXMLに書き込み（XSD準拠：属性として書き込み）"""
    elem = _create_element("SimulationTimeCondition", parent)
    elem.set("rule", condition.rule)
    # XSDではvalueは属性として定義されている（パラメータ参照の可能性があるためstr()を使用）
    elem.set("value", str(condition.value))


def write_time_headway_condition(parent: ET.Element, condition: TimeHeadwayCondition):
    """TimeHeadwayConditionをXMLに書き込み"""
    elem = _create_element("TimeHeadwayCondition", parent)
    elem.set("entityRef", condition.entity_ref)
    elem.set("value", condition.value)
    # freespaceは常に書き出す（デフォルト値でも）
    elem.set("freespace", "true" if condition.freespace else "false")
    elem.set("coordinateSystem", condition.coordinate_system)
    elem.set("relativeDistanceType", condition.relative_distance_type)
    elem.set("rule", condition.rule)


def write_offroad_condition(parent: ET.Element, condition: OffroadCondition):
    """OffroadConditionをXMLに書き込み"""
    elem = _create_element("OffroadCondition", parent)
    elem.set("duration", str(condition.duration))


def write_traveled_distance_condition(parent: ET.Element, condition: TraveledDistanceCondition):
    """TraveledDistanceConditionをXMLに書き込み"""
    elem = _create_element("TraveledDistanceCondition", parent)
    elem.set("value", str(condition.value))


def write_end_of_road_condition(parent: ET.Element, condition: EndOfRoadCondition):
    """EndOfRoadConditionをXMLに書き込み"""
    elem = _create_element("EndOfRoadCondition", parent)
    elem.set("duration", str(condition.duration))


def write_collision_condition(parent: ET.Element, condition: CollisionCondition):
    """CollisionConditionをXMLに書き込み"""
    elem = _create_element("CollisionCondition", parent)
    
    # EntityRef要素またはByType要素（choice）
    if condition.entity_ref is not None:
        entity_ref_elem = _create_element("EntityRef", elem)
        entity_ref_elem.set("entityRef", condition.entity_ref)
    elif condition.by_object_type is not None:
        by_type_elem = _create_element("ByType", elem)
        by_type_elem.set("type", condition.by_object_type.get("type", ""))


def write_time_to_collision_condition(parent: ET.Element, condition: TimeToCollisionCondition):
    """TimeToCollisionConditionをXMLに書き込み"""
    elem = _create_element("TimeToCollisionCondition", parent)
    elem.set("value", str(condition.value))
    elem.set("freespace", "true" if condition.freespace else "false")
    elem.set("coordinateSystem", condition.coordinate_system)
    elem.set("relativeDistanceType", condition.relative_distance_type)
    elem.set("rule", condition.rule)
    
    if condition.target_entity_ref:
        target_elem = _create_element("TimeToCollisionConditionTarget", elem)
        entity_ref_elem = _create_element("EntityRef", target_elem)
        entity_ref_elem.set("entityRef", condition.target_entity_ref)


def write_reach_position_condition(parent: ET.Element, condition: ReachPositionCondition):
    """ReachPositionConditionをXMLに書き込み"""
    elem = _create_element("ReachPositionCondition", parent)
    elem.set("tolerance", str(condition.tolerance))
    
    if condition.position:
        position_elem = _create_element("Position", elem)
        write_position(position_elem, condition.position)


def write_parameter_condition(parent: ET.Element, condition: ParameterCondition):
    """ParameterConditionをXMLに書き込み"""
    elem = _create_element("ParameterCondition", parent)
    elem.set("parameterRef", condition.parameter_ref)
    elem.set("value", str(condition.value))
    elem.set("rule", condition.rule)


def write_storyboard_element_state_condition(parent: ET.Element, condition: StoryboardElementStateCondition):
    """StoryboardElementStateConditionをXMLに書き込み"""
    elem = _create_element("StoryboardElementStateCondition", parent)
    elem.set("storyboardElementType", condition.storyboard_element_type)
    elem.set("storyboardElementRef", condition.storyboard_element_ref)
    elem.set("state", condition.state)


def write_by_entity_condition(parent: ET.Element, condition: ByEntityCondition):
    """ByEntityConditionをXMLに書き込み"""
    elem = _create_element("ByEntityCondition", parent)
    
    if condition.triggering_entities:
        triggering_elem = _create_element("TriggeringEntities", elem)
        triggering_elem.set("triggeringEntitiesRule", condition.triggering_entities_rule)
        for entity_ref in condition.triggering_entities:
            entity_ref_elem = _create_element("EntityRef", triggering_elem)
            entity_ref_elem.set("entityRef", entity_ref)
    
    has_entity_condition = (
        condition.entity_condition is not None or
        condition.offroad_condition is not None or
        condition.traveled_distance_condition is not None or
        condition.time_to_collision_condition is not None or
        condition.reach_position_condition is not None or
        condition.end_of_road_condition is not None or
        condition.collision_condition is not None
    )
    
    if has_entity_condition:
        entity_condition_elem = _create_element("EntityCondition", elem)
        if condition.entity_condition is not None:
            write_time_headway_condition(entity_condition_elem, condition.entity_condition)
        elif condition.offroad_condition is not None:
            write_offroad_condition(entity_condition_elem, condition.offroad_condition)
        elif condition.traveled_distance_condition is not None:
            write_traveled_distance_condition(entity_condition_elem, condition.traveled_distance_condition)
        elif condition.time_to_collision_condition is not None:
            write_time_to_collision_condition(entity_condition_elem, condition.time_to_collision_condition)
        elif condition.reach_position_condition is not None:
            write_reach_position_condition(entity_condition_elem, condition.reach_position_condition)
        elif condition.end_of_road_condition is not None:
            write_end_of_road_condition(entity_condition_elem, condition.end_of_road_condition)
        elif condition.collision_condition is not None:
            write_collision_condition(entity_condition_elem, condition.collision_condition)


def write_condition(parent: ET.Element, condition: Condition):
    """ConditionをXMLに書き込み"""
    # OpenSCENARIO仕様では、Conditionには必ずByValueConditionまたはByEntityConditionが必要
    # すべての条件がNoneの場合は、Condition要素を書き出さない
    if (condition.simulation_time_condition is None and 
        condition.by_entity_condition is None and 
        condition.storyboard_element_state_condition is None and
        condition.parameter_condition is None):
        # 空のConditionは無効なので、書き出さない
        return
    
    elem = _create_element("Condition", parent)
    if condition.name:
        elem.set("name", condition.name)
    # delayは常に書き出す（元のXMLではデフォルト値でも明示的に書かれている場合がある）
    elem.set("delay", str(condition.delay))
    elem.set("conditionEdge", condition.condition_edge)
    
    # ByValueCondition内の条件を書き込み
    by_value_needed = (condition.simulation_time_condition is not None or
                       condition.storyboard_element_state_condition is not None or
                       condition.parameter_condition is not None)
    
    if by_value_needed:
        by_value_elem = _create_element("ByValueCondition", elem)
        if condition.simulation_time_condition is not None:
            write_simulation_time_condition(by_value_elem, condition.simulation_time_condition)
        elif condition.storyboard_element_state_condition is not None:
            write_storyboard_element_state_condition(by_value_elem, condition.storyboard_element_state_condition)
        elif condition.parameter_condition is not None:
            write_parameter_condition(by_value_elem, condition.parameter_condition)
    
    if condition.by_entity_condition is not None:
        write_by_entity_condition(elem, condition.by_entity_condition)


def write_condition_group(parent: ET.Element, condition_group: ConditionGroup):
    """ConditionGroupをXMLに書き込み"""
    # 有効なConditionが存在するか確認
    valid_conditions = []
    for condition in condition_group.conditions:
        if (condition.simulation_time_condition is not None or 
            condition.by_entity_condition is not None or 
            condition.storyboard_element_state_condition is not None or
            condition.parameter_condition is not None):
            valid_conditions.append(condition)
    
    # 有効なConditionがない場合は、ConditionGroupを書き出さない
    if not valid_conditions:
        return
    
    elem = _create_element("ConditionGroup", parent)
    for condition in valid_conditions:
        write_condition(elem, condition)


def write_start_trigger(parent: ET.Element, start_trigger: StartTrigger, tag_name: str = "StartTrigger"):
    """StartTriggerまたはStopTriggerをXMLに書き込み"""
    if not start_trigger.condition_groups:
        return
    
    elem = _create_element(tag_name, parent)
    for cg in start_trigger.condition_groups:
        write_condition_group(elem, cg)
    
    # 有効なConditionGroupが書き出されなかった場合でも、StartTrigger要素は残す
    # （EventにはStartTriggerが必要なため）


def write_event(parent: ET.Element, event: Event):
    """EventをXMLに書き込み（XSD準拠：Action要素を正しく書き込み）"""
    elem = _create_element("Event", parent)
    elem.set("name", event.name)
    
    # priority属性は必須（XSD準拠）
    if event.priority is None:
        raise ValueError(f"Event '{event.name}' must have a priority attribute")
    elem.set("priority", event.priority.value)
    
    # Action要素は1つ以上必須（XSD準拠）
    if not event.actions:
        raise ValueError(f"Event '{event.name}' must have at least one Action element")
    
    for action in event.actions:
        write_action(elem, action)
    
    if event.start_trigger is not None:
        write_start_trigger(elem, event.start_trigger)


def write_maneuver(parent: ET.Element, maneuver: Maneuver):
    """ManeuverをXMLに書き込み"""
    elem = _create_element("Maneuver", parent)
    elem.set("name", maneuver.name)
    
    for event in maneuver.events:
        write_event(elem, event)


def write_maneuver_group(parent: ET.Element, maneuver_group: ManeuverGroup):
    """ManeuverGroupをXMLに書き込み"""
    elem = _create_element("ManeuverGroup", parent)
    elem.set("name", maneuver_group.name)
    
    # XSDではmaximumExecutionCountは必須属性として定義されている
    elem.set("maximumExecutionCount", str(maneuver_group.maximum_execution_count))
    
    # Actors要素は必須（XSD準拠）
    if not maneuver_group.actors:
        raise ValueError(f"ManeuverGroup '{maneuver_group.name}' must have at least one Actor")
    
    actors_elem = _create_element("Actors", elem)
    # selectTriggeringEntities属性は必須（XSD準拠）、Noneの場合はデフォルト値falseを設定
    select_triggering = maneuver_group.select_triggering_entities if maneuver_group.select_triggering_entities is not None else False
    actors_elem.set("selectTriggeringEntities", "true" if select_triggering else "false")
    
    for actor in maneuver_group.actors:
        entity_ref_elem = _create_element("EntityRef", actors_elem)
        entity_ref_elem.set("entityRef", actor)
    
    for maneuver in maneuver_group.maneuvers:
        write_maneuver(elem, maneuver)


def write_act(parent: ET.Element, act: Act):
    """ActをXMLに書き込み"""
    elem = _create_element("Act", parent)
    elem.set("name", act.name)
    
    # ManeuverGroup要素は1つ以上必須（XSD準拠）
    if not act.maneuver_groups:
        raise ValueError(f"Act '{act.name}' must have at least one ManeuverGroup element")
    
    for mg in act.maneuver_groups:
        write_maneuver_group(elem, mg)
    
    # StartTrigger要素は必須（XSD準拠）
    if act.start_trigger is None:
        raise ValueError(f"Act '{act.name}' must have a StartTrigger element")
    write_start_trigger(elem, act.start_trigger)
    
    if act.stop_trigger is not None:
        write_start_trigger(elem, act.stop_trigger, tag_name="StopTrigger")


def write_story(parent: ET.Element, story: Story):
    """StoryをXMLに書き込み"""
    elem = _create_element("Story", parent)
    elem.set("name", story.name)
    
    if story.parameter_declarations is not None:
        write_parameter_declarations(elem, story.parameter_declarations)
    
    for act in story.acts:
        write_act(elem, act)


def write_init(parent: ET.Element, init: Init):
    """InitをXMLに書き込み（XSD準拠：Private要素を正しく書き込み）"""
    elem = _create_element("Init", parent)
    
    if init.actions:
        actions_elem = _create_element("Actions", elem)
        for private in init.actions:
            write_private(actions_elem, private)


def write_storyboard(parent: ET.Element, storyboard: Storyboard):
    """StoryboardをXMLに書き込み"""
    elem = _create_element("Storyboard", parent)
    
    # Init要素は必須（XSD準拠）
    if storyboard.init is None:
        raise ValueError("Storyboard must have an Init element")
    write_init(elem, storyboard.init)
    
    for story in storyboard.stories:
        write_story(elem, story)
    
    # StopTrigger要素は必須（XSD準拠）
    if storyboard.stop_trigger is None:
        raise ValueError("Storyboard must have a StopTrigger element")
    write_start_trigger(elem, storyboard.stop_trigger, tag_name="StopTrigger")


def write_center(parent: ET.Element, center: Center):
    """CenterをXMLに書き込み"""
    elem = _create_element("Center", parent)
    elem.set("x", str(center.x))
    elem.set("y", str(center.y))
    elem.set("z", str(center.z))


def write_dimensions(parent: ET.Element, dimensions: Dimensions):
    """DimensionsをXMLに書き込み"""
    elem = _create_element("Dimensions", parent)
    elem.set("height", str(dimensions.height))
    elem.set("length", str(dimensions.length))
    elem.set("width", str(dimensions.width))


def write_bounding_box(parent: ET.Element, bounding_box: BoundingBox):
    """BoundingBoxをXMLに書き込み"""
    elem = _create_element("BoundingBox", parent)
    write_center(elem, bounding_box.center)
    write_dimensions(elem, bounding_box.dimensions)


def write_performance(parent: ET.Element, performance: Performance):
    """PerformanceをXMLに書き込み"""
    elem = _create_element("Performance", parent)
    elem.set("maxAcceleration", str(performance.max_acceleration))
    elem.set("maxDeceleration", str(performance.max_deceleration))
    elem.set("maxSpeed", str(performance.max_speed))
    if performance.max_acceleration_rate is not None:
        elem.set("maxAccelerationRate", str(performance.max_acceleration_rate))
    if performance.max_deceleration_rate is not None:
        elem.set("maxDecelerationRate", str(performance.max_deceleration_rate))


def write_axle(parent: ET.Element, axle: Axle):
    """AxleをXMLに書き込み"""
    elem = _create_element("Axle", parent)
    elem.set("maxSteering", str(axle.max_steering))
    elem.set("positionX", str(axle.position_x))
    elem.set("positionZ", str(axle.position_z))
    elem.set("trackWidth", str(axle.track_width))
    elem.set("wheelDiameter", str(axle.wheel_diameter))


def write_axles(parent: ET.Element, axles: Axles):
    """AxlesをXMLに書き込み"""
    elem = _create_element("Axles", parent)
    front_axle_elem = _create_element("FrontAxle", elem)
    write_axle(front_axle_elem, axles.front_axle)
    rear_axle_elem = _create_element("RearAxle", elem)
    write_axle(rear_axle_elem, axles.rear_axle)
    for additional_axle in axles.additional_axles:
        additional_axle_elem = _create_element("AdditionalAxle", elem)
        write_axle(additional_axle_elem, additional_axle)


def write_vehicle(parent: ET.Element, vehicle: Vehicle):
    """VehicleをXMLに書き込み"""
    elem = _create_element("Vehicle", parent)
    elem.set("name", vehicle.name)
    elem.set("vehicleCategory", vehicle.vehicle_category)
    if vehicle.role:
        elem.set("role", vehicle.role)
    if vehicle.mass is not None:
        elem.set("mass", str(vehicle.mass))
    if vehicle.model3d:
        elem.set("model3d", vehicle.model3d)
    
    if vehicle.parameter_declarations:
        write_parameter_declarations(elem, vehicle.parameter_declarations)
    
    if vehicle.bounding_box:
        write_bounding_box(elem, vehicle.bounding_box)
    
    if vehicle.performance:
        write_performance(elem, vehicle.performance)
    
    if vehicle.axles:
        write_axles(elem, vehicle.axles)
    
    # Propertiesは必須要素（XSDでは必須だが、空でもOK）
    if vehicle.properties is not None:
        write_properties(elem, vehicle.properties)


def write_catalog_reference(parent: ET.Element, catalog_ref: CatalogReference):
    """CatalogReferenceをXMLに書き込み"""
    elem = _create_element("CatalogReference", parent)
    elem.set("catalogName", catalog_ref.catalog_name)
    elem.set("entryName", catalog_ref.entry_name)


def write_properties(parent: ET.Element, properties: Properties):
    """PropertiesをXMLに書き込み"""
    elem = _create_element("Properties", parent)
    for prop in properties.properties:
        prop_elem = _create_element("Property", elem)
        prop_elem.set("name", prop.name)
        prop_elem.set("value", prop.value)


def write_controller(parent: ET.Element, controller: Controller):
    """ControllerをXMLに書き込み"""
    elem = _create_element("Controller", parent)
    elem.set("name", controller.name)
    
    if controller.properties and controller.properties.properties:
        write_properties(elem, controller.properties)


def write_object_controller(parent: ET.Element, object_controller: ObjectController):
    """ObjectControllerをXMLに書き込み"""
    elem = _create_element("ObjectController", parent)
    
    if object_controller.controller is not None:
        write_controller(elem, object_controller.controller)
    elif object_controller.catalog_reference is not None:
        write_catalog_reference(elem, object_controller.catalog_reference)


def write_pedestrian(parent: ET.Element, pedestrian: Pedestrian):
    """PedestrianをXMLに書き込み"""
    elem = _create_element("Pedestrian", parent)
    elem.set("name", pedestrian.name)
    elem.set("mass", str(pedestrian.mass))  # massは必須
    elem.set("pedestrianCategory", pedestrian.pedestrian_category)
    if pedestrian.model:
        elem.set("model", pedestrian.model)  # deprecatedだが保持
    if pedestrian.model3d:
        elem.set("model3d", pedestrian.model3d)
    if pedestrian.role:
        elem.set("role", pedestrian.role)
    
    if pedestrian.parameter_declarations:
        write_parameter_declarations(elem, pedestrian.parameter_declarations)
    
    if pedestrian.bounding_box:
        write_bounding_box(elem, pedestrian.bounding_box)
    
    # Propertiesは必須要素（XSDでは必須だが、空でもOK）
    if pedestrian.properties is not None:
        write_properties(elem, pedestrian.properties)


def write_scenario_object(parent: ET.Element, scenario_object: ScenarioObject):
    """ScenarioObjectをXMLに書き込み"""
    elem = _create_element("ScenarioObject", parent)
    elem.set("name", scenario_object.name)
    
    if scenario_object.catalog_reference is not None:
        write_catalog_reference(elem, scenario_object.catalog_reference)
    elif scenario_object.vehicle is not None:
        write_vehicle(elem, scenario_object.vehicle)
    elif scenario_object.pedestrian is not None:
        write_pedestrian(elem, scenario_object.pedestrian)
    
    if scenario_object.object_controller is not None:
        write_object_controller(elem, scenario_object.object_controller)


def write_entities(parent: ET.Element, entities: Entities):
    """EntitiesをXMLに書き込み"""
    elem = _create_element("Entities", parent)
    
    for obj in entities.scenario_objects:
        write_scenario_object(elem, obj)


def write_xml(scenario: ScenarioDefinition, file_path: str, pretty_print: bool = True):
    """ScenarioDefinitionをXMLファイルに書き込み"""
    # ルート要素を名前空間なしで作成（例ファイルと同じ形式）
    root = ET.Element("OpenSCENARIO")
    
    # XMLスキーマインスタンス名前空間を設定（オプション）
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "../Schema/OpenSCENARIO.xsd")
    
    # FileHeaderがNoneの場合はデフォルト値で作成（OpenSCENARIO 1.2）
    if scenario.file_header is not None:
        write_file_header(root, scenario.file_header)
    else:
        default_header = FileHeader(rev_major=1, rev_minor=2)
        write_file_header(root, default_header)
    
    if scenario.parameter_declarations is not None:
        write_parameter_declarations(root, scenario.parameter_declarations)
    
    if scenario.catalog_locations is not None:
        write_catalog_locations(root, scenario.catalog_locations)
    
    if scenario.road_network is not None:
        write_road_network(root, scenario.road_network)
    
    if scenario.entities is not None:
        write_entities(root, scenario.entities)
    
    if scenario.storyboard is not None:
        write_storyboard(root, scenario.storyboard)
    
    tree = ET.ElementTree(root)
    
    if pretty_print:
        # インデントを追加（Python 3.9+）
        try:
            ET.indent(tree, space="  ")
        except AttributeError:
            # Python < 3.9 の場合、インデントはスキップ
            pass
    
    tree.write(file_path, encoding="utf-8", xml_declaration=True)


