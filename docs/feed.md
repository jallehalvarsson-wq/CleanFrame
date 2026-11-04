# Movie feeds

The **New** and **Most watched** controls in the top-right of Home open poster
grids for the catalog apps currently on Home. Both use the same grid and movie
detail view.

## What they show

- **New**: movies recently added to the provider catalogues in Sweden.
- **Most watched**: movies from each provider catalogue in JustWatch popularity
  order. This is a public popularity signal, not a record of what has been
  watched on this TV.

Both panels show:

- Poster, provider name and title in the grid
- Only movies (`/se/film/...`), not TV series
- Only providers whose apps are on Home:
  `Netflix`, `SVT Play`, `TV4 Play`, `HBO Max`, `Prime Video`, `Viaplay`
- The feed source (`JustWatch`) and a relative last-updated age, refreshed every
  minute while the panel is open
- A **Refresh** button; each feed is cached separately in localStorage

OK on a grid tile opens a **movie detail view** with:

- The full title, provider and poster
- Year, runtime and genres
- Director and top cast
- Synopsis
- The source and last-updated line
- **Open <provider>**: launches the provider app on its home screen
- **Back**: returns to the feed

The provider app opens on its home screen; the TV apps do not expose a reliable
public per-title deep link. The detail view always shows the full title and
synopsis even when the grid tile has to truncate a long name. The feed JSON
also carries the provider watch URL, but the current app does not expose a
separate exact-link action.

Stremio, Internet, YouTube and Steam Link are not catalogue services, so they
are not part of either feed.

## Data flow

```text
JustWatch Sweden "new" and provider movie pages
        ↓
scripts/feed/scrape.py --kind new|popular  (GitHub Action, daily)
        ↓
feed branch: docs/feed/new-se.json
             docs/feed/popular-se.json
        ↓
CleanFrame fetches the raw JSON and filters it to Home apps
```

The app reads:

```text
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/new-se.json
https://raw.githubusercontent.com/jallehalvarsson-wq/CleanFrame/feed/docs/feed/popular-se.json
```

The `feed` branch is separate from `main`, so daily feed commits do not clutter
the main history. The action is in
`.github/workflows/new-movies-feed.yml`; it can also be started manually.

Each JSON file also carries `source` (`JustWatch`), `kind` and `generated` (an
ISO-8601 timestamp). The app uses those fields for the source and relative
last-updated line; no extra network request is needed for the metadata.

The provider movie pages are sorted by JustWatch popularity. The scraper
interleaves the providers so the first grid page mixes services while keeping
each provider's most popular titles first.

## Limits

- The JustWatch pages are public but unofficial; the structure can change.
- “Most watched” is a JustWatch popularity ranking, not a measurement of
  viewing on this TV or a global play-count chart.
- If a feed is unavailable, the app keeps the last cached copy and offers
  Refresh.
- The feeds are refreshed daily by the action; opening the app does not force
  a new JustWatch scrape.
- Deep-linking to a specific movie inside the provider app is not guaranteed.
