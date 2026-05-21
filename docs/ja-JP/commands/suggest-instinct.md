---
name: suggest-instinct
description: 新しいインスティンクトを提案する
command: true
---

# インスティンクト提案コマンド

現在の作業コンテキストを分析して、追加すべき新しいインスティンクトを提案します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" suggest [--context CONTEXT]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py suggest [--context CONTEXT]
```

## 使い方

```bash
/suggest-instinct                            # 現在のコンテキストから提案
/suggest-instinct --context "エラーハンドリング"  # 特定コンテキストから提案
```

## 動作内容

1. 最近の作業パターンを分析
2. 既存インスティンクトとのギャップを特定
3. 具体的なインスティンクト候補を生成
4. ユーザーが承認したものをライブラリに追加
