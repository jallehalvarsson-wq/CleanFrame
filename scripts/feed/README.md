# Sweden movie feeds

`scrape.py` reads public JustWatch Sweden pages for the providers in the
CleanFrame dock and writes small JSON feeds for the TV app.

## Providers

```text
Netflix, SVT Play, TV4 Play, HBO Max, Prime Video, Viaplay
```

Only movie pages (`/se/film/...`) are included. Stremio, Internet, YouTube and
Steam Link are not catalog services and are not part of either feed.

## Feed kinds

- `new` reads each provider's `/nya` page and feeds the **New** panel.
- `popular` reads each provider's movie catalogue (`/filmer`), which JustWatch
  orders by popularity, and feeds the **Most watched** panel. This is a public
  popularity signal, not a record of playback on the TV.

The scraper interleaves providers so the first grid page mixes services while
keeping each provider's most popular titles first.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/feed/requirements.txt
.venv/bin/python scripts/feed/scrape.py --kind new --output docs/feed/new-se.json
.venv/bin/python scripts/feed/scrape.py --kind popular --output docs/feed/popular-se.json
```

The scraper also fetches each movie's JustWatch detail page. Use
`--no-details` for a faster basic feed, or `--detail-delay 0` to remove the
small pause between detail requests. If `--output` is omitted, it defaults to
`docs/feed/<kind>-se.json`.

The JSON contains:

```json
{
  "generated": "2026-11-01T...",
  "country": "SE",
  "kind": "new",
  "source": "JustWatch",
  "providers": [{"slug": "netflix", "name": "Netflix"}],
  "items": [
    {
      "provider": "Netflix",
      "providerSlug": "netflix",
      "title": "Example",
      "url": "https://www.justwatch.com/se/film/example",
      "poster": "https://images.justwatch.com/poster/.../s592/example.jpg",
      "year": 2025,
      "runtime": 118,
      "genres": ["Drama", "Thriller"],
      "rating": 72,
      "ratingScale": "100",
      "description": "Short synopsis...",
      "director": ["Director Name"],
      "cast": ["Actor One", "Actor Two"],
      "watchUrl": "https://www.netflix.com/title/..."
    }
  ]
}
```

The app uses the detail fields for the selected-movie view. `watchUrl` is kept
in the feed for future use; the current app opens the provider app's home
screen rather than exposing an exact-link action.

## GitHub Action

`.github/workflows/new-movies-feed.yml` runs both scrapers daily and commits the
JSON to the `feed` branch. The TV app reads:

```text
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/new-se.json
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/popular-se.json
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
