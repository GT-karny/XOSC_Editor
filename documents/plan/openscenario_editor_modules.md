# OpenSCENARIO エディタ モジュール構成（案）

このドキュメントは、ASAM OpenSCENARIO 1.2 対応エディタの「全体モジュール構成」を俯瞰するための設計メモです。
実装言語やフレームワーク（C++ / C# / Python / TypeScript など）には依存しない、論理的な分割を示します。

---

## 1. 全体構成

エディタ全体は大きく次のレイヤーに分けます。

1. **インフラ層（Infrastructure Layer）**
   - ファイル入出力（XML 読み書き）
   - OpenSCENARIO XSD に基づいたモデル定義
   - バリデーション・スキーマ検証
   - 設定・プロジェクト管理
2. **ドメイン層（Domain Layer）**
   - シナリオデータモデル（Storyboard / Entities / Parameters / Environment など）
   - ドメインサービス（検索・参照解決・一括更新）
3. **アプリケーション層（Application Layer）**
   - コマンド / Undo-Redo
   - シナリオテンプレート生成
   - シミュレータ連携 I/F（必要なら）
4. **プレゼンテーション層（Presentation/UI Layer）**
   - 各種エディタビュー（シナリオ設定ビュー、エンティティビュー、ストーリーボードビュー etc）
   - 共通 UI コンポーネント（ツリー、タイムライン、プロパティパネル、ノードグラフ）

---

## 2. インフラ層モジュール

### 2.1 File I/O モジュール

- 役割
  - OpenSCENARIO XML ファイルの読み込み・保存
  - エンコーディング管理（UTF-8 / BOM など）
  - 将来的なバージョン差異（1.0 / 1.1 / 1.2）への吸収
- 主な機能
  - `ScenarioDefinition` / `CatalogDefinition` / `ParameterValueDistributionDefinition` の判別
  - ファイルのパス履歴・最近開いたファイルの管理

### 2.2 OpenSCENARIO モデルバインディング

- 役割
  - XSD をもとに生成 / 実装したクラス群（C# / TS / Python など）と XML の相互変換
- 主な機能
  - XML → オブジェクトグラフのデシリアライズ
  - オブジェクトグラフ → XML のシリアライズ
  - 名前空間・スキーマバージョン管理

### 2.3 スキーマ・バリデーションモジュール

- 役割
  - XSD に基づいた構文レベルの検証
- 主な機能
  - 保存前の検証
  - 手動検証（「バリデーション実行」ボタン）
  - 検証結果（エラー / 警告）の一覧表示用データ出力

### 2.4 設定・プロジェクト管理モジュール

- 役割
  - エディタ全体の設定と、シナリオプロジェクト固有の情報を管理
- 主な機能
  - 既定の RoadNetwork / Catalog の検索パス
  - 使用する XSD のパス
  - シミュレータへの接続設定（必要なら）

---

## 3. ドメイン層モジュール

### 3.1 シナリオモデル（Scenario Model）

OpenSCENARIO の論理構造に合わせたクラス群（または型定義）。

- ファイルルート
  - `ScenarioDefinition`
- グローバル
  - `FileHeader`
  - `ParameterDeclarations`
  - `RoadNetwork`
  - `CatalogLocations`
- シナリオ構造
  - `Entities`（`ScenarioObject`, `EntitySelection`）
  - `Storyboard`
    - `Init`
    - `Story`
      - `Act`
        - `ManeuverGroup`
          - `Actors`
          - `Maneuver`
            - `Event`
              - `Action`（各種）
              - `StartTrigger`
    - 終了条件（`StopTrigger`）

### 3.2 アクションモデル（Action Model）

各アクションの詳細設定を表現するクラス群。

- Longitudinal / Speed 系
  - `SpeedAction`
  - `LongitudinalDistanceAction`
- Lateral / Lane 系
  - `LaneChangeAction`
  - `LaneOffsetAction`
  - `LateralDistanceAction`
- コントローラ系
  - `ActivateControllerAction`
  - `AssignControllerAction`
- 位置系
  - `TeleportAction`
  - `FollowTrajectoryAction` など
- 環境 / その他
  - `EnvironmentAction`
  - `VisibilityAction`
  - `SynchronizeAction` など

### 3.3 トリガ / 条件モデル（Trigger & Condition Model）

- `Trigger`
  - `ConditionGroup`（AND）
    - `Condition`（OR）
      - `ByEntityCondition`
      - `ByValueCondition`
      - `ByStateCondition` ほか

### 3.4 カタログモデル（Catalog Model）

- Vehicle / Pedestrian / MiscObject / Controller / Route / Maneuver / Environment など
- カタログ参照の解決（`CatalogReference` → 実体）用ヘルパー

### 3.5 ドメインサービス

- 参照解決サービス
  - Entity 名 → `ScenarioObject` の解決
  - Catalog 名 → Catalog アイテムの解決
- クエリサービス
  - 「この Entity が関わる Maneuver / Action を列挙」
  - 「指定時間以降に発火する Event を列挙」

---

## 4. アプリケーション層モジュール

### 4.1 コマンド / Undo-Redo モジュール

- 役割
  - すべての編集操作を「コマンド」として記録し、Undo/Redo を提供する。
- 主な機能
  - 追加 / 削除 / 更新の各操作をコマンド化
  - Undo/Redo スタック管理
  - マルチセレクションへの一括コマンド適用

### 4.2 シナリオテンプレート / ウィザードモジュール

- 役割
  - 典型的なシナリオ骨組みをワンクリックで作成
- 例
  - 「前走車追従シナリオ」
  - 「対向車とのすれ違いシナリオ」

