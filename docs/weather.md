# Local weather line

This fork adds a current-weather line under the Home clock. A typical line is:

```text
Stockholm · 10° Overcast · Feels like 7°
```

## What it shows

- A small weather icon
- The selected city name
- The current temperature in Celsius, rounded to the nearest degree
- A short condition label
- The real feel / apparent temperature

The line is hidden until a reading is available for the selected city. If the
request fails, the last successful reading for that city stays visible. It does
not affect app launching or offline Home use.

## Choose the location

Open **Settings → Weather** and select a city from the grid. The choice is saved
only on the TV in localStorage under `cleanframe.weather.location.v1`. The
public default is **Stockholm**, so a fresh install does not identify the
owner's own city.

The built-in list is in `WEATHER_PLACES` near the top of `app/main.js`. To add
another Swedish city, add its name, latitude and longitude to that array and
rebuild. Changing the city clears the weather cache and requests a new reading.

The last reading is cached in `cleanframe.weather.v1`. It records the city ID,
so a reading for a different city is ignored after a location change.

## Data source

[Open-Meteo](https://open-meteo.com/) is called directly from the TV. It needs
no API key or account.

```text
https://api.open-meteo.com/v1/forecast
  ?latitude=<selected latitude>
  &longitude=<selected longitude>
  &current=temperature_2m,weather_code,is_day,apparent_temperature
  &temperature_unit=celsius
  &timezone=Europe%2FStockholm
```

The request runs when Home starts, about every 15 minutes, and when the app
returns to the foreground if the reading is more than 10 minutes old. The WMO
code labels and icons are in the `WMO` map in `app/main.js`.

## Permissions

`app/config.xml` adds:

```xml
<access origin="*" subdomains="true"/>
<tizen:privilege name="http://tizen.org/privilege/internet"/>
```

The `internet` privilege is a public privilege. If the TV blocks the direct
HTTPS request, use a local proxy or a native Tizen HTTP helper; do not embed a
web player or account credentials.

## Troubleshooting

1. Confirm the TV has internet access.
2. Open the app in debug mode and check the browser console for the Open-Meteo
   request.
3. Confirm the installed widget contains the `internet` privilege and the
   `<access>` element.
4. Confirm the current WMO code is in the `WMO` map in `app/main.js`.
5. Check **Settings → Weather** if the line shows a different city or is waiting
   for its first reading.

Launcher wallpaper is separate from native Art Mode. Runtime photos, materials and
available fonts are local assets; they do not require the Mac or a network
download.
