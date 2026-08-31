---
title: "Roberto Park"
toc: false
page-layout: full
---

```{=html}
<div class="hero">
  <div class="mesh-blob mesh-blob-1"></div>
  <div class="mesh-blob mesh-blob-2"></div>
  <div class="mesh-blob mesh-blob-3"></div>
  <div class="mesh-blob mesh-blob-4"></div>
  <div class="mesh-blob mesh-blob-5"></div>
  <div class="hero-content">
    <h1 class="hero-name">Roberto Park</h1>
    <div class="hero-role">
      I <span id="typed-role"></span><span class="typed-cursor">|</span>
    </div>
  </div>
  <!-- Filled from Open-Meteo by the script below; stays hidden if the fetch fails. -->
  <div class="hero-wx" role="status" aria-live="polite">
    <i class="bi hero-wx-icon" aria-hidden="true"></i>
    <span class="hero-wx-temp"></span>
    <span class="hero-wx-more"><span class="hero-wx-sep" aria-hidden="true">·</span> <span class="hero-wx-cond"></span> <span class="hero-wx-sep" aria-hidden="true">·</span> Seoul</span>
  </div>
</div>

<script>
(function() {
  // Firefly: cursor-tracking radial glow inside the hero.
  document.querySelectorAll('.hero').forEach(function(hero) {
    hero.addEventListener('mousemove', function(e) {
      var rect = hero.getBoundingClientRect();
      hero.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
      hero.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
    });
  });

  // Typewriter: cycle through roles.
  var typedEl = document.getElementById('typed-role');
  if (typedEl) {
    var roles = [
      'am a Data Engineer', 'love automation', 'use the Kitty Terminal', 
      'like the Catppuccin Theme', 'read New Courier'
    ];
    var i = 0, j = 0, deleting = false;
    function tickType() {
      var word = roles[i];
      if (deleting) {
        j--;
        typedEl.textContent = word.slice(0, j);
        if (j === 0) { deleting = false; i = (i + 1) % roles.length; setTimeout(tickType, 400); return; }
      } else {
        j++;
        typedEl.textContent = word.slice(0, j);
        if (j === word.length) { deleting = true; setTimeout(tickType, 1600); return; }
      }
      setTimeout(tickType, deleting ? 45 : 90);
    }
    tickType();
  }

  // Weather pill: current conditions from Open-Meteo, which needs no API key
  // and so can be called straight from the browser on a static site.
  // Location is fixed to Seoul rather than the visitor's: no geolocation
  // prompt, no IP-lookup dependency, and my weather is the one worth showing
  // on my own page.
  var WX_URL = 'https://api.open-meteo.com/v1/forecast'
    + '?latitude=37.5665&longitude=126.9780'
    + '&current=temperature_2m,weather_code,is_day'
    + '&timezone=Asia%2FSeoul';
  var WX_CACHE_KEY = 'hero-wx';
  var WX_TTL_MS = 30 * 60 * 1000;

  // WMO weather codes -> [label, day icon, night icon, tint class].
  // Open-Meteo documents the full set; codes not listed here fall back to the
  // plain cloud, which is wrong-looking but never blank.
  var WMO = {
    0:  ['Clear',            'bi-sun',              'bi-moon-stars',  'is-clear'],
    1:  ['Mainly clear',     'bi-sun',              'bi-moon-stars',  'is-clear'],
    2:  ['Partly cloudy',    'bi-cloud-sun',        'bi-cloud-moon',  ''],
    3:  ['Overcast',         'bi-cloud',            'bi-cloud',       ''],
    45: ['Fog',              'bi-cloud-fog',        'bi-cloud-fog',   'is-fog'],
    48: ['Freezing fog',     'bi-cloud-fog',        'bi-cloud-fog',   'is-fog'],
    51: ['Light drizzle',    'bi-cloud-drizzle',    'bi-cloud-drizzle', 'is-rain'],
    53: ['Drizzle',          'bi-cloud-drizzle',    'bi-cloud-drizzle', 'is-rain'],
    55: ['Heavy drizzle',    'bi-cloud-drizzle',    'bi-cloud-drizzle', 'is-rain'],
    56: ['Freezing drizzle', 'bi-cloud-sleet',      'bi-cloud-sleet', 'is-rain'],
    57: ['Freezing drizzle', 'bi-cloud-sleet',      'bi-cloud-sleet', 'is-rain'],
    61: ['Light rain',       'bi-cloud-rain',       'bi-cloud-rain',  'is-rain'],
    63: ['Rain',             'bi-cloud-rain',       'bi-cloud-rain',  'is-rain'],
    65: ['Heavy rain',       'bi-cloud-rain-heavy', 'bi-cloud-rain-heavy', 'is-rain'],
    66: ['Freezing rain',    'bi-cloud-sleet',      'bi-cloud-sleet', 'is-rain'],
    67: ['Freezing rain',    'bi-cloud-sleet',      'bi-cloud-sleet', 'is-rain'],
    71: ['Light snow',       'bi-cloud-snow',       'bi-cloud-snow',  'is-snow'],
    73: ['Snow',             'bi-cloud-snow',       'bi-cloud-snow',  'is-snow'],
    75: ['Heavy snow',       'bi-snow',             'bi-snow',        'is-snow'],
    77: ['Snow grains',      'bi-snow',             'bi-snow',        'is-snow'],
    80: ['Light showers',    'bi-cloud-rain',       'bi-cloud-rain',  'is-rain'],
    81: ['Showers',          'bi-cloud-rain',       'bi-cloud-rain',  'is-rain'],
    82: ['Heavy showers',    'bi-cloud-rain-heavy', 'bi-cloud-rain-heavy', 'is-rain'],
    85: ['Snow showers',     'bi-cloud-snow',       'bi-cloud-snow',  'is-snow'],
    86: ['Snow showers',     'bi-cloud-snow',       'bi-cloud-snow',  'is-snow'],
    95: ['Thunderstorm',     'bi-cloud-lightning',  'bi-cloud-lightning', 'is-storm'],
    96: ['Thunderstorm',     'bi-cloud-lightning-rain', 'bi-cloud-lightning-rain', 'is-storm'],
    99: ['Thunderstorm',     'bi-cloud-lightning-rain', 'bi-cloud-lightning-rain', 'is-storm']
  };

  function paintWeather(data) {
    var pill = document.querySelector('.hero-wx');
    if (!pill || typeof data.temp !== 'number') return;
    var entry = WMO[data.code] || ['Cloudy', 'bi-cloud', 'bi-cloud', ''];
    var icon = pill.querySelector('.hero-wx-icon');
    icon.className = 'bi hero-wx-icon ' + (data.day ? entry[1] : entry[2]);
    if (entry[3]) icon.classList.add(entry[3]);
    pill.querySelector('.hero-wx-temp').textContent = Math.round(data.temp) + '°C';
    pill.querySelector('.hero-wx-cond').textContent = entry[0];
    pill.classList.add('is-ready');
    applyWash(entry[3], data.day);
  }

  // Palette wash: the banner's own mesh blobs recoloured to the condition.
  // Five CSS custom properties on .hero and nothing else — no canvas, no
  // animation loop, so there is no still-frame fallback to get wrong and
  // nothing for a resize to clear. Keys are the tint class the pill already
  // computes, so the pill and the wash can never disagree.
  var WASH = {
    'is-clear': {
      day:   ['#f9e2af', '#fab387', '#f5e0dc', '#f2cdcd', '#eba0ac'],
      night: ['#b4befe', '#89b4fa', '#cba6f7', '#74c7ec', '#585b70'],
      opacity: { day: 0.55, night: 0.45 }
    },
    'is-rain':  { day: ['#89b4fa', '#74c7ec', '#89dceb', '#b4befe', '#9399b2'] },
    'is-storm': { day: ['#7f849c', '#585b70', '#9399b2', '#6c7086', '#585b70'], opacity: { day: 0.6 } },
    'is-snow':  { day: ['#cdd6f4', '#94e2d5', '#89dceb', '#b4befe', '#bac2de'], opacity: { day: 0.42 } },
    'is-fog':   { day: ['#bac2de', '#9399b2', '#a6adc8', '#b4befe', '#7f849c'], opacity: { day: 0.4 } }
  };

  // Overcast is the most common condition here, and greying the banner out on
  // an ordinary day would cost the site its own look for no gain — so plain
  // cloud has no entry and the signature palette stays.
  function applyWash(tint, isDay) {
    var hero = document.querySelector('.hero');
    var spec = WASH[tint];
    if (!hero || !spec) return;
    var when = (spec.night && !isDay) ? 'night' : 'day';
    var pal = spec[when] || spec.day;
    for (var i = 0; i < pal.length; i++) hero.style.setProperty('--blob-' + (i + 1), pal[i]);
    if (spec.opacity && spec.opacity[when]) {
      hero.style.setProperty('--blob-opacity', spec.opacity[when]);
    }
  }

  // Read-through cache so a click around the site isn't a call per page view.
  // Any failure — offline, rate limit, malformed body — leaves the pill hidden
  // rather than showing a blank or an error in the banner.
  (function loadWeather() {
    if (!window.fetch) return;
    try {
      var hit = JSON.parse(sessionStorage.getItem(WX_CACHE_KEY));
      if (hit && Date.now() - hit.at < WX_TTL_MS) { paintWeather(hit); return; }
    } catch (e) { /* no usable cache; fall through to the network */ }

    fetch(WX_URL)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (body) {
        var c = body && body.current;
        if (!c) return;
        var data = { temp: c.temperature_2m, code: c.weather_code, day: c.is_day === 1, at: Date.now() };
        try { sessionStorage.setItem(WX_CACHE_KEY, JSON.stringify(data)); } catch (e) { /* private mode */ }
        paintWeather(data);
      })
      .catch(function () { /* leave the pill hidden */ });
  })();
})();
</script>
```

{{< include assets/_aboutme.md >}}

## Explore

```{=html}
<div class="explore-grid">
  <a href="portfolio.html" class="explore-card">
    <div class="explore-card-title"><i class="bi bi-person-badge"></i> Portfolio</div>
    <p>Résumé, experience, tech stack.</p>
  </a>
  <a href="projects/projects.html" class="explore-card">
    <div class="explore-card-title"><i class="bi bi-collection"></i> Projects</div>
    <p>Case studies and code.</p>
  </a>
  <a href="notes/index.html" class="explore-card">
    <div class="explore-card-title"><i class="bi bi-journal-text"></i> Notes</div>
    <p>Technical notes across the data stack.</p>
  </a>
  <a href="blog/index.html" class="explore-card">
    <div class="explore-card-title"><i class="bi bi-pencil-square"></i> Blog</div>
    <p>Long-form posts.</p>
  </a>
</div>
```

