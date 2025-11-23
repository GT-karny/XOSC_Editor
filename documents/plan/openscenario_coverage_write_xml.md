# OpenSCENARIO要素対応状況（write_xml.py）

このドキュメントは、OpenSCENARIO.xsdで定義されている要素と、現在の`write_xml.py`での実装状況を比較したものです。

## 凡例

- ✅ 対応済み：完全に実装されている
- ⚠️ 一部対応：部分的に実装されている（主要機能のみ、属性の一部のみなど）
- ❌ 未対応：実装されていない

## サマリー

| カテゴリ | 対応済み | 一部対応 | 未対応 | 合計 | 対応率 |
|---------|---------|---------|--------|------|--------|
| 基本構造要素 | 14 | 1 | 2 | 17 | 88% |
| Position関連 | 11 | 0 | 2 | 13 | 85% |
| Action関連 | 20 | 2 | 12 | 34 | 71% |
| Condition関連 | 21 | 1 | 0 | 22 | 95% |
| Entity関連 | 11 | 1 | 4 | 16 | 75% |
| Trajectory関連 | 8 | 0 | 1 | 9 | 89% |
| Dynamics関連 | 3 | 0 | 0 | 3 | 100% |
| Route関連 | 2 | 0 | 1 | 3 | 67% |
| ParameterValueDistribution関連 | 10 | 0 | 0 | 10 | 100% |
| Variable関連 | 9 | 0 | 0 | 9 | 100% |
| その他 | 4 | 1 | 13 | 18 | 28% |
| **合計** | **112** | **4** | **39** | **155** | **75%** |

## 1. 基本構造要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| OpenSCENARIO | ✅ | ルート要素。FileHeader, ScenarioDefinitionに対応 |
| FileHeader | ✅ | 基本属性（revMajor, revMinor, date, description, author）に対応 |
| License | ❌ | FileHeader内のLicense要素未対応 |
| Properties (FileHeader内) | ❌ | FileHeader内のProperties要素未対応 |
| ParameterDeclarations | ✅ | 完全対応。ParameterDeclarationのリストに対応 |
| ParameterDeclaration | ✅ | name, parameterType, value属性に対応 |
| VariableDeclarations | ✅ | 完全対応。VariableDeclarationのリストに対応 |
| VariableDeclaration | ✅ | name, variableType, value属性に対応 |
| CatalogLocations | ✅ | すべてのCatalogLocationに対応（VehicleCatalog, RouteCatalog, ControllerCatalog, PedestrianCatalog, MiscObjectCatalog, EnvironmentCatalog, ManeuverCatalog, TrajectoryCatalog） |
| CatalogReference | ✅ | catalogName, entryName属性、ParameterAssignmentsに対応 |
| ParameterAssignments | ✅ | CatalogReference内のParameterAssignmentsに対応 |
| ParameterAssignment | ✅ | parameterRef, value属性に対応 |
| RoadNetwork | ⚠️ | LogicFile, SceneGraphFileのみ対応。TrafficSignals, UsedAreaは未対応 |
| Entities | ✅ | ScenarioObjectのリストに対応 |
| ScenarioObject | ✅ | Vehicle, Pedestrian, CatalogReference, ObjectControllerに対応 |
| Storyboard | ✅ | Init, Story, StopTriggerに対応 |

## 2. Storyboard関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Init | ✅ | Actions内のPrivate要素に対応 |
| InitActions | ✅ | Private要素のリストに対応。GlobalAction, UserDefinedActionは未対応 |
| Story | ✅ | ParameterDeclarations, Actのリストに対応 |
| Act | ✅ | ManeuverGroup, StartTrigger, StopTriggerに対応 |
| ManeuverGroup | ⚠️ | Actors内のEntityRefのみ対応。CatalogReference, selectTriggeringEntitiesは対応済み |
| Maneuver | ✅ | ParameterDeclarations, Eventのリストに対応 |
| Event | ⚠️ | Action, StartTriggerに対応。maximumExecutionCount属性は未対応 |
| Private | ✅ | entityRef属性、PrivateActionのリストに対応 |

