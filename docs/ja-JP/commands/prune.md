---
name: prune
description: 低品質または陳腐化したインスティンクトを削除する
command: true
---

# プルーンコマンド

信頼度が低い、または長期間使用されていないインスティンクトを削除してライブラリを整理します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" prune [--dry-run] [--min-confidence CONF] [--max-age DAYS]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py prune [--dry-run] [--min-confidence CONF] [--max-age DAYS]
```

## 使い方

```bash
/prune                           # デフォルト設定でプルーニング
/prune --dry-run                 # 削除対象をプレビュー
/prune --min-confidence 0.7      # 信頼度0.7未満を削除
/prune --max-age 90              # 90日以上未使用を削除
```

## 動作内容

1. 全インスティンクトをスキャン
2. 信頼度と最終使用日を確認
3. 削除対象をリストアップ
4. 確認後に削除を実行
