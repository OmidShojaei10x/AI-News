#!/usr/bin/env python3
"""Log an AI news check to Supabase (no Telegram send)."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts._supabase import log_check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True)
    parser.add_argument("--lookback", type=int, required=True)
    parser.add_argument("--found", type=int, required=True)
    parser.add_argument("--sent", type=int, default=0)
    args = parser.parse_args()

    log_check(args.slot, args.lookback, args.found, args.sent)
    print(json.dumps({"logged": True, "slot": args.slot, "found": args.found, "sent": args.sent}))


if __name__ == "__main__":
    main()
