# OpenSCENARIO要素対応状況

このドキュメントは、OpenSCENARIO.xsdで定義されている要素と、現在の`parse_xml.py`での実装状況を比較したものです。

## 凡例

- ✅ 対応済み：完全に実装されている
- ⚠️ 一部対応：部分的に実装されている（主要機能のみ、属性の一部のみなど）
- ❌ 未対応：実装されていない

## サマリー

| カテゴリ | 対応済み | 一部対応 | 未対応 | 合計 | 対応率 |
|---------|---------|---------|--------|------|--------|
| 基本構造要素 | 15 | 1 | 1 | 17 | 94% |
| Position関連 | 11 | 0 | 2 | 13 | 85% |
| Action関連 | 12 | 5 | 19 | 36 | 47% |
| Condition関連 | 9 | 2 | 10 | 21 | 52% |
| Entity関連 | 12 | 1 | 3 | 16 | 81% |
| Trajectory関連 | 8 | 0 | 1 | 9 | 89% |
| Dynamics関連 | 2 | 0 | 1 | 3 | 67% |
| Route関連 | 2 | 0 | 1 | 3 | 67% |
| その他 | 2 | 1 | 15 | 18 | 17% |
| **合計** | **73** | **5** | **55** | **133** | **59%** |

## 1. 基本構造要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| FileHeader | ✅ | 基本属性（revMajor, revMinor, date, description, author）に対応 |
| License | ❌ | FileHeader内のLicense要素未対応 |
| Properties (FileHeader内) | ❌ | FileHeader内のProperties要素未対応 |
| ParameterDeclarations | ✅ | 完全対応 |
| ParameterDeclaration | ✅ | 完全対応 |
| CatalogLocations | ✅ | すべてのCatalogLocationに対応（VehicleCatalog, RouteCatalog, ControllerCatalog, PedestrianCatalog, MiscObjectCatalog, EnvironmentCatalog, ManeuverCatalog, TrajectoryCatalog） |
| CatalogReference | ✅ | 基本属性（catalogName, entryName）に対応。ParameterAssignmentsに対応 |
| ParameterAssignments | ✅ | CatalogReference内のParameterAssignmentsに対応 |
| ParameterAssignment | ✅ | ParameterAssignments内のParameterAssignmentに対応 |
| RoadNetwork | ⚠️ | LogicFile, SceneGraphFileのみ対応。TrafficSignals, UsedAreaは未対応 |
| Entities | ✅ | ScenarioObjectのリストに対応 |
| ScenarioObject | ✅ | Vehicle, Pedestrian, CatalogReference, ObjectControllerに対応 |
| Storyboard | ✅ | Init, Story, StopTriggerに対応 |
| Init | ✅ | Actions内のPrivate要素に対応 |
| InitActions | ✅ | Private要素のリストに対応 |
| Story | ✅ | ParameterDeclarations, Actのリストに対応 |
| Act | ✅ | ManeuverGroup, StartTrigger, StopTriggerに対応 |
| ManeuverGroup | ⚠️ | Actors内のEntityRefのみ対応。CatalogReference, selectTriggeringEntitiesは未対応 |
| Maneuver | ✅ | Eventのリストに対応 |
| Event | ⚠️ | Action, StartTriggerに対応。maximumExecutionCount属性は未対応 |

