---
name: refactor-clean
description: コードのリファクタリングと整理を行う
command: true
---

# リファクタークリーンコマンド

コードの可読性、保守性、パフォーマンスを向上させるためのリファクタリングを提案・実行します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/refactor/scripts/refactor-cli.py" clean [--auto] [target]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/refactor/scripts/refactor-cli.py clean [--auto] [target]
```

## 使い方

```bash
/refactor-clean src/          # ソースディレクトリをリファクタリング
/refactor-clean --auto        # 自動リファクタリングを実行
/refactor-clean app.py        # 単一ファイルをリファクタリング
```

## リファクタリング項目

- 不要なコードの削除
- 関数・クラスの分割・統合
- 変数名の改善
- インポートの整理
- コメントの最適化
