---
name: remove-instinct
description: 特定のインスティンクトを削除する
command: true
---

# インスティンクト削除コマンド

指定されたインスティンクトをライブラリから削除します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" remove <instinct-id> [--force]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py remove <instinct-id> [--force]
```

## 使い方

```bash
/remove-instinct abc123        # 確認後に削除
/remove-instinct abc123 --force  # 確認なしに削除
```

## 動作内容

1. 指定されたIDのインスティンクトを検索
2. インスティンクトの詳細を表示
3. 削除の確認を求める（--forceなし）
4. 確認後にファイルを削除