## 3. Position関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| WorldPosition | ✅ | 完全対応（x, y, z, h, p, r属性） |
| LanePosition | ✅ | 完全対応（roadId, laneId, s, offset属性、Orientation要素） |
| RoutePosition | ✅ | RouteRef内のCatalogReference/Route要素、InRoutePosition内のFromCurrentEntity/FromRoadCoordinates/FromLaneCoordinates、Orientationに対応 |
| RelativeWorldPosition | ✅ | 完全対応（entityRef, dx, dy, dz属性、Orientation要素） |
| RelativeObjectPosition | ✅ | 完全対応（entityRef, dx, dy, dz属性、Orientation要素） |
| RoadPosition | ✅ | 完全対応（roadId, s, t属性、Orientation要素） |
| RelativeRoadPosition | ✅ | 完全対応（entityRef, ds, dt属性、Orientation要素） |
| RelativeLanePosition | ✅ | 完全対応（entityRef, dLane, ds, offset, dsLane属性、Orientation要素） |
| GeoPosition | ❌ | 未対応 |
| TrajectoryPosition | ❌ | 未対応 |
| Orientation | ✅ | 全Positionタイプで対応（type, h, p, r属性） |
| InRoutePosition | ✅ | FromCurrentEntity, FromRoadCoordinates, FromLaneCoordinatesすべてに対応 |
| PositionOfCurrentEntity | ✅ | InRoutePosition内のFromCurrentEntityに対応 |
| PositionInRoadCoordinates | ✅ | InRoutePosition内のFromRoadCoordinatesに対応 |
| PositionInLaneCoordinates | ✅ | InRoutePosition内のFromLaneCoordinatesに対応 |

## 4. Action関連

### 4.1 PrivateAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| TeleportAction | ✅ | 全Positionタイプに対応 |
| SpeedAction | ✅ | SpeedActionDynamics, AbsoluteTargetSpeed, RelativeTargetSpeedに対応 |
| LaneChangeAction | ✅ | LaneChangeActionDynamics, RelativeTargetLane, AbsoluteTargetLane, targetLaneOffsetに対応 |
| LaneOffsetAction | ✅ | LaneOffsetActionDynamics, AbsoluteTargetLaneOffset, RelativeTargetLaneOffset, continuous属性に対応 |
| AssignRouteAction | ✅ | CatalogReferenceとRoute要素に対応 |
| FollowTrajectoryAction | ✅ | Trajectory（deprecated）, TrajectoryRef, TimeReference, TrajectoryFollowingMode, initialDistanceOffsetに対応 |
| AcquirePositionAction | ✅ | Position要素（全Positionタイプ）に対応 |
| RoutingAction | ✅ | AssignRouteAction, FollowTrajectoryAction, AcquirePositionActionに対応 |
| ActivateControllerAction | ✅ | controllerRef, longitudinal, lateral, animation, lighting属性に対応 |
| ControllerAction | ✅ | AssignControllerAction, OverrideControllerValueAction, ActivateControllerActionに対応 |
| VisibilityAction | ✅ | graphics, sensors, traffic属性に対応。SensorReferenceSetは未対応 |
| SynchronizeAction | ✅ | masterEntityRef, TargetPositionMaster, TargetPosition, targetToleranceMaster, targetTolerance, FinalSpeedに対応 |
| AppearanceAction | ⚠️ | LightStateAction, AnimationActionの基本属性に対応。LightType/LightState, AnimationType/AnimationStateの詳細は未対応 |
| LongitudinalAction | ✅ | SpeedAction, LongitudinalDistanceAction, SpeedProfileActionに対応 |
| LateralAction | ✅ | LaneChangeAction, LaneOffsetAction, LateralDistanceActionに対応 |
| LongitudinalDistanceAction | ✅ | entityRef, continuous, freespace, distance, timeGap, displacement, coordinateSystem, DynamicConstraintsに対応 |
| SpeedProfileAction | ✅ | followingMode, entityRef, DynamicConstraints, SpeedProfileEntry（speed, time属性）に対応 |
| LateralDistanceAction | ✅ | entityRef, continuous, freespace, distance, displacement, coordinateSystem, DynamicConstraintsに対応 |

