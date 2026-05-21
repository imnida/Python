---
name: update-instinct
description: 既存のインスティンクトを更新する
command: true
---

# インスティンクト更新コマンド

指定されたインスティンクトの内容を更新します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" update <instinct-id> [--field FIELD] [--value VALUE]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py update <instinct-id> [--field FIELD] [--value VALUE]
```

## 使い方

```bash
/update-instinct abc123 --field confidence --value 0.9   # 信頼度を更新
/update-instinct abc123 --field description --value "新しい説明"  # 説明を更新
/update-instinct abc123                                  # インタラクティブ更新
```

## 更新可能なフィールド

- `title`: インスティンクトのタイトル
- `description`: 説明文
- `confidence`: 信頼度スコア (0.0-1.0)
- `tags`: タグリスト
- `examples`: 使用例
