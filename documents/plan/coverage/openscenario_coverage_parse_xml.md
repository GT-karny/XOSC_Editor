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
| Action関連 | 19 | 2 | 13 | 34 | 68% |
| Condition関連 | 21 | 1 | 0 | 22 | 95% |
| Entity関連 | 12 | 1 | 3 | 16 | 81% |
| Trajectory関連 | 8 | 0 | 1 | 9 | 89% |
| Dynamics関連 | 3 | 0 | 0 | 3 | 100% |
| Route関連 | 2 | 0 | 1 | 3 | 67% |
| ParameterValueDistribution関連 | 10 | 0 | 0 | 10 | 100% |
| その他 | 17 | 1 | 0 | 18 | 94% |
| **合計** | **114** | **3** | **27** | **144** | **79%** |

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
| ScenarioObject | ✅ | Vehicle, Pedestrian, MiscObject, CatalogReference, ObjectControllerに対応 |
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
| LaneOffsetAction | ✅ | LaneOffsetActionDynamics, AbsoluteTargetLaneOffset, RelativeTargetLaneOffsetに対応 |
| AssignRouteAction | ✅ | CatalogReferenceとRoute要素に対応 |
| FollowTrajectoryAction | ✅ | Trajectory（deprecated）, TrajectoryRef, TimeReference, TrajectoryFollowingMode, initialDistanceOffsetに対応 |
| RoutingAction | ✅ | AssignRouteAction, FollowTrajectoryAction, AcquirePositionActionに対応 |
| ActivateControllerAction | ✅ | longitudinal, lateral属性に対応 |
| LongitudinalAction | ✅ | SpeedAction, LongitudinalDistanceAction, SpeedProfileActionに対応 |
| LateralAction | ✅ | LaneChangeAction, LaneOffsetAction, LateralDistanceActionに対応 |
| LongitudinalDistanceAction | ✅ | entityRef, continuous, freespace, distance, timeGap, displacement, coordinateSystem, DynamicConstraintsに対応 |
| SpeedProfileAction | ✅ | followingMode, entityRef, DynamicConstraints, SpeedProfileEntry（speed, time属性）に対応 |
| LateralDistanceAction | ✅ | entityRef, continuous, freespace, distance, displacement, coordinateSystem, DynamicConstraintsに対応 |
| VisibilityAction | ✅ | graphics, sensors, traffic属性に対応。SensorReferenceSetは未対応 |
| SynchronizeAction | ✅ | masterEntityRef, TargetPositionMaster, TargetPosition, targetToleranceMaster, targetTolerance, FinalSpeedに対応 |
| ControllerAction | ✅ | AssignControllerAction, OverrideControllerValueAction, ActivateControllerActionに対応 |
| AppearanceAction | ⚠️ | LightStateAction, AnimationActionの基本属性に対応。LightType/LightState, AnimationType/AnimationStateは未対応 |
| LightStateAction | ⚠️ | transitionTime属性のみ対応。LightType, LightStateは未対応 |
| AnimationAction | ⚠️ | loop, animationDuration属性のみ対応。AnimationType, AnimationStateは未対応 |
| AcquirePositionAction | ✅ | Position要素（全Positionタイプ）に対応 |

### 3.2 GlobalAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| GlobalAction | ⚠️ | ParameterAction, VariableActionのみ対応。EnvironmentAction, EntityAction, InfrastructureAction, TrafficActionは未対応 |
| ParameterAction | ✅ | SetActionに対応。ModifyActionは未対応（deprecated） |
| VariableAction | ✅ | VariableSetAction, VariableModifyActionに対応 |
| EnvironmentAction | ❌ | 未対応 |
| EntityAction | ❌ | AddEntityAction, DeleteEntityActionは未対応 |
| InfrastructureAction | ❌ | TrafficSignalActionは未対応 |
| TrafficAction | ❌ | TrafficSourceAction, TrafficSinkAction, TrafficSwarmAction, TrafficStopActionは未対応 |

