---
name: show-context
description: 現在のコンテキストとアクティブなインスティンクトを表示する
command: true
---

# コンテキスト表示コマンド

現在のプロジェクトコンテキスト、アクティブなインスティンクト、セッション情報を表示します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" show-context [--verbose]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py show-context [--verbose]
```

## 使い方

```bash
/show-context            # 現在のコンテキストを表示
/show-context --verbose  # 詳細情報を含めて表示
```

## 表示内容

- 現在のプロジェクト情報
- アクティブなインスティンクト一覧
- セッションID と開始時刻
- 適用されているインスティンクトの数
