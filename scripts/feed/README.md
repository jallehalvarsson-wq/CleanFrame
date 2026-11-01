# Sweden new-movies feed

`scrape.py` reads the public JustWatch Sweden "new" pages for the providers in
the CleanFrame dock and writes a small JSON feed.

## Providers

```text
Netflix, SVT Play, TV4 Play, HBO Max, Prime Video, Viaplay
```

Only movie pages (`/se/film/...`) are included. Stremio, Internet and YouTube
are not catalog services and are not part of the feed.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/feed/requirements.txt
.venv/bin/python scripts/feed/scrape.py --output docs/feed/new-se.json
```

The JSON contains:

```json
{
  "generated": "2026-11-01T...",
  "country": "SE",
  "providers": [{"slug": "netflix", "name": "Netflix"}],
  "items": [
    {
      "provider": "Netflix",
      "providerSlug": "netflix",
      "title": "Example",
      "url": "https://www.justwatch.com/se/film/example",
      "poster": "https://images.justwatch.com/poster/.../s592/example.jpg"
    }
  ]
}
```

## GitHub Action

`.github/workflows/new-movies-feed.yml` runs the scraper daily and commits the
JSON to the `feed` branch. The TV app reads:

```text
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/new-se.json
```

The branch is separate from `main`, so the daily feed commits do not clutter the
main history. The workflow can also be started manually with
`workflow_dispatch`.

## Notes

- This is a personal, low-volume scraper. JustWatch is not affiliated with
  CleanFrame, and the page structure can change.
- If a provider fails, the scraper keeps the other providers and records the
  error in the JSON. If every provider fails, it exits without overwriting the
  last feed.
- Poster URLs use the `s592` size for a sharper TV grid.
