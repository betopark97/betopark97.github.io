-- Convert Obsidian-style callouts into Quarto's rendered callout HTML.
--
-- Obsidian syntax:
--   > [!type] Optional title         -- non-collapsible
--   > [!type]+ Optional title        -- collapsible, starts open
--   > [!type]- Optional title        -- collapsible, starts closed
--   > Body content
--
-- We emit the full Quarto callout div tree directly because Quarto's
-- own callout filter runs on the initial AST and never sees Divs that
-- other Lua filters create later.
--
-- Each alias is mapped to its canonical Obsidian type. That canonical
-- name is emitted verbatim as a `data-callout` attribute, and
-- assets/scss/obsidian-callouts.scss keys off it to reproduce Obsidian's
-- per-type icon and colour. The set of types/aliases below mirrors
-- https://help.obsidian.md/callouts exactly.

local type_map = {
  note = "note",
  abstract = "abstract", summary = "abstract", tldr = "abstract",
  info = "info",
  todo = "todo",
  tip = "tip", hint = "tip",
  important = "important",
  success = "success", check = "success", done = "success",
  question = "question", help = "question", faq = "question",
  warning = "warning", caution = "warning", attention = "warning",
  failure = "failure", fail = "failure", missing = "failure",
  danger = "danger", error = "danger",
  bug = "bug",
  example = "example",
  quote = "quote", cite = "quote",
}

local collapse_counter = 0

function BlockQuote(elem)
  local first = elem.content[1]
  if not first or first.t ~= "Para" then return nil end

  local inlines = first.content
  if #inlines == 0 or inlines[1].t ~= "Str" then return nil end

  local kind, collapse_marker = inlines[1].text:match("^%[!([%w]+)%]([%+%-]?)$")
  if not kind then return nil end

  local callout_type = type_map[kind:lower()]
  if not callout_type then return nil end

  table.remove(inlines, 1)
  if #inlines > 0 and inlines[1].t == "Space" then
    table.remove(inlines, 1)
  end

  local title_inlines = {}
  while #inlines > 0
        and inlines[1].t ~= "SoftBreak"
        and inlines[1].t ~= "LineBreak" do
    table.insert(title_inlines, inlines[1])
    table.remove(inlines, 1)
  end
  if #inlines > 0 then
    table.remove(inlines, 1)
  end

  local body_blocks = {}
  if #inlines > 0 then
    table.insert(body_blocks, pandoc.Para(inlines))
  end
  for i = 2, #elem.content do
    table.insert(body_blocks, elem.content[i])
  end

  if #title_inlines == 0 then
    -- Obsidian's default title is the type keyword as typed, title-cased.
    local title = kind:sub(1, 1):upper() .. kind:sub(2):lower()
    title_inlines = { pandoc.Str(title) }
  end

  local is_collapsible = collapse_marker == "+" or collapse_marker == "-"
  local starts_open = collapse_marker == "+"

  local icon_div = pandoc.Div(
    { pandoc.RawBlock("html", '<i class="callout-icon"></i>') },
    pandoc.Attr("", { "callout-icon-container" }, {})
  )
  local title_div = pandoc.Div(
    { pandoc.Plain(title_inlines) },
    pandoc.Attr("", { "callout-title-container", "flex-fill" }, {})
  )

  local header_children = { icon_div, title_div }
  local header_attrs = {}

  if is_collapsible then
    collapse_counter = collapse_counter + 1
    local n = collapse_counter
    local target = "callout-" .. n .. "-contents"

    header_attrs["data-bs-toggle"] = "collapse"
    header_attrs["data-bs-target"] = "." .. target
    header_attrs["aria-controls"] = "callout-" .. n
    header_attrs["aria-expanded"] = starts_open and "true" or "false"
    header_attrs["aria-label"] = "Toggle callout"

    local toggle_btn = pandoc.RawBlock(
      "html",
      '<div class="callout-btn-toggle d-inline-block border-0 py-1 ps-1 pe-0 float-end">' ..
      '<i class="callout-toggle"></i></div>'
    )
    table.insert(header_children, toggle_btn)
  end

  local header_div = pandoc.Div(
    header_children,
    pandoc.Attr("", { "callout-header", "d-flex", "align-content-center" }, header_attrs)
  )
  local body_inner = pandoc.Div(
    body_blocks,
    pandoc.Attr("", { "callout-body-container", "callout-body" }, {})
  )

  local children = { header_div }

  -- Only emit a body when there is content. A title-only callout (e.g. a
  -- one-line quote written entirely in the title) then renders as a clean
  -- framed header with no dangling divider or empty content area.
  if #body_blocks > 0 then
    local body_block
    if is_collapsible then
      local n = collapse_counter
      local collapse_classes = { "callout-" .. n .. "-contents", "callout-collapse", "collapse" }
      if starts_open then
        table.insert(collapse_classes, "show")
      end
      body_block = pandoc.Div(
        { body_inner },
        pandoc.Attr("callout-" .. n, collapse_classes, {})
      )
    else
      body_block = body_inner
    end
    table.insert(children, body_block)
  end

  return pandoc.Div(
    children,
    pandoc.Attr("", {
      "callout", "callout-style-default", "callout-titled",
    }, { ["data-callout"] = callout_type })
  )
end
