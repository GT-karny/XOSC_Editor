"""プロパティ編集パネル"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QListWidget,
    QAbstractItemView,
)
from PySide6.QtCore import Signal, Qt
from typing import Optional
from osc_editor.core.model import (
    ScenarioObject,
    PrivateAction,
    TeleportAction,
    SpeedAction,
    LaneChangeAction,
    WorldPosition,
    LanePosition,
    RoadPosition,
    RoutePosition,
    RelativeWorldPosition,
    RelativeLanePosition,
    RelativeRoadPosition,
    RelativeObjectPosition,
    Dynamics,
    DynamicsDimension,
    DynamicsShape,
    Event,
    StartTrigger,
    Condition,
    ConditionGroup,
    ByEntityCondition,
    SimulationTimeCondition,
    TimeHeadwayCondition,
    DistanceCondition,
    RelativeDistanceCondition,
    SpeedCondition,
    RelativeSpeedCondition,
    TraveledDistanceCondition,
    ReachPositionCondition,
    ParameterCondition,
    TimeOfDayCondition,
    UserDefinedValueCondition,
    TrafficSignalCondition,
    TrafficSignalControllerCondition,
    VariableCondition,
    StoryboardElementStateCondition,
    Rule,
    RelativeTargetSpeed,
    Story,
    Act,
    ManeuverGroup,
    Maneuver,
    Action,
    Private,
    ScenarioDefinition,
)


class PropertiesPanel(QWidget):
    """プロパティ編集パネル"""
    
    # プロパティ変更時のシグナル
    property_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_node = None
        self._scenario: Optional[ScenarioDefinition] = None
        self._setup_ui()
    
    def set_scenario(self, scenario: Optional[ScenarioDefinition]):
        """シナリオを設定（エンティティ一覧取得用）"""
        self._scenario = scenario
    
    def _setup_ui(self):
        """UIのセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._form_widget = QWidget()
        self._form_layout = QFormLayout(self._form_widget)
        layout.addWidget(self._form_widget)
        
        layout.addStretch()
    
    def set_node(self, node):
        """編集対象ノードを設定"""
        self._current_node = node
        self._clear_form()
        
        if node is None:
            return
        
        # ノードタイプに応じてフォームを構築
        if isinstance(node, ScenarioObject):
            self._build_scenario_object_form(node)
        elif isinstance(node, PrivateAction):
            self._build_private_action_form(node)
        elif isinstance(node, TeleportAction):
            self._build_teleport_action_form(node)
        elif isinstance(node, SpeedAction):
            self._build_speed_action_form(node)
        elif isinstance(node, LaneChangeAction):
            self._build_lane_change_action_form(node)
        elif isinstance(node, Event):
            self._build_event_form(node)
        elif isinstance(node, StartTrigger):
            self._build_start_trigger_form(node)
        elif isinstance(node, ConditionGroup):
            # ConditionGroupを選択した場合、最初のConditionを編集
            if node.conditions:
                self._build_condition_form(node.conditions[0])
            else:
                # Conditionが存在しない場合は新規作成
                new_condition = Condition()
                node.conditions.append(new_condition)
                self._build_condition_form(new_condition)
        elif isinstance(node, Condition):
            self._build_condition_form(node)
        elif isinstance(node, Story):
            self._build_story_form(node)
        elif isinstance(node, Act):
            self._build_act_form(node)
        elif isinstance(node, ManeuverGroup):
            self._build_maneuver_group_form(node)
        elif isinstance(node, Maneuver):
            self._build_maneuver_form(node)
        elif isinstance(node, Action):
            self._build_action_form(node)
        elif isinstance(node, Private):
            self._build_private_form(node)
        else:
            # その他のノードタイプ
            label = QLabel(f"編集未対応: {type(node).__name__}")
            self._form_layout.addRow(label)
    
    def _clear_form(self):
        """フォームをクリア"""
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _build_scenario_object_form(self, obj: ScenarioObject):
        """ScenarioObject用フォーム"""
        name_edit = QLineEdit(obj.name)
        name_edit.textChanged.connect(lambda text: setattr(obj, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
        
        if obj.vehicle:
            vehicle_label = QLabel(f"Vehicle: {obj.vehicle.name} ({obj.vehicle.vehicle_category})")
            self._form_layout.addRow("車両:", vehicle_label)
    
    def _build_private_action_form(self, action: PrivateAction):
        """PrivateAction用フォーム"""
        if action.teleport_action:
            self._build_teleport_action_form(action.teleport_action)
        elif action.speed_action:
            self._build_speed_action_form(action.speed_action)
        elif action.lane_change_action:
            self._build_lane_change_action_form(action.lane_change_action)
    
    def _build_teleport_action_form(self, action: TeleportAction):
        """TeleportAction用フォーム"""
        group = QGroupBox("TeleportAction")
        form = QFormLayout()
        
        # 現在のPositionタイプを判定
        current_position_type = None
        if action.position:
            current_position_type = "WorldPosition"
        elif action.lane_position:
            current_position_type = "LanePosition"
        elif action.road_position:
            current_position_type = "RoadPosition"
        elif action.relative_world_position:
            current_position_type = "RelativeWorldPosition"
        elif action.relative_lane_position:
            current_position_type = "RelativeLanePosition"
        elif action.relative_road_position:
            current_position_type = "RelativeRoadPosition"
        elif action.relative_object_position:
            current_position_type = "RelativeObjectPosition"
        else:
            current_position_type = "WorldPosition"  # デフォルト
        
        # Positionタイプ選択UI
        position_type_combo = QComboBox()
        position_type_combo.addItems([
            "WorldPosition",
            "LanePosition",
            "RoadPosition",
            "RelativeWorldPosition",
            "RelativeLanePosition",
            "RelativeRoadPosition",
            "RelativeObjectPosition"
        ])
        position_type_combo.setCurrentText(current_position_type)
        form.addRow("Position Type:", position_type_combo)
        
        # 各Positionタイプ用のウィジェット
        world_pos_widget = QWidget()
        world_pos_form = QFormLayout(world_pos_widget)
        
        lane_pos_widget = QWidget()
        lane_pos_form = QFormLayout(lane_pos_widget)
        
        road_pos_widget = QWidget()
        road_pos_form = QFormLayout(road_pos_widget)
        
        relative_world_pos_widget = QWidget()
        relative_world_pos_form = QFormLayout(relative_world_pos_widget)
        
        relative_lane_pos_widget = QWidget()
        relative_lane_pos_form = QFormLayout(relative_lane_pos_widget)
        
        relative_road_pos_widget = QWidget()
        relative_road_pos_form = QFormLayout(relative_road_pos_widget)
        
        relative_object_pos_widget = QWidget()
        relative_object_pos_form = QFormLayout(relative_object_pos_widget)
        
        # WorldPositionフォーム
        def build_world_position_form():
            if action.position is None:
                action.position = WorldPosition(x=0.0, y=0.0)
            pos = action.position
            
            x_spin = QDoubleSpinBox()
            x_spin.setRange(-10000, 10000)
            if isinstance(pos.x, (int, float)):
                x_spin.setValue(pos.x)
            x_spin.valueChanged.connect(lambda v: setattr(pos, "x", v) or self.property_changed.emit())
            world_pos_form.addRow("X:", x_spin)
            
            y_spin = QDoubleSpinBox()
            y_spin.setRange(-10000, 10000)
            if isinstance(pos.y, (int, float)):
                y_spin.setValue(pos.y)
            y_spin.valueChanged.connect(lambda v: setattr(pos, "y", v) or self.property_changed.emit())
            world_pos_form.addRow("Y:", y_spin)
            
            z_spin = QDoubleSpinBox()
            z_spin.setRange(-100, 100)
            if isinstance(pos.z, (int, float)):
                z_spin.setValue(pos.z)
            z_spin.valueChanged.connect(lambda v: setattr(pos, "z", v) or self.property_changed.emit())
            world_pos_form.addRow("Z:", z_spin)
            
            h_spin = QDoubleSpinBox()
            h_spin.setRange(-360, 360)
            if isinstance(pos.h, (int, float)):
                h_spin.setValue(pos.h)
            h_spin.valueChanged.connect(lambda v: setattr(pos, "h", v) or self.property_changed.emit())
            world_pos_form.addRow("H (Heading):", h_spin)
            
            p_spin = QDoubleSpinBox()
            p_spin.setRange(-180, 180)
            if isinstance(pos.p, (int, float)):
                p_spin.setValue(pos.p)
            p_spin.valueChanged.connect(lambda v: setattr(pos, "p", v) or self.property_changed.emit())
            world_pos_form.addRow("P (Pitch):", p_spin)
            
            r_spin = QDoubleSpinBox()
            r_spin.setRange(-180, 180)
            if isinstance(pos.r, (int, float)):
                r_spin.setValue(pos.r)
            r_spin.valueChanged.connect(lambda v: setattr(pos, "r", v) or self.property_changed.emit())
            world_pos_form.addRow("R (Roll):", r_spin)
        
        # LanePositionフォーム
        def build_lane_position_form():
            if action.lane_position is None:
                action.lane_position = LanePosition(road_id="", lane_id="")
            lane_pos = action.lane_position
            
            road_edit = QLineEdit(lane_pos.road_id)
            road_edit.textChanged.connect(lambda text: setattr(lane_pos, "road_id", text) or self.property_changed.emit())
            lane_pos_form.addRow("Road ID:", road_edit)
            
            lane_edit = QLineEdit(str(lane_pos.lane_id))
            lane_edit.textChanged.connect(lambda text: setattr(lane_pos, "lane_id", text) or self.property_changed.emit())
            lane_pos_form.addRow("Lane ID:", lane_edit)
            
            s_spin = QDoubleSpinBox()
            s_spin.setRange(0, 100000)
            if isinstance(lane_pos.s, (int, float)):
                s_spin.setValue(lane_pos.s)
            s_spin.valueChanged.connect(lambda v: setattr(lane_pos, "s", v) or self.property_changed.emit())
            lane_pos_form.addRow("S:", s_spin)
            
            offset_spin = QDoubleSpinBox()
            offset_spin.setRange(-10, 10)
            if isinstance(lane_pos.offset, (int, float)):
                offset_spin.setValue(lane_pos.offset)
            offset_spin.valueChanged.connect(lambda v: setattr(lane_pos, "offset", v) or self.property_changed.emit())
            lane_pos_form.addRow("Offset:", offset_spin)
            
            # Orientation
            if lane_pos.orientation is None:
                lane_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(lane_pos_form, lane_pos.orientation, lambda: self.property_changed.emit())
        
        # RoadPositionフォーム
        def build_road_position_form():
            if action.road_position is None:
                action.road_position = RoadPosition(road_id="", s=0.0, t=0.0)
            road_pos = action.road_position
            
            road_edit = QLineEdit(road_pos.road_id)
            road_edit.textChanged.connect(lambda text: setattr(road_pos, "road_id", text) or self.property_changed.emit())
            road_pos_form.addRow("Road ID:", road_edit)
            
            s_spin = QDoubleSpinBox()
            s_spin.setRange(0, 100000)
            if isinstance(road_pos.s, (int, float)):
                s_spin.setValue(road_pos.s)
            s_spin.valueChanged.connect(lambda v: setattr(road_pos, "s", v) or self.property_changed.emit())
            road_pos_form.addRow("S:", s_spin)
            
            t_spin = QDoubleSpinBox()
            t_spin.setRange(-100, 100)
            if isinstance(road_pos.t, (int, float)):
                t_spin.setValue(road_pos.t)
            t_spin.valueChanged.connect(lambda v: setattr(road_pos, "t", v) or self.property_changed.emit())
            road_pos_form.addRow("T:", t_spin)
            
            # Orientation
            if road_pos.orientation is None:
                road_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(road_pos_form, road_pos.orientation, lambda: self.property_changed.emit())
        
        # RelativeWorldPositionフォーム
        def build_relative_world_position_form():
            entity_names = self._get_entity_names()
            if action.relative_world_position is None:
                action.relative_world_position = RelativeWorldPosition(
                    entity_ref=entity_names[0] if entity_names else "",
                    dx=0.0,
                    dy=0.0
                )
            rel_pos = action.relative_world_position
            
            entity_combo = QComboBox()
            entity_combo.addItems(entity_names if entity_names else [rel_pos.entity_ref])
            if rel_pos.entity_ref in entity_names:
                entity_combo.setCurrentText(rel_pos.entity_ref)
            elif entity_names:
                entity_combo.setCurrentIndex(0)
                rel_pos.entity_ref = entity_names[0]
            entity_combo.currentTextChanged.connect(
                lambda text: (setattr(rel_pos, "entity_ref", text), self.property_changed.emit())
            )
            relative_world_pos_form.addRow("Entity Ref:", entity_combo)
            
            dx_spin = QDoubleSpinBox()
            dx_spin.setRange(-10000, 10000)
            if isinstance(rel_pos.dx, (int, float)):
                dx_spin.setValue(rel_pos.dx)
            dx_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dx", v) or self.property_changed.emit())
            relative_world_pos_form.addRow("DX:", dx_spin)
            
            dy_spin = QDoubleSpinBox()
            dy_spin.setRange(-10000, 10000)
            if isinstance(rel_pos.dy, (int, float)):
                dy_spin.setValue(rel_pos.dy)
            dy_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dy", v) or self.property_changed.emit())
            relative_world_pos_form.addRow("DY:", dy_spin)
            
            dz_spin = QDoubleSpinBox()
            dz_spin.setRange(-100, 100)
            if isinstance(rel_pos.dz, (int, float)):
                dz_spin.setValue(rel_pos.dz)
            dz_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dz", v) or self.property_changed.emit())
            relative_world_pos_form.addRow("DZ:", dz_spin)
            
            # Orientation
            if rel_pos.orientation is None:
                rel_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(relative_world_pos_form, rel_pos.orientation, lambda: self.property_changed.emit())
        
        # RelativeLanePositionフォーム
        def build_relative_lane_position_form():
            entity_names = self._get_entity_names()
            if action.relative_lane_position is None:
                action.relative_lane_position = RelativeLanePosition(
                    entity_ref=entity_names[0] if entity_names else "",
                    d_lane=0
                )
            rel_pos = action.relative_lane_position
            
            entity_combo = QComboBox()
            entity_combo.addItems(entity_names if entity_names else [rel_pos.entity_ref])
            if rel_pos.entity_ref in entity_names:
                entity_combo.setCurrentText(rel_pos.entity_ref)
            elif entity_names:
                entity_combo.setCurrentIndex(0)
                rel_pos.entity_ref = entity_names[0]
            entity_combo.currentTextChanged.connect(
                lambda text: (setattr(rel_pos, "entity_ref", text), self.property_changed.emit())
            )
            relative_lane_pos_form.addRow("Entity Ref:", entity_combo)
            
            d_lane_spin = QSpinBox()
            d_lane_spin.setRange(-10, 10)
            if isinstance(rel_pos.d_lane, int):
                d_lane_spin.setValue(rel_pos.d_lane)
            d_lane_spin.valueChanged.connect(lambda v: setattr(rel_pos, "d_lane", v) or self.property_changed.emit())
            relative_lane_pos_form.addRow("D Lane:", d_lane_spin)
            
            ds_spin = QDoubleSpinBox()
            ds_spin.setRange(-100000, 100000)
            if rel_pos.ds is not None and isinstance(rel_pos.ds, (int, float)):
                ds_spin.setValue(rel_pos.ds)
            ds_spin.valueChanged.connect(lambda v: setattr(rel_pos, "ds", v) or self.property_changed.emit())
            relative_lane_pos_form.addRow("DS:", ds_spin)
            
            offset_spin = QDoubleSpinBox()
            offset_spin.setRange(-10, 10)
            if rel_pos.offset is not None and isinstance(rel_pos.offset, (int, float)):
                offset_spin.setValue(rel_pos.offset)
            offset_spin.valueChanged.connect(lambda v: setattr(rel_pos, "offset", v) or self.property_changed.emit())
            relative_lane_pos_form.addRow("Offset:", offset_spin)
            
            ds_lane_spin = QDoubleSpinBox()
            ds_lane_spin.setRange(-100000, 100000)
            if rel_pos.ds_lane is not None and isinstance(rel_pos.ds_lane, (int, float)):
                ds_lane_spin.setValue(rel_pos.ds_lane)
            ds_lane_spin.valueChanged.connect(lambda v: setattr(rel_pos, "ds_lane", v) or self.property_changed.emit())
            relative_lane_pos_form.addRow("DS Lane:", ds_lane_spin)
            
            # Orientation
            if rel_pos.orientation is None:
                rel_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(relative_lane_pos_form, rel_pos.orientation, lambda: self.property_changed.emit())
        
        # RelativeRoadPositionフォーム
        def build_relative_road_position_form():
            entity_names = self._get_entity_names()
            if action.relative_road_position is None:
                action.relative_road_position = RelativeRoadPosition(
                    entity_ref=entity_names[0] if entity_names else "",
                    ds=0.0,
                    dt=0.0
                )
            rel_pos = action.relative_road_position
            
            entity_combo = QComboBox()
            entity_combo.addItems(entity_names if entity_names else [rel_pos.entity_ref])
            if rel_pos.entity_ref in entity_names:
                entity_combo.setCurrentText(rel_pos.entity_ref)
            elif entity_names:
                entity_combo.setCurrentIndex(0)
                rel_pos.entity_ref = entity_names[0]
            entity_combo.currentTextChanged.connect(
                lambda text: (setattr(rel_pos, "entity_ref", text), self.property_changed.emit())
            )
            relative_road_pos_form.addRow("Entity Ref:", entity_combo)
            
            ds_spin = QDoubleSpinBox()
            ds_spin.setRange(-100000, 100000)
            if isinstance(rel_pos.ds, (int, float)):
                ds_spin.setValue(rel_pos.ds)
            ds_spin.valueChanged.connect(lambda v: setattr(rel_pos, "ds", v) or self.property_changed.emit())
            relative_road_pos_form.addRow("DS:", ds_spin)
            
            dt_spin = QDoubleSpinBox()
            dt_spin.setRange(-100, 100)
            if isinstance(rel_pos.dt, (int, float)):
                dt_spin.setValue(rel_pos.dt)
            dt_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dt", v) or self.property_changed.emit())
            relative_road_pos_form.addRow("DT:", dt_spin)
            
            # Orientation
            if rel_pos.orientation is None:
                rel_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(relative_road_pos_form, rel_pos.orientation, lambda: self.property_changed.emit())
        
        # RelativeObjectPositionフォーム
        def build_relative_object_position_form():
            entity_names = self._get_entity_names()
            if action.relative_object_position is None:
                action.relative_object_position = RelativeObjectPosition(
                    entity_ref=entity_names[0] if entity_names else "",
                    dx=0.0,
                    dy=0.0
                )
            rel_pos = action.relative_object_position
            
            entity_combo = QComboBox()
            entity_combo.addItems(entity_names if entity_names else [rel_pos.entity_ref])
            if rel_pos.entity_ref in entity_names:
                entity_combo.setCurrentText(rel_pos.entity_ref)
            elif entity_names:
                entity_combo.setCurrentIndex(0)
                rel_pos.entity_ref = entity_names[0]
            entity_combo.currentTextChanged.connect(
                lambda text: (setattr(rel_pos, "entity_ref", text), self.property_changed.emit())
            )
            relative_object_pos_form.addRow("Entity Ref:", entity_combo)
            
            dx_spin = QDoubleSpinBox()
            dx_spin.setRange(-10000, 10000)
            if isinstance(rel_pos.dx, (int, float)):
                dx_spin.setValue(rel_pos.dx)
            dx_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dx", v) or self.property_changed.emit())
            relative_object_pos_form.addRow("DX:", dx_spin)
            
            dy_spin = QDoubleSpinBox()
            dy_spin.setRange(-10000, 10000)
            if isinstance(rel_pos.dy, (int, float)):
                dy_spin.setValue(rel_pos.dy)
            dy_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dy", v) or self.property_changed.emit())
            relative_object_pos_form.addRow("DY:", dy_spin)
            
            dz_spin = QDoubleSpinBox()
            dz_spin.setRange(-100, 100)
            if rel_pos.dz is not None and isinstance(rel_pos.dz, (int, float)):
                dz_spin.setValue(rel_pos.dz)
            dz_spin.valueChanged.connect(lambda v: setattr(rel_pos, "dz", v) or self.property_changed.emit())
            relative_object_pos_form.addRow("DZ:", dz_spin)
            
            # Orientation
            if rel_pos.orientation is None:
                rel_pos.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
            self._build_orientation_form(relative_object_pos_form, rel_pos.orientation, lambda: self.property_changed.emit())
        
        # 各フォームを構築
        build_world_position_form()
        build_lane_position_form()
        build_road_position_form()
        build_relative_world_position_form()
        build_relative_lane_position_form()
        build_relative_road_position_form()
        build_relative_object_position_form()
        
        # Positionタイプ切り替え時の処理
        def on_position_type_changed(text: str):
            # すべてのウィジェットを非表示
            world_pos_widget.setVisible(False)
            lane_pos_widget.setVisible(False)
            road_pos_widget.setVisible(False)
            relative_world_pos_widget.setVisible(False)
            relative_lane_pos_widget.setVisible(False)
            relative_road_pos_widget.setVisible(False)
            relative_object_pos_widget.setVisible(False)
            
            # 既存のPositionをクリア
            action.position = None
            action.lane_position = None
            action.road_position = None
            action.relative_world_position = None
            action.relative_lane_position = None
            action.relative_road_position = None
            action.relative_object_position = None
            
            # 選択されたタイプに応じて表示とPositionオブジェクトを作成
            if text == "WorldPosition":
                world_pos_widget.setVisible(True)
                if action.position is None:
                    action.position = WorldPosition(x=0.0, y=0.0)
            elif text == "LanePosition":
                lane_pos_widget.setVisible(True)
                if action.lane_position is None:
                    action.lane_position = LanePosition(road_id="", lane_id="")
            elif text == "RoadPosition":
                road_pos_widget.setVisible(True)
                if action.road_position is None:
                    action.road_position = RoadPosition(road_id="", s=0.0, t=0.0)
            elif text == "RelativeWorldPosition":
                relative_world_pos_widget.setVisible(True)
                entity_names = self._get_entity_names()
                if action.relative_world_position is None:
                    action.relative_world_position = RelativeWorldPosition(
                        entity_ref=entity_names[0] if entity_names else "",
                        dx=0.0,
                        dy=0.0
                    )
            elif text == "RelativeLanePosition":
                relative_lane_pos_widget.setVisible(True)
                entity_names = self._get_entity_names()
                if action.relative_lane_position is None:
                    action.relative_lane_position = RelativeLanePosition(
                        entity_ref=entity_names[0] if entity_names else "",
                        d_lane=0
                    )
            elif text == "RelativeRoadPosition":
                relative_road_pos_widget.setVisible(True)
                entity_names = self._get_entity_names()
                if action.relative_road_position is None:
                    action.relative_road_position = RelativeRoadPosition(
                        entity_ref=entity_names[0] if entity_names else "",
                        ds=0.0,
                        dt=0.0
                    )
            elif text == "RelativeObjectPosition":
                relative_object_pos_widget.setVisible(True)
                entity_names = self._get_entity_names()
                if action.relative_object_position is None:
                    action.relative_object_position = RelativeObjectPosition(
                        entity_ref=entity_names[0] if entity_names else "",
                        dx=0.0,
                        dy=0.0
                    )
            
            self.property_changed.emit()
        
        position_type_combo.currentTextChanged.connect(on_position_type_changed)
        
        # 初期表示を設定
        on_position_type_changed(current_position_type)
        
        # 各ウィジェットをフォームに追加
        form.addRow(world_pos_widget)
        form.addRow(lane_pos_widget)
        form.addRow(road_pos_widget)
        form.addRow(relative_world_pos_widget)
        form.addRow(relative_lane_pos_widget)
        form.addRow(relative_road_pos_widget)
        form.addRow(relative_object_pos_widget)
        
        group.setLayout(form)
        self._form_layout.addRow(group)
    
    def _build_speed_action_form(self, action: SpeedAction):
        """SpeedAction用フォーム"""
        group = QGroupBox("SpeedAction")
        form = QFormLayout()
        
        # SpeedActionTargetタイプの選択
        target_type_group = QButtonGroup()
        absolute_radio = QRadioButton("AbsoluteTargetSpeed")
        relative_radio = QRadioButton("RelativeTargetSpeed")
        target_type_group.addButton(absolute_radio, 0)
        target_type_group.addButton(relative_radio, 1)
        
        # 現在の状態に応じてラジオボタンを選択
        if action.relative_target_speed is not None:
            relative_radio.setChecked(True)
        else:
            absolute_radio.setChecked(True)
        
        type_layout = QVBoxLayout()
        type_layout.addWidget(absolute_radio)
        type_layout.addWidget(relative_radio)
        form.addRow("ターゲットタイプ:", type_layout)
        
        # AbsoluteTargetSpeed用のUI
        absolute_widget = QWidget()
        absolute_form = QFormLayout(absolute_widget)
        
        # 数値入力用のSpinBox
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0, 200)
        if action.speed_target is not None:
            speed_spin.setValue(action.speed_target)
        else:
            speed_spin.setValue(0.0)
        speed_spin.setSuffix(" m/s")
        speed_spin.valueChanged.connect(
            lambda v: (
                setattr(action, "speed_target", v),
                setattr(action, "speed_target_str", None),
                setattr(action, "relative_target_speed", None),
                self.property_changed.emit()
            )
        )
        absolute_form.addRow("速度 (数値):", speed_spin)
        
        # パラメータ式入力用のLineEdit
        speed_expr_edit = QLineEdit()
        if action.speed_target_str is not None:
            speed_expr_edit.setText(action.speed_target_str)
        speed_expr_edit.setPlaceholderText("例: ${$EgoSpeed / 3.6}")
        speed_expr_edit.textChanged.connect(
            lambda text: (
                setattr(action, "speed_target_str", text if text else None),
                setattr(action, "speed_target", None),
                setattr(action, "relative_target_speed", None),
                self.property_changed.emit()
            )
        )
        absolute_form.addRow("速度 (パラメータ式):", speed_expr_edit)
        
        # RelativeTargetSpeed用のUI
        relative_widget = QWidget()
        relative_form = QFormLayout(relative_widget)
        
        # entityRef
        entity_ref_edit = QLineEdit()
        if action.relative_target_speed:
            entity_ref_edit.setText(action.relative_target_speed.entity_ref)
        entity_ref_edit.textChanged.connect(
            lambda text: (
                self._ensure_relative_target_speed(action),
                setattr(action.relative_target_speed, "entity_ref", text),
                self.property_changed.emit()
            )
        )
        relative_form.addRow("Entity Ref:", entity_ref_edit)
        
        # value（パラメータ式対応）
        relative_value_edit = QLineEdit()
        if action.relative_target_speed:
            relative_value_edit.setText(action.relative_target_speed.value)
        relative_value_edit.setPlaceholderText("例: $TargetSpeedFactor")
        relative_value_edit.textChanged.connect(
            lambda text: (
                self._ensure_relative_target_speed(action),
                setattr(action.relative_target_speed, "value", text),
                self.property_changed.emit()
            )
        )
        relative_form.addRow("Value:", relative_value_edit)
        
        # speedTargetValueType
        value_type_combo = QComboBox()
        value_type_combo.addItems(["delta", "factor"])
        if action.relative_target_speed:
            value_type_combo.setCurrentText(action.relative_target_speed.speed_target_value_type)
        value_type_combo.currentTextChanged.connect(
            lambda text: (
                self._ensure_relative_target_speed(action),
                setattr(action.relative_target_speed, "speed_target_value_type", text),
                self.property_changed.emit()
            )
        )
        relative_form.addRow("Value Type:", value_type_combo)
        
        # continuous
        continuous_check = QCheckBox()
        if action.relative_target_speed:
            continuous_check.setChecked(action.relative_target_speed.continuous)
        continuous_check.stateChanged.connect(
            lambda state: (
                self._ensure_relative_target_speed(action),
                setattr(action.relative_target_speed, "continuous", state == Qt.CheckState.Checked),
                self.property_changed.emit()
            )
        )
        relative_form.addRow("Continuous:", continuous_check)
        
        # ラジオボタンの切り替えで表示を変更
        def on_target_type_changed(button_id):
            if button_id == 0:  # AbsoluteTargetSpeed
                absolute_widget.setVisible(True)
                relative_widget.setVisible(False)
                # RelativeTargetSpeedをクリア
                if action.relative_target_speed is not None:
                    action.relative_target_speed = None
                    self.property_changed.emit()
            else:  # RelativeTargetSpeed
                absolute_widget.setVisible(False)
                relative_widget.setVisible(True)
                # AbsoluteTargetSpeedをクリア
                if action.speed_target is not None or action.speed_target_str is not None:
                    action.speed_target = None
                    action.speed_target_str = None
                    self.property_changed.emit()
                # RelativeTargetSpeedを確実に作成
                self._ensure_relative_target_speed(action)
        
        target_type_group.buttonClicked.connect(lambda btn: on_target_type_changed(target_type_group.id(btn)))
        # 初期表示を設定
        on_target_type_changed(0 if absolute_radio.isChecked() else 1)
        
        form.addRow(absolute_widget)
        form.addRow(relative_widget)
        
        # Dynamics
        if action.dynamics:
            self._build_dynamics_form(form, action.dynamics)
        else:
            # Dynamicsを新規作成
            action.dynamics = Dynamics()
            self._build_dynamics_form(form, action.dynamics)
        
        group.setLayout(form)
        self._form_layout.addRow(group)
    
    def _ensure_relative_target_speed(self, action: SpeedAction):
        """RelativeTargetSpeedが存在することを保証"""
        if action.relative_target_speed is None:
            action.relative_target_speed = RelativeTargetSpeed(
                entity_ref="",
                value="",
                speed_target_value_type="delta",
                continuous=True
            )
    
    def _build_lane_change_action_form(self, action: LaneChangeAction):
        """LaneChangeAction用フォーム"""
        group = QGroupBox("LaneChangeAction")
        form = QFormLayout()
        
        lane_spin = QSpinBox()
        lane_spin.setRange(-10, 10)
        lane_spin.setValue(action.target_lane)
        lane_spin.valueChanged.connect(lambda v: setattr(action, "target_lane", v) or self.property_changed.emit())
        form.addRow("ターゲットレーン:", lane_spin)
        
        if action.dynamics:
            self._build_dynamics_form(form, action.dynamics)
        else:
            action.dynamics = Dynamics()
            self._build_dynamics_form(form, action.dynamics)
        
        group.setLayout(form)
        self._form_layout.addRow(group)
    
    def _build_dynamics_form(self, parent_layout: QFormLayout, dynamics: Dynamics):
        """Dynamics用フォーム"""
        dim_combo = QComboBox()
        dim_combo.addItems([d.value for d in DynamicsDimension])
        dim_combo.setCurrentText(dynamics.dynamics_dimension.value)
        dim_combo.currentTextChanged.connect(
            lambda text: setattr(dynamics, "dynamics_dimension", DynamicsDimension(text)) or self.property_changed.emit()
        )
        parent_layout.addRow("次元:", dim_combo)
        
        shape_combo = QComboBox()
        shape_combo.addItems([s.value for s in DynamicsShape])
        shape_combo.setCurrentText(dynamics.dynamics_shape.value)
        shape_combo.currentTextChanged.connect(
            lambda text: setattr(dynamics, "dynamics_shape", DynamicsShape(text)) or self.property_changed.emit()
        )
        parent_layout.addRow("形状:", shape_combo)
        
        if dynamics.value is not None:
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 1000)
            value_spin.setValue(dynamics.value)
            value_spin.valueChanged.connect(lambda v: setattr(dynamics, "value", v) or self.property_changed.emit())
            parent_layout.addRow("値:", value_spin)
    
    def _build_event_form(self, event: Event):
        """Event用フォーム"""
        name_edit = QLineEdit(event.name)
        name_edit.textChanged.connect(lambda text: setattr(event, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
        
        priority_combo = QComboBox()
        priority_combo.addItems([r.value for r in Rule])
        priority_combo.setCurrentText(event.priority.value)
        priority_combo.currentTextChanged.connect(
            lambda text: setattr(event, "priority", Rule(text)) or self.property_changed.emit()
        )
        self._form_layout.addRow("優先度:", priority_combo)
    
    def _build_condition_form(self, cond: Condition):
        """Condition用フォーム（Conditionを直接選択した場合）"""
        # ByValueConditionかByEntityConditionかを判定
        is_by_value = (cond.simulation_time_condition is not None or
                      cond.parameter_condition is not None or
                      cond.storyboard_element_state_condition is not None or
                      cond.time_of_day_condition is not None or
                      cond.user_defined_value_condition is not None or
                      cond.traffic_signal_condition is not None or
                      cond.traffic_signal_controller_condition is not None or
                      cond.variable_condition is not None)
        is_by_entity = cond.by_entity_condition is not None
        
        # Conditionタイプを判定
        current_condition_category = None
        current_condition_type = None
        
        if is_by_value:
            current_condition_category = "ByValueCondition"
            # XSDの定義順序に合わせて判定（choice要素なので、1つしか存在しない）
            if cond.parameter_condition:
                current_condition_type = "ParameterCondition"
            elif cond.time_of_day_condition:
                current_condition_type = "TimeOfDayCondition"
            elif cond.simulation_time_condition:
                current_condition_type = "SimulationTimeCondition"
            elif cond.storyboard_element_state_condition:
                current_condition_type = "StoryboardElementStateCondition"
            elif cond.user_defined_value_condition:
                current_condition_type = "UserDefinedValueCondition"
            elif cond.traffic_signal_condition:
                current_condition_type = "TrafficSignalCondition"
            elif cond.traffic_signal_controller_condition:
                current_condition_type = "TrafficSignalControllerCondition"
            elif cond.variable_condition:
                current_condition_type = "VariableCondition"
            else:
                current_condition_type = "SimulationTimeCondition"  # デフォルト
        elif is_by_entity:
            current_condition_category = "ByEntityCondition"
            # XSDの定義順序に合わせて判定（choice要素なので、1つしか存在しない）
            if cond.by_entity_condition.end_of_road_condition:
                current_condition_type = "EndOfRoadCondition"
            elif cond.by_entity_condition.collision_condition:
                current_condition_type = "CollisionCondition"
            elif cond.by_entity_condition.offroad_condition:
                current_condition_type = "OffroadCondition"
            elif cond.by_entity_condition.entity_condition:  # TimeHeadwayCondition
                current_condition_type = "TimeHeadwayCondition"
            elif cond.by_entity_condition.time_to_collision_condition:
                current_condition_type = "TimeToCollisionCondition"
            elif cond.by_entity_condition.acceleration_condition:
                current_condition_type = "AccelerationCondition"
            elif cond.by_entity_condition.stand_still_condition:
                current_condition_type = "StandStillCondition"
            elif cond.by_entity_condition.speed_condition:
                current_condition_type = "SpeedCondition"
            elif cond.by_entity_condition.relative_speed_condition:
                current_condition_type = "RelativeSpeedCondition"
            elif cond.by_entity_condition.traveled_distance_condition:
                current_condition_type = "TraveledDistanceCondition"
            elif cond.by_entity_condition.reach_position_condition:
                current_condition_type = "ReachPositionCondition"
            elif cond.by_entity_condition.distance_condition:
                current_condition_type = "DistanceCondition"
            elif cond.by_entity_condition.relative_distance_condition:
                current_condition_type = "RelativeDistanceCondition"
            elif cond.by_entity_condition.relative_clearance_condition:
                current_condition_type = "RelativeClearanceCondition"
            else:
                current_condition_type = "TimeHeadwayCondition"  # デフォルト
        else:
            current_condition_category = "ByValueCondition"  # デフォルト
            current_condition_type = "SimulationTimeCondition"  # デフォルト
        
        # Condition名
        name_edit = QLineEdit(cond.name if cond.name else "")
        name_edit.setPlaceholderText("Condition名（オプション）")
        name_edit.textChanged.connect(lambda text: setattr(cond, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
        
        # delay（変数対応）
        delay_widget = self._build_value_input_widget(cond, "delay", "Delay:", " s", 0, 10000, allow_string=True)
        self._form_layout.addRow("Delay:", delay_widget)
        
        # conditionEdge（変数対応）
        condition_edge_combo = QComboBox()
        condition_edge_combo.addItems(["rising", "falling", "none", "risingOrFalling"])
        condition_edge_combo.setEditable(True)  # 変数入力も可能にする
        condition_edge_combo.setCurrentText(str(cond.condition_edge))
        condition_edge_combo.currentTextChanged.connect(
            lambda text: (setattr(cond, "condition_edge", text), self.property_changed.emit())
        )
        condition_edge_combo.lineEdit().setPlaceholderText("例: rising または ${ConditionEdge}")
        self._form_layout.addRow("Condition Edge:", condition_edge_combo)
        
        # Conditionカテゴリ選択（ByValueCondition / ByEntityCondition）
        condition_category_combo = QComboBox()
        condition_category_combo.addItems(["ByValueCondition", "ByEntityCondition"])
        condition_category_combo.setCurrentText(current_condition_category)
        self._form_layout.addRow("Condition Category:", condition_category_combo)
        
        # Conditionタイプ選択ComboBox
        condition_type_combo = QComboBox()
        self._form_layout.addRow("Condition Type:", condition_type_combo)
        
        # 各Conditionフォーム用のウィジェット
        condition_widgets = {}
        
        # Conditionカテゴリ切り替え時の処理
        def on_condition_category_changed(category: str):
            # 既存のConditionをクリア
            cond.simulation_time_condition = None
            cond.parameter_condition = None
            cond.storyboard_element_state_condition = None
            cond.time_of_day_condition = None
            cond.user_defined_value_condition = None
            cond.traffic_signal_condition = None
            cond.traffic_signal_controller_condition = None
            cond.variable_condition = None
            if cond.by_entity_condition:
                cond.by_entity_condition.entity_condition = None
                cond.by_entity_condition.distance_condition = None
                cond.by_entity_condition.relative_distance_condition = None
                cond.by_entity_condition.speed_condition = None
                cond.by_entity_condition.relative_speed_condition = None
                cond.by_entity_condition.traveled_distance_condition = None
                cond.by_entity_condition.reach_position_condition = None
            
            # Conditionタイプリストを更新
            condition_type_combo.clear()
            if category == "ByValueCondition":
                condition_type_combo.addItems([
                    "SimulationTimeCondition",
                    "ParameterCondition",
                    "StoryboardElementStateCondition",
                    "TimeOfDayCondition",
                    "UserDefinedValueCondition",
                    "TrafficSignalCondition",
                    "TrafficSignalControllerCondition",
                    "VariableCondition"
                ])
                condition_type_combo.setCurrentText("SimulationTimeCondition")
            else:  # ByEntityCondition
                condition_type_combo.addItems([
                    "TimeHeadwayCondition",
                    "DistanceCondition",
                    "RelativeDistanceCondition",
                    "SpeedCondition",
                    "RelativeSpeedCondition",
                    "TraveledDistanceCondition",
                    "ReachPositionCondition"
                ])
                condition_type_combo.setCurrentText("TimeHeadwayCondition")
            
            # すべてのウィジェットを非表示
            for widget in condition_widgets.values():
                widget.setVisible(False)
            
            self.property_changed.emit()
        
        # Conditionタイプ切り替え時の処理
        def on_condition_type_changed(text: str):
            # すべてのウィジェットを非表示
            for widget in condition_widgets.values():
                widget.setVisible(False)
            
            category = condition_category_combo.currentText()
            
            # 既存のConditionをクリア
            if category == "ByValueCondition":
                cond.simulation_time_condition = None
                cond.parameter_condition = None
                cond.storyboard_element_state_condition = None
                cond.time_of_day_condition = None
                cond.user_defined_value_condition = None
                cond.traffic_signal_condition = None
                cond.traffic_signal_controller_condition = None
                cond.variable_condition = None
            else:  # ByEntityCondition
                if cond.by_entity_condition:
                    cond.by_entity_condition.entity_condition = None
                    cond.by_entity_condition.distance_condition = None
                    cond.by_entity_condition.relative_distance_condition = None
                    cond.by_entity_condition.speed_condition = None
                    cond.by_entity_condition.relative_speed_condition = None
                    cond.by_entity_condition.traveled_distance_condition = None
                    cond.by_entity_condition.reach_position_condition = None
            
            # 選択されたタイプに応じて表示とConditionオブジェクトを作成
            new_widget = None
            if category == "ByValueCondition":
                if text == "SimulationTimeCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_simulation_time_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "ParameterCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_parameter_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "StoryboardElementStateCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_storyboard_element_state_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TimeOfDayCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_time_of_day_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "UserDefinedValueCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_user_defined_value_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TrafficSignalCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traffic_signal_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TrafficSignalControllerCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traffic_signal_controller_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "VariableCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_variable_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
            else:  # ByEntityCondition
                if text == "TimeHeadwayCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_time_headway_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "DistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "RelativeDistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_relative_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "SpeedCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_speed_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "RelativeSpeedCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_relative_speed_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TraveledDistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traveled_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "ReachPositionCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_reach_position_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
            
            # 新しいウィジェットが作成された場合、レイアウトに追加
            if new_widget is not None:
                self._form_layout.addRow(new_widget)
            
            self.property_changed.emit()
        
        condition_category_combo.currentTextChanged.connect(on_condition_category_changed)
        condition_type_combo.currentTextChanged.connect(on_condition_type_changed)
        
        # 初期表示を設定
        on_condition_category_changed(current_condition_category)
        condition_type_combo.setCurrentText(current_condition_type)
        on_condition_type_changed(current_condition_type)
        
        # 初期化時に作成されたウィジェットをフォームに追加
        for widget in condition_widgets.values():
            self._form_layout.addRow(widget)
    
    def _build_start_trigger_form(self, trigger: StartTrigger):
        """StartTrigger用フォーム"""
        if not trigger.condition_groups:
            # ConditionGroupが存在しない場合は作成
            trigger.condition_groups = [ConditionGroup(conditions=[Condition()])]
        
        cg = trigger.condition_groups[0]
        if not cg.conditions:
            # Conditionが存在しない場合は作成
            cg.conditions = [Condition()]
        
        cond = cg.conditions[0]
        
        # Condition名
        name_edit = QLineEdit(cond.name if cond.name else "")
        name_edit.setPlaceholderText("Condition名（オプション）")
        name_edit.textChanged.connect(lambda text: setattr(cond, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
        
        # delay（変数対応）
        delay_widget = self._build_value_input_widget(cond, "delay", "Delay:", " s", 0, 10000, allow_string=True)
        self._form_layout.addRow("Delay:", delay_widget)
        
        # conditionEdge（変数対応）
        condition_edge_combo = QComboBox()
        condition_edge_combo.addItems(["rising", "falling", "none", "risingOrFalling"])
        condition_edge_combo.setEditable(True)  # 変数入力も可能にする
        condition_edge_combo.setCurrentText(str(cond.condition_edge))
        condition_edge_combo.currentTextChanged.connect(
            lambda text: (setattr(cond, "condition_edge", text), self.property_changed.emit())
        )
        condition_edge_combo.lineEdit().setPlaceholderText("例: rising または ${ConditionEdge}")
        self._form_layout.addRow("Condition Edge:", condition_edge_combo)
        
        # ByValueConditionかByEntityConditionかを判定
        is_by_value = (cond.simulation_time_condition is not None or
                      cond.parameter_condition is not None or
                      cond.storyboard_element_state_condition is not None or
                      cond.time_of_day_condition is not None or
                      cond.user_defined_value_condition is not None or
                      cond.traffic_signal_condition is not None or
                      cond.traffic_signal_controller_condition is not None or
                      cond.variable_condition is not None)
        is_by_entity = cond.by_entity_condition is not None
        
        # Conditionタイプを判定
        current_condition_category = None
        current_condition_type = None
        
        if is_by_value:
            current_condition_category = "ByValueCondition"
            # XSDの定義順序に合わせて判定（choice要素なので、1つしか存在しない）
            if cond.parameter_condition:
                current_condition_type = "ParameterCondition"
            elif cond.time_of_day_condition:
                current_condition_type = "TimeOfDayCondition"
            elif cond.simulation_time_condition:
                current_condition_type = "SimulationTimeCondition"
            elif cond.storyboard_element_state_condition:
                current_condition_type = "StoryboardElementStateCondition"
            elif cond.user_defined_value_condition:
                current_condition_type = "UserDefinedValueCondition"
            elif cond.traffic_signal_condition:
                current_condition_type = "TrafficSignalCondition"
            elif cond.traffic_signal_controller_condition:
                current_condition_type = "TrafficSignalControllerCondition"
            elif cond.variable_condition:
                current_condition_type = "VariableCondition"
            else:
                current_condition_type = "SimulationTimeCondition"  # デフォルト
        elif is_by_entity:
            current_condition_category = "ByEntityCondition"
            # XSDの定義順序に合わせて判定（choice要素なので、1つしか存在しない）
            if cond.by_entity_condition.end_of_road_condition:
                current_condition_type = "EndOfRoadCondition"
            elif cond.by_entity_condition.collision_condition:
                current_condition_type = "CollisionCondition"
            elif cond.by_entity_condition.offroad_condition:
                current_condition_type = "OffroadCondition"
            elif cond.by_entity_condition.entity_condition:  # TimeHeadwayCondition
                current_condition_type = "TimeHeadwayCondition"
            elif cond.by_entity_condition.time_to_collision_condition:
                current_condition_type = "TimeToCollisionCondition"
            elif cond.by_entity_condition.acceleration_condition:
                current_condition_type = "AccelerationCondition"
            elif cond.by_entity_condition.stand_still_condition:
                current_condition_type = "StandStillCondition"
            elif cond.by_entity_condition.speed_condition:
                current_condition_type = "SpeedCondition"
            elif cond.by_entity_condition.relative_speed_condition:
                current_condition_type = "RelativeSpeedCondition"
            elif cond.by_entity_condition.traveled_distance_condition:
                current_condition_type = "TraveledDistanceCondition"
            elif cond.by_entity_condition.reach_position_condition:
                current_condition_type = "ReachPositionCondition"
            elif cond.by_entity_condition.distance_condition:
                current_condition_type = "DistanceCondition"
            elif cond.by_entity_condition.relative_distance_condition:
                current_condition_type = "RelativeDistanceCondition"
            elif cond.by_entity_condition.relative_clearance_condition:
                current_condition_type = "RelativeClearanceCondition"
            else:
                current_condition_type = "TimeHeadwayCondition"  # デフォルト
        else:
            current_condition_category = "ByValueCondition"  # デフォルト
            current_condition_type = "SimulationTimeCondition"  # デフォルト
        
        # Conditionカテゴリ選択（ByValueCondition / ByEntityCondition）
        condition_category_combo = QComboBox()
        condition_category_combo.addItems(["ByValueCondition", "ByEntityCondition"])
        condition_category_combo.setCurrentText(current_condition_category)
        self._form_layout.addRow("Condition Category:", condition_category_combo)
        
        # Conditionタイプ選択ComboBox
        condition_type_combo = QComboBox()
        self._form_layout.addRow("Condition Type:", condition_type_combo)
        
        # 各Conditionフォーム用のウィジェット
        condition_widgets = {}
        
        # Conditionカテゴリ切り替え時の処理
        def on_condition_category_changed(category: str):
            # 既存のConditionをクリア
            cond.simulation_time_condition = None
            cond.parameter_condition = None
            cond.storyboard_element_state_condition = None
            cond.time_of_day_condition = None
            cond.user_defined_value_condition = None
            cond.traffic_signal_condition = None
            cond.traffic_signal_controller_condition = None
            cond.variable_condition = None
            if cond.by_entity_condition:
                cond.by_entity_condition.entity_condition = None
                cond.by_entity_condition.distance_condition = None
                cond.by_entity_condition.relative_distance_condition = None
                cond.by_entity_condition.speed_condition = None
                cond.by_entity_condition.relative_speed_condition = None
                cond.by_entity_condition.traveled_distance_condition = None
                cond.by_entity_condition.reach_position_condition = None
            
            # Conditionタイプリストを更新
            condition_type_combo.clear()
            if category == "ByValueCondition":
                condition_type_combo.addItems([
                    "SimulationTimeCondition",
                    "ParameterCondition",
                    "StoryboardElementStateCondition",
                    "TimeOfDayCondition",
                    "UserDefinedValueCondition",
                    "TrafficSignalCondition",
                    "TrafficSignalControllerCondition",
                    "VariableCondition"
                ])
                condition_type_combo.setCurrentText("SimulationTimeCondition")
            else:  # ByEntityCondition
                condition_type_combo.addItems([
                    "TimeHeadwayCondition",
                    "DistanceCondition",
                    "RelativeDistanceCondition",
                    "SpeedCondition",
                    "RelativeSpeedCondition",
                    "TraveledDistanceCondition",
                    "ReachPositionCondition"
                ])
                condition_type_combo.setCurrentText("TimeHeadwayCondition")
            
            # すべてのウィジェットを非表示
            for widget in condition_widgets.values():
                widget.setVisible(False)
            
            self.property_changed.emit()
        
        # Conditionタイプ切り替え時の処理
        def on_condition_type_changed(text: str):
            # すべてのウィジェットを非表示
            for widget in condition_widgets.values():
                widget.setVisible(False)
            
            category = condition_category_combo.currentText()
            
            # 既存のConditionをクリア
            if category == "ByValueCondition":
                cond.simulation_time_condition = None
                cond.parameter_condition = None
                cond.storyboard_element_state_condition = None
                cond.time_of_day_condition = None
                cond.user_defined_value_condition = None
                cond.traffic_signal_condition = None
                cond.traffic_signal_controller_condition = None
                cond.variable_condition = None
            else:  # ByEntityCondition
                if cond.by_entity_condition:
                    cond.by_entity_condition.entity_condition = None
                    cond.by_entity_condition.distance_condition = None
                    cond.by_entity_condition.relative_distance_condition = None
                    cond.by_entity_condition.speed_condition = None
                    cond.by_entity_condition.relative_speed_condition = None
                    cond.by_entity_condition.traveled_distance_condition = None
                    cond.by_entity_condition.reach_position_condition = None
            
            # 選択されたタイプに応じて表示とConditionオブジェクトを作成
            new_widget = None
            if category == "ByValueCondition":
                if text == "SimulationTimeCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_simulation_time_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "ParameterCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_parameter_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "StoryboardElementStateCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_storyboard_element_state_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TimeOfDayCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_time_of_day_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "UserDefinedValueCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_user_defined_value_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TrafficSignalCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traffic_signal_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TrafficSignalControllerCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traffic_signal_controller_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "VariableCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_variable_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
            else:  # ByEntityCondition
                if text == "TimeHeadwayCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_time_headway_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "DistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "RelativeDistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_relative_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "SpeedCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_speed_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "RelativeSpeedCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_relative_speed_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "TraveledDistanceCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_traveled_distance_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
                elif text == "ReachPositionCondition":
                    if text not in condition_widgets:
                        new_widget = self._build_reach_position_condition_form(cond)
                        condition_widgets[text] = new_widget
                    condition_widgets[text].setVisible(True)
            
            # 新しいウィジェットが作成された場合、レイアウトに追加
            if new_widget is not None:
                self._form_layout.addRow(new_widget)
            
            self.property_changed.emit()
        
        condition_category_combo.currentTextChanged.connect(on_condition_category_changed)
        condition_type_combo.currentTextChanged.connect(on_condition_type_changed)
        
        # 初期表示を設定
        on_condition_category_changed(current_condition_category)
        condition_type_combo.setCurrentText(current_condition_type)
        on_condition_type_changed(current_condition_type)
        
        # 初期化時に作成されたウィジェットをフォームに追加
        for widget in condition_widgets.values():
            self._form_layout.addRow(widget)
    
    def _build_story_form(self, story: Story):
        """Story用フォーム"""
        name_edit = QLineEdit(story.name)
        name_edit.textChanged.connect(lambda text: setattr(story, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
    
    def _build_act_form(self, act: Act):
        """Act用フォーム"""
        name_edit = QLineEdit(act.name)
        name_edit.textChanged.connect(lambda text: setattr(act, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
    
    def _build_maneuver_form(self, maneuver: Maneuver):
        """Maneuver用フォーム"""
        name_edit = QLineEdit(maneuver.name)
        name_edit.textChanged.connect(lambda text: setattr(maneuver, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
    
    def _build_action_form(self, action: Action):
        """Action用フォーム"""
        name_edit = QLineEdit(action.name)
        name_edit.textChanged.connect(lambda text: setattr(action, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
    
    def _build_private_form(self, private: Private):
        """Private用フォーム"""
        entity_ref_edit = QLineEdit(private.entity_ref)
        entity_ref_edit.textChanged.connect(lambda text: setattr(private, "entity_ref", text) or self.property_changed.emit())
        self._form_layout.addRow("Entity Ref:", entity_ref_edit)
    
    def _get_entity_names(self) -> list[str]:
        """シナリオ内のエンティティ名一覧を取得"""
        entity_names = []
        if self._scenario and self._scenario.entities:
            for scenario_obj in self._scenario.entities.scenario_objects:
                entity_names.append(scenario_obj.name)
        return sorted(entity_names)
    
    def _build_value_input_widget(self, obj, attr_name: str, label: str, suffix: str = "", min_val: float = 0, max_val: float = 10000, allow_string: bool = False) -> QWidget:
        """数値または変数（文字列）を入力するウィジェットを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        current_value = getattr(obj, attr_name)
        
        # 数値入力用のSpinBox
        value_spin = QDoubleSpinBox()
        value_spin.setRange(min_val, max_val)
        value_spin.setSuffix(suffix)
        if isinstance(current_value, (int, float)):
            value_spin.setValue(current_value)
        value_spin.valueChanged.connect(
            lambda v: (setattr(obj, attr_name, v), self.property_changed.emit())
        )
        
        # 変数入力用のLineEdit
        value_edit = QLineEdit()
        if isinstance(current_value, str):
            value_edit.setText(current_value)
        value_edit.setPlaceholderText("例: ${StartTime} または $VariableName")
        value_edit.textChanged.connect(
            lambda text: (setattr(obj, attr_name, text), self.property_changed.emit())
        )
        
        # 数値/変数切り替え用のラジオボタン
        if allow_string:
            type_group = QButtonGroup()
            numeric_radio = QRadioButton("数値")
            variable_radio = QRadioButton("変数/パラメータ式")
            type_group.addButton(numeric_radio, 0)
            type_group.addButton(variable_radio, 1)
            
            # 現在の値に応じてラジオボタンを選択
            if isinstance(current_value, (int, float)):
                numeric_radio.setChecked(True)
                value_spin.setVisible(True)
                value_edit.setVisible(False)
            else:
                variable_radio.setChecked(True)
                value_spin.setVisible(False)
                value_edit.setVisible(True)
            
            def on_type_changed(button_id):
                if button_id == 0:  # 数値
                    value_spin.setVisible(True)
                    value_edit.setVisible(False)
                    # 現在の値を取得して変換を試みる
                    current = getattr(obj, attr_name)
                    if isinstance(current, str):
                        try:
                            val = float(current)
                            value_spin.setValue(val)
                            setattr(obj, attr_name, val)
                        except (ValueError, TypeError):
                            value_spin.setValue(0.0)
                            setattr(obj, attr_name, 0.0)
                else:  # 変数
                    value_spin.setVisible(False)
                    value_edit.setVisible(True)
                    # 現在の値を取得して変換を試みる
                    current = getattr(obj, attr_name)
                    if isinstance(current, (int, float)):
                        value_edit.setText("")
                        setattr(obj, attr_name, "")
                self.property_changed.emit()
            
            type_group.buttonClicked.connect(lambda btn: on_type_changed(type_group.id(btn)))
            
            type_layout = QHBoxLayout()
            type_layout.addWidget(numeric_radio)
            type_layout.addWidget(variable_radio)
            layout.addLayout(type_layout)
        
        layout.addWidget(value_spin)
        layout.addWidget(value_edit)
        
        if not allow_string:
            value_edit.setVisible(False)
        
        return widget
    
    def _build_simulation_time_condition_form(self, cond: Condition) -> QWidget:
        """SimulationTimeCondition用フォーム"""
        if cond.simulation_time_condition is None:
            cond.simulation_time_condition = SimulationTimeCondition(value=0.0, rule="greaterThan")
        
        stc = cond.simulation_time_condition
        group = QGroupBox("SimulationTimeCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # value（数値または変数対応）
        value_widget = self._build_value_input_widget(stc, "value", "時間:", " s", 0, 10000, allow_string=True)
        form.addRow("時間:", value_widget)
        
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(stc.rule)
        rule_combo.currentTextChanged.connect(lambda text: setattr(stc, "rule", text) or self.property_changed.emit())
        form.addRow("ルール:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_parameter_condition_form(self, cond: Condition) -> QWidget:
        """ParameterCondition用フォーム"""
        if cond.parameter_condition is None:
            cond.parameter_condition = ParameterCondition(parameter_ref="", value=0.0, rule="greaterThan")
        
        pc = cond.parameter_condition
        group = QGroupBox("ParameterCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # parameterRef
        param_ref_edit = QLineEdit(pc.parameter_ref)
        param_ref_edit.setPlaceholderText("例: StartTime")
        param_ref_edit.textChanged.connect(
            lambda text: (setattr(pc, "parameter_ref", text), self.property_changed.emit())
        )
        form.addRow("Parameter Ref:", param_ref_edit)
        
        # value（String型なので、常に文字列として扱う）
        value_edit = QLineEdit(str(pc.value))
        value_edit.setPlaceholderText("例: 1.0 または ${ParameterValue}")
        value_edit.textChanged.connect(
            lambda text: (setattr(pc, "value", text), self.property_changed.emit())
        )
        form.addRow("Value:", value_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(pc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(pc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_storyboard_element_state_condition_form(self, cond: Condition) -> QWidget:
        """StoryboardElementStateCondition用フォーム"""
        if cond.storyboard_element_state_condition is None:
            cond.storyboard_element_state_condition = StoryboardElementStateCondition(
                storyboard_element_type="maneuver",
                storyboard_element_ref="",
                state="endTransition"
            )
        
        sec = cond.storyboard_element_state_condition
        group = QGroupBox("StoryboardElementStateCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # storyboardElementType
        element_type_combo = QComboBox()
        element_type_combo.addItems(["act", "action", "event", "maneuver", "maneuverGroup", "story"])
        element_type_combo.setCurrentText(sec.storyboard_element_type)
        element_type_combo.currentTextChanged.connect(
            lambda text: (setattr(sec, "storyboard_element_type", text), self.property_changed.emit())
        )
        form.addRow("Storyboard Element Type:", element_type_combo)
        
        # storyboardElementRef
        element_ref_edit = QLineEdit(sec.storyboard_element_ref)
        element_ref_edit.setPlaceholderText("例: CutInManeuver")
        element_ref_edit.textChanged.connect(
            lambda text: (setattr(sec, "storyboard_element_ref", text), self.property_changed.emit())
        )
        form.addRow("Storyboard Element Ref:", element_ref_edit)
        
        # state
        state_combo = QComboBox()
        state_combo.addItems(["startTransition", "endTransition", "stopTransition", "skipTransition", "completeState"])
        state_combo.setCurrentText(sec.state)
        state_combo.currentTextChanged.connect(
            lambda text: (setattr(sec, "state", text), self.property_changed.emit())
        )
        form.addRow("State:", state_combo)
        
        group.setLayout(form)
        return group
    
    def _build_time_of_day_condition_form(self, cond: Condition) -> QWidget:
        """TimeOfDayCondition用フォーム"""
        if cond.time_of_day_condition is None:
            cond.time_of_day_condition = TimeOfDayCondition(date_time="2024-01-01T00:00:00", rule="greaterThan")
        
        toc = cond.time_of_day_condition
        group = QGroupBox("TimeOfDayCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # dateTime（文字列または変数）
        date_time_edit = QLineEdit(str(toc.date_time))
        date_time_edit.setPlaceholderText("例: 2024-01-01T00:00:00 または ${StartDateTime}")
        date_time_edit.textChanged.connect(
            lambda text: (setattr(toc, "date_time", text), self.property_changed.emit())
        )
        form.addRow("Date Time:", date_time_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(toc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(toc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_user_defined_value_condition_form(self, cond: Condition) -> QWidget:
        """UserDefinedValueCondition用フォーム"""
        if cond.user_defined_value_condition is None:
            cond.user_defined_value_condition = UserDefinedValueCondition(name="", value="", rule="greaterThan")
        
        udvc = cond.user_defined_value_condition
        group = QGroupBox("UserDefinedValueCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # name
        name_edit = QLineEdit(udvc.name)
        name_edit.setPlaceholderText("例: CustomSignal")
        name_edit.textChanged.connect(
            lambda text: (setattr(udvc, "name", text), self.property_changed.emit())
        )
        form.addRow("Name:", name_edit)
        
        # value
        value_edit = QLineEdit(udvc.value)
        value_edit.setPlaceholderText("例: 1.0 または ${CustomValue}")
        value_edit.textChanged.connect(
            lambda text: (setattr(udvc, "value", text), self.property_changed.emit())
        )
        form.addRow("Value:", value_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(udvc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(udvc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_traffic_signal_condition_form(self, cond: Condition) -> QWidget:
        """TrafficSignalCondition用フォーム"""
        if cond.traffic_signal_condition is None:
            cond.traffic_signal_condition = TrafficSignalCondition(name="", state="")
        
        tsc = cond.traffic_signal_condition
        group = QGroupBox("TrafficSignalCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # name
        name_edit = QLineEdit(tsc.name)
        name_edit.setPlaceholderText("例: TrafficLight1")
        name_edit.textChanged.connect(
            lambda text: (setattr(tsc, "name", text), self.property_changed.emit())
        )
        form.addRow("Name:", name_edit)
        
        # state
        state_edit = QLineEdit(tsc.state)
        state_edit.setPlaceholderText("例: red, yellow, green")
        state_edit.textChanged.connect(
            lambda text: (setattr(tsc, "state", text), self.property_changed.emit())
        )
        form.addRow("State:", state_edit)
        
        group.setLayout(form)
        return group
    
    def _build_traffic_signal_controller_condition_form(self, cond: Condition) -> QWidget:
        """TrafficSignalControllerCondition用フォーム"""
        if cond.traffic_signal_controller_condition is None:
            cond.traffic_signal_controller_condition = TrafficSignalControllerCondition(
                traffic_signal_controller_ref="",
                phase=""
            )
        
        tscc = cond.traffic_signal_controller_condition
        group = QGroupBox("TrafficSignalControllerCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # trafficSignalControllerRef
        controller_ref_edit = QLineEdit(tscc.traffic_signal_controller_ref)
        controller_ref_edit.setPlaceholderText("例: Controller1")
        controller_ref_edit.textChanged.connect(
            lambda text: (setattr(tscc, "traffic_signal_controller_ref", text), self.property_changed.emit())
        )
        form.addRow("Traffic Signal Controller Ref:", controller_ref_edit)
        
        # phase
        phase_edit = QLineEdit(tscc.phase)
        phase_edit.setPlaceholderText("例: phase1")
        phase_edit.textChanged.connect(
            lambda text: (setattr(tscc, "phase", text), self.property_changed.emit())
        )
        form.addRow("Phase:", phase_edit)
        
        group.setLayout(form)
        return group
    
    def _build_variable_condition_form(self, cond: Condition) -> QWidget:
        """VariableCondition用フォーム"""
        if cond.variable_condition is None:
            cond.variable_condition = VariableCondition(variable_ref="", value="", rule="greaterThan")
        
        vc = cond.variable_condition
        group = QGroupBox("VariableCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # variableRef
        variable_ref_edit = QLineEdit(vc.variable_ref)
        variable_ref_edit.setPlaceholderText("例: MyVariable")
        variable_ref_edit.textChanged.connect(
            lambda text: (setattr(vc, "variable_ref", text), self.property_changed.emit())
        )
        form.addRow("Variable Ref:", variable_ref_edit)
        
        # value
        value_edit = QLineEdit(vc.value)
        value_edit.setPlaceholderText("例: 1.0 または ${OtherVariable}")
        value_edit.textChanged.connect(
            lambda text: (setattr(vc, "value", text), self.property_changed.emit())
        )
        form.addRow("Value:", value_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(vc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(vc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_time_headway_condition_form(self, cond: Condition) -> QWidget:
        """TimeHeadwayCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.entity_condition is None:
            entity_names = self._get_entity_names()
            cond.by_entity_condition.entity_condition = TimeHeadwayCondition(
                entity_ref=entity_names[0] if entity_names else "",
                value="0.0",
                freespace=False,
                coordinate_system="entity",
                relative_distance_type="longitudinal",
                rule="greaterThan"
            )
        
        thc = cond.by_entity_condition.entity_condition
        group = QGroupBox("TimeHeadwayCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # entityRef
        entity_names = self._get_entity_names()
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [thc.entity_ref])
        if thc.entity_ref in entity_names:
            entity_combo.setCurrentText(thc.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            thc.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(thc, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        # value（パラメータ式対応）
        value_edit = QLineEdit(str(thc.value))
        value_edit.setPlaceholderText("例: 2.0 または ${HeadwayTime}")
        value_edit.textChanged.connect(lambda text: setattr(thc, "value", text) or self.property_changed.emit())
        form.addRow("Value:", value_edit)
        
        # freespace
        freespace_check = QCheckBox()
        freespace_check.setChecked(thc.freespace)
        freespace_check.stateChanged.connect(
            lambda state: (setattr(thc, "freespace", state == Qt.CheckState.Checked), self.property_changed.emit())
        )
        form.addRow("Freespace:", freespace_check)
        
        # coordinateSystem
        coord_combo = QComboBox()
        coord_combo.addItems(["entity", "road"])
        coord_combo.setCurrentText(thc.coordinate_system)
        coord_combo.currentTextChanged.connect(
            lambda text: (setattr(thc, "coordinate_system", text), self.property_changed.emit())
        )
        form.addRow("Coordinate System:", coord_combo)
        
        # relativeDistanceType
        rel_dist_combo = QComboBox()
        rel_dist_combo.addItems(["longitudinal", "lateral"])
        rel_dist_combo.setCurrentText(thc.relative_distance_type)
        rel_dist_combo.currentTextChanged.connect(
            lambda text: (setattr(thc, "relative_distance_type", text), self.property_changed.emit())
        )
        form.addRow("Relative Distance Type:", rel_dist_combo)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(thc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(thc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        group.setLayout(form)
        return group
    
    def _build_distance_condition_form(self, cond: Condition) -> QWidget:
        """DistanceCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.distance_condition is None:
            cond.by_entity_condition.distance_condition = DistanceCondition(
                value=0.0,
                freespace=True,
                rule="greaterThan"
            )
        
        dc = cond.by_entity_condition.distance_condition
        group = QGroupBox("DistanceCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # value（パラメータ式対応）
        if isinstance(dc.value, (int, float)):
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 100000)
            value_spin.setValue(dc.value)
            value_spin.setSuffix(" m")
            value_spin.valueChanged.connect(lambda v: setattr(dc, "value", v) or self.property_changed.emit())
            form.addRow("Value:", value_spin)
        else:
            value_edit = QLineEdit(str(dc.value))
            value_edit.setPlaceholderText("例: ${Distance}")
            value_edit.textChanged.connect(lambda text: setattr(dc, "value", text) or self.property_changed.emit())
            form.addRow("Value (パラメータ式):", value_edit)
        
        # position（Position選択UI）
        position_widget = self._build_position_selector_form(dc, "position")
        form.addRow("Position:", position_widget)
        
        # freespace
        freespace_check = QCheckBox()
        freespace_check.setChecked(dc.freespace)
        freespace_check.stateChanged.connect(
            lambda state: (setattr(dc, "freespace", state == Qt.CheckState.Checked), self.property_changed.emit())
        )
        form.addRow("Freespace:", freespace_check)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(dc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(dc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        # coordinateSystem
        coord_combo = QComboBox()
        coord_combo.addItems(["", "entity", "lane", "road", "trajectory"])
        if dc.coordinate_system:
            coord_combo.setCurrentText(dc.coordinate_system)
        coord_combo.currentTextChanged.connect(
            lambda text: (setattr(dc, "coordinate_system", text if text else None), self.property_changed.emit())
        )
        form.addRow("Coordinate System:", coord_combo)
        
        # relativeDistanceType
        rel_dist_combo = QComboBox()
        rel_dist_combo.addItems(["", "longitudinal", "lateral", "cartesianDistance", "euclidianDistance"])
        if dc.relative_distance_type:
            rel_dist_combo.setCurrentText(dc.relative_distance_type)
        rel_dist_combo.currentTextChanged.connect(
            lambda text: (setattr(dc, "relative_distance_type", text if text else None), self.property_changed.emit())
        )
        form.addRow("Relative Distance Type:", rel_dist_combo)
        
        # routingAlgorithm
        routing_combo = QComboBox()
        routing_combo.addItems(["", "assignedRoute", "fastest", "leastIntersections", "shortest", "undefined"])
        if dc.routing_algorithm:
            routing_combo.setCurrentText(dc.routing_algorithm)
        routing_combo.currentTextChanged.connect(
            lambda text: (setattr(dc, "routing_algorithm", text if text else None), self.property_changed.emit())
        )
        form.addRow("Routing Algorithm:", routing_combo)
        
        # alongRoute（deprecated）
        if dc.along_route is not None:
            along_route_check = QCheckBox()
            along_route_check.setChecked(dc.along_route)
            along_route_check.stateChanged.connect(
                lambda state: (setattr(dc, "along_route", state == Qt.CheckState.Checked), self.property_changed.emit())
            )
            form.addRow("Along Route (deprecated):", along_route_check)
        
        group.setLayout(form)
        return group
    
    def _build_relative_distance_condition_form(self, cond: Condition) -> QWidget:
        """RelativeDistanceCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.relative_distance_condition is None:
            entity_names = self._get_entity_names()
            cond.by_entity_condition.relative_distance_condition = RelativeDistanceCondition(
                entity_ref=entity_names[0] if entity_names else "",
                value=0.0,
                freespace=True,
                relative_distance_type="longitudinal",
                rule="greaterThan"
            )
        
        rdc = cond.by_entity_condition.relative_distance_condition
        group = QGroupBox("RelativeDistanceCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # entityRef
        entity_names = self._get_entity_names()
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [rdc.entity_ref])
        if rdc.entity_ref in entity_names:
            entity_combo.setCurrentText(rdc.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            rdc.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(rdc, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        # value（パラメータ式対応）
        if isinstance(rdc.value, (int, float)):
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 100000)
            value_spin.setValue(rdc.value)
            value_spin.setSuffix(" m")
            value_spin.valueChanged.connect(lambda v: setattr(rdc, "value", v) or self.property_changed.emit())
            form.addRow("Value:", value_spin)
        else:
            value_edit = QLineEdit(str(rdc.value))
            value_edit.setPlaceholderText("例: ${Distance}")
            value_edit.textChanged.connect(lambda text: setattr(rdc, "value", text) or self.property_changed.emit())
            form.addRow("Value (パラメータ式):", value_edit)
        
        # freespace
        freespace_check = QCheckBox()
        freespace_check.setChecked(rdc.freespace)
        freespace_check.stateChanged.connect(
            lambda state: (setattr(rdc, "freespace", state == Qt.CheckState.Checked), self.property_changed.emit())
        )
        form.addRow("Freespace:", freespace_check)
        
        # relativeDistanceType
        rel_dist_combo = QComboBox()
        rel_dist_combo.addItems(["longitudinal", "lateral", "cartesianDistance", "euclidianDistance"])
        rel_dist_combo.setCurrentText(rdc.relative_distance_type)
        rel_dist_combo.currentTextChanged.connect(
            lambda text: (setattr(rdc, "relative_distance_type", text), self.property_changed.emit())
        )
        form.addRow("Relative Distance Type:", rel_dist_combo)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(rdc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(rdc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        # coordinateSystem
        coord_combo = QComboBox()
        coord_combo.addItems(["", "entity", "lane", "road", "trajectory"])
        if rdc.coordinate_system:
            coord_combo.setCurrentText(rdc.coordinate_system)
        coord_combo.currentTextChanged.connect(
            lambda text: (setattr(rdc, "coordinate_system", text if text else None), self.property_changed.emit())
        )
        form.addRow("Coordinate System:", coord_combo)
        
        # routingAlgorithm
        routing_combo = QComboBox()
        routing_combo.addItems(["", "assignedRoute", "fastest", "leastIntersections", "shortest", "undefined"])
        if rdc.routing_algorithm:
            routing_combo.setCurrentText(rdc.routing_algorithm)
        routing_combo.currentTextChanged.connect(
            lambda text: (setattr(rdc, "routing_algorithm", text if text else None), self.property_changed.emit())
        )
        form.addRow("Routing Algorithm:", routing_combo)
        
        group.setLayout(form)
        return group
    
    def _build_speed_condition_form(self, cond: Condition) -> QWidget:
        """SpeedCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.speed_condition is None:
            cond.by_entity_condition.speed_condition = SpeedCondition(
                value=0.0,
                rule="greaterThan"
            )
        
        sc = cond.by_entity_condition.speed_condition
        group = QGroupBox("SpeedCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # value（パラメータ式対応）
        if isinstance(sc.value, (int, float)):
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 200)
            value_spin.setValue(sc.value)
            value_spin.setSuffix(" m/s")
            value_spin.valueChanged.connect(lambda v: setattr(sc, "value", v) or self.property_changed.emit())
            form.addRow("Value:", value_spin)
        else:
            value_edit = QLineEdit(str(sc.value))
            value_edit.setPlaceholderText("例: ${Speed}")
            value_edit.textChanged.connect(lambda text: setattr(sc, "value", text) or self.property_changed.emit())
            form.addRow("Value (パラメータ式):", value_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(sc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(sc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        # direction
        direction_combo = QComboBox()
        direction_combo.addItems(["", "longitudinal", "lateral", "vertical"])
        if sc.direction:
            direction_combo.setCurrentText(sc.direction)
        direction_combo.currentTextChanged.connect(
            lambda text: (setattr(sc, "direction", text if text else None), self.property_changed.emit())
        )
        form.addRow("Direction:", direction_combo)
        
        group.setLayout(form)
        return group
    
    def _build_relative_speed_condition_form(self, cond: Condition) -> QWidget:
        """RelativeSpeedCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.relative_speed_condition is None:
            entity_names = self._get_entity_names()
            cond.by_entity_condition.relative_speed_condition = RelativeSpeedCondition(
                entity_ref=entity_names[0] if entity_names else "",
                value=0.0,
                rule="greaterThan"
            )
        
        rsc = cond.by_entity_condition.relative_speed_condition
        group = QGroupBox("RelativeSpeedCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # entityRef
        entity_names = self._get_entity_names()
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [rsc.entity_ref])
        if rsc.entity_ref in entity_names:
            entity_combo.setCurrentText(rsc.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            rsc.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(rsc, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        # value（パラメータ式対応）
        if isinstance(rsc.value, (int, float)):
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 200)
            value_spin.setValue(rsc.value)
            value_spin.setSuffix(" m/s")
            value_spin.valueChanged.connect(lambda v: setattr(rsc, "value", v) or self.property_changed.emit())
            form.addRow("Value:", value_spin)
        else:
            value_edit = QLineEdit(str(rsc.value))
            value_edit.setPlaceholderText("例: ${Speed}")
            value_edit.textChanged.connect(lambda text: setattr(rsc, "value", text) or self.property_changed.emit())
            form.addRow("Value (パラメータ式):", value_edit)
        
        # rule
        rule_combo = QComboBox()
        rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
        rule_combo.setCurrentText(rsc.rule)
        rule_combo.currentTextChanged.connect(
            lambda text: (setattr(rsc, "rule", text), self.property_changed.emit())
        )
        form.addRow("Rule:", rule_combo)
        
        # direction
        direction_combo = QComboBox()
        direction_combo.addItems(["", "longitudinal", "lateral", "vertical"])
        if rsc.direction:
            direction_combo.setCurrentText(rsc.direction)
        direction_combo.currentTextChanged.connect(
            lambda text: (setattr(rsc, "direction", text if text else None), self.property_changed.emit())
        )
        form.addRow("Direction:", direction_combo)
        
        group.setLayout(form)
        return group
    
    def _build_traveled_distance_condition_form(self, cond: Condition) -> QWidget:
        """TraveledDistanceCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.traveled_distance_condition is None:
            cond.by_entity_condition.traveled_distance_condition = TraveledDistanceCondition(value=0.0)
        
        tdc = cond.by_entity_condition.traveled_distance_condition
        group = QGroupBox("TraveledDistanceCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # value（パラメータ式対応）
        if isinstance(tdc.value, (int, float)):
            value_spin = QDoubleSpinBox()
            value_spin.setRange(0, 100000)
            value_spin.setValue(tdc.value)
            value_spin.setSuffix(" m")
            value_spin.valueChanged.connect(lambda v: setattr(tdc, "value", v) or self.property_changed.emit())
            form.addRow("Value:", value_spin)
        else:
            value_edit = QLineEdit(str(tdc.value))
            value_edit.setPlaceholderText("例: ${Distance}")
            value_edit.textChanged.connect(lambda text: setattr(tdc, "value", text) or self.property_changed.emit())
            form.addRow("Value (パラメータ式):", value_edit)
        
        group.setLayout(form)
        return group
    
    def _build_reach_position_condition_form(self, cond: Condition) -> QWidget:
        """ReachPositionCondition用フォーム"""
        if cond.by_entity_condition is None:
            cond.by_entity_condition = ByEntityCondition()
        
        if cond.by_entity_condition.reach_position_condition is None:
            cond.by_entity_condition.reach_position_condition = ReachPositionCondition(tolerance=0.0)
        
        rpc = cond.by_entity_condition.reach_position_condition
        group = QGroupBox("ReachPositionCondition")
        group.setParent(self._form_widget)
        form = QFormLayout()
        
        # tolerance（パラメータ式対応）
        if isinstance(rpc.tolerance, (int, float)):
            tolerance_spin = QDoubleSpinBox()
            tolerance_spin.setRange(0, 1000)
            tolerance_spin.setValue(rpc.tolerance)
            tolerance_spin.setSuffix(" m")
            tolerance_spin.valueChanged.connect(lambda v: setattr(rpc, "tolerance", v) or self.property_changed.emit())
            form.addRow("Tolerance:", tolerance_spin)
        else:
            tolerance_edit = QLineEdit(str(rpc.tolerance))
            tolerance_edit.setPlaceholderText("例: ${Tolerance}")
            tolerance_edit.textChanged.connect(lambda text: setattr(rpc, "tolerance", text) or self.property_changed.emit())
            form.addRow("Tolerance (パラメータ式):", tolerance_edit)
        
        # position（Position選択UI）
        position_widget = self._build_position_selector_form(rpc, "position")
        form.addRow("Position:", position_widget)
        
        group.setLayout(form)
        return group
    
    def _build_position_selector_form(self, obj, attr_name: str) -> QWidget:
        """Position選択UIを構築（DistanceCondition/ReachPositionCondition用）"""
        position = getattr(obj, attr_name)
        
        # 現在のPositionタイプを判定
        current_position_type = None
        if position is None:
            current_position_type = "WorldPosition"
        elif isinstance(position, WorldPosition):
            current_position_type = "WorldPosition"
        elif isinstance(position, LanePosition):
            current_position_type = "LanePosition"
        elif isinstance(position, RoadPosition):
            current_position_type = "RoadPosition"
        elif isinstance(position, RoutePosition):
            current_position_type = "RoutePosition"
        elif isinstance(position, RelativeWorldPosition):
            current_position_type = "RelativeWorldPosition"
        elif isinstance(position, RelativeLanePosition):
            current_position_type = "RelativeLanePosition"
        elif isinstance(position, RelativeRoadPosition):
            current_position_type = "RelativeRoadPosition"
        elif isinstance(position, RelativeObjectPosition):
            current_position_type = "RelativeObjectPosition"
        else:
            current_position_type = "WorldPosition"  # デフォルト
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Positionタイプ選択ComboBox
        position_type_combo = QComboBox()
        position_type_combo.addItems([
            "WorldPosition",
            "LanePosition",
            "RoadPosition",
            "RoutePosition",
            "RelativeWorldPosition",
            "RelativeLanePosition",
            "RelativeRoadPosition",
            "RelativeObjectPosition"
        ])
        position_type_combo.setCurrentText(current_position_type)
        layout.addWidget(position_type_combo)
        
        # 各Positionタイプ用のウィジェット
        position_widgets = {}
        
        # Positionタイプ切り替え時の処理
        def on_position_type_changed(text: str):
            # すべてのウィジェットを非表示
            for w in position_widgets.values():
                w.setVisible(False)
            
            # 既存のPositionをクリア
            setattr(obj, attr_name, None)
            
            # 選択されたタイプに応じて表示とPositionオブジェクトを作成
            if text == "WorldPosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_world_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "LanePosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_lane_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RoadPosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_road_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RoutePosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_route_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RelativeWorldPosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_relative_world_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RelativeLanePosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_relative_lane_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RelativeRoadPosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_relative_road_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            elif text == "RelativeObjectPosition":
                if text not in position_widgets:
                    position_widgets[text] = self._build_relative_object_position_widget(obj, attr_name)
                position_widgets[text].setVisible(True)
            
            self.property_changed.emit()
        
        position_type_combo.currentTextChanged.connect(on_position_type_changed)
        
        # 初期表示を設定
        on_position_type_changed(current_position_type)
        
        # 各ウィジェットをレイアウトに追加
        for w in position_widgets.values():
            layout.addWidget(w)
        
        return widget
    
    def _build_world_position_widget(self, obj, attr_name: str) -> QWidget:
        """WorldPosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        if position is None:
            position = WorldPosition(x=0.0, y=0.0)
            setattr(obj, attr_name, position)
        
        x_spin = QDoubleSpinBox()
        x_spin.setRange(-10000, 10000)
        if isinstance(position.x, (int, float)):
            x_spin.setValue(position.x)
        x_spin.valueChanged.connect(lambda v: (setattr(position, "x", v), self.property_changed.emit()))
        form.addRow("X:", x_spin)
        
        y_spin = QDoubleSpinBox()
        y_spin.setRange(-10000, 10000)
        if isinstance(position.y, (int, float)):
            y_spin.setValue(position.y)
        y_spin.valueChanged.connect(lambda v: (setattr(position, "y", v), self.property_changed.emit()))
        form.addRow("Y:", y_spin)
        
        z_spin = QDoubleSpinBox()
        z_spin.setRange(-100, 100)
        if isinstance(position.z, (int, float)):
            z_spin.setValue(position.z)
        z_spin.valueChanged.connect(lambda v: (setattr(position, "z", v), self.property_changed.emit()))
        form.addRow("Z:", z_spin)
        
        h_spin = QDoubleSpinBox()
        h_spin.setRange(-360, 360)
        if isinstance(position.h, (int, float)):
            h_spin.setValue(position.h)
        h_spin.valueChanged.connect(lambda v: (setattr(position, "h", v), self.property_changed.emit()))
        form.addRow("H (Heading):", h_spin)
        
        p_spin = QDoubleSpinBox()
        p_spin.setRange(-180, 180)
        if isinstance(position.p, (int, float)):
            p_spin.setValue(position.p)
        p_spin.valueChanged.connect(lambda v: (setattr(position, "p", v), self.property_changed.emit()))
        form.addRow("P (Pitch):", p_spin)
        
        r_spin = QDoubleSpinBox()
        r_spin.setRange(-180, 180)
        if isinstance(position.r, (int, float)):
            r_spin.setValue(position.r)
        r_spin.valueChanged.connect(lambda v: (setattr(position, "r", v), self.property_changed.emit()))
        form.addRow("R (Roll):", r_spin)
        
        return widget
    
    def _build_lane_position_widget(self, obj, attr_name: str) -> QWidget:
        """LanePosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        if position is None:
            position = LanePosition(road_id="", lane_id="")
            setattr(obj, attr_name, position)
        
        road_edit = QLineEdit(position.road_id)
        road_edit.textChanged.connect(lambda text: (setattr(position, "road_id", text), self.property_changed.emit()))
        form.addRow("Road ID:", road_edit)
        
        lane_edit = QLineEdit(str(position.lane_id))
        lane_edit.textChanged.connect(lambda text: (setattr(position, "lane_id", text), self.property_changed.emit()))
        form.addRow("Lane ID:", lane_edit)
        
        s_spin = QDoubleSpinBox()
        s_spin.setRange(0, 100000)
        if isinstance(position.s, (int, float)):
            s_spin.setValue(position.s)
        s_spin.valueChanged.connect(lambda v: (setattr(position, "s", v), self.property_changed.emit()))
        form.addRow("S:", s_spin)
        
        offset_spin = QDoubleSpinBox()
        offset_spin.setRange(-10, 10)
        if isinstance(position.offset, (int, float)):
            offset_spin.setValue(position.offset)
        offset_spin.valueChanged.connect(lambda v: (setattr(position, "offset", v), self.property_changed.emit()))
        form.addRow("Offset:", offset_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_road_position_widget(self, obj, attr_name: str) -> QWidget:
        """RoadPosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        if position is None:
            position = RoadPosition(road_id="", s=0.0, t=0.0)
            setattr(obj, attr_name, position)
        
        road_edit = QLineEdit(position.road_id)
        road_edit.textChanged.connect(lambda text: (setattr(position, "road_id", text), self.property_changed.emit()))
        form.addRow("Road ID:", road_edit)
        
        s_spin = QDoubleSpinBox()
        s_spin.setRange(0, 100000)
        if isinstance(position.s, (int, float)):
            s_spin.setValue(position.s)
        s_spin.valueChanged.connect(lambda v: (setattr(position, "s", v), self.property_changed.emit()))
        form.addRow("S:", s_spin)
        
        t_spin = QDoubleSpinBox()
        t_spin.setRange(-100, 100)
        if isinstance(position.t, (int, float)):
            t_spin.setValue(position.t)
        t_spin.valueChanged.connect(lambda v: (setattr(position, "t", v), self.property_changed.emit()))
        form.addRow("T:", t_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_relative_world_position_widget(self, obj, attr_name: str) -> QWidget:
        """RelativeWorldPosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        entity_names = self._get_entity_names()
        if position is None:
            position = RelativeWorldPosition(
                entity_ref=entity_names[0] if entity_names else "",
                dx=0.0,
                dy=0.0
            )
            setattr(obj, attr_name, position)
        
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [position.entity_ref])
        if position.entity_ref in entity_names:
            entity_combo.setCurrentText(position.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            position.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(position, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        dx_spin = QDoubleSpinBox()
        dx_spin.setRange(-10000, 10000)
        if isinstance(position.dx, (int, float)):
            dx_spin.setValue(position.dx)
        dx_spin.valueChanged.connect(lambda v: (setattr(position, "dx", v), self.property_changed.emit()))
        form.addRow("DX:", dx_spin)
        
        dy_spin = QDoubleSpinBox()
        dy_spin.setRange(-10000, 10000)
        if isinstance(position.dy, (int, float)):
            dy_spin.setValue(position.dy)
        dy_spin.valueChanged.connect(lambda v: (setattr(position, "dy", v), self.property_changed.emit()))
        form.addRow("DY:", dy_spin)
        
        dz_spin = QDoubleSpinBox()
        dz_spin.setRange(-100, 100)
        if isinstance(position.dz, (int, float)):
            dz_spin.setValue(position.dz)
        dz_spin.valueChanged.connect(lambda v: (setattr(position, "dz", v), self.property_changed.emit()))
        form.addRow("DZ:", dz_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_relative_lane_position_widget(self, obj, attr_name: str) -> QWidget:
        """RelativeLanePosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        entity_names = self._get_entity_names()
        if position is None:
            position = RelativeLanePosition(
                entity_ref=entity_names[0] if entity_names else "",
                d_lane=0
            )
            setattr(obj, attr_name, position)
        
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [position.entity_ref])
        if position.entity_ref in entity_names:
            entity_combo.setCurrentText(position.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            position.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(position, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        d_lane_spin = QSpinBox()
        d_lane_spin.setRange(-10, 10)
        if isinstance(position.d_lane, int):
            d_lane_spin.setValue(position.d_lane)
        d_lane_spin.valueChanged.connect(lambda v: (setattr(position, "d_lane", v), self.property_changed.emit()))
        form.addRow("D Lane:", d_lane_spin)
        
        ds_spin = QDoubleSpinBox()
        ds_spin.setRange(-100000, 100000)
        if position.ds is not None and isinstance(position.ds, (int, float)):
            ds_spin.setValue(position.ds)
        ds_spin.valueChanged.connect(lambda v: (setattr(position, "ds", v), self.property_changed.emit()))
        form.addRow("DS:", ds_spin)
        
        offset_spin = QDoubleSpinBox()
        offset_spin.setRange(-10, 10)
        if position.offset is not None and isinstance(position.offset, (int, float)):
            offset_spin.setValue(position.offset)
        offset_spin.valueChanged.connect(lambda v: (setattr(position, "offset", v), self.property_changed.emit()))
        form.addRow("Offset:", offset_spin)
        
        ds_lane_spin = QDoubleSpinBox()
        ds_lane_spin.setRange(-100000, 100000)
        if position.ds_lane is not None and isinstance(position.ds_lane, (int, float)):
            ds_lane_spin.setValue(position.ds_lane)
        ds_lane_spin.valueChanged.connect(lambda v: (setattr(position, "ds_lane", v), self.property_changed.emit()))
        form.addRow("DS Lane:", ds_lane_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_relative_road_position_widget(self, obj, attr_name: str) -> QWidget:
        """RelativeRoadPosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        entity_names = self._get_entity_names()
        if position is None:
            position = RelativeRoadPosition(
                entity_ref=entity_names[0] if entity_names else "",
                ds=0.0,
                dt=0.0
            )
            setattr(obj, attr_name, position)
        
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [position.entity_ref])
        if position.entity_ref in entity_names:
            entity_combo.setCurrentText(position.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            position.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(position, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        ds_spin = QDoubleSpinBox()
        ds_spin.setRange(-100000, 100000)
        if isinstance(position.ds, (int, float)):
            ds_spin.setValue(position.ds)
        ds_spin.valueChanged.connect(lambda v: (setattr(position, "ds", v), self.property_changed.emit()))
        form.addRow("DS:", ds_spin)
        
        dt_spin = QDoubleSpinBox()
        dt_spin.setRange(-100, 100)
        if isinstance(position.dt, (int, float)):
            dt_spin.setValue(position.dt)
        dt_spin.valueChanged.connect(lambda v: (setattr(position, "dt", v), self.property_changed.emit()))
        form.addRow("DT:", dt_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_relative_object_position_widget(self, obj, attr_name: str) -> QWidget:
        """RelativeObjectPosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        entity_names = self._get_entity_names()
        if position is None:
            position = RelativeObjectPosition(
                entity_ref=entity_names[0] if entity_names else "",
                dx=0.0,
                dy=0.0
            )
            setattr(obj, attr_name, position)
        
        entity_combo = QComboBox()
        entity_combo.addItems(entity_names if entity_names else [position.entity_ref])
        if position.entity_ref in entity_names:
            entity_combo.setCurrentText(position.entity_ref)
        elif entity_names:
            entity_combo.setCurrentIndex(0)
            position.entity_ref = entity_names[0]
        entity_combo.currentTextChanged.connect(
            lambda text: (setattr(position, "entity_ref", text), self.property_changed.emit())
        )
        form.addRow("Entity Ref:", entity_combo)
        
        dx_spin = QDoubleSpinBox()
        dx_spin.setRange(-10000, 10000)
        if isinstance(position.dx, (int, float)):
            dx_spin.setValue(position.dx)
        dx_spin.valueChanged.connect(lambda v: (setattr(position, "dx", v), self.property_changed.emit()))
        form.addRow("DX:", dx_spin)
        
        dy_spin = QDoubleSpinBox()
        dy_spin.setRange(-10000, 10000)
        if isinstance(position.dy, (int, float)):
            dy_spin.setValue(position.dy)
        dy_spin.valueChanged.connect(lambda v: (setattr(position, "dy", v), self.property_changed.emit()))
        form.addRow("DY:", dy_spin)
        
        dz_spin = QDoubleSpinBox()
        dz_spin.setRange(-100, 100)
        if position.dz is not None and isinstance(position.dz, (int, float)):
            dz_spin.setValue(position.dz)
        dz_spin.valueChanged.connect(lambda v: (setattr(position, "dz", v), self.property_changed.emit()))
        form.addRow("DZ:", dz_spin)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_route_position_widget(self, obj, attr_name: str) -> QWidget:
        """RoutePosition編集ウィジェット"""
        widget = QWidget()
        form = QFormLayout(widget)
        
        position = getattr(obj, attr_name)
        if position is None:
            position = RoutePosition()
            setattr(obj, attr_name, position)
        
        # RoutePositionは複雑なため、簡易的な表示のみ
        # route_ref, route, orientation, in_route_positionなどの編集は将来の拡張
        route_info_label = QLabel("RoutePosition (詳細編集は未対応)")
        form.addRow("", route_info_label)
        
        if position.orientation is None:
            position.orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        self._build_orientation_form(form, position.orientation, lambda: self.property_changed.emit())
        
        return widget
    
    def _build_orientation_form(self, parent_layout: QFormLayout, orientation: Optional[dict], on_changed):
        """Orientation編集フォームを構築"""
        if orientation is None:
            orientation = {"type": "absolute", "h": 0.0, "p": 0.0, "r": 0.0}
        
        type_combo = QComboBox()
        type_combo.addItems(["absolute", "relative"])
        if "type" in orientation:
            type_combo.setCurrentText(orientation["type"])
        type_combo.currentTextChanged.connect(
            lambda text: (orientation.update({"type": text}), on_changed())
        )
        parent_layout.addRow("Type:", type_combo)
        
        h_spin = QDoubleSpinBox()
        h_spin.setRange(-360, 360)
        h_val = orientation.get("h", 0.0)
        if isinstance(h_val, (int, float)):
            h_spin.setValue(h_val)
        h_spin.valueChanged.connect(
            lambda v: (orientation.update({"h": v}), on_changed())
        )
        parent_layout.addRow("H (Heading):", h_spin)
        
        p_spin = QDoubleSpinBox()
        p_spin.setRange(-180, 180)
        p_val = orientation.get("p", 0.0)
        if isinstance(p_val, (int, float)):
            p_spin.setValue(p_val)
        p_spin.valueChanged.connect(
            lambda v: (orientation.update({"p": v}), on_changed())
        )
        parent_layout.addRow("P (Pitch):", p_spin)
        
        r_spin = QDoubleSpinBox()
        r_spin.setRange(-180, 180)
        r_val = orientation.get("r", 0.0)
        if isinstance(r_val, (int, float)):
            r_spin.setValue(r_val)
        r_spin.valueChanged.connect(
            lambda v: (orientation.update({"r": v}), on_changed())
        )
        parent_layout.addRow("R (Roll):", r_spin)
    
    def _build_maneuver_group_form(self, mg: ManeuverGroup):
        """ManeuverGroup用フォーム"""
        # name属性
        name_edit = QLineEdit(mg.name)
        name_edit.textChanged.connect(lambda text: setattr(mg, "name", text) or self.property_changed.emit())
        self._form_layout.addRow("名前:", name_edit)
        
        # maximumExecutionCount属性
        max_exec_spin = QSpinBox()
        max_exec_spin.setRange(0, 4294967295)  # UnsignedIntの最大値
        max_exec_spin.setValue(mg.maximum_execution_count)
        max_exec_spin.valueChanged.connect(
            lambda v: setattr(mg, "maximum_execution_count", v) or self.property_changed.emit()
        )
        self._form_layout.addRow("最大実行回数:", max_exec_spin)
        
        # selectTriggeringEntities属性
        select_triggering_check = QCheckBox()
        if mg.select_triggering_entities is not None:
            select_triggering_check.setChecked(mg.select_triggering_entities)
        else:
            select_triggering_check.setChecked(False)
        select_triggering_check.stateChanged.connect(
            lambda state: setattr(mg, "select_triggering_entities", state == Qt.CheckState.Checked) or self.property_changed.emit()
        )
        self._form_layout.addRow("トリガーエンティティを選択:", select_triggering_check)
        
        # actors（エンティティ一覧から複数選択）
        actors_label = QLabel("Actors:")
        actors_list = QListWidget()
        actors_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        # シナリオ内のエンティティ一覧を取得
        entity_names = []
        if self._scenario and self._scenario.entities:
            for scenario_obj in self._scenario.entities.scenario_objects:
                entity_names.append(scenario_obj.name)
        
        # エンティティ名をリストに追加
        for entity_name in sorted(entity_names):
            actors_list.addItem(entity_name)
        
        # 現在選択されているactorsを設定
        for i in range(actors_list.count()):
            item = actors_list.item(i)
            if item.text() in mg.actors:
                item.setSelected(True)
        
        # 選択変更時にactorsリストを更新
        def update_actors():
            selected_actors = [actors_list.item(i).text() for i in range(actors_list.count()) if actors_list.item(i).isSelected()]
            mg.actors = selected_actors
            self.property_changed.emit()
        
        actors_list.itemSelectionChanged.connect(update_actors)
        
        actors_layout = QVBoxLayout()
        actors_layout.addWidget(actors_list)
        actors_widget = QWidget()
        actors_widget.setLayout(actors_layout)
        self._form_layout.addRow(actors_label, actors_widget)

