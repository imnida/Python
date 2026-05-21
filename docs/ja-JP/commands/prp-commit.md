---
name: prp-commit
description: PRのコミットメッセージを生成する
command: true
---

# PRP コミットコマンド

現在のステージングされた変更に基づいて、意味のあるコミットメッセージを生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/pr-pilot/scripts/prp-cli.py" commit [--conventional] [--verbose]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/pr-pilot/scripts/prp-cli.py commit [--conventional] [--verbose]
```

## 使い方

```bash
/prp-commit                  # 標準コミットメッセージを生成
/prp-commit --conventional   # Conventionalコミット形式で生成
/prp-commit --verbose        # 詳細な説明付きで生成
```

## 動作内容

1. `git diff --staged` を実行して変更内容を取得
2. 変更の種類と影響範囲を分析
3. 適切なコミットメッセージを生成
4. オプションに応じてフォーマットを調整
