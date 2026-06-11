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

