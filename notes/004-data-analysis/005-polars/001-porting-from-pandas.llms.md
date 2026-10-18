# Porting from pandas

The dangerous differences between pandas and polars are not the ones that raise.\
`.empty` → `.is_empty()` and `.tolist()` → `.to_list()` fail loudly the first\
time the code runs. The four below return a *number*, just a different one, and\
only show up if you diff against the old implementation on real data.

Port with a harness: run both implementations over the same real frame and the\
same input combinations, and compare cell by cell. Every item on this page was\
found that way, not by reading the diff.

## `group_by` keeps null keys; `groupby` drops them

pandas `groupby` silently drops rows whose key is NaN. Polars gives null its own\
group. A key that is null in even a fraction of a percent of rows can aggregate\
into a group large enough to outrank real ones — and it renders as an unlabelled\
axis tick or pie slice.

``` numberSource
# pandas: rows with a null key simply vanish
df.groupby("category")["revenue"].sum()

# polars: same result requires saying so
df.drop_nulls("category").group_by("category").agg(pl.col("revenue").sum())
```

`pivot(index=...)` has the same asymmetry — `pivot_table` drops null index rows,\
`pivot` keeps them. Audit every grouping key for nulls before assuming parity;\
`df.null_count()` is the fast way to find which keys can actually be null.

## Neither `sort` is stable, so ties are undefined in both

polars `sort` is unstable by default. But pandas `sort_values` defaults to\
`kind="quicksort"`, which is *also* unstable — so the pandas output being diffed\
against had an arbitrary tie order to begin with. Do not chase an exact match on\
tied rows; make the new code deterministic instead.

``` numberSource
pivot = (
    df.pivot(on="period", index="key", values="revenue", aggregate_function="sum")
    .fill_null(0)
    .sort("key")                                        # seed a defined order
    .sort(latest_period, descending=True, maintain_order=True)  # stable from there
)
```

Two things matter, and one alone is not enough: `maintain_order=True` makes the\
sort stable, and the seed sort decides what stability preserves. pandas got its\
seed for free because `pivot_table` returns a sorted index; `pivot` returns\
first-seen order. With both, tied rows break by key in both libraries and the\
frames match exactly — including anything derived from row position, such as a\
rank-change arrow, which otherwise drifts by ±1 wherever a tie moved.

## Null propagates through `is_in` and comparisons

`pl.col(x).is_in(values)` yields null for a null `x`, not False. This is\
invisible on the positive branch and wrong on the negative one: `filter(~expr)`\
drops those rows from *both* sides, so a row present in the pandas output\
disappears from the polars one and the two branches no longer sum to the total.

``` numberSource
matched = pl.col("key").is_in(wanted).fill_null(False)
hit  = df.filter(matched)["revenue"].sum()
miss = df.filter(~matched)["revenue"].sum()   # needs the fill_null to balance
```

Same for `str.contains`, which is where pandas spells it `na=False`.

## Plotly reads order from the data, so sort instead of `category_orders`

`pd.Categorical` plus `category_orders` forced legend and axis order regardless\
of row order. Dropping both means the explicit sort *is* the ordering — plotly\
takes trace and category order from first appearance. An explicit sort is also\
faster than making either pandas or plotly do it.

Sort by the series key first when one series spans every x value:

``` numberSource
rank = {name: i for i, name in enumerate(SERIES_ORDER)}
df = (
    df.with_columns(_order=pl.col("series").replace_strict(rank, default=len(rank)))
    .sort(["_order", "x"])   # leading series covers every x, so the axis stays complete
    .drop("_order")
)
```

Sorting by x first instead would take legend order from whichever series happens\
to appear at the earliest x. Sorting by series first is only safe when the\
leading series is present at every x — a total or “all” series usually is. For a\
stacked bar where no category is guaranteed complete, sort `["x", category]`\
instead, so the axis comes out right and the stack order falls out of the\
category’s own collation.

## Lazy is where the memory actually goes

`.lazy()` on an already-loaded frame does not shrink the frame — it defers the\
work. What it buys is that a filter/aggregate chain never materialises the\
intermediates, and projection pushdown means only the columns the chain really\
reads get built. On a wide fact table sliced to a small window, that is the\
difference between a full-width copy per interaction and a few hundred rows.

``` numberSource
base = df.lazy().filter(...)              # nothing has run yet
cur  = base.filter(date_between).group_by(key).agg(...).collect()
```

Two things to keep straight:

- **Collect once where a result is reused.** Separate `.collect()` calls on the\
  same LazyFrame redo the work; the engine caches nothing between them. If three\
  views share a filtered base, collect it once and pass the DataFrame.
- **Do not mix eager and lazy in one chain.** A `join` between a DataFrame and a\
  LazyFrame raises, and a `.collect()` on an eager frame raises\
  `AttributeError: 'DataFrame' object has no attribute 'collect'`. Convert at the\
  top of the section and stay in one mode.

Scalars are worth taking off a LazyFrame too: a min/max for an axis bound is\
`lf.select(pl.col(c).min()).collect().item()`, not a materialised column.

## Things with no polars equivalent

- **`pd.Period`** — use a monotonic month index (`year * 12 + month - 1`) for\
  arithmetic, and inclusive date bounds for filtering. `pd.DateOffset(months=i)`\
  becomes a subtraction on that index.
- **`pd.Categorical` ordering** — a numeric sort-key column plus an explicit sort.
- **`.mode()`** — polars’ is unordered where pandas’ is sorted, so\
  `.mode().sort().first()` is what matches `.mode().iloc[0]`.
- **A pandas `Styler`** — no equivalent, and Streamlit’s conditional table\
  colouring is Styler-only. Convert with `.to_pandas()` at that boundary and\
  keep everything above it polars; the frame being styled is a display-sized\
  aggregate, not source data. Watch the dtype: `with_row_index` gives UInt32,\
  and appending a NaN summary row collapses an unsigned column to `object`,\
  which breaks a `"{:.0f}"` format. Cast to `float64` first.

## A few more that bite

- **`cut()` returns an Enum**, not a String. Joining that against a String key\
  raises `SchemaError: datatypes of join keys don't match`. Cast it.
- **A local variable named `pl`** silently shadows the polars import for the rest\
  of its scope. Grep for it before starting a port.
- **`pandas` 2.3 `PeriodDtype` has no `.freqstr`.** Code doing\
  `getattr(dtype, "freqstr", "")` to branch on frequency has been taking the\
  fallback branch since that attribute moved — worth checking rather than\
  porting the bug forward.

## Parsing and dtype at the boundary

- **Decimal columns** — a SQL `NUMBER` arrives as `pl.Decimal`, and\
  `.to_pandas()` turns it into an object column of `decimal.Decimal` that raises\
  `TypeError` on division by a float. Cast at the read boundary, not at the use\
  site, so no downstream page has to know.
- **`"YYYY-MM"` text** — chrono needs a day component, so `str.to_date("%Y-%m")`\
  will not parse it. Concatenate `"-01"` first and use `%Y-%m-%d` with\
  `strict=False` for the pandas `errors="coerce"` behaviour.

## Related

- [Streamlit](../../../notes/005-business-intelligence/004-streamlit.llms.md) for the display layer these frames feed
- [Performance](../../../notes/005-business-intelligence/006-performance.llms.md) for the memory difference that motivates the swap

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
