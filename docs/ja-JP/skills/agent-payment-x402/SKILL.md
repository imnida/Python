---
name: agent-payment-x402
description: x402プロトコルを使用したエージェント決済システム
version: 1.0.0
---

# エージェント決済スキル (x402)

x402プロトコルを使用してエージェントが自律的に決済を処理するスキルです。

## 概要

HTTP 402 Payment Requiredレスポンスを処理し、暗号通貨またはその他の決済手段でAPIアクセス料金を支払います。

## 機能

- **自動決済**: x402ペイウォールを自動的に検出して処理
- **マルチチェーン**: 複数のブロックチェーンネットワークに対応
- **残高管理**: エージェントウォレットの残高を管理
- **監査ログ**: すべての決済トランザクションを記録

## 使い方

```bash
/pay-x402                         # 保留中の決済を処理
/pay-x402 --check-balance         # ウォレット残高を確認
/pay-x402 --history               # 決済履歴を表示
```

## 設定

```yaml
x402:
  wallet:
    type: custodial
    network: base
  max_payment: 0.01  # USDC
  auto_approve: false
```
