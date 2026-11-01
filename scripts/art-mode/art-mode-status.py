#!/usr/bin/env python3
"""Print the current Samsung Art Mode state and collection counts.

Run:

    python3 scripts/art-mode/art-mode-status.py --host TV_IP

The TV must be on the same network. Pass the host explicitly or set
SAMSUNG_TV_HOST.
"""
import argparse
import os

from samsungtvws import SamsungTVWS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=None,
                        help="TV IP address; also reads SAMSUNG_TV_HOST.")
    args = parser.parse_args()
    host = args.host or os.environ.get("SAMSUNG_TV_HOST")
    if not host:
        parser.error("pass --host or set SAMSUNG_TV_HOST")

    tv = SamsungTVWS(host=host, port=8001, name="CleanFrame Art", timeout=30)
    art = tv.art()
    print("Art Mode:", art.get_artmode())
    print("Current:", art.get_current())
    print("Slideshow:", art.get_slideshow_status())
    print("Favorites:", len(art.available("MY-C0004")))
    print("My Pictures:", len(art.available("MY-C0002")))
    print("Store:", len(art.available("MY-C0008")))


if __name__ == "__main__":
    main()
