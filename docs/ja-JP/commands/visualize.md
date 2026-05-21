---
name: visualize
description: コードベースやデータを視覚化する
command: true
---

# ビジュアライズコマンド

コードベースの構造、依存関係グラフ、データフローを視覚的に表現します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/visualizer/scripts/viz-cli.py" [type] [--output FORMAT]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/visualizer/scripts/viz-cli.py [type] [--output FORMAT]
```

## 使い方

```bash
/visualize deps                  # 依存関係グラフを表示
/visualize structure             # ディレクトリ構造を視覚化
/visualize --output mermaid      # Mermaid形式で出力
/visualize --output dot          # Graphviz DOT形式で出力
```

## 視覚化タイプ

- `deps`: 依存関係グラフ
- `structure`: ディレクトリ/ファイル構造
- `flow`: データフロー図
- `classes`: クラス継承図
