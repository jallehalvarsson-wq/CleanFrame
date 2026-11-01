#!/usr/bin/env python3
"""Upload photos to a Samsung The Frame and inspect Art Mode.

Run:

    python3 scripts/art-mode/art-mode-setup.py --host TV_IP --folder ~/Pictures

The TV must be on the same network. The first run may show an Allow prompt on
the TV; accept it once. The samsungtvws library saves the Art API token.

This helper uploads photos to My Pictures. On firmware that reports Art API
5.0.1.0, the old favorites/slideshow set commands are rejected; finish those
settings in the TV's Art Mode UI.
"""
import argparse
import os
import tempfile
from pathlib import Path

from PIL import Image
from samsungtvws import SamsungTVWS

DEFAULT_FOLDER = "~/Pictures"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def image_paths(folder, limit):
    files = sorted(
        p for p in Path(folder).expanduser().iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    return files[:limit]


def prepare(path, tmpdir):
    """Convert WebP to JPEG; leave JPEG/PNG untouched."""
    if path.suffix.lower() == ".webp":
        out = Path(tmpdir) / (path.stem + ".jpg")
        Image.open(path).convert("RGB").save(out, "JPEG", quality=92)
        return out
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=None,
                        help="TV IP address; also reads SAMSUNG_TV_HOST.")
    parser.add_argument("--folder", default=DEFAULT_FOLDER)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--minutes", type=int, default=10,
                        help="Slideshow interval used by --try-api or the UI prompt.")
    parser.add_argument("--store", action="append", default=None,
                        help="Art Store content ID to include; repeatable.")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--matte", default="shadowbox_polar")
    parser.add_argument("--artmode", choices=["on", "off", "leave"], default="leave")
    parser.add_argument("--try-api", action="store_true",
                        help="Also try the old favorites/slideshow API calls. "
                             "Some 2025+ firmware rejects them; use the TV UI "
                             "for Favorites and Slideshow.")
    args = parser.parse_args()

    host = args.host or os.environ.get("SAMSUNG_TV_HOST")
    if not host:
        parser.error("pass --host or set SAMSUNG_TV_HOST")

    store_ids = [] if args.no_store else (args.store or [])
    photos = image_paths(args.folder, args.limit)
    if not photos:
        raise SystemExit("No images found in " + args.folder)

    tv = SamsungTVWS(host=host, port=8001, name="CleanFrame Art", timeout=60)
    art = tv.art()
    uploaded = []

    with tempfile.TemporaryDirectory(prefix="cleanframe-art-") as tmpdir:
        for path in photos:
            source = prepare(path, tmpdir)
            print("Uploading", path.name, end=" ... ", flush=True)
            cid = art.upload(str(source), matte=args.matte,
                             portrait_matte=args.matte)
            uploaded.append(cid)
            print(cid)

    api = art.get_api_version()
    print("Art API version:", api)

    if args.try_api:
        print("Trying old favorites API ...")
        for cid in uploaded + store_ids:
            try:
                art.set_favourite(cid, "on")
                print("  favorite:", cid)
            except Exception as error:
                print("  favorite failed:", cid, error)
        print("Trying old slideshow API ...")
        try:
            print(art.set_slideshow_status(
                duration=args.minutes, type=True, category_id="MY-C0004"))
        except Exception as error:
            print("  slideshow API failed:", error)
        print("Slideshow status:", art.get_slideshow_status())
        print("Favorites:", len(art.available("MY-C0004")))
    else:
        print("Photos are in My Pictures.")
        print("If this firmware rejects Favorites/Slideshow changes, finish in"
              " the TV UI:")
        print("  1. Open Art Mode -> My Pictures.")
        print("  2. Add the new photos to Favorites (heart/star button).")
        print("  3. Art Mode Settings -> Slideshow -> Favorites or My Pictures.")
        print("  4. Set", args.minutes, "minutes and Shuffle.")
        print("The TV handles the slideshow; this computer is not required.")

    if args.artmode != "leave":
        art.set_artmode(args.artmode == "on")
        print("Art Mode:", art.get_artmode())

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(130)
