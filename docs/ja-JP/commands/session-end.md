---
name: session-end
description: セッション終了時のクリーンアップと学習記録を実行する
command: true
---

# セッション終了コマンド

セッション終了時にクリーンアップを行い、学習した内容をインスティンクトとして保存します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" session-end [--save-observations]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py session-end [--save-observations]
```

## 使い方

```bash
/session-end                          # 通常のセッション終了
/session-end --save-observations      # 観察内容を保存して終了
```

## 実行内容

1. セッション中の観察ログを収集
2. パターンとインサイトを抽出
3. インスティンクトとして保存（承認後）
4. 一時ファイルのクリーンアップ
5. セッションサマリーを表示
