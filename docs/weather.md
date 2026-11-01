# Local weather line

This fork adds a current-weather line under the Home clock. A typical line is:

```text
Malmö · 10° Overcast · Feels like 7°
```

## What it shows

- A small weather icon
- The city name
- The current temperature in Celsius, rounded to the nearest degree
- A short condition label
- The real feel / apparent temperature

The line is hidden until a reading is available. If the request fails, the
last successful reading stays visible. It does not affect app launching or
offline Home use.

## Data source

[Open-Meteo](https://open-meteo.com/) is called directly from the TV. It needs
no API key or account.

```text
https://api.open-meteo.com/v1/forecast
  ?latitude=55.60587
  &longitude=13.00073
  &current=temperature_2m,weather_code,is_day,apparent_temperature
  &temperature_unit=celsius
  &timezone=Europe%2FStockholm
```

The request runs when Home starts, about every 15 minutes, and when the app
returns to the foreground if the reading is more than 10 minutes old. The last
reading is cached in localStorage under `cleanframe.weather.v1`.

## Change the location

Edit the `WEATHER` object near the top of `app/main.js`:

```js
var WEATHER = {
  lat: 55.60587, lon: 13.00073, place: 'Malmö',
  key: 'cleanframe.weather.v1', refresh: 15 * 60 * 1000
};
```

Use the latitude and longitude from Open-Meteo's geocoding API, then rebuild
and install. The place name is shown on Home and used in the screen-reader
label. The WMO code labels and icons are in the `WMO` map in the same file.

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
