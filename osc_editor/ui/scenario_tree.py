"""ストーリーボード階層表示ツリー"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
from PySide6.QtCore import Signal, Qt
from typing import Optional
from osc_editor.core.model import (
    ScenarioDefinition,
    Storyboard,
    Story,
    Act,
    ManeuverGroup,
    Maneuver,
    Event,
    Action,
    Private,
    PrivateAction,
    Entities,
    ScenarioObject,
    StartTrigger,
    ConditionGroup,
    Condition,
)


class ScenarioTreeWidget(QTreeWidget):
    """ストーリーボード階層を表示するツリーウィジェット"""
    
    # ノード選択時のシグナル
    node_selected = Signal(object)  # 選択されたノードオブジェクトを送信
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("ストーリーボード")
        self.setColumnCount(1)
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self._scenario: Optional[ScenarioDefinition] = None
    
    def _save_expanded_state(self) -> dict:
        """ツリーの展開状態を保存"""
        expanded_items = {}
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if item.childCount() > 0:
                node = item.data(0, Qt.ItemDataRole.UserRole)
                if node is not None:
                    # ノードオブジェクトをキーとして使用（idで識別）
                    node_id = id(node)
                    expanded_items[node_id] = item.isExpanded()
            iterator += 1
        return expanded_items
    
    def _restore_expanded_state(self, expanded_items: dict):
        """ツリーの展開状態を復元"""
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            if item.childCount() > 0:
                node = item.data(0, Qt.ItemDataRole.UserRole)
                if node is not None:
                    node_id = id(node)
                    if node_id in expanded_items:
                        item.setExpanded(expanded_items[node_id])
            iterator += 1
    
    def set_scenario(self, scenario: Optional[ScenarioDefinition]):
        """シナリオを設定してツリーを更新"""
        # 展開状態を保存
        expanded_state = self._save_expanded_state()
        
        self._scenario = scenario
        self.clear()
        
        if scenario is None:
            return
        
        # Entities
        if scenario.entities:
            entities_item = QTreeWidgetItem(self, ["エンティティ"])
            entities_item.setData(0, Qt.ItemDataRole.UserRole, scenario.entities)
            for obj in scenario.entities.scenario_objects:
                obj_item = QTreeWidgetItem(entities_item, [f"Entity: {obj.name}"])
                obj_item.setData(0, Qt.ItemDataRole.UserRole, obj)
        
        # Storyboard
        if scenario.storyboard:
            storyboard_item = QTreeWidgetItem(self, ["ストーリーボード"])
            storyboard_item.setData(0, Qt.ItemDataRole.UserRole, scenario.storyboard)
            
            # Init
            if scenario.storyboard.init:
                init_item = QTreeWidgetItem(storyboard_item, ["Init"])
                init_item.setData(0, Qt.ItemDataRole.UserRole, scenario.storyboard.init)
                for private in scenario.storyboard.init.actions:
                    private_item = QTreeWidgetItem(init_item, [f"Private: {private.entity_ref}"])
                    private_item.setData(0, Qt.ItemDataRole.UserRole, private)
                    for i, action in enumerate(private.actions):
                        action_item = QTreeWidgetItem(private_item, [f"Action {i+1}"])
                        action_item.setData(0, Qt.ItemDataRole.UserRole, action)
            
            # Stories
            for story in scenario.storyboard.stories:
                story_item = QTreeWidgetItem(storyboard_item, [f"Story: {story.name}"])
                story_item.setData(0, Qt.ItemDataRole.UserRole, story)
                
                # Acts
                for act in story.acts:
                    act_item = QTreeWidgetItem(story_item, [f"Act: {act.name}"])
                    act_item.setData(0, Qt.ItemDataRole.UserRole, act)
                    
                    # ManeuverGroups
                    for mg in act.maneuver_groups:
                        mg_item = QTreeWidgetItem(act_item, [f"ManeuverGroup: {mg.name}"])
                        mg_item.setData(0, Qt.ItemDataRole.UserRole, mg)
                        
                        # Maneuvers
                        for maneuver in mg.maneuvers:
                            maneuver_item = QTreeWidgetItem(mg_item, [f"Maneuver: {maneuver.name}"])
                            maneuver_item.setData(0, Qt.ItemDataRole.UserRole, maneuver)
                            
                            # Events
                            for event in maneuver.events:
                                event_item = QTreeWidgetItem(maneuver_item, [f"Event: {event.name}"])
                                event_item.setData(0, Qt.ItemDataRole.UserRole, event)
                                
                                # StartTrigger
                                if event.start_trigger:
                                    start_trigger_item = QTreeWidgetItem(event_item, ["StartTrigger"])
                                    start_trigger_item.setData(0, Qt.ItemDataRole.UserRole, event.start_trigger)
                                    
                                    # ConditionGroups
                                    for i, cg in enumerate(event.start_trigger.condition_groups):
                                        cg_item = QTreeWidgetItem(start_trigger_item, [f"ConditionGroup {i+1}"])
                                        cg_item.setData(0, Qt.ItemDataRole.UserRole, cg)
                                        
                                        # Conditions
                                        for j, cond in enumerate(cg.conditions):
                                            cond_name = cond.name if cond.name else f"Condition {j+1}"
                                            cond_item = QTreeWidgetItem(cg_item, [cond_name])
                                            cond_item.setData(0, Qt.ItemDataRole.UserRole, cond)
                                
                                # Actions
                                for action in event.actions:
                                    action_item = QTreeWidgetItem(event_item, [f"Action: {action.name}"])
                                    action_item.setData(0, Qt.ItemDataRole.UserRole, action)
                                    if action.private_action is not None:
                                        private_action_item = QTreeWidgetItem(action_item, ["PrivateAction"])
                                        private_action_item.setData(0, Qt.ItemDataRole.UserRole, action.private_action)
                    
                    # ActのStartTriggerとStopTrigger
                    if act.start_trigger:
                        act_start_trigger_item = QTreeWidgetItem(act_item, ["StartTrigger"])
                        act_start_trigger_item.setData(0, Qt.ItemDataRole.UserRole, act.start_trigger)
                        
                        # ConditionGroups
                        for i, cg in enumerate(act.start_trigger.condition_groups):
                            cg_item = QTreeWidgetItem(act_start_trigger_item, [f"ConditionGroup {i+1}"])
                            cg_item.setData(0, Qt.ItemDataRole.UserRole, cg)
                            
                            # Conditions
                            for j, cond in enumerate(cg.conditions):
                                cond_name = cond.name if cond.name else f"Condition {j+1}"
                                cond_item = QTreeWidgetItem(cg_item, [cond_name])
                                cond_item.setData(0, Qt.ItemDataRole.UserRole, cond)
                    
                    if act.stop_trigger:
                        act_stop_trigger_item = QTreeWidgetItem(act_item, ["StopTrigger"])
                        act_stop_trigger_item.setData(0, Qt.ItemDataRole.UserRole, act.stop_trigger)
                        
                        # ConditionGroups
                        for i, cg in enumerate(act.stop_trigger.condition_groups):
                            cg_item = QTreeWidgetItem(act_stop_trigger_item, [f"ConditionGroup {i+1}"])
                            cg_item.setData(0, Qt.ItemDataRole.UserRole, cg)
                            
                            # Conditions
                            for j, cond in enumerate(cg.conditions):
                                cond_name = cond.name if cond.name else f"Condition {j+1}"
                                cond_item = QTreeWidgetItem(cg_item, [cond_name])
                                cond_item.setData(0, Qt.ItemDataRole.UserRole, cond)
            
            storyboard_item.setExpanded(True)
        
        # 展開状態を復元
        self._restore_expanded_state(expanded_state)
    
    def _on_selection_changed(self):
        """選択変更時のハンドラ"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node is not None:
                self.node_selected.emit(node)