### 4.2 GlobalAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| GlobalAction | ⚠️ | ParameterAction, VariableActionのみ対応。EnvironmentAction, EntityAction, InfrastructureAction, TrafficActionは未対応 |
| ParameterAction | ✅ | SetActionに対応（deprecatedだが実装済み） |
| VariableAction | ✅ | VariableSetAction, VariableModifyActionに対応 |
| VariableSetAction | ✅ | value属性に対応 |
| VariableModifyAction | ✅ | VariableModifyRuleに対応 |
| VariableModifyRule | ✅ | AddValue, MultiplyByValueに対応 |
| VariableAddValueRule | ✅ | value属性に対応 |
| VariableMultiplyByValueRule | ✅ | value属性に対応 |
| EnvironmentAction | ❌ | 未対応 |
| EntityAction | ❌ | AddEntityAction, DeleteEntityActionは未対応 |
| InfrastructureAction | ❌ | TrafficSignalActionは未対応 |
| TrafficAction | ❌ | TrafficSourceAction, TrafficSinkAction, TrafficSwarmAction, TrafficStopActionは未対応 |

### 4.3 UserDefinedAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| UserDefinedAction | ❌ | 未対応 |
| CustomCommandAction | ❌ | 未対応 |

### 4.4 Action関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| SpeedActionTarget | ✅ | AbsoluteTargetSpeed, RelativeTargetSpeedに対応 |
| AbsoluteTargetSpeed | ✅ | value属性に対応（SteadyStateは含まれない） |
| RelativeTargetSpeed | ✅ | entityRef, value, speedTargetValueType, continuous属性に対応 |
| LaneChangeTarget | ✅ | RelativeTargetLane, AbsoluteTargetLaneに対応 |
| RelativeTargetLane | ✅ | value, entityRef属性に対応 |
| AbsoluteTargetLane | ✅ | value属性に対応（String型） |
| LaneOffsetTarget | ✅ | AbsoluteTargetLaneOffset, RelativeTargetLaneOffsetに対応 |
| AbsoluteTargetLaneOffset | ✅ | value属性に対応 |
| RelativeTargetLaneOffset | ✅ | entityRef, value属性に対応 |
| FinalSpeed | ✅ | SynchronizeAction内でAbsoluteSpeed, RelativeSpeedToMasterに対応（SteadyState含む） |
| AbsoluteSpeed | ✅ | SynchronizeAction内でvalue属性とSteadyStateに対応 |
| RelativeSpeedToMaster | ✅ | SynchronizeAction内でspeedTargetValueType, value属性とSteadyStateに対応 |

## 5. Condition関連

### 5.1 ByValueCondition

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ByValueCondition | ✅ | すべてのCondition要素に対応 |
| SimulationTimeCondition | ✅ | value, rule属性に対応 |
| ParameterCondition | ✅ | parameterRef, value, rule属性に対応 |
| StoryboardElementStateCondition | ✅ | storyboardElementType, storyboardElementRef, state属性に対応 |
| TimeOfDayCondition | ✅ | dateTime, rule属性に対応 |
| UserDefinedValueCondition | ✅ | name, value, rule属性に対応 |
| TrafficSignalCondition | ✅ | name, state属性に対応 |
| TrafficSignalControllerCondition | ✅ | trafficSignalControllerRef, phase属性に対応 |
| VariableCondition | ✅ | variableRef, value, rule属性に対応 |

