-- Convert Obsidian-style callouts to Quarto callouts.
--
-- Obsidian syntax:
--   > [!type] Optional title
--   > Body content
--   > More body
--
-- Trailing `+` opens by default, trailing `-` starts collapsed.
-- Unknown types fall through unchanged (rendered as a plain blockquote).

local type_map = {
  -- Quarto callout-note
  note = "note", info = "note", todo = "note", abstract = "note",
  summary = "note", tldr = "note", question = "note", help = "note",
  faq = "note", example = "note", quote = "note", cite = "note",
  -- Quarto callout-tip
  tip = "tip", hint = "tip", success = "tip", check = "tip", done = "tip",
  -- Quarto callout-warning
  warning = "warning", caution = "warning", attention = "warning",
  -- Quarto callout-caution
  failure = "caution", fail = "caution", missing = "caution", bug = "caution",
  -- Quarto callout-important
  danger = "important", error = "important", important = "important",
}

function BlockQuote(elem)
  local first = elem.content[1]
  if not first or first.t ~= "Para" then return nil end

  local inlines = first.content
  if #inlines == 0 or inlines[1].t ~= "Str" then return nil end

  local kind, collapse_marker = inlines[1].text:match("^%[!([%w]+)%]([%+%-]?)$")
  if not kind then return nil end

  local quarto_type = type_map[kind:lower()]
  if not quarto_type then return nil end

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

  local new_blocks = {}
  if #inlines > 0 then
    table.insert(new_blocks, pandoc.Para(inlines))
  end
  for i = 2, #elem.content do
    table.insert(new_blocks, elem.content[i])
  end

  local attrs = {}
  if #title_inlines > 0 then
    attrs.title = pandoc.utils.stringify(title_inlines)
  end
  if collapse_marker == "+" then
    attrs.collapse = "false"
  elseif collapse_marker == "-" then
    attrs.collapse = "true"
  end

  return pandoc.Div(
    new_blocks,
    pandoc.Attr("", { "callout-" .. quarto_type }, attrs)
  )
end
