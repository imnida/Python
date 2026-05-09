"""
╔══════════════════════════════════════════════════════╗
║     RANGE TRADING BOT — BTC/ETH COINBASE API        ║
║     Thierry — Systematic Trading 2026               ║
╚══════════════════════════════════════════════════════╝

CONFIGURATION:
    Créer fichier .env avec:
    COINBASE_API_KEY=your_key
    COINBASE_API_SECRET=your_secret
    TELEGRAM_BOT_TOKEN=your_token (optionnel)
    TELEGRAM_CHAT_ID=your_chat_id (optionnel)

USAGE:
    python range_bot.py --mode paper    # Test sans argent
    python range_bot.py --mode live     # Production
    python range_bot.py --mode status   # Voir ordres actifs
    python range_bot.py --mode monitor  # Surveillance continue
    python range_bot.py --mode cancel   # Annuler tous les ordres
"""

import os
import time
import json
import hmac
import hashlib
import uuid
import argparse
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

# ══════════════════════════════════════════
#  CHARGEMENT .ENV (stdlib uniquement)
# ══════════════════════════════════════════

def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

# ══════════════════════════════════════════
#  CONFIGURATION RANGES
# ══════════════════════════════════════════

RANGES = {
    "BTC-USDC": {
        "buy_levels": [
            {"price": 78000, "pct_capital": 0.10, "label": "Buy1 - Résistance 80K retest"},
            {"price": 75000, "pct_capital": 0.15, "label": "Buy2 - Support intermédiaire"},
            {"price": 72000, "pct_capital": 0.15, "label": "Buy3 - Niveau vente historique"},
            {"price": 68000, "pct_capital": 0.20, "label": "Buy4 - Zone accumulation"},
            {"price": 63000, "pct_capital": 0.20, "label": "Buy5 - Bottom range confirmé"},
        ],
        "sell_levels": [
            {"price": 80000, "pct_stack": 0.23, "label": "Sell1 - Résistance basse"},
            {"price": 81500, "pct_stack": 0.23, "label": "Sell2 - Résistance mid"},
            {"price": 83000, "pct_stack": 0.23, "label": "Sell3 - Résistance haute"},
            {"price": 84500, "pct_stack": 0.17, "label": "Sell4 - Top range"},
            # 14% restant = forever hold (pas d'ordre sell)
        ],
        "cash_reserve_pct": 0.20,
        "breakout_up": 85500,
        "breakout_down": 61500,
        "min_order_usdc": 10,
    },
    "ETH-USDC": {
        "buy_levels": [
            {"price": 2150, "pct_capital": 0.10, "label": "Buy1 - Support intermédiaire"},
            {"price": 2000, "pct_capital": 0.15, "label": "Buy2 - Niveau psychologique"},
            {"price": 1850, "pct_capital": 0.20, "label": "Buy3 - Fibo 618%"},
            {"price": 1700, "pct_capital": 0.20, "label": "Buy4 - Support majeur"},
            {"price": 1400, "pct_capital": 0.15, "label": "Buy5 - Opportunité maximale"},
        ],
        "sell_levels": [
            {"price": 2380, "pct_stack": 0.22, "label": "Sell1 - Résistance immédiate"},
            {"price": 2450, "pct_stack": 0.22, "label": "Sell2 - Haut range court"},
            {"price": 2500, "pct_stack": 0.22, "label": "Sell3 - Résistance majeure"},
            {"price": 2600, "pct_stack": 0.22, "label": "Sell4 - Top range"},
            # 12% restant = forever hold
        ],
        "cash_reserve_pct": 0.20,
        "breakout_up": 2650,
        "breakout_down": 1650,
        "min_order_usdc": 10,
    }
}

CAPITAL_ALLOCATION = {
    "BTC-USDC": 3000,
    "ETH-USDC": 1600,
}

# ══════════════════════════════════════════
#  TELEGRAM (stdlib urllib)
# ══════════════════════════════════════════

