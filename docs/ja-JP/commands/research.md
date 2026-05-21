---
name: research
description: 指定されたトピックをリサーチして知識を整理する
command: true
---

# リサーチコマンド

指定されたトピックについてコードベースや関連ファイルを調査し、知識を整理して報告します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/research/scripts/research-cli.py" [topic] [--depth DEPTH]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/research/scripts/research-cli.py [topic] [--depth DEPTH]
```

## 使い方

```bash
/research "認証システム"          # トピックをリサーチ
/research --depth deep           # 詳細な調査を実行
/research "API設計" --depth quick # 簡易調査を実行
```

## 動作内容

1. トピックに関連するファイルを検索
2. コードパターンとアーキテクチャを分析
3. 依存関係を追跡
4. 整理された調査報告を生成
