---
name: quality-gate
description: コードの品質基準をチェックする
command: true
---

# クオリティゲートコマンド

定義された品質基準に対してコードをチェックし、マージ前の品質を保証します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/quality-gate/scripts/gate-cli.py" [--config CONFIG] [--strict]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/quality-gate/scripts/gate-cli.py [--config CONFIG] [--strict]
```

## 使い方

```bash
/quality-gate              # デフォルト設定で品質チェック
/quality-gate --strict     # 厳格モードで実行
/quality-gate --config .quality-gate.yml  # カスタム設定ファイルを使用
```

## チェック項目

- テストカバレッジ率
- 複雑度メトリクス
- 重複コードの検出
- セキュリティスキャン
- ドキュメントカバレッジ