### 4.3 シミュレータ連携モジュール

- 役割
  - 外部シミュレータ（esmini, 自社シミュレータなど）と連携し、
    再生プレビュー・ログ取得を行う。
- 主な機能
  - シナリオの一時保存 → シミュレータ起動
  - 実行結果のログを収集し、UI へフィードバック

---

## 5. プレゼンテーション層モジュール（UI）

### 5.1 メインシェル / レイアウト

- 役割
  - メインウィンドウのレイアウト管理
- 主な機能
  - メニュー / ツールバー
  - ドッキングパネル（ツリー / タイムライン / プロパティなど）
  - ステータスバー（バリデーション結果、カーソル時間など）

### 5.2 シナリオ設定ビュー（Scenario Settings View）

- 編集対象
  - `FileHeader`
  - `RoadNetwork`
  - グローバル `Environment`（必要なら）
- UI イメージ
  - プロパティグリッド形式のフォーム
  - マップファイル / XODR のパス選択ダイアログ

### 5.3 エンティティビュー（Entities View）

- 編集対象
  - `Entities`
    - `ScenarioObject`
    - `EntitySelection`
- 主な機能
  - Entity の追加 / 削除 / 名前変更
  - Catalog からの車種割当
  - 初期位置・初期速度編集（Init との連携）
  - グループ化（Selection）の編集

### 5.4 パラメータビュー（Parameter View）

- 編集対象
  - `ParameterDeclarations`
- 主な機能
  - パラメータの追加 / 削除
  - 型（double / int / bool / string / enum）の指定
  - デフォルト値・説明の編集
  - 使用箇所一覧（どこで参照されているか）

### 5.5 ストーリーボードビュー（Storyboard View）

- 編集対象
  - `Storyboard` 全体構造
    - Story / Act / ManeuverGroup / Maneuver / Event / Action
- UI パターン案
  1. **ツリー表示 + プロパティパネル**
  2. **タイムライン表示**
  3. **ノードグラフ（フローチャート）表示**
- 主な機能
  - Story / Act / Maneuver / Event / Action の追加 / 削除 / 並び替え
  - ManeuverGroup と Actors（対象 Entity）編集
  - 各 Action の詳細設定画面へのナビゲーション

### 5.6 アクションエディタ（Action Editor）

- 編集対象
  - `SpeedAction`, `LaneChangeAction`, `ActivateControllerAction` など
- 主な機能
  - アクション種別ごとの専用フォーム
  - Dynamics の設定
    - 目標値（速度 / レーン / オフセット など）
    - `dynamicsDimension`（time / distance / rate）
    - `dynamicsShape`（linear / step / cubic etc）
  - 対象 Entity の確認・変更（必要に応じて）

### 5.7 トリガ / 条件エディタ（Trigger & Condition Editor）

- 編集対象
  - `StartTrigger` / `StopTrigger`
  - `ConditionGroup` / `Condition`
- UI イメージ
  - 条件グループ（AND）と条件（OR）をカード or ノードとして表示
  - 条件タイプ（ByEntity / ByValue / ByState）を選択してフォーム入力
- 主な機能
  - 条件の追加 / 削除 / 複製
  - 比較対象（位置・距離・速度・時間など）の選択
  - 閾値・比較演算子の編集

### 5.8 環境エディタ（Environment Editor）［拡張］

- 編集対象
  - `Environment` / `Weather` / `RoadCondition` など
- 主な機能
  - 時刻（太陽高度）
  - 天候プリセット（晴れ / 雨 / 霧 / 雪 など）
  - 詳細パラメータ（視程距離・路面摩擦係数など）

### 5.9 カタログエディタ（Catalog Editor）［拡張］

- 編集対象
  - Vehicle / Pedestrian / MiscObject / Controller / Route / Maneuver / Environment Catalog
- 主な機能
  - カタログ項目一覧
  - 基本情報編集（名称・カテゴリ・物理パラメータ）
  - カタログファイルの追加 / 分割 / 統合

### 5.10 ビジュアルプレビュー / マップビュー［任意］

- 役割
  - RoadNetwork（XODR）上での Entity の初期位置・アクションのイメージ表示
- 主な機能
  - 2D トップビューでのレーン・交差点表示
  - Entity の初期位置 / テレポート位置 / 代表的なポイントの可視化

---

## 6. 将来的な拡張ポイント

- **ロジカルシナリオ対応**
  - `ParameterValueDistributionDefinition` の編集
  - Monte-Carlo 用の分布設定 UI
- **一般交通（Traffic）エディタ**
  - `TrafficDefinition` / `TrafficGroup` の編集
- **外部ツール連携**
  - RoadRunner / シミュレータログビューア / テスト管理ツール との連携
- **プラグイン機構**
  - Action / Condition / Catalog などの拡張をプラグインとして追加できるしくみ

---

## 7. MVP（最初の版）で欲しいモジュール候補

少ない工数で実用性を出すために、初期リリースで優先したいモジュールは次の通りです。

1. インフラ層
   - File I/O モジュール
   - モデルバインディング
   - 基本的なバリデーション
2. ドメイン層
   - シナリオモデル（Storyboard / Entities / Parameters / RoadNetwork）
   - 代表的な Action / Trigger / Condition
3. アプリケーション層
   - コマンド / Undo-Redo
4. プレゼンテーション層
   - シナリオ設定ビュー
   - エンティティビュー
   - パラメータビュー
   - ストーリーボードビュー
   - アクションエディタ（Speed / LaneChange / ActivateController など）
   - トリガ / 条件エディタ

この構成をベースに、今後詳細設計（クラス図・UI ワイヤーフレームなど）を詰めていくことを想定しています。
