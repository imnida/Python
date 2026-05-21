---
name: prompt-optimize
description: 現在の会話からプロンプト最適化候補を生成する
command: true
---

# プロンプト最適化コマンド

現在の会話コンテキストを分析して、指定されたトピックについてより効果的なプロンプトを生成します。

## 実装

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-optimizer/scripts/optimize-cli.py" [--topic TOPIC] [--output-format FORMAT]
```

または `CLAUDE_PLUGIN_ROOT` が設定されていない場合:

```bash
python3 ~/.claude/skills/prompt-optimizer/scripts/optimize-cli.py [--topic TOPIC] [--output-format FORMAT]
```

## 使い方

```bash
/prompt-optimize                        # 汎用的なプロンプト最適化
/prompt-optimize --topic "コードレビュー"   # 特定トピックに特化
/prompt-optimize --output-format json   # JSON形式で出力
```

## パラメータ

| パラメータ | 説明 | デフォルト |
|-----------|------|----------|
| `--topic` | 最適化対象のトピック | 汎用 |
| `--output-format` | 出力形式 (text/json/markdown) | text |

## 動作内容

1. 最近の会話コンテキストを分析
2. 繰り返しのパターンを検出
3. 効果的なプロンプト構造を提案
4. 具体的な改善例を生成
