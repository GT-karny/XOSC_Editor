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
    SpeedAction,
    RelativeTargetSpeed,
    LaneChangeAction,
    LaneOffsetAction,
    LaneOffsetActionDynamics,
    WorldPosition,
    LanePosition,
    Dynamics,
    DynamicsShape,
    StartTrigger,
    ConditionGroup,
    Condition,
    SimulationTimeCondition,
    ByEntityCondition,
    TimeHeadwayCondition,
    OffroadCondition,
    ParameterCondition,
    StoryboardElementStateCondition,
    GlobalAction,
    ParameterAction,
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
        if param.value:
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
    
    if condition.entity_condition is not None or condition.offroad_condition is not None:
        entity_condition_elem = _create_element("EntityCondition", elem)
        if condition.entity_condition is not None:
            write_time_headway_condition(entity_condition_elem, condition.entity_condition)
        elif condition.offroad_condition is not None:
            write_offroad_condition(entity_condition_elem, condition.offroad_condition)


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
    elem.set("priority", event.priority.value)
    
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
    
    if maneuver_group.actors:
        actors_elem = _create_element("Actors", elem)
        if maneuver_group.select_triggering_entities is not None:
            actors_elem.set("selectTriggeringEntities", "true" if maneuver_group.select_triggering_entities else "false")
        for actor in maneuver_group.actors:
            entity_ref_elem = _create_element("EntityRef", actors_elem)
            entity_ref_elem.set("entityRef", actor)
    
    for maneuver in maneuver_group.maneuvers:
        write_maneuver(elem, maneuver)


def write_act(parent: ET.Element, act: Act):
    """ActをXMLに書き込み"""
    elem = _create_element("Act", parent)
    elem.set("name", act.name)
    
    for mg in act.maneuver_groups:
        write_maneuver_group(elem, mg)
    
    if act.start_trigger is not None:
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
    
    if storyboard.init is not None:
        write_init(elem, storyboard.init)
    
    for story in storyboard.stories:
        write_story(elem, story)
    
    if storyboard.stop_trigger is not None:
        write_start_trigger(elem, storyboard.stop_trigger, tag_name="StopTrigger")


def write_vehicle(parent: ET.Element, vehicle: Vehicle):
    """VehicleをXMLに書き込み"""
    elem = _create_element("Vehicle", parent)
    elem.set("name", vehicle.name)
    elem.set("vehicleCategory", vehicle.vehicle_category)


def write_catalog_reference(parent: ET.Element, catalog_ref: CatalogReference):
    """CatalogReferenceをXMLに書き込み"""
    elem = _create_element("CatalogReference", parent)
    elem.set("catalogName", catalog_ref.catalog_name)
    elem.set("entryName", catalog_ref.entry_name)


def write_pedestrian(parent: ET.Element, pedestrian: Pedestrian):
    """PedestrianをXMLに書き込み"""
    elem = _create_element("Pedestrian", parent)
    elem.set("name", pedestrian.name)
    if pedestrian.mass is not None:
        elem.set("mass", str(pedestrian.mass))
    if pedestrian.model:
        elem.set("model", pedestrian.model)
    elem.set("pedestrianCategory", pedestrian.pedestrian_category)
    if pedestrian.model3d:
        elem.set("model3d", pedestrian.model3d)


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


