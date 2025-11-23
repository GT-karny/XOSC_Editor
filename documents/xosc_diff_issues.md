# XOSCファイル差分確認結果と問題点

## テスト概要

- **テスト日時**: 2025-11-23 12:57:06
- **比較対象**: 書き出し成功した34ファイル
- **問題検出数**: 18件

## 問題点の分類

### 1. ParameterDeclarationsの欠落（5件）🔴

**問題**: 元ファイルに空の`<ParameterDeclarations/>`要素がある場合、書き出しファイルでは完全に欠落している

**影響ファイル**:
1. `bicycle_fall_over.xosc`
2. `cut-in_sumo.xosc`
3. `routing-test.xosc`
4. `sumo-test.xosc`
5. `tunnels.xosc` (属性の違いも1件)

**原因**:
- `write_parameter_declarations`関数（`write_xml.py:150-163`）で、`param_decls.parameters`が空の場合に`return`している
- しかし、元ファイルには空の`<ParameterDeclarations/>`要素が存在する場合がある
- OpenSCENARIO仕様では、空の`ParameterDeclarations`要素も有効

**対応方針**:
```python
def write_parameter_declarations(parent: ET.Element, param_decls: ParameterDeclarations):
    """ParameterDeclarationsをXMLに書き込み"""
    elem = _create_element("ParameterDeclarations", parent)
    # 空の場合でも要素を作成（元ファイルとの互換性のため）
    if param_decls.parameters:
        for param in param_decls.parameters:
            # ... 既存の処理
```

### 2. ParameterValueDistributionの未サポート（1件）🔴

**問題**: `cut-in_parameter_set.xosc`は`ParameterValueDistribution`要素を含む特殊なファイルで、現在のパーサー/ライターではサポートされていない

**影響ファイル**:
- `cut-in_parameter_set.xosc`

**元ファイルの構造**:
```xml
<OpenSCENARIO>
  <FileHeader ... />
  <ParameterValueDistribution>
    <ScenarioFile filepath="cut-in.xosc" />
    <Deterministic>
      <!-- パラメータ分布の定義 -->
    </Deterministic>
  </ParameterValueDistribution>
</OpenSCENARIO>
```

**書き出しファイルの構造**:
```xml
<OpenSCENARIO>
  <FileHeader ... />
</OpenSCENARIO>
```

**原因**:
- `ParameterValueDistribution`はOpenSCENARIO 1.2の拡張機能で、パラメータ値の分布を定義する
- 現在のモデル（`model.py`）とパーサー（`parse_xml.py`）でサポートされていない
- そのため、読み込み時に無視され、書き出し時に欠落する

**対応方針**:
- `ParameterValueDistribution`のサポートを追加するか
- または、このファイルタイプを別途処理する

### 3. ファイルサイズの大幅な減少（12件）🟡

**問題**: すべてのファイルで40-80%のサイズ減少

**影響ファイル**:
1. `controller_test.xosc` (-61.0%)
2. `cut-in_parameter_set.xosc` (-81.9%) - ParameterValueDistributionの欠落も影響
3. `cut-in_visibility.xosc` (-50.3%)
4. `drop-bike.xosc` (-54.0%)
5. `highway_merge_advanced.xosc` (-51.1%)
6. `lane-change_clothoid_based_trajectory.xosc` (-50.8%)
7. `lane_change_simple.xosc` (-52.4%)
8. `pedestrian.xosc` (-54.6%)
9. `pedestrian_collision.xosc` (-56.0%)
10. `synch_with_steady_state.xosc` (-50.7%)
11. `trailer_connect.xosc` (-55.3%)
12. `trajectory-test.xosc` (-57.2%)
13. `two_plus_one_road.xosc` (-52.6%)

**原因**:
1. **XMLフォーマットの違い**
   - 元ファイル: インデント付きの整形されたXML（複数行）
   - 書き出しファイル: 1行にまとめられたXML（`pretty_print=True`でも2行のみ）
   - `ET.indent()`が正しく機能していない可能性

2. **コメントの欠落**
   - 元ファイルにはXMLコメント（`<!-- ... -->`）が含まれている
   - 現在のパーサー/ライターではコメントを保持していない

3. **空要素の処理方法の違い**
   - 元ファイル: `<Element/>`（自己完結タグ）
   - 書き出しファイル: `<Element></Element>`（開始/終了タグ）または欠落

**対応方針**:
1. **XMLフォーマットの改善**
   - `ET.indent()`の動作を確認
   - 必要に応じて、カスタムのフォーマット関数を実装

2. **コメントの保持**
   - XMLコメントをパースして保持する機能を追加
   - または、コメントを無視することを明示

3. **空要素の処理**
   - 空要素の処理方法を統一

### 4. その他の問題

#### 4.1 行数の大幅な減少

**問題**: すべてのファイルで行数が大幅に減少（元ファイル: 97-363行 → 書き出しファイル: 2行）

**原因**:
- XMLが1行にまとめられている
- `ET.indent()`が正しく機能していない

**確認が必要**:
- `write_xml`関数の`pretty_print=True`オプションが正しく機能しているか
- `ET.indent()`がPython 3.9+で利用可能か

## 優先度

### 高優先度 🔴
1. **ParameterDeclarationsの欠落** - 5ファイルで構造の違いが発生
2. **ParameterValueDistributionの未サポート** - 1ファイルで主要な要素が欠落

### 中優先度 🟡
3. **XMLフォーマットの問題** - すべてのファイルで可読性が低下
4. **コメントの欠落** - 元ファイルの情報が失われる

### 低優先度 🟢
5. **空要素の処理方法の違い** - 機能的には問題ないが、互換性のため統一すべき

## 推奨される対応手順

1. **ParameterDeclarationsの修正**
   - `write_parameter_declarations`関数を修正して、空の場合でも要素を作成

2. **XMLフォーマットの確認**
   - `ET.indent()`の動作を確認
   - 必要に応じて、カスタムのフォーマット関数を実装

3. **ParameterValueDistributionの検討**
   - サポートを追加するか、別途処理するかを決定

4. **コメントの保持（オプション）**
   - 必要に応じて、コメントを保持する機能を追加

## 参考情報

- 差分レポート: `out/xosc/diff_report_20251123_125706.txt`
- 比較スクリプト: `scripts/compare_xosc_files.py`
- 書き出し関数: `osc_editor/core/write_xml.py`

