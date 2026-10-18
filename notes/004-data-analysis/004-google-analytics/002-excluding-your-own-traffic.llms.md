# Excluding Your Own Traffic

Analytics on a site you built are answering the wrong question until your own visits are out of them. Development traffic is the worst offender: every local reload counts as a fresh visit, so the numbers report how often you rebuilt the site rather than whether anyone reads it.

There are three mechanisms. They are not equivalent, and the obvious one is the weakest.

## The host guard — best value, near-zero cost

Load analytics only when the page is being served from the real domain:

``` numberSource
(function () {
  if (location.hostname !== 'example.com') return;
  // ... load and configure the tag here ...
})();
```

Local dev servers, preview builds, and staging all have a different hostname, so they fall out automatically. Nothing to remember, nothing to re-check, nothing to configure in a console.

**Do this at run time, not build time.** A build-time flag requires your local build and your CI build to produce different output, which is more machinery and one more thing that can silently drift. A hostname check keeps one artifact behaving correctly wherever it is served.

The limitation is honest and worth stating: this excludes *development* traffic only. Visiting your own live site still counts, because the hostname matches there.

## The per-device flag — covers your own devices

For the case the host guard cannot reach, keep a persistent opt-out in the browser and check it before the tag loads:

``` numberSource
try {
  var q = new URLSearchParams(location.search).get('analytics');
  if (q === 'off') localStorage.setItem('analytics-opt-out', '1');
  if (q === 'on')  localStorage.removeItem('analytics-opt-out');
  if (localStorage.getItem('analytics-opt-out')) return;
} catch (e) { /* storage unavailable — fall through and track */ }
```

Visit `example.com/?analytics=off` once in each browser you use. It survives IP changes, works on cellular, and works from any network — which is exactly where IP-based approaches fall apart.

**Wrap the storage access in `try/catch`.** `localStorage` *throws* rather than returning null in Safari private mode, and an uncaught throw in a `<head>` script takes out every script after it.

Its weaknesses: the flag is per browser profile, so private windows and any cleared-site-data event quietly resume counting you, and you have to remember the one-time visit on each new device.

**This is often not worth building.** Your own visits to your own live site collapse into a single returning user rather than inflating traffic, so the reports still answer “does anyone else read this”. Weigh that against a flag you must re-set in every browser.

## The IP filter — the obvious answer, and usually the wrong one

GA4 has this built in. Admin → Data Streams → Configure tag settings → **Define internal traffic** creates a rule matching an IP and stamps `traffic_type: internal` on those hits. Admin → Data Settings → **Data Filters** then excludes them.

Two traps:

- **The filter ships as “Testing”, which filters nothing.** It has to be switched to **Active**. A filter left in Testing looks configured and does not work.
- **It degrades silently.** A residential IP rotates on the ISP’s schedule and a phone on cellular never matches. The rule keeps *looking* correct while quietly counting you again, and nothing notifies you.

It also cannot separate local development from ordinary browsing at home, since both come from the same address.

Treat an IP filter as a backstop on a static office IP, never as the primary mechanism.

## Blocking versus tagging

Once the site knows it is you, it can either **not send anything** or **send with `traffic_type: 'internal'`** and let a GA4 filter exclude it.

Blocking is simpler, has fewer places to misconfigure, and does not send your browsing to Google at all. Tagging is reversible — flip the filter between Active and Testing to see reports with and without yourself — at the cost of splitting the logic across your code and a console setting.

If the mechanism is a guard that returns before the tag loads, the choice is already made: nothing has loaded, so there is nothing to tag.

## Verifying it, including the control

Confirm against live GA4, not by reading the code:

1.  **Excluded context** — load the site with the browser’s Network tab filtered to `googletagmanager`. Expect zero requests.
2.  **Included context** — from a browser that is *not* excluded, browse with GA4 **Realtime** open. Your session should appear within about thirty seconds.

Step 2 is the one people skip and the only one that proves anything. An empty Realtime report is indistinguishable from analytics being broken outright — which is precisely the failure that quietly reports “nobody visits”.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
