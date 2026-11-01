# Art Mode helpers

The scripts in [`scripts/art-mode/`](../scripts/art-mode/) use Samsung's local
Art API through [`samsungtvws`](https://github.com/xchwarze/samsung-tv-ws-api).
They are deck-side helpers, not part of the packaged CleanFrame widget.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/art-mode/requirements.txt
```

The TV must be on the same network. The first run may show an **Allow** prompt
on the TV; accept it once. The library saves the Art API token. Treat that
token as a credential.

## Upload photos

```sh
.venv/bin/python scripts/art-mode/art-mode-setup.py \
  --host 192.168.1.50 --folder ~/Pictures --limit 10
```

`--host` can be omitted if `SAMSUNG_TV_HOST` is set. WebP files are converted
to JPEG. The script prints the new content IDs.

On firmware that reports **Art API 5.0.1.0**, uploads and `select_image` work,
but the library's old `change_favorite` and `set_slideshow_status` calls can
be rejected with error `-7`. Upload the photos here, then finish in the TV UI:

1. Open **Art Mode → My Pictures**.
2. Add the photos to **Favorites** with the heart/star button.
3. Open **Art Mode Settings → Slideshow**.
4. Choose **Favorites** or **My Pictures**, set the interval, and enable
   **Shuffle**.

The TV then handles the rotation; the computer is not required.

## Check status

```sh
.venv/bin/python scripts/art-mode/art-mode-status.py --host 192.168.1.50
```

This prints Art Mode state, the current artwork, the legacy slideshow status,
and counts for My Pictures, Favorites and the Art Store. On newer firmware the
legacy `get_slideshow_status` call may report `off` even when the UI slideshow
is active; the TV UI is the source of truth.

## Categories

```text
MY-C0002   My Pictures
MY-C0004   Favorites
MY-C0008   Art Store
```

## Notes

- The Art API is a local, undocumented Samsung interface. It may change after
  a firmware update.
- Uploads are accepted at small sizes, but 4K images look best on a Frame.
- The Art Mode brightness and motion settings are not changed by these
  scripts.
