import argparse
from .logging_config import configure_logging
from .binance_client import BinanceClient  # unified client
from .orders.market_orders import place_market_order
from .orders.limit_orders import place_limit_order
from .advanced.stop_limit_orders import place_stop_limit_order
from .advanced.oco_orders import place_oco_order
from .advanced.twap_strategy import twap
#from .advanced.oco_orders import place_bracket  # futures-style OCO emulation


def main():
    configure_logging()
    parser = argparse.ArgumentParser(prog="binance-bot")
    sub = parser.add_subparsers(dest="cmd")

    # ---------------- Market ----------------
    m = sub.add_parser("market")
    m.add_argument("symbol")
    m.add_argument("side", choices=["BUY", "SELL"])
    m.add_argument("qty", type=float)
    m.add_argument("--user", default="user")
    m.add_argument("--dry-run", action="store_true")

    # ---------------- Limit ----------------
    l = sub.add_parser("limit")
    l.add_argument("symbol")
    l.add_argument("side", choices=["BUY", "SELL"])
    l.add_argument("price", type=float)
    l.add_argument("qty", type=float)
    l.add_argument("--user", default="user")
    l.add_argument("--dry-run", action="store_true")

    # ---------------- Stop-Limit ----------------
    sl = sub.add_parser("stop_limit")
    sl.add_argument("symbol")
    sl.add_argument("side", choices=["BUY", "SELL"])
    sl.add_argument("stop_price", type=float)
    sl.add_argument("limit_price", type=float)
    sl.add_argument("qty", type=float)
    sl.add_argument("--user", default="user")
    sl.add_argument("--dry-run", action="store_true")

    # ---------------- TWAP ----------------
    t = sub.add_parser("twap")
    t.add_argument("symbol")
    t.add_argument("side", choices=["BUY", "SELL"])
    t.add_argument("total_qty", type=float)
    t.add_argument("--slices", type=int, default=6)
    t.add_argument("--interval", type=int, default=60)
    t.add_argument("--user", default="user")
    t.add_argument("--dry-run", action="store_true")

    # ---------------- Bracket (Futures-style OCO) ----------------
    b = sub.add_parser("bracket")
    b.add_argument("symbol")
    b.add_argument("side", choices=["BUY", "SELL"])
    b.add_argument("qty", type=float)
    b.add_argument("tp", type=float)
    b.add_argument("sl", type=float)
    b.add_argument("--user", default="user")
    b.add_argument("--dry-run", action="store_true")

    # ---------------- OCO (Spot API) ----------------
    oco = sub.add_parser("oco")
    oco.add_argument("symbol")
    oco.add_argument("side", choices=["BUY", "SELL"])
    oco.add_argument("qty", type=float)
    oco.add_argument("price", type=float)
    oco.add_argument("stop_price", type=float)
    oco.add_argument("stop_limit_price", type=float)
    oco.add_argument("--user", default="user")
    oco.add_argument("--dry-run", action="store_true")

    # ---------------- Parse args ----------------
    args = parser.parse_args()
    client = BinanceClient()

    # ---------------- Dispatch ----------------
    if args.cmd == "market":
        out = place_market_order(
            client, args.user, args.symbol.upper(), args.side, args.qty, dry_run=args.dry_run
        )
        print(out)

    elif args.cmd == "limit":
        out = place_limit_order(
            client, args.user, args.symbol.upper(), args.side, args.price, args.qty, dry_run=args.dry_run
        )
        print(out)

    elif args.cmd == "stop_limit":
        out = place_stop_limit_order(
            client, args.user, args.symbol.upper(), args.side,
            args.stop_price, args.limit_price, args.qty, dry_run=args.dry_run
        )
        print(out)

    elif args.cmd == "twap":
        out = twap(
            client, args.symbol.upper(), args.side, args.total_qty,
            slices=args.slices, interval_seconds=args.interval, dry_run=args.dry_run
        )
        print(out)

    #elif args.cmd == "bracket":
        #out = place_bracket(
            #client, args.symbol.upper(), args.side, args.qty, args.tp, args.sl, dry_run=args.dry_run
        #)
        print(out)

    elif args.cmd == "oco":
        out = place_oco_order(
            client, args.user, args.symbol.upper(), args.side,
            args.qty, args.price, args.stop_price, args.stop_limit_price,
            dry_run=args.dry_run
        )
        print(out)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
