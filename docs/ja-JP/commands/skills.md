---
name: skills
description: インストールされているスキルを一覧表示する
command: true
---

# スキルコマンド

インストールされているすべてのスキルとその状態を一覧表示します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/skill-manager/scripts/skill-cli.py" list [--verbose]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/skill-manager/scripts/skill-cli.py list [--verbose]
```

## 使い方

```bash
/skills              # スキル一覧を表示
/skills --verbose    # 詳細情報付きで表示
```

## 表示内容

- スキル名とバージョン
- インストール状態（有効/無効）
- 最終更新日
- 提供するコマンド数
- 簡単な説明
