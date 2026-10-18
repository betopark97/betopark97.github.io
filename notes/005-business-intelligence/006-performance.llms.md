# Performance

A dashboard that takes 30 seconds to load does not get used. People go back to asking for a raw extract and doing it in a spreadsheet. Performance is a UI/UX concern, not an infrastructure one.

The mental model: every dashboard has a cost at three layers — the query, the transport, and the render. Fixing the wrong layer wastes effort, so find out which one is slow before optimizing.

## Minimize fields and records

The cheapest data is the data you never fetch. Push filtering as far upstream as possible — into the query, not into the dashboard after the data has already arrived. Same for columns: select only what the view actually uses. Pulling every column drags unused data across the wire and into memory.

Defaults matter here. If a date filter defaults to “all time”, every user pays for a full scan on first load. Default to a narrow recent window and let people widen it deliberately.

## Reduce the marks in the view

A “mark” is one data point drawn on screen — a bar, a dot, a cell. Rendering cost scales with mark count, and past a few thousand marks the client is the bottleneck, not the data source.

- Load top N and let the user drill for the rest.
- Paginate tables. Nobody scrolls 50,000 rows.
- Watch the cardinality of whatever is on the axes. A bar chart grouped by a unique ID is not a chart, it is a table with extra steps. Group by a dimension with tens of values, not thousands.
- Aggregate before plotting. If the chart shows a monthly trend, aggregate to month upstream instead of sending daily rows and rolling them up in the view.

The cardinality point is the one people miss. Filtering rows helps, but if the grouping dimension is high-cardinality the mark count stays high regardless.

## Prefer cheap types

Comparisons on integers and booleans are much cheaper than on strings, and they compress better in columnar storage.

- Continuous date filters (a range: from x to y) over discrete lists of date strings. A range is a scan boundary; a list of strings is N equality checks and usually defeats partition pruning.
- Booleans over status strings when the flag is genuinely binary.
- Integer keys for joins and filters, with the label joined on only for display.

The general rule: filter on the number, display the string.

## Materialize your tables

Views are fine for development and for thin logic on top of an already-small table. In a real company the data is not small, and a dashboard built on a stack of views re-executes that whole stack on every interaction — every filter change, every page load, every user.

Materialize the table that backs the dashboard. Let the dashboard hit one pre-aggregated table, and move the joins and window functions into a scheduled build. The dashboard query should be close to reading one table with a date filter.

This trades freshness for speed, which is almost always the right trade for BI — stakeholders making weekly decisions do not need second-level freshness. Ask what refresh interval the decision actually requires before assuming real-time.

## Cache

Once the query is as small as it will get, cache the result so repeated views do not re-run it. Whatever the tool’s caching mechanism is, match its expiry to the upstream refresh schedule — expiring sooner than the data changes only buys re-queries for identical results.

------------------------------------------------------------------------

Last modified: 2026-09-03

Back to top