## 2. Position関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| WorldPosition | ✅ | 完全対応（x, y, z, h, p, r） |
| LanePosition | ✅ | 完全対応（roadId, laneId, s, offset, Orientation） |
| RoutePosition | ✅ | RouteRef内のCatalogReference/Route要素、InRoutePosition内のFromCurrentEntity/FromRoadCoordinates/FromLaneCoordinates、Orientationに対応 |
| RelativeWorldPosition | ✅ | 完全対応（entityRef, dx, dy, dz, Orientation） |
| RelativeObjectPosition | ✅ | 完全対応（entityRef, dx, dy, dz, Orientation） |
| RoadPosition | ✅ | 完全対応（roadId, s, t, Orientation） |
| RelativeRoadPosition | ✅ | 完全対応（entityRef, ds, dt, Orientation） |
| RelativeLanePosition | ✅ | 完全対応（entityRef, dLane, ds, offset, dsLane, Orientation） |
| GeoPosition | ❌ | 未対応 |
| TrajectoryPosition | ❌ | 未対応 |
| Orientation | ✅ | 全Positionタイプで対応（type, h, p, r） |
| InRoutePosition | ✅ | FromCurrentEntity, FromRoadCoordinates, FromLaneCoordinatesすべてに対応 |
| PositionOfCurrentEntity | ✅ | InRoutePosition内のFromCurrentEntityに対応 |
| PositionInRoadCoordinates | ✅ | InRoutePosition内のFromRoadCoordinatesに対応 |
| PositionInLaneCoordinates | ✅ | InRoutePosition内のFromLaneCoordinatesに対応 |

## 3. Action関連

### 3.1 PrivateAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| TeleportAction | ✅ | WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition, RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPositionに対応 |
| SpeedAction | ✅ | SpeedActionDynamics, AbsoluteTargetSpeed, RelativeTargetSpeedに対応 |
| LaneChangeAction | ✅ | LaneChangeActionDynamics, RelativeTargetLane, AbsoluteTargetLaneに対応 |
| LaneOffsetAction | ✅ | LaneOffsetActionDynamics, AbsoluteTargetLaneOffsetに対応 |
| AssignRouteAction | ✅ | CatalogReferenceとRoute要素に対応 |
| FollowTrajectoryAction | ✅ | Trajectory（deprecated）, TrajectoryRef, TimeReference, TrajectoryFollowingMode, initialDistanceOffsetに対応 |
| RoutingAction | ✅ | AssignRouteAction, FollowTrajectoryActionに対応 |
| ActivateControllerAction | ✅ | longitudinal, lateral属性に対応 |
| LongitudinalAction | ⚠️ | SpeedActionのみ対応。LongitudinalDistanceAction, SpeedProfileActionは未対応 |
| LateralAction | ⚠️ | LaneChangeAction, LaneOffsetActionのみ対応。LateralDistanceActionは未対応 |
| LongitudinalDistanceAction | ❌ | 未対応 |
| SpeedProfileAction | ❌ | 未対応 |
| LateralDistanceAction | ❌ | 未対応 |
| VisibilityAction | ✅ | graphics, sensors, traffic属性に対応。SensorReferenceSetは未対応 |
| SynchronizeAction | ✅ | masterEntityRef, TargetPositionMaster, TargetPosition, targetToleranceMaster, targetTolerance, FinalSpeedに対応 |
| ControllerAction | ⚠️ | ActivateControllerActionのみ対応。AssignControllerAction, OverrideControllerValueActionは未対応 |
| AppearanceAction | ⚠️ | LightStateAction, AnimationActionの基本属性に対応。LightType/LightState, AnimationType/AnimationStateは未対応 |
| LightStateAction | ⚠️ | transitionTime属性のみ対応。LightType, LightStateは未対応 |
| AnimationAction | ⚠️ | loop, animationDuration属性のみ対応。AnimationType, AnimationStateは未対応 |
| AcquirePositionAction | ❌ | 未対応 |

### 3.2 GlobalAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| GlobalAction | ⚠️ | ParameterActionのみ対応 |
| ParameterAction | ✅ | SetActionに対応。ModifyActionは未対応（deprecated） |
| EnvironmentAction | ❌ | 未対応 |
| EntityAction | ❌ | AddEntityAction, DeleteEntityActionは未対応 |
| InfrastructureAction | ❌ | TrafficSignalActionは未対応 |
| TrafficAction | ❌ | TrafficSourceAction, TrafficSinkAction, TrafficSwarmAction, TrafficStopActionは未対応 |
| VariableAction | ❌ | 未対応 |

### 3.3 UserDefinedAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| UserDefinedAction | ❌ | 未対応 |
| CustomCommandAction | ❌ | 未対応 |

