"""プロパティ編集パネル"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
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
    SimulationTimeCondition,
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
    
    def _build_start_trigger_form(self, trigger: StartTrigger):
        """StartTrigger用フォーム"""
        if trigger.condition_groups:
            cg = trigger.condition_groups[0]
            if cg.conditions:
                cond = cg.conditions[0]
                if cond.simulation_time_condition:
                    stc = cond.simulation_time_condition
                    group = QGroupBox("SimulationTimeCondition")
                    form = QFormLayout()
                    
                    value_spin = QDoubleSpinBox()
                    value_spin.setRange(0, 10000)
                    value_spin.setValue(stc.value)
                    value_spin.setSuffix(" s")
                    value_spin.valueChanged.connect(lambda v: setattr(stc, "value", v) or self.property_changed.emit())
                    form.addRow("時間:", value_spin)
                    
                    rule_combo = QComboBox()
                    rule_combo.addItems(["greaterThan", "lessThan", "equalTo"])
                    rule_combo.setCurrentText(stc.rule)
                    rule_combo.currentTextChanged.connect(lambda text: setattr(stc, "rule", text) or self.property_changed.emit())
                    form.addRow("ルール:", rule_combo)
                    
                    group.setLayout(form)
                    self._form_layout.addRow(group)
    
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

