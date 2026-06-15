-- Auto-wrap fenced code blocks in a `.term` div so the SCSS chrome
-- (mac traffic-light bar + language label) applies without per-block
-- `::: {.term ...}` fences in markdown.
--
-- Blocks with no language fall back to "text". Diagram-like languages are
-- skipped so they keep rendering through their own pipelines.

local skip_langs = {
  mermaid = true, dot = true, graphviz = true,
  pseudocode = true, tikz = true,
}

function CodeBlock(elem)
  local lang = "text"
  if #elem.classes > 0 then
    lang = elem.classes[1]
    if skip_langs[lang] then return nil end
  else
    -- Plain ``` blocks skip Pandoc's source-code pipeline by default, which
    -- means no per-line spans and no line numbers. Add a language class
    -- (Skylighting passes through unknown languages without tokenizing) plus
    -- numberLines so the gutter is rendered the same as highlighted blocks.
    elem.classes:insert("default")
    elem.classes:insert("numberLines")
  end
  return pandoc.Div(
    { elem },
    pandoc.Attr("", { "term" }, { ["data-title"] = lang })
  )
end
