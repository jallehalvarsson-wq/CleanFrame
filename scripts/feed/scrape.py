#!/usr/bin/env python3
"""Build small movie feeds from the public JustWatch Sweden pages.

`new` reads the providers' "nya" (new) pages. `popular` reads their movie
catalogues, which JustWatch orders by popularity. This is a personal,
low-volume scraper; JustWatch is not affiliated with this project and the page
structure can change without notice.
"""
import argparse
import json
import re
import sys
import time
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
FEED_PAGES = {"new": "nya", "popular": "filmer"}


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


PROVIDER_ALIASES = {
    "netflix": ["netflix"],
    "svt": ["svt play"],
    "tv4-play": ["tv4 play"],
    "hbo-max": ["hbo max", "max"],
    "amazon-prime-video": ["amazon prime video", "amazon video", "prime video"],
    "viaplay": ["viaplay"],
}


def duration_minutes(value):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", str(value or ""))
    if not match:
        return None
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    total = hours * 60 + minutes + (1 if seconds >= 30 else 0)
    return total or None


def detail_for(url, cache):
    if url in cache:
        return cache[url]
    soup = BeautifulSoup(fetch(url), "html.parser")
    script = soup.find("script", type="application/ld+json")
    data = json.loads(script.get_text()) if script else {}
    nodes = data.get("@graph") or [data]
    movie = next((node for node in nodes if node.get("@type") == "Movie"), {})
    rating = movie.get("aggregateRating") or {}
    actions = []
    for action in movie.get("potentialAction") or []:
        offer = action.get("expectsAcceptanceOf") or {}
        org = (offer.get("offeredBy") or {}).get("name")
        target = (action.get("target") or {}).get("urlTemplate")
        if org and target:
            actions.append({
                "provider": org,
                "url": target,
                "businessFunction": offer.get("businessFunction") or "",
            })
    details = {
        "year": None,
        "runtime": duration_minutes(movie.get("duration")),
        "genres": movie.get("genre") if isinstance(movie.get("genre"), list) else ([movie.get("genre")] if movie.get("genre") else []),
        "rating": rating.get("ratingValue"),
        "ratingScale": rating.get("bestRating"),
        "description": str(movie.get("description") or "").strip(),
        "director": [person.get("name") for person in (movie.get("director") or []) if person.get("name")][:3],
        "cast": [role.get("actor", {}).get("name") for role in (movie.get("actor") or []) if role.get("actor", {}).get("name")][:5],
        "contentRating": movie.get("contentRating"),
        "actions": actions,
    }
    date = str(movie.get("dateCreated") or movie.get("datePublished") or "")
    year = re.search(r"\d{4}", date)
    details["year"] = int(year.group()) if year else None
    cache[url] = details
    return details


def watch_url(details, slug):
    aliases = PROVIDER_ALIASES.get(slug, [])
    actions = details.get("actions", [])
    exact = [action for action in actions
             if action["provider"].strip().lower() in aliases]
    matches = exact or [action for action in actions
                        if any(alias in action["provider"].lower() for alias in aliases)]
    preferred = [action for action in matches
                 if "provideservice" in action.get("businessFunction", "").lower()]
    chosen = (preferred or matches)
    return chosen[0]["url"] if chosen else ""


def scrape_provider(slug, name, limit, page):
    # The page path uses the Swedish word "leverantör" (encoded).
    url = f"{BASE}/se/leverant%C3%B6r/{urllib.parse.quote(slug)}/{page}"
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
    parser.add_argument("--kind", choices=sorted(FEED_PAGES), default="new",
                        help="Feed to build: new releases or popular movies.")
    parser.add_argument("--output",
                        help="Output path; defaults to docs/feed/<kind>-se.json.")
    parser.add_argument("--limit", type=int, default=12,
                        help="Maximum movie cards per provider.")
    parser.add_argument("--providers", default="",
                        help="Comma-separated provider slugs; default all.")
    parser.add_argument("--no-details", action="store_true",
                        help="Skip movie detail pages (faster, less metadata).")
    parser.add_argument("--detail-delay", type=float, default=0.15,
                        help="Seconds between detail-page requests.")
    args = parser.parse_args()

    wanted = {p.strip() for p in args.providers.split(",") if p.strip()}
    selected = [p for p in PROVIDERS if not wanted or p[0] in wanted]
    if not selected:
        raise SystemExit("No matching providers.")

    page = FEED_PAGES[args.kind]
    lists, errors = [], []
    for slug, name in selected:
        try:
            items = scrape_provider(slug, name, args.limit, page)
            lists.append((slug, items))
            print(f"{name}: {len(items)} movie cards", file=sys.stderr)
        except Exception as error:
            errors.append(f"{name}: {error}")
            print(f"{name}: failed: {error}", file=sys.stderr)

    if not any(items for _, items in lists):
        raise SystemExit("No movie cards scraped. The page structure may have "
                         "changed or JustWatch is blocking this host.")

    # Interleave providers so the first screen shows a mix. The provider pages
    # are already in JustWatch popularity order for both feed kinds.
    items = []
    longest = max((len(group) for _, group in lists), default=0)
    for index in range(longest):
        for _, group in lists:
            if index < len(group):
                items.append(group[index])

    if not args.no_details:
        cache = {}
        for index, item in enumerate(items, 1):
            try:
                details = detail_for(item["url"], cache)
                for key in ("year", "runtime", "genres", "rating", "ratingScale",
                            "description", "director", "cast", "contentRating"):
                    if details.get(key) not in (None, "", []):
                        item[key] = details[key]
                link = watch_url(details, item["providerSlug"])
                if link:
                    item["watchUrl"] = link
                if index % 10 == 0:
                    print(f"details: {index}/{len(items)}", file=sys.stderr)
            except Exception as error:
                errors.append(f"{item['title']}: detail {error}")
                print(f"{item['title']}: detail failed: {error}", file=sys.stderr)
            if args.detail_delay:
                time.sleep(args.detail_delay)

    feed = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "country": "SE",
        "kind": args.kind,
        "source": "JustWatch",
        "providers": [{"slug": slug, "name": name} for slug, name in selected],
        "errors": errors,
        "items": items,
    }
    output = Path(args.output or f"docs/feed/{args.kind}-se.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"wrote {len(items)} items to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
