---
title: "Blog"
toc: false
sidebar: false
# The listing *is* the page, so Quarto's prev/next pagination has nothing
# sensible to point at — it renders as a lone, unstyled link to whichever post
# sorts first, floating below the cards. Posts keep their own pagination.
page-navigation: false
listing:
  id: blog-posts
  template: ../assets/ejs/post-card.ejs
  contents: posts
  sort: "date desc"
  fields: [title, date, reading-time, description, categories]
  date-format: "iso"
  categories: false
  sort-ui: false
  filter-ui: false
---

<!-- >>> blog-intro (synced from the Obsidian Blog index.md by scripts/sync_blog.py) -->
> [!quote] "Writing is thinking. To write well is to think clearly. That's why it's so hard." — David McCullough

Half-formed ideas, worked out in public — notes that grew up enough to share.
<!-- <<< blog-intro -->

::: {#blog-posts}
:::

```{=html}
<script>
(function () {
  // Category filter for the post cards. The pills and each card's `data-cats`
  // are emitted by assets/ejs/post-card.ejs; Quarto's own filter UI is off, so
  // this is the only thing driving visibility.
  var pills = document.querySelectorAll('.post-filter-pill');
  var cards = document.querySelectorAll('.post-card');
  if (!pills.length) return;

  pills.forEach(function (pill) {
    pill.addEventListener('click', function () {
      var cat = pill.dataset.cat;
      pills.forEach(function (p) { p.classList.toggle('is-active', p === pill); });

      cards.forEach(function (card) {
        // data-cats is pipe-delimited *and* pipe-wrapped ("|PKM|Obsidian|"),
        // so a bare indexOf can't match a category that is only a prefix of
        // another one.
        card.hidden = !(cat === '*' || card.dataset.cats.indexOf('|' + cat + '|') !== -1);
      });
    });
  });
})();
</script>
```
