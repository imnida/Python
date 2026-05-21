---
name: agent-introspection-debugging
description: エージェントの自己診断とデバッグを支援するスキル
version: 1.0.0
---

# エージェント自己診断・デバッグスキル

Claude Codeエージェントが自身の動作を診断し、問題をデバッグするためのスキルです。

## 概要

エージェントの実行状態、メモリ使用量、ツール呼び出しパターン、エラーを分析して問題を特定します。

## 機能

- **状態検査**: エージェントの現在の状態とコンテキストを検査
- **ツール分析**: ツール呼び出しパターンと成功率を分析
- **エラー追跡**: エラーと例外の詳細追跡
- **パフォーマンス測定**: レスポンス時間とリソース使用量の測定

## 使い方

```bash
/debug-agent              # エージェント状態を診断
/debug-agent --trace      # 詳細な実行トレースを表示
/debug-agent --memory     # メモリ使用状況を確認
```

## 出力例

```
Agent State: Running
Context Size: 45,230 tokens
Tool Calls: 12 (11 success, 1 error)
Last Error: FileNotFoundError at step 8
```
