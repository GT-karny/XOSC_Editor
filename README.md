# XOSC_Editor

本プロジェクトは **ASAM OpenSCENARIO 1.2 に対応したデスクトップ型シナリオエディタ** です。  
Python を用いた柔軟な実装と、esmini を利用した高速再生を特徴としています。

---

## 🚀 目的

- XML を直接編集せず、GUI で OpenSCENARIO 1.2 シナリオを構築できるようにする
- esmini と連携し **編集 → 再生 → 挙動確認** をワンストップで実現
- 将来的に RoadRunner / UE / ROS2 / 自社シミュレータ等と統合可能な基盤を用意する

---

## 🧩 アーキテクチャ概要

```
osc_editor/
  core/       ← OpenSCENARIO モデル・XML処理
  esmini/     ← esmini 実行ラッパ
  ui/         ← PySide6 GUI
  app.py      ← エントリポイント
```

### core/
- `model.py`  
  OpenSCENARIO 1.2 のデータモデル（dataclass）
- `parse_xml.py`  
  XML → model への変換
- `write_xml.py`  
  model → XML の生成
- `validate.py`  
  XSD バリデーション（後で実装予定）

### esmini/
- `runner.py`  
  `subprocess` 経由で esmini を起動  
  一時ファイルにシナリオを書き出して実行

### ui/
- `main_window.py`  
  メイン画面（メニュー・レイアウト）
- `scenario_tree.py`  
  Storyboard 階層表示（Story / Act / Maneuver / Event）
- `properties_panel.py`  
  SpeedAction / LaneChangeAction などの編集フォーム
- `menu_actions.py`  
  新規 / 開く / 保存 / esmini 再生

---

## 🎯 MVP 機能

### 必須で実装する内容
- シナリオの新規作成 / 保存 / 読み込み
- Entities（車両1台）の設定
- Storyboard構造の編集（Story → Act → Maneuver → Event → Action）
- 以下の Action を編集可能：
  - TeleportAction（初期位置）
  - SpeedAction（初期速度・目標速度）
  - LaneChangeAction（ターゲットレーン）
- StartTrigger（Time > X秒）の設定
- esmini での再生機能

### MVPで省略
- Traffic
- Catalog編集
- Environment
- 複雑なトリガ（距離判定など）
- 通常の複数 Story / 複数車両

---

## 🛠️ 技術スタック

- **Python 3.11+**
- **PySide6**（Qt for Python）
- **Poetry**（依存管理）
- **xml.etree / lxml**
- **esmini**（外部シミュレータ）

---

## 📦 セットアップ

### 1. Poetry インストール
```
pip install poetry
```

### 2. 依存インストール
```
poetry install
```

### 3. 実行
```
poetry run python -m osc_editor
```

---

## ▶️ esmini 連携

本エディタでは、GUI から「再生」ボタンを押すと：

1. 編集中の ScenarioDefinition を一時XMLへ出力  
2. `esmini --osc <tempfile>` を subprocess で起動  
3. 標準出力を GUI のログビューにリアルタイム表示  

という流れで動作します。

---

## 🧭 開発ロードマップ

### Phase 0  
- プロジェクト初期化  
- PySide6 のメインウィンドウ作成

### Phase 1  
- Dataclass モデル  
- XML パーサ / シリアライザ

### Phase 2  
- esmini runner（subprocess ラッパ）

### Phase 3  
- GUI骨格（ツリー＋プロパティ）

### Phase 4  
- GUI から XML 生成 → esmini 再生統合

### Phase 5  
- Action / Trigger の拡充  
- Catalog エディタ  
- Environment / Traffic 対応  
- 2D/3D View 連携（任意）