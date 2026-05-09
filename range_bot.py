"""
╔══════════════════════════════════════════════════════╗
║     RANGE TRADING BOT — BTC/ETH COINBASE API        ║
║     Thierry — Systematic Trading 2026               ║
╚══════════════════════════════════════════════════════╝

INSTALLATION:
    pip install coinbase-advanced-py requests python-dotenv

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
"""

import os
import time
import json
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv
from coinbase.rest import RESTClient

load_dotenv()

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
        "cash_reserve_pct": 0.20,      # 20% cash jamais déployé
        "breakout_up": 85500,           # Cassure haussière
        "breakout_down": 61500,         # Cassure baissière
        "min_order_usdc": 10,           # Minimum Coinbase
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

# Capital alloué par asset (à ajuster selon ton capital réel)
CAPITAL_ALLOCATION = {
    "BTC-USDC": 3000,   # USDC alloués au range BTC
    "ETH-USDC": 1600,   # USDC alloués au range ETH
}

# ══════════════════════════════════════════
#  TELEGRAM ALERTES
# ══════════════════════════════════════════

def send_telegram(msg: str):
    """Envoie alerte Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"[TELEGRAM DISABLED] {msg}")
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": f"🤖 RANGE BOT\n{msg}"}, timeout=5)
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

# ══════════════════════════════════════════
#  COINBASE CLIENT
# ══════════════════════════════════════════

def get_client():
    """Initialise client Coinbase Advanced Trade."""
    key = os.getenv("COINBASE_API_KEY")
    secret = os.getenv("COINBASE_API_SECRET")
    if not key or not secret:
        raise ValueError("COINBASE_API_KEY et COINBASE_API_SECRET requis dans .env")
    return RESTClient(api_key=key, api_secret=secret)

def get_price(client, pair: str) -> float:
    """Récupère prix actuel."""
    try:
        product = client.get_best_bid_ask(product_ids=[pair])
        bid = float(product["pricebooks"][0]["bids"][0]["price"])
        ask = float(product["pricebooks"][0]["asks"][0]["price"])
        return (bid + ask) / 2
    except Exception as e:
        print(f"[PRICE ERROR] {pair}: {e}")
        return 0.0

def get_usdc_balance(client) -> float:
    """Récupère balance USDC disponible."""
    try:
        accounts = client.get_accounts()
        for acc in accounts["accounts"]:
            if acc["currency"] == "USDC":
                return float(acc["available_balance"]["value"])
        return 0.0
    except Exception as e:
        print(f"[BALANCE ERROR] {e}")
        return 0.0

def get_crypto_balance(client, currency: str) -> float:
    """Récupère balance crypto (BTC ou ETH)."""
    try:
        accounts = client.get_accounts()
        for acc in accounts["accounts"]:
            if acc["currency"] == currency:
                return float(acc["available_balance"]["value"])
        return 0.0
    except Exception as e:
        print(f"[BALANCE ERROR] {currency}: {e}")
        return 0.0

def get_open_orders(client, pair: str) -> list:
    """Récupère ordres ouverts pour une paire."""
    try:
        orders = client.list_orders(
            product_id=pair,
            order_status=["OPEN"]
        )
        return orders.get("orders", [])
    except Exception as e:
        print(f"[ORDERS ERROR] {pair}: {e}")
        return []

def cancel_order(client, order_id: str, paper: bool = False) -> bool:
    """Annule un ordre."""
    if paper:
        print(f"  [PAPER] Annulation ordre {order_id[:8]}...")
        return True
    try:
        client.cancel_orders(order_ids=[order_id])
        return True
    except Exception as e:
        print(f"  [CANCEL ERROR] {order_id}: {e}")
        return False

def place_limit_order(client, pair: str, side: str, price: float,
                       size: float, paper: bool = False) -> dict | None:
    """Place un ordre limit."""
    label = f"{side} {size:.6f} {pair.split('-')[0]} @ {price:,.0f}$"
    if paper:
        print(f"  [PAPER] {label}")
        return {"order_id": f"paper_{int(time.time())}", "label": label}
    try:
        import uuid
        order = client.create_order(
            client_order_id=str(uuid.uuid4()),
            product_id=pair,
            side=side,
            order_configuration={
                "limit_limit_gtc": {
                    "base_size": str(round(size, 8)),
                    "limit_price": str(price),
                    "post_only": True
                }
            }
        )
        return order
    except Exception as e:
        print(f"  [ORDER ERROR] {label}: {e}")
        return None

# ══════════════════════════════════════════
#  LOGIQUE RANGE TRADING
# ══════════════════════════════════════════

def calculate_buy_size(price: float, capital_usdc: float,
                        pct: float, min_order: float) -> float:
    """Calcule la taille BTC/ETH pour un ordre buy."""
    usdc_amount = capital_usdc * pct
    if usdc_amount < min_order:
        return 0.0
    return round(usdc_amount / price, 8)

def place_buy_orders(client, pair: str, config: dict,
                     capital: float, paper: bool):
    """Place tous les ordres buy du range."""
    print(f"\n📗 PLACEMENT ORDRES BUY — {pair}")
    placed = 0
    for level in config["buy_levels"]:
        size = calculate_buy_size(
            level["price"], capital,
            level["pct_capital"], config["min_order_usdc"]
        )
        if size <= 0:
            print(f"  ⚠️ Montant trop faible @ {level['price']:,}$")
            continue
        result = place_limit_order(
            client, pair, "BUY",
            level["price"], size, paper
        )
        if result:
            print(f"  ✅ {level['label']} — {size:.6f} {pair.split('-')[0]} @ {level['price']:,}$")
            placed += 1
        time.sleep(0.3)  # Rate limit protection
    return placed

def place_sell_orders(client, pair: str, config: dict,
                      crypto_balance: float, paper: bool):
    """Place tous les ordres sell du range."""
    print(f"\n📕 PLACEMENT ORDRES SELL — {pair}")
    if crypto_balance <= 0:
        print(f"  ⚠️ Pas de {pair.split('-')[0]} disponible")
        return 0
    placed = 0
    for level in config["sell_levels"]:
        size = round(crypto_balance * level["pct_stack"], 8)
        if size * level["price"] < config["min_order_usdc"]:
            print(f"  ⚠️ Trop petit @ {level['price']:,}$")
            continue
        result = place_limit_order(
            client, pair, "SELL",
            level["price"], size, paper
        )
        if result:
            print(f"  ✅ {level['label']} — {size:.6f} {pair.split('-')[0]} @ {level['price']:,}$")
            placed += 1
        time.sleep(0.3)
    return placed

def check_breakout(price: float, config: dict, pair: str) -> str | None:
    """Vérifie si le prix casse le range."""
    if price > config["breakout_up"]:
        return f"🚀 CASSURE HAUSSIÈRE {pair}: {price:,.0f}$ > {config['breakout_up']:,}$"
    if price < config["breakout_down"]:
        return f"💥 CASSURE BAISSIÈRE {pair}: {price:,.0f}$ < {config['breakout_down']:,}$"
    return None

def monitor_and_replace(client, pair: str, config: dict,
                         capital: float, paper: bool):
    """
    Vérifie ordres filled et replace automatiquement.
    Logique: si ordre buy filled → place sell correspondant
             si ordre sell filled → place buy correspondant
    """
    buy_prices = {l["price"] for l in config["buy_levels"]}
    sell_prices = {l["price"] for l in config["sell_levels"]}
    open_orders = get_open_orders(client, pair)
    open_buy_prices = set()
    open_sell_prices = set()

    for o in open_orders:
        p = float(o["order_configuration"]["limit_limit_gtc"]["limit_price"])
        if o["side"] == "BUY":
            open_buy_prices.add(p)
        else:
            open_sell_prices.add(p)

    # Ordres buy filled (plus dans open orders)
    filled_buys = buy_prices - open_buy_prices
    filled_sells = sell_prices - open_sell_prices

    replaced = 0
    for price in filled_buys:
        level = next((l for l in config["buy_levels"] if l["price"] == price), None)
        if level:
            print(f"\n  🔔 BUY FILLED @ {price:,}$ → Placement sell correspondant")
            crypto_bal = get_crypto_balance(client, pair.split("-")[0])
            place_sell_orders(client, pair, config, crypto_bal, paper)
            msg = f"✅ BUY FILLED {pair} @ {price:,}$\nOrdres sell replacés automatiquement."
            send_telegram(msg)
            replaced += 1

    for price in filled_sells:
        level = next((l for l in config["sell_levels"] if l["price"] == price), None)
        if level:
            print(f"\n  🔔 SELL FILLED @ {price:,}$ → Placement buy correspondant")
            place_buy_orders(client, pair, config, capital, paper)
            msg = f"✅ SELL FILLED {pair} @ {price:,}$\nOrdres buy replacés automatiquement."
            send_telegram(msg)
            replaced += 1

    return replaced

# ══════════════════════════════════════════
#  COMMANDES PRINCIPALES
# ══════════════════════════════════════════

def cmd_status(client):
    """Affiche status complet portfolio."""
    print("\n" + "═"*50)
    print("  📊 STATUS PORTFOLIO")
    print("═"*50)

    usdc = get_usdc_balance(client)
    print(f"\n💵 USDC disponible: {usdc:,.2f}$")

    for pair, config in RANGES.items():
        currency = pair.split("-")[0]
        price = get_price(client, pair)
        balance = get_crypto_balance(client, currency)
        open_orders = get_open_orders(client, pair)
        buys = [o for o in open_orders if o["side"] == "BUY"]
        sells = [o for o in open_orders if o["side"] == "SELL"]

        # Breakout check
        alert = check_breakout(price, config, pair)

        print(f"\n{'─'*40}")
        print(f"  {currency} @ {price:,.0f}$")
        print(f"  Balance: {balance:.6f} {currency} (~{balance*price:,.0f}$)")
        print(f"  Ordres buy ouverts:  {len(buys)}/{len(config['buy_levels'])}")
        print(f"  Ordres sell ouverts: {len(sells)}/{len(config['sell_levels'])}")
        if alert:
            print(f"\n  ⚠️  {alert}")

    print("\n" + "═"*50 + "\n")

def cmd_setup(client, paper: bool):
    """Place tous les ordres initiaux."""
    print("\n" + "═"*50)
    mode = "📄 PAPER MODE" if paper else "🔴 LIVE MODE"
    print(f"  🚀 SETUP INITIAL — {mode}")
    print("═"*50)

    for pair, config in RANGES.items():
        capital = CAPITAL_ALLOCATION[pair]
        capital_deployable = capital * (1 - config["cash_reserve_pct"])

        print(f"\n{'─'*40}")
        print(f"  {pair} — Capital: {capital:,}$ (deployable: {capital_deployable:,}$)")

        # Place buy orders
        placed = place_buy_orders(client, pair, config, capital_deployable, paper)
        print(f"  → {placed} ordres buy placés")

        # Place sell orders si balance existante
        currency = pair.split("-")[0]
        balance = get_crypto_balance(client, currency)
        if balance > 0:
            placed = place_sell_orders(client, pair, config, balance, paper)
            print(f"  → {placed} ordres sell placés")

    msg = f"🚀 SETUP COMPLET\nBTC + ETH range orders placés\nMode: {'PAPER' if paper else 'LIVE'}"
    send_telegram(msg)
    print("\n✅ Setup terminé.\n")

def cmd_monitor(client, paper: bool, interval: int = 60):
    """Boucle monitoring + replacement automatique."""
    print(f"\n👁️  MONITORING ACTIF — Check toutes {interval}s")
    print("   Ctrl+C pour arrêter\n")

    while True:
        try:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] Check en cours...", end=" ")

            total_replaced = 0
            for pair, config in RANGES.items():
                price = get_price(client, pair)

                # Vérifier breakout
                alert = check_breakout(price, config, pair)
                if alert:
                    print(f"\n⚠️  {alert}")
                    send_telegram(f"⚠️ BREAKOUT DÉTECTÉ!\n{alert}\nAction manuelle requise.")

                # Monitor et replace si nécessaire
                capital = CAPITAL_ALLOCATION[pair] * (1 - config["cash_reserve_pct"])
                replaced = monitor_and_replace(client, pair, config, capital, paper)
                total_replaced += replaced

            if total_replaced == 0:
                print("✅ Aucun changement")
            else:
                print(f"🔄 {total_replaced} ordres replacés")

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring arrêté.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            time.sleep(30)

def cmd_cancel_all(client, pair: str = None, paper: bool = False):
    """Annule tous les ordres ouverts."""
    pairs = [pair] if pair else list(RANGES.keys())
    for p in pairs:
        orders = get_open_orders(client, p)
        print(f"\n  Annulation {len(orders)} ordres {p}...")
        for o in orders:
            cancel_order(client, o["order_id"], paper)
            time.sleep(0.2)
    print("  ✅ Terminé")

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Range Trading Bot BTC/ETH")
    parser.add_argument("--mode", choices=["paper", "live", "status", "setup",
                                            "monitor", "cancel"],
                        default="status", help="Mode d'exécution")
    parser.add_argument("--interval", type=int, default=60,
                        help="Intervalle monitoring en secondes (défaut: 60)")
    parser.add_argument("--pair", type=str, default=None,
                        help="Paire spécifique (BTC-USDC ou ETH-USDC)")
    args = parser.parse_args()

    paper = args.mode == "paper"

    try:
        client = get_client()
    except ValueError as e:
        print(f"❌ {e}")
        return

    print(f"\n🤖 RANGE TRADING BOT — {'PAPER' if paper else args.mode.upper()}")

    if args.mode == "status":
        cmd_status(client)

    elif args.mode in ("setup", "paper"):
        cmd_setup(client, paper=paper)

    elif args.mode == "live":
        confirm = input("\n⚠️  MODE LIVE — Confirmer? (oui/non): ")
        if confirm.lower() == "oui":
            cmd_setup(client, paper=False)
        else:
            print("Annulé.")

    elif args.mode == "monitor":
        cmd_monitor(client, paper=False, interval=args.interval)

    elif args.mode == "cancel":
        cmd_cancel_all(client, args.pair, paper=False)

if __name__ == "__main__":
    main()
