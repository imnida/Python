---
name: run-checks
description: プロジェクトの全チェックを実行する
command: true
---

# チェック実行コマンド

リント、テスト、型チェックなど、設定されたすべてのチェックを順番に実行します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/run-checks/scripts/checks-cli.py" [--fix] [--parallel]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/run-checks/scripts/checks-cli.py [--fix] [--parallel]
```

## 使い方

```bash
/run-checks              # 全チェックを実行
/run-checks --fix        # 自動修正可能なものを修正
/run-checks --parallel   # 並列実行でスピードアップ
```

## 実行されるチェック

- ESLint / Ruff (リント)
- Jest / Pytest (テスト)
- TypeScript / mypy (型チェック)
- Prettier / Black (フォーマット)
