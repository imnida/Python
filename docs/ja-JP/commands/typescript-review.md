---
name: typescript-review
description: TypeScriptコードのレビューを実行する
command: true
---

# TypeScriptレビューコマンド

TypeScriptコードに対して包括的なコードレビューを実行し、型安全性と品質を向上させます。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/code-review/scripts/review-cli.py" --language typescript [file_or_directory]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/code-review/scripts/review-cli.py --language typescript [file_or_directory]
```

## 使い方

```bash
/typescript-review src/        # ディレクトリ全体をレビュー
/typescript-review app.ts      # 単一ファイルをレビュー
/typescript-review --strict    # 厳格モードでレビュー
```

## レビュー項目

- 型アノテーションの正確性
- `any`型の不適切な使用
- null/undefined の安全な処理
- インターフェースとジェネリクスの活用
- 非同期処理のパターン
