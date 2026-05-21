---
name: scaffold
description: 新しいコンポーネントやモジュールのスキャフォールドを作成する
command: true
---

# スキャフォールドコマンド

指定されたタイプの新しいコンポーネント、モジュール、またはサービスのボイラープレートコードを生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/scaffold/scripts/scaffold-cli.py" [type] [name] [--template TEMPLATE]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/scaffold/scripts/scaffold-cli.py [type] [name] [--template TEMPLATE]
```

## 使い方

```bash
/scaffold component UserCard      # Reactコンポーネントを生成
/scaffold service AuthService     # サービスクラスを生成
/scaffold api /users              # APIエンドポイントを生成
/scaffold --template custom       # カスタムテンプレートを使用
```

## 生成されるファイル

- メインファイル（コンポーネント/サービス/API）
- テストファイル
- 型定義ファイル
- インデックスエクスポート
