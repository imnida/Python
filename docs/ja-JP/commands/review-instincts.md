---
name: review-instincts
description: 現在のインスティンクトライブラリをレビューする
command: true
---

# インスティンクトレビューコマンド

インスティンクトライブラリを表示し、品質、関連性、改善の機会を評価します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" review [--scope SCOPE] [--sort-by FIELD]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py review [--scope SCOPE] [--sort-by FIELD]
```

## 使い方

```bash
/review-instincts                         # 全インスティンクトをレビュー
/review-instincts --scope global          # グローバルスコープのみ
/review-instincts --sort-by confidence    # 信頼度でソート
/review-instincts --sort-by last-used     # 最終使用日でソート
```

## 表示項目

- インスティンクトID、タイトル、スコープ
- 信頼度スコア
- 使用回数と最終使用日
- 関連するプロジェクト数