### 5.2 ByEntityCondition

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ByEntityCondition | ✅ | すべてのEntityCondition要素に対応 |
| TriggeringEntities | ✅ | EntityRefのリスト、triggeringEntitiesRule属性に対応 |
| EntityCondition | ✅ | すべてのCondition要素に対応 |
| TimeHeadwayCondition | ✅ | entityRef, value, freespace, coordinateSystem, relativeDistanceType, rule属性に対応 |
| OffroadCondition | ✅ | duration属性に対応 |
| TraveledDistanceCondition | ✅ | value属性に対応 |
| TimeToCollisionCondition | ✅ | value, freespace, coordinateSystem, relativeDistanceType, rule, target_entity_refに対応 |
| ReachPositionCondition | ✅ | tolerance, position（全Positionタイプ）に対応（deprecatedだが実装済み） |
| EndOfRoadCondition | ✅ | duration属性に対応 |
| CollisionCondition | ✅ | EntityRef, ByType（ByObjectType）に対応 |
| AccelerationCondition | ✅ | rule, value, direction属性に対応 |
| StandStillCondition | ✅ | duration属性に対応 |
| SpeedCondition | ✅ | rule, value, direction属性に対応 |
| RelativeSpeedCondition | ✅ | entityRef, rule, value, direction属性に対応 |
| DistanceCondition | ✅ | value, position, freespace, rule, coordinateSystem, relativeDistanceType, routingAlgorithm, alongRoute（deprecated）属性に対応 |
| RelativeDistanceCondition | ✅ | entityRef, value, freespace, relativeDistanceType, rule, coordinateSystem, routingAlgorithm属性に対応 |
| RelativeClearanceCondition | ✅ | relativeLaneRanges, entityRefs, oppositeLanes, distanceForward, distanceBackward, freeSpace属性に対応 |

### 5.3 Condition関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Condition | ✅ | ByEntityCondition, ByValueConditionに対応。name, delay, conditionEdge属性に対応 |
| ConditionGroup | ✅ | Conditionのリストに対応 |
| StartTrigger | ✅ | ConditionGroupのリストに対応 |
| Trigger | ✅ | StartTrigger, StopTriggerで使用 |
| RelativeLaneRange | ✅ | RelativeClearanceCondition内で使用（from, to属性） |

## 6. Entity関連

### 6.1 Vehicle

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

### 6.2 Pedestrian

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Pedestrian | ✅ | name, mass（必須）, pedestrianCategory, model（deprecated）, model3d, role属性、ParameterDeclarations, BoundingBox, Propertiesに対応 |
| BoundingBox | ✅ | Pedestrian内のBoundingBoxに対応（Center, Dimensions） |
| Properties | ✅ | Propertyのリストに対応 |

### 6.3 MiscObject

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| MiscObject | ❌ | 未対応 |

### 6.4 Controller

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Controller | ⚠️ | name, Propertiesのみ対応。ParameterDeclarations, controllerTypeは未対応 |
| ObjectController | ✅ | Controller, CatalogReferenceに対応 |
| Properties | ✅ | Propertyのリストに対応 |
| Property | ✅ | name, value属性に対応 |
| File | ❌ | Properties内のFile要素未対応 |
| CustomContent | ❌ | Properties内のCustomContent未対応 |

### 6.5 Entity関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| EntityRef | ✅ | entityRef属性に対応 |
| EntitySelection | ❌ | 未対応 |
| SelectedEntities | ❌ | 未対応 |
| ByType | ❌ | SelectedEntities内のByType未対応 |
| ByObjectType | ✅ | CollisionCondition内のByObjectType（type属性）に対応 |
| ExternalObjectReference | ❌ | 未対応 |

## 7. Trajectory関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Trajectory | ✅ | name, closed, ParameterDeclarations, Shape（Polyline, Clothoid, Nurbs）に対応 |
| TrajectoryRef | ✅ | FollowTrajectoryAction内のTrajectoryRefに対応（TrajectoryまたはCatalogReferenceのchoice） |
| Shape | ✅ | Polyline, Clothoid, Nurbsに対応 |
| Polyline | ✅ | Vertexのリストに対応 |
| Vertex | ✅ | 全Positionタイプとtime属性に対応 |
| Clothoid | ✅ | curvature, length, curvaturePrime, startTime, stopTime属性、Positionに対応 |
| Nurbs | ✅ | order属性、ControlPoint（2以上）、Knot（2以上）に対応 |
| ControlPoint | ✅ | Position, time, weight属性に対応 |
| Knot | ✅ | value属性に対応 |
| TimeReference | ⚠️ | None, Timingに対応 |
| Timing | ⚠️ | domainAbsoluteRelative, offset, scale属性に対応 |

## 8. Route関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Route | ✅ | name, closed, ParameterDeclarations, Waypoint（2以上）に対応 |
| Waypoint | ✅ | routeStrategy属性、Position要素に対応 |
| RouteRef | ✅ | RouteまたはCatalogReferenceのchoiceに対応 |

