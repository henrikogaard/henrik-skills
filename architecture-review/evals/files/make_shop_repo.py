#!/usr/bin/env python3
"""Build the eval fixture: a git repo of shop-src/ with a year of history.

Usage: make_shop_repo.py <dest>   (dest must not exist)

The history makes shop/orders.py the hot spot, couples it to shop/reports.py
and tests/test_orders.py, and leaves utils.py and storage.py nearly untouched.
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DAY = 86400

# (days ago, message, files to touch)
HISTORY = [
    (300, "Add food tax rate", ["shop/orders.py", "tests/test_orders.py"]),
    (280, "Fix rounding of totals", ["shop/orders.py", "shop/reports.py", "tests/test_orders.py"]),
    (250, "Add STAFF discount", ["shop/orders.py", "shop/reports.py"]),
    (230, "Email: include total", ["shop/orders.py"]),
    (200, "Report: skip cancelled orders", ["shop/reports.py", "shop/orders.py"]),
    (180, "Add tshirt SKU", ["shop/orders.py", "tests/test_orders.py"]),
    (160, "Export JSON", ["shop/orders.py", "shop/order_service.py"]),
    (140, "Tax on discounted amount", ["shop/orders.py", "shop/reports.py", "tests/test_orders.py"]),
    (120, "Stock check before order", ["shop/orders.py", "tests/test_orders.py"]),
    (100, "Cancel restores stock", ["shop/orders.py"]),
    (80, "Report money format", ["shop/reports.py", "shop/orders.py"]),
    (60, "More tests", ["tests/test_orders.py", "tests/test_order_service.py"]),
    (45, "Fix tax ratio for zero subtotal", ["shop/orders.py", "tests/test_orders.py"]),
    (30, "Discount code validation", ["shop/orders.py", "shop/reports.py"]),
    (20, "Helpers", ["shop/utils.py"]),
    (10, "Email copy tweak", ["shop/orders.py"]),
]


def git(dest, *args, when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Dev", GIT_AUTHOR_EMAIL="dev@shop.example",
               GIT_COMMITTER_NAME="Dev", GIT_COMMITTER_EMAIL="dev@shop.example")
    if when is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{int(when)} +0000"
    subprocess.run(["git", "-C", dest, *args], check=True, capture_output=True, env=env)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = os.path.abspath(sys.argv[1])
    if os.path.exists(dest):
        sys.exit(f"{dest} already exists")
    shutil.copytree(os.path.join(HERE, "shop-src"), dest,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "orders.json"))
    now = time.time()
    git(dest, "init", "-q", "-b", "main")
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "Initial shop", when=now - 330 * DAY)
    for days, msg, files in HISTORY:
        for f in files:
            with open(os.path.join(dest, f), "a") as fh:
                fh.write(f"# {msg}\n")
        git(dest, "add", "-A")
        git(dest, "commit", "-q", "-m", msg, when=now - days * DAY)
    print(dest)


if __name__ == "__main__":
    main()
