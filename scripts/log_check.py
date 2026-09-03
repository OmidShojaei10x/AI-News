#!/usr/bin/env python3
"""Log a check run with no articles sent."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.supabase_storage import log_check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=["morning", "noon", "evening"])
    parser.add_argument("--lookback", type=int, required=True)
    parser.add_argument("--found", type=int, required=True)
    parser.add_argument("--sent", type=int, default=0)
    args = parser.parse_args()

    log_check(args.slot, args.lookback, args.found, args.sent)
    print(f"Logged check: slot={args.slot}, found={args.found}, sent={args.sent}")


if __name__ == "__main__":
    main()