def send_telegram(msg: str):
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"[TELEGRAM DISABLED] {msg}")
        return
    try:
        payload = json.dumps({"chat_id": chat_id, "text": f"🤖 RANGE BOT\n{msg}"}).encode()
        req = Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=5):
            pass
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

# ══════════════════════════════════════════
#  COINBASE API (HMAC, stdlib urllib)
# ══════════════════════════════════════════

_BASE = "https://api.coinbase.com"

def _api(method: str, path: str, params: dict = None, body: dict = None) -> dict:
    key    = os.environ.get("COINBASE_API_KEY", "")
    secret = os.environ.get("COINBASE_API_SECRET", "")
    if not key or not secret:
        raise ValueError("COINBASE_API_KEY et COINBASE_API_SECRET requis dans .env")

    qs       = ("?" + urlencode(params)) if params else ""
    qs_path  = path + qs
    body_str = json.dumps(body) if body else ""
    ts       = str(int(time.time()))

    msg = ts + method.upper() + qs_path + body_str
    sig = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()

    headers = {
        "CB-ACCESS-KEY":       key,
        "CB-ACCESS-SIGN":      sig,
        "CB-ACCESS-TIMESTAMP": ts,
        "Content-Type":        "application/json",
        "Accept":              "application/json",
    }

    req = Request(
        _BASE + qs_path,
        data=body_str.encode() if body_str else None,
        headers=headers,
        method=method.upper(),
    )
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f"[API {e.code}] {method} {path}: {e.read().decode()[:200]}")
        return {}
    except URLError as e:
        print(f"[URL ERROR] {method} {path}: {e}")
        return {}

# ── Helpers API ───────────────────────────────────────────────────────────────

def get_price(pair: str) -> float:
    data = _api("GET", "/api/v3/brokerage/best_bid_ask", {"product_ids": pair})
    try:
        pb  = data["pricebooks"][0]
        bid = float(pb["bids"][0]["price"])
        ask = float(pb["asks"][0]["price"])
        return (bid + ask) / 2
    except (KeyError, IndexError, ValueError) as e:
        print(f"[PRICE ERROR] {pair}: {e}")
        return 0.0

def get_balance(currency: str) -> float:
    data = _api("GET", "/api/v3/brokerage/accounts")
    for acc in data.get("accounts", []):
        if acc.get("currency") == currency:
            return float(acc["available_balance"]["value"])
    return 0.0

def get_open_orders(pair: str) -> list:
    data = _api("GET", "/api/v3/brokerage/orders/historical/batch", {
        "product_id":   pair,
        "order_status": "OPEN",
    })
    return data.get("orders", [])

def cancel_order(order_id: str, paper: bool = False) -> bool:
    if paper:
        print(f"  [PAPER] Annulation ordre {order_id[:8]}...")
        return True
    data = _api("POST", "/api/v3/brokerage/orders/batch_cancel", body={"order_ids": [order_id]})
    return bool(data)

def place_limit_order(pair: str, side: str, price: float,
                      size: float, paper: bool = False) -> dict | None:
    label = f"{side} {size:.6f} {pair.split('-')[0]} @ {price:,.0f}$"
    if paper:
        print(f"  [PAPER] {label}")
        return {"order_id": f"paper_{int(time.time())}"}
    result = _api("POST", "/api/v3/brokerage/orders", body={
        "client_order_id": str(uuid.uuid4()),
        "product_id":      pair,
        "side":            side,
        "order_configuration": {
            "limit_limit_gtc": {
                "base_size":   str(round(size, 8)),
                "limit_price": str(price),
                "post_only":   True,
            }
        },
    })
    if result.get("success"):
        return result
    print(f"  [ORDER ERROR] {label}: {result.get('error_response', result)}")
    return None

# ══════════════════════════════════════════
#  LOGIQUE RANGE TRADING
# ══════════════════════════════════════════

def _buy_size(price: float, capital: float, pct: float, min_order: float) -> float:
    amount = capital * pct
    return round(amount / price, 8) if amount >= min_order else 0.0

