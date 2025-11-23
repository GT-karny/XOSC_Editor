# XOSCバッチ処理テスト結果と課題

## テスト概要

- **テスト日時**: 2025-11-23
- **テスト対象**: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/` 内の全40ファイル
- **テスト内容**: 
  1. XOSCファイルの読み込み（parse_xml）
  2. XOSCファイルの書き出し（write_xml）
  3. esminiでの実行

## テスト結果サマリー

- **総ファイル数**: 40
- **読み込み成功**: 40 (100%)
- **書き出し成功**: 34 (85%)
- **書き出しエラー**: 6 (15%)
- **esmini実行成功**: 0 (0%)
- **esmini実行エラー**: 40 (100%)

## 課題一覧

### 1. 書き出しエラー（6件）

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
- OpenSCENARIO仕様では、ActのStartTriggerは必須ではない場合もある

**対応方針**:
- `write_act`関数のバリデーションを緩和する
- StartTriggerがNoneの場合は、デフォルトのStartTriggerを生成するか、エラーではなく警告として扱う
- または、元のXOSCファイルの構造を確認し、StartTriggerが本当に必要かどうかを判断する

#### 1.2 ManeuverGroupにActorがない（3件）

**エラー内容**:
```
ValueError: ManeuverGroup 'DummyManueverGroup' must have at least one Actor
ValueError: ManeuverGroup 'empty' must have at least one Actor
```

**影響ファイル**:
- `ltap-od.xosc` (ManeuverGroup: DummyManueverGroup)
- `trailer_connect.xosc` (ManeuverGroup: DummyManueverGroup)
- `trailers.xosc` (ManeuverGroup: empty)

**原因**:
- `write_xml.py`の`write_maneuver_group`関数で、ManeuverGroupにActorが必須としてチェックしている
- しかし、元のXOSCファイルでは空のManeuverGroupが存在している可能性がある
- これらはダミーのManeuverGroupで、実際には使用されていない可能性がある

**対応方針**:
- `write_maneuver_group`関数のバリデーションを緩和する
- Actorが空の場合は、エラーではなく警告として扱うか、スキップする
- または、元のXOSCファイルの構造を確認し、空のManeuverGroupが本当に必要かどうかを判断する

### 2. esmini実行エラー（40件）

#### 2.1 Catalogファイルが見つからない

**エラー内容**:
```
[] [error] Couldn't locate OpenSCENARIO file VehicleCatalog
[] [error] Exception: [] [error] Couldn't locate OpenSCENARIO file VehicleCatalog
```

**影響ファイル**: 全40ファイル

**原因**:
- esmini実行時に、一時ファイルのディレクトリから相対パスでCatalogファイルを解決しようとしている
- しかし、Catalogファイルは元のXOSCファイルのディレクトリ（`thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/Catalogs/`）にある
- 一時ファイルのディレクトリからは、このパスにアクセスできない

**検索パス（esminiが試行したパス）**:
```
C:/Users/Owner/AppData/Local/Temp/xosc_editor_xxx/../xosc/Catalogs/Vehicles/./VehicleCatalog.xosc
E:\Repository\XOSC_Editor\thirdparty\esmini\bin/../resources/xosc/Catalogs/Vehicles/./VehicleCatalog.xosc
```

**対応方針**:
1. **一時ファイルのディレクトリにCatalogファイルをコピー/シンボリックリンクする**
   - 一時ファイル作成時に、必要なCatalogファイルを一時ディレクトリにコピー
   - または、シンボリックリンクを作成（Windowsでは管理者権限が必要な場合がある）

2. **esmini実行時に適切なリソースパスを指定する**
   - esminiの`--path`オプションを使用して、リソースディレクトリを指定
   - または、環境変数でリソースパスを設定

3. **元のXOSCファイルのディレクトリ構造を維持する**
   - 一時ファイルではなく、元のディレクトリ構造を維持した場所に書き出す
   - または、元のXOSCファイルを直接使用する

#### 2.2 OpenDRIVEファイルの相対パス解決

**状況**:
- OpenDRIVEファイル（`../xodr/straight_500m.xodr`など）は正常に読み込まれている
- これは、esmini実行時に作業ディレクトリを元のXOSCファイルのディレクトリに設定したため

**確認事項**:
- OpenDRIVEファイルの読み込みは成功している
- 問題はCatalogファイルの解決のみ

#### 2.3 その他の警告

**警告内容**:
```
[] [error] Unsupported geo reference attr: +no_defs
[] [error] Unsupported object type: guide-post - interpret as NONE
[] [error] Unsupported object type: rail-pole - interpret as NONE
```

**影響**: これらの警告はesminiの実装によるもので、XOSC Editorの問題ではない

## 優先度

### 高優先度
1. **Catalogファイルの解決** - esmini実行が全く成功していないため、最優先で対応が必要
2. **ActのStartTriggerバリデーション** - 3ファイルで書き出しエラーが発生

### 中優先度
3. **ManeuverGroupのActorバリデーション** - 3ファイルで書き出しエラーが発生

### 低優先度
4. **その他の警告** - esminiの実装によるもので、XOSC Editor側での対応は不要

## 推奨される対応手順

1. **Catalogファイルの解決を実装**
   - 一時ファイル作成時に、Catalogファイルを一時ディレクトリにコピー
   - または、esminiの`--path`オプションを使用

2. **バリデーションの緩和**
   - `write_act`関数: StartTriggerがNoneの場合は警告またはデフォルト値を生成
   - `write_maneuver_group`関数: Actorが空の場合は警告またはスキップ

3. **再テスト**
   - 修正後に再度バッチ処理を実行
   - エラーレポートを確認

## 参考情報

- エラーレポート: `out/xosc/error_report_20251123_125009.txt`
- バッチ処理スクリプト: `scripts/batch_test_xosc.py`
- テスト対象ディレクトリ: `thirdparty/esmini-demo_Windows/esmini-demo/resources/xosc/`

