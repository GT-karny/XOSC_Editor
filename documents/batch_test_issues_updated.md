# XOSCバッチ処理テスト結果と課題（更新版）

## テスト概要

- **テスト日時**: 2025-11-23 12:52:15
- **テスト対象**: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/` 内の全40ファイル
- **テスト内容**: 
  1. XOSCファイルの読み込み（parse_xml）
  2. XOSCファイルの書き出し（write_xml）
  3. esminiでの実行

## テスト結果サマリー

- **総ファイル数**: 40
- **読み込み成功**: 40 (100%) ✅
- **書き出し成功**: 34 (85%) ⚠️
- **書き出しエラー**: 6 (15%)
- **esmini実行成功**: 0 (0%) ❌
- **esmini実行エラー**: 40 (100%)

## 課題一覧

### 1. 書き出しエラー（6件）⚠️

#### 1.1 ActにStartTriggerがない（3件）

**エラー内容**:
```
ValueError: Act 'Act_DistTest' must have a StartTrigger element
ValueError: Act 'SpeedProfileAct' must have a StartTrigger element
ValueError: Act 'act' must have a StartTrigger element
```

**影響ファイル**:
- `distance_test.xosc` (Act: Act_DistTest)
- `speed-profile.xosc` (Act: SpeedProfileAct)
- `swarm.xosc` (Act: act)

**原因**:
- `write_xml.py`の`write_act`関数で、ActにStartTriggerが必須としてチェックしている
- しかし、元のXOSCファイルではStartTriggerが省略されている可能性がある

**対応方針**:
- `write_act`関数のバリデーションを緩和する
- StartTriggerがNoneの場合は、デフォルトのStartTriggerを生成するか、エラーではなく警告として扱う

#### 1.2 ManeuverGroupにActorがない（3件）

**エラー内容**:
```
ValueError: ManeuverGroup 'DummyManueverGroup' must have at least one Actor
ValueError: ManeuverGroup 'empty' must have at least one Actor
```

**影響ファイル**:
- `parking_lot.xosc` (ManeuverGroup: DummyManueverGroup)
- `trailers.xosc` (ManeuverGroup: empty)
- `truck_with_rotating_axle.xosc` (ManeuverGroup: DummyManueverGroup)

**原因**:
- `write_xml.py`の`write_maneuver_group`関数で、ManeuverGroupにActorが必須としてチェックしている
- しかし、元のXOSCファイルでは空のManeuverGroupが存在している可能性がある
- これらはダミーのManeuverGroupで、実際には使用されていない可能性がある

**対応方針**:
- `write_maneuver_group`関数のバリデーションを緩和する
- Actorが空の場合は、エラーではなく警告として扱うか、スキップする

### 2. esmini実行エラー（40件）❌

#### 2.1 Catalogファイルが見つからない（継続中）

**エラー内容**:
```
[] [error] Couldn't locate OpenSCENARIO file VehicleCatalog
[] [error] Exception: [] [error] Couldn't locate OpenSCENARIO file VehicleCatalog
```

**影響ファイル**: 全40ファイル

**esminiが検索したパス**:
```
C:/Users/Owner/AppData/Local/Temp/xosc_editor_xxx/../xosc/Catalogs/Vehicles/./VehicleCatalog.xosc
E:\Repository\XOSC_Editor\thirdparty\esmini\bin/../resources/xosc/Catalogs/Vehicles/./VehicleCatalog.xosc
```

**実際のCatalogファイルの場所**:
```
thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/Catalogs/Vehicles/VehicleCatalog.xosc
```

**問題点**:
- esminiは一時ファイルのディレクトリから相対パスでCatalogファイルを解決しようとしている
- しかし、Catalogファイルは元のXOSCファイルのディレクトリにある
- 一時ファイルのディレクトリからは、このパスにアクセスできない

**現在の状況**:
- ユーザーが「Catalogファイルを解決しました」と報告しているが、まだエラーが発生している
- `EsminiRunner`クラスにCatalogファイルをコピーする機能が追加されていない可能性がある

**確認が必要な点**:
1. `EsminiRunner._create_temp_scenario`メソッドでCatalogファイルをコピーしているか
2. 一時ディレクトリに`xosc/Catalogs/`構造を作成しているか
3. または、esminiの`--path`オプションを使用してリソースパスを指定しているか

#### 2.2 その他のエラー

**cut-in_sumo.xosc**:
```
[] [error] Exception: invalid stof argument
```
- 数値変換エラー（stof = string to float）
- パラメータ値の形式に問題がある可能性

**trajectory-test.xosc**:
```
[] [error] Exception: invalid stof argument
```
- 同様の数値変換エラー

**cut-in_parameter_set.xosc**:
- ヘルプメッセージが表示されている（コマンドライン引数の問題の可能性）

#### 2.3 警告（esmini実装によるもの）

以下の警告はesminiの実装によるもので、XOSC Editorの問題ではない：
- `Unsupported geo reference attr: +no_defs`
- `Unsupported object type: guide-post - interpret as NONE`
- `Unsupported object type: rail-pole - interpret as NONE`

## 優先度

### 高優先度 🔴
1. **Catalogファイルの解決** - esmini実行が全く成功していないため、最優先で対応が必要
   - `EsminiRunner._create_temp_scenario`メソッドでCatalogファイルをコピーする機能を追加
   - または、esminiの`--path`オプションを使用してリソースパスを指定

### 中優先度 🟡
2. **ActのStartTriggerバリデーション** - 3ファイルで書き出しエラーが発生
3. **ManeuverGroupのActorバリデーション** - 3ファイルで書き出しエラーが発生

### 低優先度 🟢
4. **数値変換エラー** - 2ファイルで発生（パラメータ値の形式の問題の可能性）
5. **その他の警告** - esminiの実装によるもので、XOSC Editor側での対応は不要

## 推奨される対応手順

1. **Catalogファイルの解決を確認・実装**
   - `EsminiRunner._create_temp_scenario`メソッドを確認
   - Catalogファイルを一時ディレクトリにコピーする機能を追加
   - または、esminiの`--path`オプションを使用

2. **バリデーションの緩和**
   - `write_act`関数: StartTriggerがNoneの場合は警告またはデフォルト値を生成
   - `write_maneuver_group`関数: Actorが空の場合は警告またはスキップ

3. **再テスト**
   - 修正後に再度バッチ処理を実行
   - エラーレポートを確認

## 参考情報

- エラーレポート: `out/xosc/error_report_20251123_125215.txt`
- バッチ処理スクリプト: `scripts/batch_test_xosc.py`
- テスト対象ディレクトリ: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/`
- Catalogファイルの場所: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/Catalogs/`

