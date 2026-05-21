---
name: test-strategy
description: プロジェクトのテスト戦略を分析・提案する
command: true
---

# テスト戦略コマンド

現在のテストカバレッジを分析し、包括的なテスト戦略を提案します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/test-strategy/scripts/strategy-cli.py" [--analyze] [--suggest]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/test-strategy/scripts/strategy-cli.py [--analyze] [--suggest]
```

## 使い方

```bash
/test-strategy              # テスト戦略の概要を表示
/test-strategy --analyze    # 現在のテスト状況を分析
/test-strategy --suggest    # 改善提案を生成
```

## 分析内容

- ユニットテスト、統合テスト、E2Eテストのバランス
- カバレッジが不足している領域
- テストの重複や冗長性
- モックとスタブの適切な使用
