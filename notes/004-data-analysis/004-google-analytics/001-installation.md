---
title: Installation
---
There are two ways to put GA4 on a site, they look almost identical, and the difference matters.

## gtag.js — the tag itself

`gtag.js` *is* the analytics library. It measures. The snippet loads the script and then configures it against a measurement ID:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

That `config` call is what sends the pageview. The tag is hardcoded in the HTML, so changing anything about the tracking means editing and redeploying the site.

## Google Tag Manager — a container, not a tag

GTM measures nothing on its own. It is a container you fill with tags through a web console, plus the delivery mechanism that fetches and fires them. Its entire value is **changing what you track without touching code or redeploying**.

```html
<script>(function(w,d,s,l,i){ /* loads gtm.js?id=GTM-XXXXXXX */ })(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
```

If you never open the console and configure tags, a GTM container does exactly nothing — while still downloading its runtime on every pageview.

## Loading both is the classic double-count

Because GTM is a box that can hold a copy of the thing, this happens easily:

```
page loads
├── gtag.js       → page_view → G-XXXXXXXXXX
└── GTM container → GA4 tag   → page_view → G-XXXXXXXXXX   ← same property, second hit
```

Two hits, one visitor. Every figure in the reports doubles — for every visitor, not just you — and nothing in the GA4 interface flags it. The usual path in is chronological rather than careless: GA4 hands you the gtag.js snippet when you create a data stream, and GTM's own setup wizard later walks you into creating a GA4 Configuration tag. Neither step mentions the other.

**Pick one.** Hardcoded gtag.js is simpler and one less request; GTM earns its keep only once you actually want to add or change tags without a deploy. If both are already present, [audit the container](003-auditing-a-container.md) before assuming which to remove.

## Two snippet details worth knowing

**`function gtag()` is fragile once you move it.** The stock snippet declares it at top level. Nest that declaration inside a block — an `if`, a loop, an IIFE — and you are relying on function-declaration-in-block scoping, which is inconsistent across engines. Assign it explicitly instead, and call it the same way:

```js
window.dataLayer = window.dataLayer || [];
window.gtag = function () { window.dataLayer.push(arguments); };
window.gtag('config', 'G-XXXXXXXXXX');
```

The unqualified `gtag(...)` resolves only because `window` happens to be the global object. True, but not worth depending on.

**The GTM `<noscript>` iframe is near-useless for GA4.** GTM's install instructions include an iframe fallback for JS-disabled browsers. GA4 cannot do anything meaningful without JavaScript, so it buys almost nothing — and no JS-based guard can suppress it, since by definition JS is not running.

***

[Last modified: 2026-08-30]{.note-modified}
