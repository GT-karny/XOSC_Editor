"""XML → モデルへの変換"""

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
    SpeedAction,
    LaneChangeAction,
    WorldPosition,
    LanePosition,
    Dynamics,
    DynamicsDimension,
    DynamicsShape,
    StartTrigger,
    ConditionGroup,
    Condition,
    SimulationTimeCondition,
    Rule,
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


def _get_attr_float(element: ET.Element, attr_name: str, default: float = 0.0) -> float:
    """要素の属性から浮動小数点数を取得"""
    if element is None:
        return default
    attr_value = element.get(attr_name)
    if attr_value is None:
        return default
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


def _get_attr_bool(element: ET.Element, attr_name: str, default: bool = False) -> bool:
    """要素の属性から真偽値を取得"""
    if element is None:
        return default
    attr_value = element.get(attr_name)
    if attr_value is None:
        return default
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
    """CatalogLocationsをパース（MVPでは空）"""
    return CatalogLocations()


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
    return LanePosition(
        road_id=_get_attr(element, "roadId", ""),
        lane_id=_get_attr(element, "laneId", ""),  # XSDではString型
        s=_get_attr_float(element, "s", 0.0),
        offset=_get_attr_float(element, "offset", 0.0),
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


def parse_teleport_action(element: ET.Element) -> Optional[TeleportAction]:
    """TeleportActionをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    position_elem = element.find(f"./{ns}Position/{ns}WorldPosition")
    lane_position_elem = element.find(f"./{ns}Position/{ns}LanePosition")
    
    position = None
    lane_position = None
    
    if position_elem is not None:
        position = parse_world_position(position_elem)
    if lane_position_elem is not None:
        lane_position = parse_lane_position(lane_position_elem)
    
    if position is None and lane_position is None:
        return None
    
    return TeleportAction(position=position, lane_position=lane_position)


def parse_speed_action(element: ET.Element) -> Optional[SpeedAction]:
    """SpeedActionをパース（XSD準拠）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    # SpeedActionDynamicsはTransitionDynamics型（属性から取得）
    dynamics_elem = element.find(f"./{ns}SpeedActionDynamics")
    dynamics = parse_transition_dynamics(dynamics_elem) if dynamics_elem is not None else None
    
    # SpeedActionTargetからAbsoluteTargetSpeedのvalue属性を取得
    speed_target_elem = element.find(f"./{ns}SpeedActionTarget/{ns}AbsoluteTargetSpeed")
    if speed_target_elem is None:
        return None
    
    speed = _get_attr_float(speed_target_elem, "value", 0.0)
    
    return SpeedAction(speed_target=speed, dynamics=dynamics)


def parse_lane_change_action(element: ET.Element) -> Optional[LaneChangeAction]:
    """LaneChangeActionをパース（XSD準拠）"""
    if element is None:
        return None
    
    ns = _detect_namespace(element)
    # LaneChangeActionDynamicsはTransitionDynamics型（属性から取得）
    dynamics_elem = element.find(f"./{ns}LaneChangeActionDynamics")
    dynamics = parse_transition_dynamics(dynamics_elem) if dynamics_elem is not None else None
    
    # LaneChangeTargetからRelativeTargetLaneのvalue属性を取得（Int型）
    target_lane_elem = element.find(f"./{ns}LaneChangeTarget/{ns}RelativeTargetLane")
    if target_lane_elem is None:
        return None
    
    target_lane = _get_attr_int(target_lane_elem, "value", 0)
    
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
        dynamics=dynamics,
        target_lane_offset=target_lane_offset,
    )


def parse_private_action(element: ET.Element) -> Optional[PrivateAction]:
    """PrivateActionをパース"""
    if element is None:
        return None
    ns = _detect_namespace(element)
    teleport_elem = element.find(f"./{ns}TeleportAction")
    speed_elem = element.find(f"./{ns}LongitudinalAction/{ns}SpeedAction")
    lane_change_elem = element.find(f"./{ns}LateralAction/{ns}LaneChangeAction")
    
    teleport_action = parse_teleport_action(teleport_elem) if teleport_elem is not None else None
    speed_action = parse_speed_action(speed_elem) if speed_elem is not None else None
    lane_change_action = parse_lane_change_action(lane_change_elem) if lane_change_elem is not None else None
    
    if teleport_action is None and speed_action is None and lane_change_action is None:
        return None
    
    return PrivateAction(
        teleport_action=teleport_action,
        speed_action=speed_action,
        lane_change_action=lane_change_action,
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
    
    # 将来の拡張: GlobalAction, UserDefinedAction
    
    return Action(
        name=name,
        private_action=private_action,
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


def parse_condition(element: ET.Element) -> Condition:
    """Conditionをパース（XSD準拠：属性から取得）"""
    if element is None:
        return Condition()
    name = _get_attr(element, "name", "")
    delay = _get_attr_float(element, "delay", 0.0)
    condition_edge = _get_attr(element, "conditionEdge", "rising")
    
    ns = _detect_namespace(element)
    sim_time_elem = element.find(f"./{ns}ByValueCondition/{ns}SimulationTimeCondition")
    sim_time_condition = parse_simulation_time_condition(sim_time_elem) if sim_time_elem is not None else None
    
    return Condition(
        name=name,
        delay=delay,
        condition_edge=condition_edge,
        simulation_time_condition=sim_time_condition,
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
    priority_str = element.get("priority", "override")
    try:
        priority = Rule(priority_str)
    except ValueError:
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
    actors_elem = element.find(f"./{ns}Actors")
    if actors_elem is not None:
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
    acts = []
    for act_elem in element.findall(f"./{ns}Act"):
        acts.append(parse_act(act_elem))
    
    return Story(name=name, acts=acts)


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


def parse_vehicle(element: ET.Element) -> Vehicle:
    """Vehicleをパース"""
    name = element.get("name", "")
    category = element.get("vehicleCategory", "car")
    return Vehicle(name=name, vehicle_category=category)


def parse_scenario_object(element: ET.Element) -> ScenarioObject:
    """ScenarioObjectをパース"""
    if element is None:
        return ScenarioObject(name="")
    name = element.get("name", "")
    ns = _detect_namespace(element)
    vehicle_elem = element.find(f"./{ns}Vehicle")
    vehicle = parse_vehicle(vehicle_elem) if vehicle_elem is not None else None
    
    return ScenarioObject(name=name, vehicle=vehicle)


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


