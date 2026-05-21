---
name: prp-plan
description: タスクの実装計画を立案する
command: true
---

# PRP プランコマンド

与えられたタスクまたは問題に対して、構造化された実装計画を生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/pr-pilot/scripts/prp-cli.py" plan [task_description]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/pr-pilot/scripts/prp-cli.py plan [task_description]
```

## 使い方

```bash
/prp-plan "新しいAPIエンドポイントを追加する"    # タスク計画を生成
/prp-plan                                      # インタラクティブモードで起動
```

## 動作内容

1. タスクの説明を解析
2. 必要なステップを特定
3. 依存関係と順序を整理
4. 推定工数と注意点を含む計画書を出力