### 3.4 Action関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| SpeedActionTarget | ✅ | AbsoluteTargetSpeed, RelativeTargetSpeedに対応 |
| AbsoluteTargetSpeed | ⚠️ | value属性のみ対応。SteadyStateは未対応 |
| RelativeTargetSpeed | ✅ | entityRef, value, speedTargetValueType, continuousに対応 |
| LaneChangeTarget | ✅ | RelativeTargetLane, AbsoluteTargetLaneに対応 |
| RelativeTargetLane | ⚠️ | value, entityRefのみ対応 |
| AbsoluteTargetLane | ⚠️ | valueのみ対応（String型として扱う必要あり） |
| LaneOffsetTarget | ⚠️ | AbsoluteTargetLaneOffsetのみ対応 |
| AbsoluteTargetLaneOffset | ✅ | value属性に対応 |
| RelativeTargetLaneOffset | ❌ | 未対応 |
| FinalSpeed | ⚠️ | SynchronizeAction内でAbsoluteSpeed, RelativeSpeedToMasterに対応 |
| AbsoluteSpeed | ✅ | SynchronizeAction内でvalue属性に対応 |
| RelativeSpeedToMaster | ✅ | SynchronizeAction内でspeedTargetValueType, value属性に対応 |

## 4. Condition関連

### 4.1 ByValueCondition

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ByValueCondition | ⚠️ | SimulationTimeCondition, ParameterCondition, StoryboardElementStateConditionのみ対応 |
| SimulationTimeCondition | ✅ | value, rule属性に対応 |
| ParameterCondition | ✅ | parameterRef, value, rule属性に対応 |
| StoryboardElementStateCondition | ✅ | storyboardElementType, storyboardElementRef, state属性に対応 |
| TimeOfDayCondition | ❌ | 未対応 |
| UserDefinedValueCondition | ❌ | 未対応 |
| TrafficSignalCondition | ❌ | 未対応 |
| TrafficSignalControllerCondition | ❌ | 未対応 |
| VariableCondition | ❌ | 未対応 |

### 4.2 ByEntityCondition

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ByEntityCondition | ⚠️ | TriggeringEntities, EntityConditionの一部のみ対応 |
| TriggeringEntities | ⚠️ | EntityRefのみ対応。triggeringEntitiesRuleは対応 |
| EntityCondition | ⚠️ | TimeHeadwayCondition, OffroadCondition, TraveledDistanceCondition, TimeToCollisionCondition, ReachPositionCondition, EndOfRoadCondition, CollisionConditionに対応 |
| TimeHeadwayCondition | ✅ | entityRef, value, freespace, coordinateSystem, relativeDistanceType, ruleに対応 |
| OffroadCondition | ✅ | duration属性に対応 |
| TraveledDistanceCondition | ✅ | value属性に対応 |
| TimeToCollisionCondition | ✅ | value, freespace, coordinateSystem, relativeDistanceType, rule, target_entity_refに対応 |
| ReachPositionCondition | ✅ | tolerance, position（全Positionタイプ）に対応（deprecatedだが実装済み） |
| EndOfRoadCondition | ✅ | duration属性に対応 |
| CollisionCondition | ✅ | EntityRef, ByType（ByObjectType）に対応 |
| AccelerationCondition | ❌ | 未対応 |
| StandStillCondition | ❌ | 未対応 |
| SpeedCondition | ❌ | 未対応 |
| RelativeSpeedCondition | ❌ | 未対応 |
| DistanceCondition | ❌ | 未対応 |
| RelativeDistanceCondition | ❌ | 未対応 |
| RelativeClearanceCondition | ❌ | 未対応 |

### 4.3 Condition関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Condition | ✅ | ByEntityCondition, ByValueConditionに対応 |
| ConditionGroup | ✅ | Conditionのリストに対応 |
| StartTrigger | ✅ | ConditionGroupのリストに対応 |
| Trigger | ✅ | StartTrigger, StopTriggerで使用 |

