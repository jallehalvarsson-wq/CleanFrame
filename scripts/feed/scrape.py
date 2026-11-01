#!/usr/bin/env python3
"""Build a small "new movies in Sweden" feed from JustWatch.

This is a personal, low-volume scraper for the public JustWatch Sweden pages.
It writes JSON for the CleanFrame TV app. JustWatch is not affiliated with this
project; the page structure can change without notice.
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

BASE = "https://www.justwatch.com"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
PROVIDERS = [
    ("netflix", "Netflix"),
    ("svt", "SVT Play"),
    ("tv4-play", "TV4 Play"),
    ("hbo-max", "HBO Max"),
    ("amazon-prime-video", "Prime Video"),
    ("viaplay", "Viaplay"),
]


def fetch(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def poster_url(src):
    if not src:
        return ""
    if src.startswith("//"):
        src = "https:" + src
    return src.replace("/s332/", "/s592/")


def scrape_provider(slug, name, limit):
    # The page path uses the Swedish word "leverantör" (encoded).
    url = f"{BASE}/se/leverant%C3%B6r/{urllib.parse.quote(slug)}/nya"
    soup = BeautifulSoup(fetch(url), "html.parser")
    items, seen = [], set()
    for anchor in soup.select('a[href^="/se/film/"]'):
        image = anchor.find("img")
        if not image:
            continue
        href = anchor.get("href")
        title = (image.get("alt") or "").strip()
        poster = poster_url(image.get("src") or "")
        if not href or not title or not poster or href in seen:
            continue
        seen.add(href)
        items.append({
            "provider": name,
            "providerSlug": slug,
            "title": title,
            "url": urllib.parse.urljoin(BASE, href),
            "poster": poster,
        })
        if len(items) >= limit:
            break
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/feed/new-se.json")
    parser.add_argument("--limit", type=int, default=12,
                        help="Maximum movie cards per provider.")
    parser.add_argument("--providers", default="",
                        help="Comma-separated provider slugs; default all.")
    args = parser.parse_args()

    wanted = {p.strip() for p in args.providers.split(",") if p.strip()}
    selected = [p for p in PROVIDERS if not wanted or p[0] in wanted]
    if not selected:
        raise SystemExit("No matching providers.")

    lists, errors = [], []
    for slug, name in selected:
        try:
            items = scrape_provider(slug, name, args.limit)
            lists.append((slug, items))
            print(f"{name}: {len(items)} movie cards", file=sys.stderr)
        except Exception as error:
            errors.append(f"{name}: {error}")
            print(f"{name}: failed: {error}", file=sys.stderr)

    if not any(items for _, items in lists):
        raise SystemExit("No movie cards scraped. The page structure may have "
                         "changed or JustWatch is blocking this host.")

    # Interleave providers so the first screen shows a mix.
    items = []
    longest = max((len(group) for _, group in lists), default=0)
    for index in range(longest):
        for _, group in lists:
            if index < len(group):
                items.append(group[index])

    feed = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "country": "SE",
        "source": "JustWatch",
        "providers": [{"slug": slug, "name": name} for slug, name in selected],
        "errors": errors,
        "items": items,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"wrote {len(items)} items to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
