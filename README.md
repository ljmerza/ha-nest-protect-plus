[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/ljmerza/ha-nest-protect-plus.svg)](https://github.com/ljmerza/ha-nest-protect-plus/releases/)

# Nest Protect Plus for Home Assistant

Custom component for Home Assistant that talks to Nest Protect smoke/CO alarms, Nest Temperature Sensors and Nest x Yale locks through Nest's undocumented and unofficial API. Google's SDM API doesn't support Nest Protect, so the core [Nest integration](https://www.home-assistant.io/integrations/nest/) can't see these devices.

This is a fork of [iMicknl/ha-nest-protect](https://github.com/iMicknl/ha-nest-protect). It uses the same `nest_protect` domain, so it replaces the original rather than running next to it. Don't install both.

## What's different from the original

- **Login that doesn't expire.** You can sign in with a Google *master token*: the same long-lived credential the Nest mobile app uses. It only stops working if you change your Google password or revoke access. Browser cookies, which the original relies on, expire on their own and force you to re-authenticate. Cookie login is still available. The master-token login is based on [#532](https://github.com/iMicknl/ha-nest-protect/pull/532) by @CaelanBorowiec.
- **Upstream improvements that haven't been released yet.** It includes about 20 open pull requests from the original repository, merged and tested together. The main ones:
  - Session refreshes are serialized.
  - Rotated cookies are saved straight away.
  - Temporary Google or Nest outages are retried instead of forcing re-authentication.
  - Commands retry once with a fresh session.
  - Entities go unavailable when Nest stops sending updates, instead of showing stale smoke/CO values.
  - New devices are picked up automatically.
  - State is kept in `entry.runtime_data`.
- **More entities.** Real online status per Protect, alarm hushed, CO previous peak, battery voltage, home safety summary, and smoke/CO alarm state sensors. See [Entities](#entities).

## Installation

Requires Home Assistant 2026.7 or newer.

### HACS

1. In HACS, open the menu → **Custom repositories**, add `https://github.com/ljmerza/ha-nest-protect-plus` with type **Integration**.
1. Search for **Nest Protect Plus**, download it, and restart Home Assistant.
1. Add the integration from **Settings → Devices & services**, or use the button below.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=nest_protect)

If you're switching from iMicknl/ha-nest-protect, remove that repository in HACS first. Your existing config entry and entities are kept, because the domain is the same.

### Manual

Copy `custom_components/nest_protect` into your Home Assistant `custom_components` folder, restart Home Assistant, then add the integration.

## Authentication

Only Google accounts are supported; legacy Nest accounts aren't.

### Recommended: master token

You only do this once. Home Assistant exchanges a one-time token for a master token, stores that, and mints short-lived Nest access tokens from it.

1. Open an **Incognito/Private** window and go to [accounts.google.com/EmbeddedSetup](https://accounts.google.com/EmbeddedSetup).
1. Sign in with the Google account that owns your Nest devices. 2-step verification is fine.
1. If asked **"Who will be using this device?"**, choose **I will be using this device**.
1. Click **I agree** if prompted. The page may then spin forever. That's expected.
1. Open **Developer Tools** (F12) → **Application** → **Cookies** → `https://accounts.google.com`.
1. Copy the value of the **`oauth_token`** cookie. It starts with `oauth2_4/`.
1. In Home Assistant, choose **Master token**, then enter your Google email and paste the value.

The `oauth_token` works only once and expires quickly, so paste it straight away. If it's rejected, sign in again for a fresh one.

> The master token grants access to your Google account. Treat it like a password. It's stored in your Home Assistant config entry and redacted from diagnostics.

To switch an existing install to a master token, open the integration in **Settings → Devices & services** → **⋮** → **Reconfigure**.

### Alternative: browser cookies

These come from a browser session and expire on their own, so expect to re-authenticate from time to time.

#### Chrome extension

1. Download `nest-auth-helper.zip` from the [upstream v0.4.4 release](https://github.com/iMicknl/ha-nest-protect/releases/download/v0.4.4/nest-auth-helper.zip) and unzip it.
1. In Chrome, go to `chrome://extensions`, enable **Developer mode**, and click **Load unpacked** to load the unzipped folder.
1. Sign in to [home.nest.com](https://home.nest.com) in a regular browser window.
1. Click the extension icon → **Extract Credentials** → **Copy Code**.
1. In Home Assistant, choose **Chrome Extension** and paste the code.

#### Developer Tools

> Third-party cookies must be enabled for `home.nest.com`, otherwise the site loops on redirects. Don't use an Incognito/Private window for this method.

1. Open a regular Chrome/Edge window and open Developer Tools (F12) → **Network**, with **Preserve log** checked.
1. Filter on `issueToken`, go to [home.nest.com](https://home.nest.com) and click **Sign in with Google**.
1. Click the `iframerpc` request and copy its full **Request URL** (starts with `https://accounts.google.com`). This is your `issue_token`.
1. Filter on `oauth2/iframe`, click the last `iframe` request, and copy the whole **cookie** request header value (without `cookie:`). This is your `cookies`.
1. Close the tab without logging out of home.nest.com. Logging out invalidates the cookies.

(adapted from the [homebridge-nest documentation](https://github.com/chrisjshull/homebridge-nest))

## Entities

### Nest Protect

| Type | Entities |
|---|---|
| Binary sensor | Smoke status, CO status, Heat status, Online, Alarm hushed, Battery health, Line power, Occupancy (wired Protects) |
| Binary sensor (diagnostic, disabled by default) | Self-tests: smoke, CO, heat, humidity, ambient light, temperature, PIR, LED, speaker, buzzer, Wi-Fi; Removed from base |
| Sensor | Smoke alarm state, CO alarm state, CO previous peak, Battery level, Battery voltage (disabled by default), Replace by, Last audio self-test, Last manual test |
| Switch | Pathlight, Nightly promise, Heads-Up, Steam check |
| Select | Night light brightness |

*Online* is Nest's own connectivity flag. It's not the same as the *Wi-Fi test* self-test sensor, where `off` means the test passed.

### Home

| Type | Entities |
|---|---|
| Sensor | Safety critical failures, Safety warnings (the home safety status shown in the Nest app) |

### Nest Temperature Sensor

| Type | Entities |
|---|---|
| Sensor | Temperature, Battery level |

### Nest x Yale lock

| Type | Entities |
|---|---|
| Lock | Lock / unlock |
| Sensor | Battery |

Every entity goes unavailable when Nest stops sending updates for a while, so an outage can't look like a healthy "no smoke" reading.

## Known limitations

- Wired Protect occupancy stays `on` for 10 minutes after it's triggered. That's an API limitation.
- The master-token login uses an unofficial Google flow ([gpsoauth](https://github.com/simon-weber/gpsoauth)), so Google could change or block it.

## Troubleshooting

Please [open an issue](https://github.com/ljmerza/ha-nest-protect-plus/issues/new) if something doesn't work. Diagnostics (**Settings → Devices & services → Nest Protect Plus → ⋮ → Download diagnostics**) and debug logs help a lot. Diagnostics redact credentials and personal details.

### Enable debug logging

```yaml
logger:
  default: warning
  logs:
    custom_components.nest_protect: debug
```

## Credits

- [iMicknl/ha-nest-protect](https://github.com/iMicknl/ha-nest-protect) and its contributors. Almost all of this code comes from there.
- [@CaelanBorowiec](https://github.com/CaelanBorowiec) for the master-token approach ([#532](https://github.com/iMicknl/ha-nest-protect/pull/532)).
- Based on the research and implementation of [homebridge-nest](https://github.com/chrisjshull/homebridge-nest).
