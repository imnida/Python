---
name: smart-commit
description: インスティンクトを活用したスマートコミットを実行する
command: true
---

# スマートコミットコマンド

インスティンクトと変更の文脈を組み合わせて、高品質なコミットメッセージを自動生成してコミットします。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/smart-commit/scripts/commit-cli.py" [--push] [--branch BRANCH]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/smart-commit/scripts/commit-cli.py [--push] [--branch BRANCH]
```

## 使い方

```bash
/smart-commit              # スマートコミットを実行
/smart-commit --push       # コミット後にプッシュ
/smart-commit --branch dev # 特定ブランチにコミット
```

## 動作内容

1. ステージングされた変更を分析
2. 関連インスティンクトを参照
3. Conventionalコミット形式でメッセージを生成
4. プレビューを表示し確認後にコミット
