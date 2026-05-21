---
name: spec
description: 機能仕様書を生成する
command: true
---

# スペックコマンド

要件や会話コンテキストから、詳細な機能仕様書を生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/spec-writer/scripts/spec-cli.py" [feature_description] [--format FORMAT]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/spec-writer/scripts/spec-cli.py [feature_description] [--format FORMAT]
```

## 使い方

```bash
/spec "ユーザー認証機能"          # 機能仕様書を生成
/spec --format markdown          # Markdown形式で生成
/spec --format json              # JSON形式で生成
```

## 仕様書の内容

- 機能の概要と目的
- ユーザーストーリー
- 受け入れ基準
- 技術的要件
- 除外事項
