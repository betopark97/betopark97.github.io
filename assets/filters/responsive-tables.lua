-- Wrap each table in a `.table-responsive` div so wide tables scroll
-- horizontally on narrow viewports instead of getting squashed into the
-- body column. Bootstrap (bundled by Quarto) supplies the overflow rule.

function Table(tbl)
  return pandoc.Div(
    { tbl },
    pandoc.Attr("", { "table-responsive" })
  )
end
