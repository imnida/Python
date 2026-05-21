---
name: skill-doctor
description: スキルの健全性チェックと診断を実行する
command: true
---

# スキルドクターコマンド

インストールされているスキルの健全性チェック、設定の問題、依存関係の欠落を診断します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/skill-manager/scripts/skill-doctor.py" [--skill SKILL] [--fix]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/skill-manager/scripts/skill-doctor.py [--skill SKILL] [--fix]
```

## 使い方

```bash
/skill-doctor                           # 全スキルの診断
/skill-doctor --skill continuous-learning  # 特定スキルの診断
/skill-doctor --fix                     # 問題を自動修正
```

## 診断項目

- スキルファイルの存在確認
- 依存パッケージのチェック
- 設定ファイルの妥当性
- パーミッションの確認
- バージョン互換性
