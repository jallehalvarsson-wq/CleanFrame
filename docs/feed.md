# New in Sweden movies feed

The **New** control in the top-right of Home opens a poster grid of newly added
movies in Sweden for the apps currently on Home.

## What it shows

- Poster, provider name and title
- Only movies (`/se/film/...`), not TV series
- Only providers whose apps are on Home:
  `Netflix`, `SVT Play`, `TV4 Play`, `HBO Max`, `Prime Video`, `Viaplay`
- A **Refresh** button; the feed is cached in localStorage

OK launches the matching provider app. The app opens on its home screen; the
exact movie is not deep-linked, because the TV apps do not expose a reliable
public deep link for every title.

Stremio, Internet and YouTube are not catalogue services, so they are not part
of this feed.

## Data flow

```text
JustWatch Sweden "new" pages
        ↓
scripts/feed/scrape.py  (GitHub Action, daily)
        ↓
feed branch: docs/feed/new-se.json
        ↓
CleanFrame fetches the raw JSON and filters it to Home apps
```

The app reads:

```text
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/new-se.json
```

The `feed` branch is separate from `main`, so daily feed commits do not clutter
the main history. The action is in
`.github/workflows/new-movies-feed.yml`; it can also be started manually.

## Limits

- The JustWatch pages are public but unofficial; the structure can change.
- If the feed is unavailable, the app keeps the last cached copy and offers
  Refresh.
- The feed is refreshed daily by the action; opening the app does not force a
  new JustWatch scrape.
- Deep-linking to a specific movie inside the provider app is not guaranteed.
