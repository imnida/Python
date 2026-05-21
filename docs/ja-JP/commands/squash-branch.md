---
name: squash-branch
description: ブランチのコミットをスカッシュする
command: true
---

# スカッシュブランチコマンド

現在のブランチのすべてのコミットを1つのコミットにスカッシュします。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/git-tools/scripts/squash-cli.py" [--base BASE_BRANCH] [--message MSG]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/git-tools/scripts/squash-cli.py [--base BASE_BRANCH] [--message MSG]
```

## 使い方

```bash
/squash-branch                          # デフォルトでmainからスカッシュ
/squash-branch --base develop           # developからのコミットをスカッシュ
/squash-branch --message "feat: new"    # コミットメッセージを指定
```

## 動作内容

1. ベースブランチとの差分を確認
2. スカッシュするコミット一覧を表示
3. 確認後に `git rebase --squash` を実行
4. 新しいコミットメッセージを入力
