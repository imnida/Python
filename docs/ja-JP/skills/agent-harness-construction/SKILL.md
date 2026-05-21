---
name: agent-harness-construction
description: エージェント実行ハーネスを構築・設定するスキル
version: 1.0.0
---

# エージェントハーネス構築スキル

Claude Codeエージェントのための実行ハーネスを構築・設定するスキルです。

## 概要

このスキルは以下のユースケースに対応しています：

- ウェブ上のClaude Codeのセットアップ
- テストとリンターを実行するためのSessionStartフックの作成
- エージェント実行環境の設定と最適化

## 使い方

ユーザーがClaude Code on the webのリポジトリをセットアップしたい場合、またはウェブセッション中にプロジェクトのテストとリンターを確実に実行するためのSessionStartフックを作成したい場合にこのスキルを使用します。

## 機能

- **ハーネス設定**: エージェント実行環境の設定ファイルを生成
- **フック管理**: SessionStart/Stopフックの作成と管理
- **環境検証**: 実行環境の要件確認
- **デバッグサポート**: ハーネス設定の問題診断

## 設定例

```yaml
harness:
  session_start:
    - run_tests: true
    - run_linters: true
  timeout: 300
  environment:
    NODE_ENV: test
```
