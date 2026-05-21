---
name: search-instincts
description: キーワードでインスティンクトを検索する
command: true
---

# インスティンクト検索コマンド

キーワードやタグでインスティンクトライブラリを検索します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" search <query> [--scope SCOPE] [--tag TAG]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py search <query> [--scope SCOPE] [--tag TAG]
```

## 使い方

```bash
/search-instincts "エラーハンドリング"          # キーワード検索
/search-instincts "テスト" --scope global      # グローバルスコープのみ検索
/search-instincts --tag python                # タグで検索
```

## 検索対象

- インスティンクトのタイトル
- 説明文
- タグ
- 例示コード