## 9. Dynamics関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Dynamics | ✅ | dynamicsDimension, dynamicsShape, value属性に対応 |
| DynamicsDimension | ✅ | time, distance, rateに対応 |
| DynamicsShape | ✅ | linear, step, cubic, sinusoidalに対応 |
| DynamicConstraints | ✅ | maxAcceleration, maxAccelerationRate, maxDeceleration, maxDecelerationRate, maxSpeed属性に対応 |
| LaneOffsetActionDynamics | ✅ | dynamicsShape, maxLateralAcc属性に対応 |

## 10. Variable関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| VariableDeclarations | ✅ | VariableDeclarationのリストに対応 |
| VariableDeclaration | ✅ | name, variableType, value属性に対応 |
| VariableAction | ✅ | variableRef属性、SetActionまたはModifyActionに対応 |
| VariableSetAction | ✅ | value属性に対応 |
| VariableModifyAction | ✅ | VariableModifyRuleに対応 |
| VariableModifyRule | ✅ | AddValueまたはMultiplyByValueに対応 |
| VariableAddValueRule | ✅ | value属性に対応 |
| VariableMultiplyByValueRule | ✅ | value属性に対応 |
| VariableCondition | ✅ | variableRef, value, rule属性に対応 |

## 11. ParameterValueDistribution関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ParameterValueDistribution | ✅ | ScenarioFile, DeterministicまたはStochasticに対応 |
| ScenarioFile | ✅ | filepath属性に対応 |
| Deterministic | ✅ | DeterministicMultiParameterDistribution, DeterministicSingleParameterDistributionのリストに対応 |
| DeterministicMultiParameterDistribution | ✅ | ValueSetDistributionに対応 |
| DeterministicSingleParameterDistribution | ✅ | parameterName属性、DistributionSet, DistributionRange, UserDefinedDistributionに対応 |
| ValueSetDistribution | ✅ | ParameterValueSetのリストに対応 |
| ParameterValueSet | ✅ | ParameterAssignmentのリストに対応 |
| DistributionSet | ✅ | Elementのリスト（value属性）に対応 |
| DistributionRange | ✅ | stepWidth属性、Range要素に対応 |
| Range | ✅ | lowerLimit, upperLimit属性に対応 |

## 12. 未対応の主要要素

### 12.1 GlobalAction内の未対応要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| EnvironmentAction | ❌ | Environment, CatalogReferenceに対応する必要あり |
| EntityAction | ❌ | AddEntityAction, DeleteEntityActionに対応する必要あり |
| InfrastructureAction | ❌ | TrafficSignalActionに対応する必要あり |
| TrafficAction | ❌ | TrafficSourceAction, TrafficSinkAction, TrafficSwarmAction, TrafficStopActionに対応する必要あり |

### 12.2 その他未対応要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| UserDefinedAction | ❌ | CustomCommandActionに対応する必要あり |
| GeoPosition | ❌ | 地理座標系の位置指定に対応する必要あり |
| TrajectoryPosition | ❌ | 軌跡上の位置指定に対応する必要あり |
| MiscObject | ❌ | その他オブジェクトの定義に対応する必要あり |
| EntitySelection | ❌ | エンティティ選択機能に対応する必要あり |
| LightStateAction詳細 | ❌ | LightType, LightStateの詳細実装が必要 |
| AnimationAction詳細 | ❌ | AnimationType, AnimationStateの詳細実装が必要 |
| RoadNetwork詳細 | ❌ | TrafficSignals, UsedAreaに対応する必要あり |
| FileHeader詳細 | ❌ | License, Properties要素に対応する必要あり |

## 更新履歴

- 2025-11-23 14:24: Action関連補助要素の実装完了（AbsoluteTargetLaneのString型対応、RelativeTargetLaneOffset、FinalSpeed内のSteadyState対応：TargetDistanceSteadyState/TargetTimeSteadyState）
- 2025-11-23 14:00: Variable関連の実装完了（VariableDeclarations, VariableDeclaration, VariableAction, VariableSetAction, VariableModifyAction, VariableModifyRule, VariableAddValueRule, VariableMultiplyByValueRule, VariableCondition）