### 3.3 UserDefinedAction

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| UserDefinedAction | ❌ | 未対応 |
| CustomCommandAction | ❌ | 未対応 |

### 3.4 Action関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| SpeedActionTarget | ✅ | AbsoluteTargetSpeed, RelativeTargetSpeedに対応 |
| AbsoluteTargetSpeed | ✅ | value属性に対応（SteadyStateは含まれない） |
| RelativeTargetSpeed | ✅ | entityRef, value, speedTargetValueType, continuousに対応 |
| LaneChangeTarget | ✅ | RelativeTargetLane, AbsoluteTargetLaneに対応 |
| RelativeTargetLane | ✅ | value, entityRefに対応 |
| AbsoluteTargetLane | ✅ | value（String型）に対応 |
| LaneOffsetTarget | ✅ | AbsoluteTargetLaneOffset, RelativeTargetLaneOffsetに対応 |
| AbsoluteTargetLaneOffset | ✅ | value属性に対応 |
| RelativeTargetLaneOffset | ✅ | entityRef, valueに対応 |
| FinalSpeed | ✅ | SynchronizeAction内でAbsoluteSpeed, RelativeSpeedToMasterに対応（SteadyState含む） |
| AbsoluteSpeed | ✅ | SynchronizeAction内でvalue属性とSteadyStateに対応 |
| RelativeSpeedToMaster | ✅ | SynchronizeAction内でspeedTargetValueType, value属性とSteadyStateに対応 |

## 4. Condition関連

### 4.1 ByValueCondition

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

### 4.2 ByEntityCondition

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ByEntityCondition | ✅ | すべてのEntityCondition要素に対応 |
| TriggeringEntities | ⚠️ | EntityRefのみ対応。triggeringEntitiesRuleは対応 |
| EntityCondition | ✅ | すべてのCondition要素に対応 |
| TimeHeadwayCondition | ✅ | entityRef, value, freespace, coordinateSystem, relativeDistanceType, ruleに対応 |
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

### 4.3 Condition関連の補助要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Condition | ✅ | ByEntityCondition, ByValueConditionに対応 |
| ConditionGroup | ✅ | Conditionのリストに対応 |
| StartTrigger | ✅ | ConditionGroupのリストに対応 |
| Trigger | ✅ | StartTrigger, StopTriggerで使用 |
| RelativeLaneRange | ✅ | RelativeClearanceCondition内で使用（from, to属性） |

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
| MiscObject | ✅ | name, miscObjectCategory（必須）, mass（必須）, model3d属性、ParameterDeclarations, BoundingBox, Propertiesに対応 |
| BoundingBox | ✅ | MiscObject内のBoundingBoxに対応（Center, Dimensions） |
| Properties | ✅ | Propertyのリストに対応 |

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
| DynamicConstraints | ✅ | maxAcceleration, maxAccelerationRate, maxDeceleration, maxDecelerationRate, maxSpeed属性に対応 |

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
| VariableDeclarations | ✅ | 対応済み |
| VariableDeclaration | ✅ | 対応済み |
| VariableAction | ✅ | 対応済み |
| VariableSetAction | ✅ | 対応済み |
| VariableModifyAction | ✅ | 対応済み |
| VariableModifyRule | ✅ | 対応済み |
| VariableAddValueRule | ✅ | 対応済み |
| VariableMultiplyByValueRule | ✅ | 対応済み |
| VariableCondition | ✅ | 対応済み（既に実装済み） |

## 13. ParameterValueDistribution関連

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| ParameterValueDistribution | ✅ | ScenarioFile, Deterministicに対応 |
| ScenarioFile | ✅ | filepath属性に対応 |
| Deterministic | ✅ | DeterministicMultiParameterDistribution, DeterministicSingleParameterDistributionに対応 |
| DeterministicMultiParameterDistribution | ✅ | ValueSetDistributionに対応 |
| ValueSetDistribution | ✅ | ParameterValueSetのリストに対応 |
| ParameterValueSet | ✅ | ParameterAssignmentのリストに対応 |
| DeterministicSingleParameterDistribution | ✅ | parameterName属性、DistributionSet、DistributionRangeに対応 |
| DistributionSet | ✅ | Elementのリスト（value属性）に対応 |
| DistributionRange | ✅ | stepWidth属性、Range要素に対応 |
| Range | ✅ | lowerLimit、upperLimit属性に対応 |
| Element | ✅ | value属性に対応 |

