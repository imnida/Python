---
name: python-review
description: Pythonコードのレビューを実行する
command: true
---

# Pythonレビューコマンド

Pythonコードに対して包括的なコードレビューを実行し、改善点を提案します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/code-review/scripts/review-cli.py" --language python [file_or_directory]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/code-review/scripts/review-cli.py --language python [file_or_directory]
```

## 使い方

```bash
/python-review src/           # ディレクトリ全体をレビュー
/python-review app.py         # 単一ファイルをレビュー
/python-review --changed      # 変更されたファイルのみレビュー
```

## レビュー項目

- PEP 8 スタイルガイドへの準拠
- 型アノテーションの使用
- エラーハンドリングの適切性
- パフォーマンスの問題
- セキュリティの脆弱性
- テストカバレッジ
