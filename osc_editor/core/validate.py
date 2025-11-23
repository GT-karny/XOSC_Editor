"""バリデーション基盤（将来のXSD検証対応を考慮）"""

from typing import List, Tuple
from osc_editor.core.model import ScenarioDefinition


class ValidationError:
    """バリデーションエラー"""
    
    def __init__(self, message: str, element_path: str = ""):
        self.message = message
        self.element_path = element_path
    
    def __str__(self):
        if self.element_path:
            return f"{self.element_path}: {self.message}"
        return self.message


def validate_scenario(scenario: ScenarioDefinition) -> List[ValidationError]:
    """シナリオをバリデーションしてエラーリストを返す"""
    errors: List[ValidationError] = []
    
    # 基本的な構造チェック
    if scenario.storyboard is None:
        errors.append(ValidationError("Storyboard is required", "OpenSCENARIO"))
    
    if scenario.entities is None or not scenario.entities.scenario_objects:
        errors.append(ValidationError("At least one Entity is required", "OpenSCENARIO/Entities"))
    
    if scenario.storyboard:
        # Storyboardの検証
        if not scenario.storyboard.stories:
            errors.append(ValidationError("At least one Story is required", "OpenSCENARIO/Storyboard"))
        
        # StoryboardのStopTriggerのConditionを検証
        if scenario.storyboard.stop_trigger and scenario.storyboard.stop_trigger.condition_groups:
            for cg in scenario.storyboard.stop_trigger.condition_groups:
                        for cond in cg.conditions:
                            if (cond.simulation_time_condition is None and 
                                cond.by_entity_condition is None and 
                                cond.storyboard_element_state_condition is None and
                                cond.parameter_condition is None):
                                errors.append(
                                    ValidationError(
                                        f"Condition '{cond.name}' in Storyboard StopTrigger must have either ByValueCondition or ByEntityCondition",
                                        f"OpenSCENARIO/Storyboard/StopTrigger/ConditionGroup/Condition[@name='{cond.name}']"
                                    )
                                )
        
        for story in scenario.storyboard.stories:
            if not story.acts:
                errors.append(
                    ValidationError(
                        f"Story '{story.name}' must have at least one Act",
                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']"
                    )
                )
            
            for act in story.acts:
                if not act.maneuver_groups:
                    errors.append(
                        ValidationError(
                            f"Act '{act.name}' must have at least one ManeuverGroup",
                            f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']"
                        )
                    )
                
                # ActのStartTriggerとStopTriggerのConditionを検証
                if act.start_trigger and act.start_trigger.condition_groups:
                    for cg in act.start_trigger.condition_groups:
                        for cond in cg.conditions:
                            if (cond.simulation_time_condition is None and 
                                cond.by_entity_condition is None and 
                                cond.storyboard_element_state_condition is None and
                                cond.parameter_condition is None):
                                errors.append(
                                    ValidationError(
                                        f"Condition '{cond.name}' in Act '{act.name}' StartTrigger must have either ByValueCondition or ByEntityCondition",
                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/StartTrigger/ConditionGroup/Condition[@name='{cond.name}']"
                                    )
                                )
                
                if act.stop_trigger and act.stop_trigger.condition_groups:
                    for cg in act.stop_trigger.condition_groups:
                        for cond in cg.conditions:
                            if (cond.simulation_time_condition is None and 
                                cond.by_entity_condition is None and 
                                cond.storyboard_element_state_condition is None and
                                cond.parameter_condition is None):
                                errors.append(
                                    ValidationError(
                                        f"Condition '{cond.name}' in Act '{act.name}' StopTrigger must have either ByValueCondition or ByEntityCondition",
                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/StopTrigger/ConditionGroup/Condition[@name='{cond.name}']"
                                    )
                                )
                
                for mg in act.maneuver_groups:
                    if not mg.actors:
                        errors.append(
                            ValidationError(
                                f"ManeuverGroup '{mg.name}' must have at least one Actor",
                                f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']"
                            )
                        )
                    
                    if not mg.maneuvers:
                        errors.append(
                            ValidationError(
                                f"ManeuverGroup '{mg.name}' must have at least one Maneuver",
                                f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']"
                            )
                        )
                    
                    for maneuver in mg.maneuvers:
                        if not maneuver.events:
                            errors.append(
                                ValidationError(
                                    f"Maneuver '{maneuver.name}' must have at least one Event",
                                    f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Maneuver[@name='{maneuver.name}']"
                                )
                            )
                        
                        for event in maneuver.events:
                            if not event.actions:
                                errors.append(
                                    ValidationError(
                                        f"Event '{event.name}' must have at least one Action",
                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Maneuver[@name='{maneuver.name}']/Event[@name='{event.name}']"
                                    )
                                )
                            
                            if event.start_trigger is None or not event.start_trigger.condition_groups:
                                errors.append(
                                    ValidationError(
                                        f"Event '{event.name}' must have a StartTrigger with at least one ConditionGroup",
                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Maneuver[@name='{maneuver.name}']/Event[@name='{event.name}']"
                                    )
                                )
                            else:
                                # Conditionの検証：ByValueConditionまたはByEntityConditionが必須
                                for cg in event.start_trigger.condition_groups:
                                    for cond in cg.conditions:
                                        has_condition = (
                                            cond.simulation_time_condition is not None or
                                            cond.by_entity_condition is not None or
                                            cond.storyboard_element_state_condition is not None or
                                            cond.parameter_condition is not None
                                        )
                                        if not has_condition:
                                            errors.append(
                                                ValidationError(
                                                    f"Condition '{cond.name}' in Event '{event.name}' must have either ByValueCondition or ByEntityCondition",
                                                    f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Maneuver[@name='{maneuver.name}']/Event[@name='{event.name}']/StartTrigger/ConditionGroup/Condition[@name='{cond.name}']"
                                                )
                                            )
    
    # Entity参照の検証（パラメータ参照を考慮）
    if scenario.entities and scenario.storyboard:
        entity_names = {obj.name for obj in scenario.entities.scenario_objects}
        
        # グローバルパラメータの名前を取得
        global_param_names = set()
        if scenario.parameter_declarations:
            global_param_names = {param.name for param in scenario.parameter_declarations.parameters}
        
        for story in scenario.storyboard.stories:
            # Storyレベルのパラメータ名を取得
            story_param_names = set()
            if story.parameter_declarations:
                story_param_names = {param.name for param in story.parameter_declarations.parameters}
            
            for act in story.acts:
                for mg in act.maneuver_groups:
                    for actor in mg.actors:
                        # パラメータ参照（$で始まる）の場合は、パラメータが定義されているか確認
                        if actor.startswith('$'):
                            param_name = actor[1:]  # $を除去
                            if param_name not in story_param_names and param_name not in global_param_names:
                                errors.append(
                                    ValidationError(
                                        f"Parameter '{param_name}' referenced in ManeuverGroup '{mg.name}' is not declared",
                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Actors"
                                    )
                                )
                        # 通常のエンティティ参照の場合は、エンティティが存在するか確認
                        elif actor not in entity_names:
                            errors.append(
                                ValidationError(
                                    f"Entity '{actor}' referenced in ManeuverGroup '{mg.name}' does not exist",
                                    f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Actors"
                                )
                            )
    
    # Vehicle/Pedestrianの詳細属性の検証
    if scenario.entities:
        for obj in scenario.entities.scenario_objects:
            if obj.vehicle:
                # Vehicleの必須要素チェック（XSDではBoundingBox, Performance, Axles, Propertiesが必須）
                if obj.vehicle.bounding_box is None:
                    errors.append(
                        ValidationError(
                            f"Vehicle '{obj.vehicle.name}' must have BoundingBox",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Vehicle[@name='{obj.vehicle.name}']"
                        )
                    )
                if obj.vehicle.performance is None:
                    errors.append(
                        ValidationError(
                            f"Vehicle '{obj.vehicle.name}' must have Performance",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Vehicle[@name='{obj.vehicle.name}']"
                        )
                    )
                if obj.vehicle.axles is None:
                    errors.append(
                        ValidationError(
                            f"Vehicle '{obj.vehicle.name}' must have Axles",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Vehicle[@name='{obj.vehicle.name}']"
                        )
                    )
                # Propertiesは必須要素だが、空のリストでもOK（XSDではminOccurs="0"だが、要素自体は必須）
                # 実際のXMLでは空の<Properties/>でも有効
                # ここでは、propertiesがNoneの場合のみエラーとする（空のリストはOK）
                # ただし、XSDではProperties要素自体は必須なので、Noneの場合はエラー
                if obj.vehicle.properties is None:
                    errors.append(
                        ValidationError(
                            f"Vehicle '{obj.vehicle.name}' must have Properties element",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Vehicle[@name='{obj.vehicle.name}']"
                        )
                    )
            
            if obj.pedestrian:
                # Pedestrianの必須要素チェック（XSDではBoundingBox, Propertiesが必須）
                if obj.pedestrian.bounding_box is None:
                    errors.append(
                        ValidationError(
                            f"Pedestrian '{obj.pedestrian.name}' must have BoundingBox",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Pedestrian[@name='{obj.pedestrian.name}']"
                        )
                    )
                # Propertiesは必須要素だが、空のリストでもOK
                if obj.pedestrian.properties is None:
                    errors.append(
                        ValidationError(
                            f"Pedestrian '{obj.pedestrian.name}' must have Properties element",
                            f"OpenSCENARIO/Entities/ScenarioObject[@name='{obj.name}']/Pedestrian[@name='{obj.pedestrian.name}']"
                        )
                    )
    
    # Route要素の検証
    if scenario.storyboard:
        for story in scenario.storyboard.stories:
            for act in story.acts:
                for mg in act.maneuver_groups:
                    for maneuver in mg.maneuvers:
                        for event in maneuver.events:
                            for action in event.actions:
                                if action.private_action and action.private_action.routing_action:
                                    if action.private_action.routing_action.assign_route_action:
                                        assign_route = action.private_action.routing_action.assign_route_action
                                        if assign_route.route:
                                            # RouteのWaypointは2つ以上必要
                                            if len(assign_route.route.waypoints) < 2:
                                                errors.append(
                                                    ValidationError(
                                                        f"Route '{assign_route.route.name}' must have at least 2 Waypoints",
                                                        f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Maneuver[@name='{maneuver.name}']/Event[@name='{event.name}']/Action[@name='{action.name}']/PrivateAction/RoutingAction/AssignRouteAction/Route[@name='{assign_route.route.name}']"
                                                    )
                                                )
    
    return errors


def validate_and_get_errors(scenario: ScenarioDefinition) -> Tuple[bool, List[ValidationError]]:
    """バリデーションを実行し、成功/失敗とエラーリストを返す"""
    errors = validate_scenario(scenario)
    return (len(errors) == 0, errors)