## 5. Entity関連

### 5.1 Vehicle

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Vehicle | ✅ | name, vehicleCategory, role, mass, model3d属性、ParameterDeclarations, BoundingBox, Performance, Axles, Propertiesに対応 |
| BoundingBox | ✅ | Center, Dimensionsに対応 |
| Center | ✅ | x, y, z属性に対応 |
| Dimensions | ✅ | height, length, width属性に対応 |
| Performance | ✅ | maxAcceleration, maxDeceleration, maxSpeed, maxAccelerationRate, maxDecelerationRate属性に対応 |
| Axles | ✅ | FrontAxle, RearAxle, AdditionalAxleに対応 |
| Axle | ✅ | maxSteering, positionX, positionZ, trackWidth, wheelDiameter属性に対応 |
| Properties | ✅ | Propertyのリストに対応 |

### 5.2 Pedestrian

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Pedestrian | ✅ | name, mass（必須）, pedestrianCategory, model（deprecated）, model3d, role属性、ParameterDeclarations, BoundingBox, Propertiesに対応 |
| BoundingBox | ✅ | Pedestrian内のBoundingBoxに対応（Center, Dimensions） |
| Properties | ✅ | Propertyのリストに対応 |

### 5.3 MiscObject

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| MiscObject | ❌ | 未対応 |

### 5.4 Controller

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Controller | ⚠️ | name, Propertiesのみ対応。ParameterDeclarations, controllerTypeは未対応 |
| ObjectController | ✅ | Controller, CatalogReferenceに対応 |
| Properties | ✅ | Propertyのリストに対応 |
| Property | ✅ | name, value属性に対応 |
| File | ❌ | Properties内のFile要素未対応 |
| CustomContent | ❌ | Properties内のCustomContent未対応 |

### 5.5 Entity関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| EntityRef | ✅ | entityRef属性に対応 |
| EntitySelection | ❌ | 未対応 |
| SelectedEntities | ❌ | 未対応 |
| ByType | ❌ | SelectedEntities内のByType未対応 |
| ByObjectType | ✅ | CollisionCondition内のByObjectType（type属性）に対応 |
| ExternalObjectReference | ❌ | 未対応 |

## 6. Trajectory関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Trajectory | ✅ | name, closed, ParameterDeclarations, Shape（Polyline, Clothoid, Nurbs）に対応 |
| TrajectoryRef | ✅ | FollowTrajectoryAction内のTrajectoryRefに対応（TrajectoryまたはCatalogReferenceのchoice） |
| Shape | ✅ | Polyline, Clothoid, Nurbsに対応 |
| Polyline | ✅ | Vertexのリストに対応 |
| Vertex | ✅ | 全Positionタイプ（WorldPosition, LanePosition, RoutePosition, RelativeWorldPosition, RelativeLanePosition, RelativeRoadPosition, RelativeObjectPosition, RoadPosition）とtime属性に対応 |
| Clothoid | ✅ | curvature, length, curvaturePrime, startTime, stopTime属性、Positionに対応 |
| Nurbs | ✅ | order属性、ControlPoint（2以上）、Knot（2以上）に対応 |
| ControlPoint | ✅ | Position, time, weight属性に対応 |
| Knot | ✅ | value属性に対応 |
| TimeReference | ⚠️ | None, Timingに対応 |
| Timing | ⚠️ | domainAbsoluteRelative, offset, scale属性に対応 |
| None | ✅ | TimeReference内のNoneに対応 |
| TrajectoryFollowingMode | ✅ | followingMode属性に対応 |

## 7. Dynamics関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| TransitionDynamics | ✅ | dynamicsDimension, dynamicsShape, value属性に対応 |
| LaneOffsetActionDynamics | ✅ | dynamicsShape, maxLateralAcc属性に対応 |
| DynamicConstraints | ❌ | 未対応 |

