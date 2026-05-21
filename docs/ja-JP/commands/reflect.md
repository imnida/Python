---
name: reflect
description: セッション終了時に学習内容を振り返る
command: true
---

# リフレクトコマンド

現在のセッションで観察したパターンや学習内容を振り返り、インスティンクトとして記録します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" reflect [--session-id ID]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py reflect [--session-id ID]
```

## 使い方

```bash
/reflect                        # 現在のセッションを振り返る
/reflect --session-id abc123    # 特定のセッションを振り返る
```

## 動作内容

1. セッションの観察ログを読み取る
2. 繰り返しパターンを識別
3. 新規または強化すべきインスティンクトを提案
4. ユーザーの承認後にインスティンクトを更新