def place_buy_orders(pair: str, config: dict, capital: float, paper: bool) -> int:
    print(f"\n📗 PLACEMENT ORDRES BUY — {pair}")
    placed = 0
    for lvl in config["buy_levels"]:
        size = _buy_size(lvl["price"], capital, lvl["pct_capital"], config["min_order_usdc"])
        if size <= 0:
            print(f"  ⚠️  Montant trop faible @ {lvl['price']:,}$")
            continue
        if place_limit_order(pair, "BUY", lvl["price"], size, paper):
            print(f"  ✅ {lvl['label']} — {size:.6f} {pair.split('-')[0]} @ {lvl['price']:,}$")
            placed += 1
        time.sleep(0.3)
    return placed

def place_sell_orders(pair: str, config: dict, crypto_balance: float, paper: bool) -> int:
    print(f"\n📕 PLACEMENT ORDRES SELL — {pair}")
    currency = pair.split("-")[0]
    if crypto_balance <= 0:
        print(f"  ⚠️  Pas de {currency} disponible")
        return 0
    placed = 0
    for lvl in config["sell_levels"]:
        size = round(crypto_balance * lvl["pct_stack"], 8)
        if size * lvl["price"] < config["min_order_usdc"]:
            print(f"  ⚠️  Trop petit @ {lvl['price']:,}$")
            continue
        if place_limit_order(pair, "SELL", lvl["price"], size, paper):
            print(f"  ✅ {lvl['label']} — {size:.6f} {currency} @ {lvl['price']:,}$")
            placed += 1
        time.sleep(0.3)
    return placed

def check_breakout(price: float, config: dict, pair: str) -> str | None:
    if price > config["breakout_up"]:
        return f"🚀 CASSURE HAUSSIÈRE {pair}: {price:,.0f}$ > {config['breakout_up']:,}$"
    if price < config["breakout_down"]:
        return f"💥 CASSURE BAISSIÈRE {pair}: {price:,.0f}$ < {config['breakout_down']:,}$"
    return None

def monitor_and_replace(pair: str, config: dict, capital: float, paper: bool) -> int:
    buy_prices  = {l["price"] for l in config["buy_levels"]}
    sell_prices = {l["price"] for l in config["sell_levels"]}
    open_orders = get_open_orders(pair)

    open_buys  = set()
    open_sells = set()
    for o in open_orders:
        p = float(o["order_configuration"]["limit_limit_gtc"]["limit_price"])
        (open_buys if o["side"] == "BUY" else open_sells).add(p)

    replaced = 0
    for price in buy_prices - open_buys:
        if any(l["price"] == price for l in config["buy_levels"]):
            print(f"\n  🔔 BUY FILLED @ {price:,}$ → replacement sell")
            bal = get_balance(pair.split("-")[0])
            place_sell_orders(pair, config, bal, paper)
            send_telegram(f"✅ BUY FILLED {pair} @ {price:,}$\nOrdres sell replacés.")
            replaced += 1

    for price in sell_prices - open_sells:
        if any(l["price"] == price for l in config["sell_levels"]):
            print(f"\n  🔔 SELL FILLED @ {price:,}$ → replacement buy")
            place_buy_orders(pair, config, capital, paper)
            send_telegram(f"✅ SELL FILLED {pair} @ {price:,}$\nOrdres buy replacés.")
            replaced += 1

    return replaced

# ══════════════════════════════════════════
#  COMMANDES
# ══════════════════════════════════════════

