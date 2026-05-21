---
name: watch
description: ファイル変更を監視して自動アクションを実行する
command: true
---

# ウォッチコマンド

ファイルの変更を監視し、変更が検出されたときに設定されたアクションを自動実行します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/watcher/scripts/watch-cli.py" [pattern] [--action ACTION]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/watcher/scripts/watch-cli.py [pattern] [--action ACTION]
```

## 使い方

```bash
/watch src/               # srcディレクトリを監視
/watch **/*.py --action test  # Pythonファイル変更時にテストを実行
/watch --action lint      # 変更時にリントを実行
```

## 監視オプション

- `--action test`: テストを実行
- `--action lint`: リントを実行
- `--action build`: ビルドを実行
- `--action custom CMD`: カスタムコマンドを実行