## 8. Route関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Route | ✅ | name, closed属性、ParameterDeclarations, Waypoint（2つ以上）に対応 |
| Waypoint | ✅ | routeStrategy属性、Position（全Positionタイプ）に対応 |
| RouteRef | ✅ | CatalogReferenceとRoute要素の両方に対応 |
| RouteCatalogLocation | ✅ | Directory/pathに対応 |

## 9. Environment関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Environment | ❌ | 未対応 |
| TimeOfDay | ❌ | 未対応 |
| Weather | ❌ | 未対応 |
| Sun | ❌ | Weather内のSun未対応 |
| Fog | ❌ | Weather内のFog未対応 |
| Precipitation | ❌ | Weather内のPrecipitation未対応 |
| Wind | ❌ | Weather内のWind未対応 |
| DomeImage | ❌ | Weather内のDomeImage未対応 |
| RoadCondition | ❌ | 未対応 |
| EnvironmentCatalogLocation | ❌ | 未対応 |

## 10. Traffic関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| TrafficSignals | ❌ | RoadNetwork内のTrafficSignals未対応 |
| TrafficSignalController | ❌ | 未対応 |
| Phase | ❌ | TrafficSignalController内のPhase未対応 |
| TrafficSignalState | ❌ | Phase内のTrafficSignalState未対応 |
| TrafficSignalGroupState | ❌ | Phase内のTrafficSignalGroupState未対応 |
| TrafficSignalAction | ❌ | InfrastructureAction内のTrafficSignalAction未対応 |
| TrafficSignalControllerAction | ❌ | 未対応 |
| TrafficSignalStateAction | ❌ | 未対応 |
| TrafficAction | ❌ | 未対応 |
| TrafficSourceAction | ❌ | 未対応 |
| TrafficSinkAction | ❌ | 未対応 |
| TrafficSwarmAction | ❌ | 未対応 |
| TrafficStopAction | ❌ | 未対応 |
| TrafficDefinition | ❌ | 未対応 |
| CentralSwarmObject | ❌ | TrafficSwarmAction内のCentralSwarmObject未対応 |
| DirectionOfTravelDistribution | ❌ | TrafficSwarmAction内のDirectionOfTravelDistribution未対応 |

## 11. Catalog関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Catalog | ❌ | 未対応 |
| VehicleCatalogLocation | ✅ | Directory/pathに対応 |
| ControllerCatalogLocation | ✅ | Directory/pathに対応 |
| RouteCatalogLocation | ✅ | Directory/pathに対応 |
| PedestrianCatalogLocation | ✅ | Directory/pathに対応 |
| MiscObjectCatalogLocation | ✅ | Directory/pathに対応 |
| EnvironmentCatalogLocation | ✅ | Directory/pathに対応 |
| ManeuverCatalogLocation | ✅ | Directory/pathに対応 |
| TrajectoryCatalogLocation | ✅ | Directory/pathに対応 |
| Directory | ✅ | path属性に対応 |

## 12. Variable関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| VariableDeclarations | ❌ | 未対応 |
| VariableDeclaration | ❌ | 未対応 |
| VariableAction | ❌ | 未対応 |
| VariableSetAction | ❌ | 未対応 |
| VariableModifyAction | ❌ | 未対応 |
| VariableModifyRule | ❌ | 未対応 |
| VariableAddValueRule | ❌ | 未対応 |
| VariableMultiplyByValueRule | ❌ | 未対応 |
| VariableCondition | ❌ | 未対応 |

