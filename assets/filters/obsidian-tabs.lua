-- Convert Obsidian "Tabs" plugin blocks into Quarto's rendered tabset HTML.
--
-- Obsidian syntax (the community "Tabs" plugin):
--   ~~~~tabs
--   tab: First title
--   ...markdown body...
--   tab: Second title
--   ...markdown body...
--   ~~~~
--
-- Pandoc otherwise treats `tabs` as an unknown code language and dumps the
-- whole thing as one literal code block. We instead emit our own `.doc-tabs`
-- markup -- deliberately NOT Quarto's Bootstrap `.panel-tabset` (its nav-tabs
-- look is bland and collides with the blog styling). The look/behaviour lives
-- in assets/scss/obsidian-tabs.scss + the switcher script in custom_body.html,
-- styled like the "content tabs" docs sites use for per-OS install steps.
--
-- Each tab body is re-parsed as real markdown blocks (not raw text) and nested
-- inside the panels, so the callouts + term-codeblocks filters -- which must be
-- listed AFTER this one -- still process code fences and callouts inside tabs.

local tabset_index = 0

local function html_escape(s)
  return (s:gsub("[&<>\"]", {
    ["&"] = "&amp;", ["<"] = "&lt;", [">"] = "&gt;", ["\""] = "&quot;",
  }))
end

local function trim(s)
  return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function CodeBlock(elem)
  if #elem.classes == 0 or elem.classes[1] ~= "tabs" then return nil end

  -- Split the raw body into tabs on lines that start with `tab:`.
  local tabs = {}
  local current = nil
  for line in (elem.text .. "\n"):gmatch("(.-)\n") do
    local title = line:match("^%s*tab:%s*(.*)$")
    if title then
      current = { title = trim(title), body = {} }
      table.insert(tabs, current)
    elseif current then
      table.insert(current.body, line)
    end
    -- Lines before the first `tab:` marker are ignored.
  end

  if #tabs == 0 then return nil end

  tabset_index = tabset_index + 1
  local prefix = "dtab-" .. tabset_index

  -- Build the tab-strip (buttons, not links -- no navigation, just switching).
  local nav = { '<div class="doc-tabs__nav" role="tablist">' }
  for i, tab in ipairs(tabs) do
    local id = prefix .. "-" .. i
    local active = (i == 1) and " is-active" or ""
    local selected = (i == 1) and "true" or "false"
    local tabindex = (i == 1) and "0" or "-1"
    table.insert(nav, table.concat({
      '<button type="button" class="doc-tabs__tab', active, '"',
      ' id="', id, '-label" role="tab"',
      ' aria-controls="', id, '" aria-selected="', selected, '"',
      ' tabindex="', tabindex, '">',
      html_escape(tab.title), '</button>',
    }))
  end
  table.insert(nav, "</div>")

  local blocks = {
    pandoc.RawBlock("html", '<div class="doc-tabs">'),
    pandoc.RawBlock("html", table.concat(nav)),
    pandoc.RawBlock("html", '<div class="doc-tabs__panels">'),
  }

  -- Emit each panel: a raw opening <div>, the re-parsed markdown blocks, then a
  -- raw closing </div>. Nesting real blocks (rather than raw HTML) lets the
  -- later callout/term filters see the code fences and callouts inside.
  for i, tab in ipairs(tabs) do
    local id = prefix .. "-" .. i
    local active = (i == 1) and " is-active" or ""
    local hidden = (i == 1) and "" or " hidden"
    table.insert(blocks, pandoc.RawBlock("html", table.concat({
      '<div id="', id, '" class="doc-tabs__panel', active, '"',
      ' role="tabpanel" aria-labelledby="', id, '-label"', hidden, '>',
    })))

    local body = trim(table.concat(tab.body, "\n"))
    local parsed = pandoc.read(body, "markdown+autolink_bare_uris+hard_line_breaks")
    for _, b in ipairs(parsed.blocks) do
      table.insert(blocks, b)
    end

    table.insert(blocks, pandoc.RawBlock("html", "</div>"))
  end

  table.insert(blocks, pandoc.RawBlock("html", "</div></div>"))
  return blocks
end
