---
name: prp-pr
description: プルリクエストの説明を生成する
command: true
---

# PRP PR コマンド

現在のブランチの変更に基づいて、包括的なプルリクエストの説明を生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/pr-pilot/scripts/prp-cli.py" pr [--template TEMPLATE] [--base BASE_BRANCH]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/pr-pilot/scripts/prp-cli.py pr [--template TEMPLATE] [--base BASE_BRANCH]
```

## 使い方

```bash
/prp-pr                         # デフォルトテンプレートでPR説明を生成
/prp-pr --template custom       # カスタムテンプレートを使用
/prp-pr --base develop          # ベースブランチを指定
```

## 動作内容

1. ベースブランチとの差分を取得
2. 変更の種類と影響を分析
3. テンプレートに従ってPR説明を構造化
4. レビュアーへの注意点も含める
