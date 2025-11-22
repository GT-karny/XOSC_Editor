"""ストーリーボード階層表示ツリー"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
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
    PrivateAction,
    Entities,
    ScenarioObject,
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
    
    def set_scenario(self, scenario: Optional[ScenarioDefinition]):
        """シナリオを設定してツリーを更新"""
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
                for i, action in enumerate(scenario.storyboard.init.actions):
                    action_item = QTreeWidgetItem(init_item, [f"Action {i+1}"])
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
                                
                                # Actions
                                for i, action in enumerate(event.actions):
                                    action_item = QTreeWidgetItem(event_item, [f"Action {i+1}"])
                                    action_item.setData(0, Qt.ItemDataRole.UserRole, action)
            
            storyboard_item.setExpanded(True)
    
    def _on_selection_changed(self):
        """選択変更時のハンドラ"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node is not None:
                self.node_selected.emit(node)


