---
name: task
description: 構造化されたタスクを実行する
command: true
---

# タスクコマンド

構造化されたタスク記述に従って、複数ステップの作業を実行します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/task-runner/scripts/task-cli.py" [task_file_or_description]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/task-runner/scripts/task-cli.py [task_file_or_description]
```

## 使い方

```bash
/task task.yml                    # タスクファイルから実行
/task "APIエンドポイントを追加"     # テキスト記述から実行
/task --list                      # 利用可能なタスクを一覧表示
```

## タスクファイル形式

```yaml
name: タスク名
steps:
  - name: ステップ1
    command: ...
  - name: ステップ2
    depends_on: [ステップ1]
    command: ...
```
