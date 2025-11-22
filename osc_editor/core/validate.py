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
    
    # Entity参照の検証
    if scenario.entities and scenario.storyboard:
        entity_names = {obj.name for obj in scenario.entities.scenario_objects}
        
        for story in scenario.storyboard.stories:
            for act in story.acts:
                for mg in act.maneuver_groups:
                    for actor in mg.actors:
                        if actor not in entity_names:
                            errors.append(
                                ValidationError(
                                    f"Entity '{actor}' referenced in ManeuverGroup '{mg.name}' does not exist",
                                    f"OpenSCENARIO/Storyboard/Story[@name='{story.name}']/Act[@name='{act.name}']/ManeuverGroup[@name='{mg.name}']/Actors"
                                )
                            )
    
    return errors


def validate_and_get_errors(scenario: ScenarioDefinition) -> Tuple[bool, List[ValidationError]]:
    """バリデーションを実行し、成功/失敗とエラーリストを返す"""
    errors = validate_scenario(scenario)
    return (len(errors) == 0, errors)


