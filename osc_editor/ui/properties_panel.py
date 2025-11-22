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
    Dynamics,
    DynamicsDimension,
    DynamicsShape,
    Event,
    StartTrigger,
    Condition,
    SimulationTimeCondition,
    Rule,
)


class PropertiesPanel(QWidget):
    """プロパティ編集パネル"""
    
    # プロパティ変更時のシグナル
    property_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_node = None
        self._setup_ui()
    
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
        
        if action.position:
            pos = action.position
            x_spin = QDoubleSpinBox()
            x_spin.setRange(-10000, 10000)
            x_spin.setValue(pos.x)
            x_spin.valueChanged.connect(lambda v: setattr(pos, "x", v) or self.property_changed.emit())
            form.addRow("X:", x_spin)
            
            y_spin = QDoubleSpinBox()
            y_spin.setRange(-10000, 10000)
            y_spin.setValue(pos.y)
            y_spin.valueChanged.connect(lambda v: setattr(pos, "y", v) or self.property_changed.emit())
            form.addRow("Y:", y_spin)
            
            z_spin = QDoubleSpinBox()
            z_spin.setRange(-100, 100)
            z_spin.setValue(pos.z)
            z_spin.valueChanged.connect(lambda v: setattr(pos, "z", v) or self.property_changed.emit())
            form.addRow("Z:", z_spin)
            
            h_spin = QDoubleSpinBox()
            h_spin.setRange(-360, 360)
            h_spin.setValue(pos.h)
            h_spin.valueChanged.connect(lambda v: setattr(pos, "h", v) or self.property_changed.emit())
            form.addRow("Heading:", h_spin)
        
        elif action.lane_position:
            lane_pos = action.lane_position
            road_edit = QLineEdit(lane_pos.road_id)
            road_edit.textChanged.connect(lambda text: setattr(lane_pos, "road_id", text) or self.property_changed.emit())
            form.addRow("Road ID:", road_edit)
            
            # lane_idは文字列型（XSDではString型）
            lane_edit = QLineEdit(str(lane_pos.lane_id))
            lane_edit.textChanged.connect(lambda text: setattr(lane_pos, "lane_id", text) or self.property_changed.emit())
            form.addRow("Lane ID:", lane_edit)
            
            s_spin = QDoubleSpinBox()
            s_spin.setRange(0, 100000)
            s_spin.setValue(lane_pos.s)
            s_spin.valueChanged.connect(lambda v: setattr(lane_pos, "s", v) or self.property_changed.emit())
            form.addRow("S:", s_spin)
            
            offset_spin = QDoubleSpinBox()
            offset_spin.setRange(-10, 10)
            offset_spin.setValue(lane_pos.offset)
            offset_spin.valueChanged.connect(lambda v: setattr(lane_pos, "offset", v) or self.property_changed.emit())
            form.addRow("Offset:", offset_spin)
        
        group.setLayout(form)
        self._form_layout.addRow(group)
    
    def _build_speed_action_form(self, action: SpeedAction):
        """SpeedAction用フォーム"""
        group = QGroupBox("SpeedAction")
        form = QFormLayout()
        
        speed_spin = QDoubleSpinBox()
        speed_spin.setRange(0, 200)
        speed_spin.setValue(action.speed_target)
        speed_spin.setSuffix(" m/s")
        speed_spin.valueChanged.connect(lambda v: setattr(action, "speed_target", v) or self.property_changed.emit())
        form.addRow("目標速度:", speed_spin)
        
        if action.dynamics:
            self._build_dynamics_form(form, action.dynamics)
        else:
            # Dynamicsを新規作成
            action.dynamics = Dynamics()
            self._build_dynamics_form(form, action.dynamics)
        
        group.setLayout(form)
        self._form_layout.addRow(group)
    
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