def cmd_status():
    print("\n" + "═"*50)
    print("  📊 STATUS PORTFOLIO")
    print("═"*50)
    usdc = get_balance("USDC")
    print(f"\n💵 USDC disponible: {usdc:,.2f}$")

    for pair, config in RANGES.items():
        currency    = pair.split("-")[0]
        price       = get_price(pair)
        balance     = get_balance(currency)
        open_orders = get_open_orders(pair)
        buys        = [o for o in open_orders if o["side"] == "BUY"]
        sells       = [o for o in open_orders if o["side"] == "SELL"]
        alert       = check_breakout(price, config, pair)

        print(f"\n{'─'*40}")
        print(f"  {currency} @ {price:,.0f}$")
        print(f"  Balance: {balance:.6f} {currency} (~{balance*price:,.0f}$)")
        print(f"  Ordres buy ouverts:  {len(buys)}/{len(config['buy_levels'])}")
        print(f"  Ordres sell ouverts: {len(sells)}/{len(config['sell_levels'])}")
        if alert:
            print(f"\n  ⚠️   {alert}")
    print("\n" + "═"*50 + "\n")

def cmd_setup(paper: bool):
    print("\n" + "═"*50)
    print(f"  🚀 SETUP — {'📄 PAPER' if paper else '🔴 LIVE'}")
    print("═"*50)

    for pair, config in RANGES.items():
        capital    = CAPITAL_ALLOCATION[pair]
        deployable = capital * (1 - config["cash_reserve_pct"])
        print(f"\n{'─'*40}")
        print(f"  {pair} — Capital: {capital:,}$ (deployable: {deployable:,}$)")

        n = place_buy_orders(pair, config, deployable, paper)
        print(f"  → {n} ordres buy placés")

        bal = get_balance(pair.split("-")[0])
        if bal > 0:
            n = place_sell_orders(pair, config, bal, paper)
            print(f"  → {n} ordres sell placés")

    send_telegram(f"🚀 SETUP COMPLET\nBTC + ETH range orders placés\nMode: {'PAPER' if paper else 'LIVE'}")
    print("\n✅ Setup terminé.\n")

def cmd_monitor(paper: bool, interval: int = 60):
    print(f"\n👁️  MONITORING ACTIF — Check toutes {interval}s  (Ctrl+C pour arrêter)\n")
    while True:
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] Check...", end=" ", flush=True)
            total = 0
            for pair, config in RANGES.items():
                price = get_price(pair)
                alert = check_breakout(price, config, pair)
                if alert:
                    print(f"\n⚠️  {alert}")
                    send_telegram(f"⚠️ BREAKOUT!\n{alert}\nAction manuelle requise.")
                capital = CAPITAL_ALLOCATION[pair] * (1 - config["cash_reserve_pct"])
                total += monitor_and_replace(pair, config, capital, paper)
            print("✅" if total == 0 else f"🔄 {total} ordres replacés")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring arrêté.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            time.sleep(30)

def cmd_cancel_all(pair: str = None, paper: bool = False):
    pairs = [pair] if pair else list(RANGES.keys())
    for p in pairs:
        orders = get_open_orders(p)
        print(f"\n  Annulation {len(orders)} ordres {p}...")
        for o in orders:
            cancel_order(o["order_id"], paper)
            time.sleep(0.2)
    print("  ✅ Terminé")

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Range Trading Bot BTC/ETH")
    parser.add_argument("--mode", choices=["paper", "live", "status", "setup", "monitor", "cancel"],
                        default="status")
    parser.add_argument("--interval", type=int, default=60,
                        help="Intervalle monitoring en secondes (défaut: 60)")
    parser.add_argument("--pair", type=str, default=None,
                        help="Paire spécifique (BTC-USDC ou ETH-USDC)")
    args = parser.parse_args()
    paper = args.mode == "paper"

    print(f"\n🤖 RANGE TRADING BOT — {'PAPER' if paper else args.mode.upper()}")

    if args.mode == "status":
        cmd_status()
    elif args.mode in ("setup", "paper"):
        cmd_setup(paper=paper)
    elif args.mode == "live":
        if input("\n⚠️  MODE LIVE — Confirmer? (oui/non): ").lower() == "oui":
            cmd_setup(paper=False)
        else:
            print("Annulé.")
    elif args.mode == "monitor":
        cmd_monitor(paper=False, interval=args.interval)
    elif args.mode == "cancel":
        cmd_cancel_all(args.pair, paper=False)

if __name__ == "__main__":
    main()