## 14. その他の要素

| 要素名 | 対応状況 | 備考 |
|--------|---------|------|
| Actors | ⚠️ | EntityRefのみ対応。selectTriggeringEntitiesは部分的に対応 |
| UsedArea | ✅ | RoadNetwork内のUsedAreaに対応（Positionのリスト、2つ以上） |
| SteadyState | ✅ | FinalSpeed内のAbsoluteSpeed, RelativeSpeedToMaster内のSteadyStateに対応 |
| TargetDistanceSteadyState | ✅ | FinalSpeed内のAbsoluteSpeed, RelativeSpeedToMaster内で対応 |
| TargetTimeSteadyState | ✅ | FinalSpeed内のAbsoluteSpeed, RelativeSpeedToMaster内で対応 |
| Color | ✅ | AppearanceAction関連で使用されるColorに対応（ColorRgb, ColorCmykのchoice、colorType属性） |
| ColorRgb | ✅ | Color内のColorRgbに対応（red, green, blue属性） |
| ColorCmyk | ✅ | Color内のColorCmykに対応（cyan, magenta, yellow, key属性） |
| LightType | ✅ | LightStateAction内のLightTypeに対応（VehicleLight, UserDefinedLightのchoice） |
| VehicleLight | ✅ | LightType内のVehicleLightに対応（vehicleLightType属性） |
| UserDefinedLight | ✅ | LightType内のUserDefinedLightに対応（userDefinedLightType属性） |
| LightState | ✅ | LightStateAction内のLightStateに対応（mode属性、Color要素、luminousIntensity, flashingOnDuration, flashingOffDuration属性） |
| AnimationType | ✅ | AnimationAction内のAnimationTypeに対応（ComponentAnimation, PedestrianAnimation, AnimationFile, UserDefinedAnimationのchoice） |
| ComponentAnimation | ✅ | AnimationType内のComponentAnimationに対応（VehicleComponent, UserDefinedComponent） |
| PedestrianAnimation | ✅ | AnimationType内のPedestrianAnimationに対応（motion, userDefinedPedestrianAnimation属性、PedestrianGestureのリスト） |
| AnimationFile | ✅ | AnimationType内のAnimationFileに対応（File要素、timeOffset属性） |
| UserDefinedAnimation | ✅ | AnimationType内のUserDefinedAnimationに対応（userDefinedAnimationType属性） |
| VehicleComponent | ✅ | ComponentAnimation内のVehicleComponentに対応（vehicleComponentType属性） |
| UserDefinedComponent | ✅ | ComponentAnimation内のUserDefinedComponentに対応（userDefinedComponentType属性） |
| PedestrianGesture | ✅ | PedestrianAnimation内のPedestrianGestureに対応（gesture属性） |
| AnimationState | ✅ | AnimationAction内のAnimationStateに対応（state属性） |
| SensorReferenceSet | ✅ | VisibilityAction内のSensorReferenceSetに対応（SensorReferenceのリスト） |
| SensorReference | ✅ | SensorReferenceSet内のSensorReferenceに対応（name属性） |
| Brake | ✅ | OverrideControllerValueAction内のBrakeに対応（value, maxRate属性） |
| BrakePercent | ✅ | BrakeInput内のBrakePercentに対応（Brake型） |
| BrakeForce | ✅ | BrakeInput内のBrakeForceに対応（Brake型） |
| BrakeInput | ✅ | OverrideBrakeAction, OverrideParkingBrakeAction内のBrakeInputに対応（BrakePercent, BrakeForceのchoice） |
| OverrideThrottleAction | ✅ | OverrideControllerValueAction内のOverrideThrottleActionに対応（active, value, maxRate属性） |
| OverrideBrakeAction | ✅ | OverrideControllerValueAction内のOverrideBrakeActionに対応（active属性、BrakeInput要素） |
| OverrideClutchAction | ✅ | OverrideControllerValueAction内のOverrideClutchActionに対応（active, value, maxRate属性） |
| OverrideParkingBrakeAction | ✅ | OverrideControllerValueAction内のOverrideParkingBrakeActionに対応（active属性、BrakeInput要素） |
| OverrideSteeringWheelAction | ✅ | OverrideControllerValueAction内のOverrideSteeringWheelActionに対応（active, value, maxRate, maxTorque属性） |
| OverrideGearAction | ✅ | OverrideControllerValueAction内のOverrideGearActionに対応（active属性、Gear要素） |
| ManualGear | ✅ | OverrideGearAction内のManualGearに対応（number属性） |
| AutomaticGear | ✅ | OverrideGearAction内のAutomaticGearに対応（gear属性） |
| Gear | ✅ | OverrideGearAction内のGearに対応（ManualGear, AutomaticGearのchoice） |
| TimeToCollisionConditionTarget | ✅ | EntityRef, Positionの両方に対応 |

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