## 13. その他の要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Actors | ⚠️ | EntityRefのみ対応。selectTriggeringEntitiesは部分的に対応 |
| UsedArea | ❌ | RoadNetwork内のUsedArea未対応 |
| SteadyState | ❌ | AbsoluteSpeed, RelativeSpeedToMaster内のSteadyState未対応 |
| TargetDistanceSteadyState | ❌ | 未対応 |
| TargetTimeSteadyState | ❌ | 未対応 |
| Color | ❌ | AppearanceAction関連で使用されるColor未対応 |
| ColorRgb | ❌ | 未対応 |
| ColorCmyk | ❌ | 未対応 |
| LightType | ❌ | LightStateAction内のLightType未対応 |
| VehicleLight | ❌ | 未対応 |
| UserDefinedLight | ❌ | 未対応 |
| LightState | ❌ | LightStateAction内のLightState未対応 |
| AnimationType | ❌ | AnimationAction内のAnimationType未対応 |
| ComponentAnimation | ❌ | 未対応 |
| PedestrianAnimation | ❌ | 未対応 |
| AnimationFile | ❌ | 未対応 |
| UserDefinedAnimation | ❌ | 未対応 |
| VehicleComponent | ❌ | ComponentAnimation内のVehicleComponent未対応 |
| UserDefinedComponent | ❌ | ComponentAnimation内のUserDefinedComponent未対応 |
| PedestrianGesture | ❌ | PedestrianAnimation内のPedestrianGesture未対応 |
| AnimationState | ❌ | AnimationAction内のAnimationState未対応 |
| SensorReferenceSet | ❌ | VisibilityAction内のSensorReferenceSet未対応 |
| SensorReference | ❌ | 未対応 |
| Brake | ❌ | OverrideControllerValueAction関連で使用されるBrake未対応 |
| BrakePercent | ❌ | 未対応 |
| BrakeForce | ❌ | 未対応 |
| OverrideThrottleAction | ❌ | 未対応 |
| OverrideBrakeAction | ❌ | 未対応 |
| OverrideClutchAction | ❌ | 未対応 |
| OverrideParkingBrakeAction | ❌ | 未対応 |
| OverrideSteeringWheelAction | ❌ | 未対応 |
| OverrideGearAction | ❌ | 未対応 |
| ManualGear | ❌ | OverrideGearAction内のManualGear未対応 |
| AutomaticGear | ❌ | OverrideGearAction内のAutomaticGear未対応 |
| Gear | ❌ | OverrideGearAction内のGear未対応 |
| TimeToCollisionConditionTarget | ⚠️ | EntityRefのみ対応。Positionは未対応 |

## 実装の優先順位

現在の実装は基本的なシナリオ編集には対応していますが、以下の領域の実装が不足しています：

1. **高優先度** ✅ 実装済み
   - ~~Position関連の相対座標系（RelativeWorldPosition, RelativeLanePosition等）~~ ✅
   - ~~Vehicle/Pedestrianの詳細属性（BoundingBox, Performance, Axles等）~~ ✅
   - ~~Route要素の完全対応~~ ✅

2. **中優先度** ✅ 実装済み
   - ~~高度なAction（VisibilityAction, SynchronizeAction, AppearanceAction等）~~ ✅
   - ~~追加のCondition（EndOfRoadCondition, CollisionCondition等）~~ ✅
   - ~~Trajectoryの高度な形状（Clothoid, Nurbs等）~~ ✅

3. **低優先度**
   - Environment関連（Weather, TimeOfDay等）
   - Traffic関連（TrafficAction, TrafficSignal等）
   - Variable関連
   - パラメータ分布関連（Deterministic, Stochastic等）

## 更新履歴

- 2025-11-23 12:13: 最優先未実装機能の実装完了（ParameterAssignments/ParameterAssignment, TrajectoryRef, PositionOfCurrentEntity/PositionInRoadCoordinates）
- 2025-11-23 11:59: Catalog関連の実装完了（PedestrianCatalogLocation, MiscObjectCatalogLocation, EnvironmentCatalogLocation, ManeuverCatalogLocation, TrajectoryCatalogLocation）
- 2025-11-23 11:30: 中優先度機能の実装完了（VisibilityAction, SynchronizeAction, AppearanceAction, EndOfRoadCondition, CollisionCondition, Clothoid, Nurbs）
- 2025-11-23 11:06: Position関連（相対座標系）、Vehicle/Pedestrian詳細属性、Route要素の実装完了
- 2025-11-23 10:47: 初版作成（OpenSCENARIO 1.2.0 XSDとの比較）

