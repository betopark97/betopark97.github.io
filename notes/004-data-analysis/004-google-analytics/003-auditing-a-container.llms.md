# Auditing a Container

A GTM container’s published configuration is served **publicly** at its own URL. You do not need console access, or even to own the container, to see exactly which tags it fires. This is the fastest way to answer “what is this thing actually doing” — on your own site or anyone else’s.

``` numberSource
curl -s "https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX" -o gtm.js
```

The response is the GTM runtime with the container’s configuration embedded in it as a JSON blob under a `"resource"` key.

## Quick answers by grep

Usually enough on its own — find out which analytics properties a container reports to:

``` numberSource
grep -oE '"(G-[A-Z0-9]{6,}|UA-[0-9]+-[0-9]+|AW-[0-9]+|DC-[0-9]+)"' gtm.js | sort -u
```

If a measurement ID you already load directly via `gtag.js` shows up here too, you have a [double-count](../../../notes/004-data-analysis/004-google-analytics/001-installation.llms.md).

## Reading the tag list properly

Brace-match the `"resource"` object out of the file and parse it:

``` numberSource
import json

s = open('gtm.js', encoding='utf-8', errors='replace').read()
start = s.index('{', s.find('"resource":'))
depth, j, instr, esc = 0, start, False, False
while j < len(s):
    c = s[j]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: break
    j += 1

r = json.loads(s[start:j+1])
print('version:', r.get('version'))
for k in ('tags', 'macros', 'predicates', 'rules'):
    print(f'{k:12}', len(r.get(k) or []))
```

Reading the result:

- **`tags`** — what actually fires. An empty list means the container does nothing at all.
- **`predicates` / `rules`** — the trigger conditions. Zero of these alongside zero tags confirms an untouched container.
- **`macros`** — variables. A handful ship with every container, so a small count here is not evidence of configuration.
- **`version: 1`** with nothing else is the signature of a container that was created and never published into.

Tag entries carry a `function` field identifying the type: `gaawc` is a GA4 Configuration, `gaawe` a GA4 Event, `html` a custom HTML tag, `img` a tracking pixel.

## An empty container is not free

The finding worth acting on is usually not a misconfiguration but dead weight. An empty container still downloads its runtime on every single pageview — on the order of **100 KB gzipped** — to execute nothing. Measure it rather than guessing:

``` numberSource
curl -s -H "Accept-Encoding: gzip" -o /dev/null \
     -w "%{size_download} bytes\n" \
     "https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX"
```

Delete the snippet if the container is empty. GTM’s value is changing tags without a redeploy, which an empty container is not providing, and the snippet pastes back from the console the moment you actually want it.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
