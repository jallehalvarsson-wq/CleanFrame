# Art Mode helpers

These scripts use Samsung's local Art API through
[`samsungtvws`](https://github.com/xchwarze/samsung-tv-ws-api). They are
deck-side helpers, not part of the packaged CleanFrame widget.

## Install

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/art-mode/requirements.txt
```

## Upload photos or inspect Art Mode

```sh
.venv/bin/python scripts/art-mode/art-mode-setup.py --host 192.168.1.50 --folder ~/Pictures
.venv/bin/python scripts/art-mode/art-mode-status.py --host 192.168.1.50
```

`--host` can be omitted if `SAMSUNG_TV_HOST` is set.

The first run may show an **Allow** prompt on the TV. Accept it once; the
library saves the Art API token.

## Firmware note

On firmware that reports **Art API 5.0.1.0**, uploads and `select_image` work,
but the library's old `change_favorite` and `set_slideshow_status` calls can
be rejected with error `-7`. In that case upload the photos here and finish
**Favorites** and **Slideshow** in the TV's Art Mode UI. The TV handles the
rotation; the computer does not need to stay on.

See [`docs/art-mode.md`](../../docs/art-mode.md) for the full guide.