- 2025-11-23 15:00: その他の要素の実装完了（UsedArea, Color関連, LightStateAction詳細, AnimationAction詳細, SensorReferenceSet, OverrideControllerValueAction詳細, TimeToCollisionConditionTargetのPosition要素対応）
- 2025-11-23 14:34: MiscObjectの実装完了（name, miscObjectCategory, mass, model3d属性、ParameterDeclarations, BoundingBox, Propertiesに対応）
- 2025-11-23 14:24: Action関連補助要素の実装完了（AbsoluteTargetLaneのString型対応、RelativeTargetLaneOffset、FinalSpeed内のSteadyState対応：TargetDistanceSteadyState/TargetTimeSteadyState）
- 2025-11-23 14:00: PrivateAction関連の実装完了（AcquirePositionAction, SpeedProfileAction, LongitudinalDistanceAction, LateralDistanceAction, ControllerAction, DynamicConstraints）
- 2025-11-23 13:45: SpeedActionDynamicsのvalue属性パラメータ式対応修正（パラメータ式を文字列として保存できるように変更）
- 2025-11-23 13:00: ParameterValueDistribution関連の実装完了（ScenarioFile, Deterministic, DeterministicMultiParameterDistribution, ValueSetDistribution, ParameterValueSet, DeterministicSingleParameterDistribution, DistributionSet, DistributionRange, Range, Element）
- 2025-11-23 12:33: Condition要素の実装完了（TimeOfDayCondition, UserDefinedValueCondition, TrafficSignalCondition, TrafficSignalControllerCondition, VariableCondition, AccelerationCondition, StandStillCondition, SpeedCondition, RelativeSpeedCondition, DistanceCondition, RelativeDistanceCondition, RelativeClearanceCondition, RelativeLaneRange）
- 2025-11-23 12:13: 最優先未実装機能の実装完了（ParameterAssignments/ParameterAssignment, TrajectoryRef, PositionOfCurrentEntity/PositionInRoadCoordinates）
- 2025-11-23 11:59: Catalog関連の実装完了（PedestrianCatalogLocation, MiscObjectCatalogLocation, EnvironmentCatalogLocation, ManeuverCatalogLocation, TrajectoryCatalogLocation）
- 2025-11-23 11:30: 中優先度機能の実装完了（VisibilityAction, SynchronizeAction, AppearanceAction, EndOfRoadCondition, CollisionCondition, Clothoid, Nurbs）
- 2025-11-23 11:06: Position関連（相対座標系）、Vehicle/Pedestrian詳細属性、Route要素の実装完了
- 2025-11-23 10:47: 初版作成（OpenSCENARIO 1.2.0 XSDとの比較）

