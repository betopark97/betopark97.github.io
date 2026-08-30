--[[
Appends a "N min read" stat to a blog post's date byline.

Quarto computes reading time for *listing* items only -- there is no
document-level option -- and the HTML title block renders a fixed set of
metadata keys, so there is no slot to hang a new one on. Folding it into `date`
puts it in the one place the template already prints, and blog.scss styles that
line as a single mono byline, so it reads as `2026-06-27 · 7 min read`.

Scoped to blog posts by input path. (The obvious gate -- the `body-classes:
blog-post` that blog/posts/_metadata.yml already sets -- doesn't work: Quarto
lifts that key into template variables before user filters run, so it reads as
empty here.) Every other page passes through untouched.

200 words/minute matches the rate Quarto uses for the listing cards, so the
number on a post agrees with the number on its card.
--]]

local WORDS_PER_MINUTE = 200

local words = 0

-- Pandoc's own wordcount recipe: one Str is one word (unless it is pure
-- punctuation), and code is counted by whitespace-separated runs.
local wordcount = {
  Str = function(el)
    if el.text:match("%P") then words = words + 1 end
  end,
  Code = function(el)
    local _, n = el.text:gsub("%S+", "")
    words = words + n
  end,
  CodeBlock = function(el)
    local _, n = el.text:gsub("%S+", "")
    words = words + n
  end,
}

function Pandoc(doc)
  local input = quarto.doc.input_file or ""
  if not input:find("/blog/posts/") or not doc.meta.date then
    return nil
  end

  words = 0
  pandoc.walk_block(pandoc.Div(doc.blocks), wordcount)
  local minutes = math.max(1, math.floor(words / WORDS_PER_MINUTE + 0.5))

  -- By the time user filters run, Quarto has already normalised `date` to the
  -- project's date-format, so stringifying it here preserves the ISO rendering.
  doc.meta.date = pandoc.MetaInlines({
    pandoc.Str(pandoc.utils.stringify(doc.meta.date)),
    pandoc.Space(),
    pandoc.Span({ pandoc.Str(minutes .. " min read") }, { class = "reading-time" }),
  })
  return doc
end
