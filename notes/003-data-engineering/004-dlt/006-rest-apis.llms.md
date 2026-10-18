# REST APIs

dlt gives you two ways to pull a REST API. **Default to the low-level one.**

|  | Low-level | Declarative |
|----|----|----|
| What you write | `RESTClient` + `@dlt.resource` / `@dlt.transformer` | one big `rest_api_source(config)` dict |
| Control | plain Python — branch, sleep, inspect, re-stamp rows | whatever the config schema exposes |
| Debugging | a normal call stack | config→object translation in between |

The declarative `rest_api` source reads nicely in a demo and fights you the moment the API misbehaves. Real APIs misbehave: they return HTTP 200 with an error envelope, echo params back in a different type than you sent, need a delay between calls, or need one field re-stamped after the response lands. Every one of those is two lines in a resource body and a config-schema hunt in the declarative version. See [Scaling: catalog + builder loop](../../../notes/003-data-engineering/004-dlt/002-conventions.llms.md#scaling-catalog-builder-loop) — an endpoint catalog plus a builder function gets you the same one-line-per-endpoint economy without giving up Python.

## Auth is not parameters

Two different things, easy to conflate:

- **Auth** — shared by every request, so it lives on the client once.
- **Query params** (`ocid`, `date`, `world_name`, …) — per-request, so they live in the resource that makes the call.

``` numberSource
client = RESTClient(
    base_url=BASE_URL,
    auth=APIKeyAuth(name="x-api-key", api_key=api_key, location="header"),
)
```

A new query param never touches `auth`.

## Fan-out: a param that comes from another endpoint

The common shape: a list endpoint returns ids, then a detail endpoint must be called once per id. Model it as `@dlt.resource` (parent) + `@dlt.transformer` (child).

``` numberSource
@dlt.resource(name="character_list", write_disposition="replace")
def character_list():
    yield client.get(path=ENDPOINTS["character_list"]["path"]).json()

# selected=False: this is a fan-out helper, not a table of its own.
@dlt.transformer(data_from=character_list, selected=False)
def filter_characters(character_list):
    for account in character_list["account_list"]:
        for character in account["character_list"]:
            yield character

@dlt.transformer(data_from=filter_characters, name="character_basic")
def character_basic(character):
    identity = {"ocid": character["ocid"]}
    yield {**identity, **client.get(path=..., params=identity).json()}
```

Points worth keeping:

- **Storage and extraction are separate.** The parent resource stores the raw payload verbatim; the intermediate transformer reshapes the stream *in memory* to one record per child. Without the split, drilling into the nested list to get the ids would also change what the parent’s table stores. `selected=False` is what keeps the helper out of the destination.
- **Stamp the query params onto each row.** The response usually does not echo what you asked for. Without the stamp, a detail row is unattributable — you cannot tell which id or date produced it, and it cannot be a merge key.
- **Re-stamp after merging the response.** If the API echoes a param back in a different shape (a KST timestamp where you sent a `YYYY-MM-DD`), dlt normalizes *its* value, not yours, and the merge key drifts. `row.update(identity)` after the spread wins, and keeps the identity columns at the front of the row.
- **HTTP 200 is not success.** Check for an error envelope and `return` early, otherwise a maintenance window writes a table of all-null rows.
- **Rate limits are a `time.sleep` at the top of the transformer body.** One line, no paginator subclass.

Write disposition follows whether the endpoint is dated:

| Endpoint shape | Disposition | Key |
|----|----|----|
| date-scoped (keeps history) | `merge` | `[id, date]` — re-running a date updates in place, new dates accumulate |
| current-state snapshot | `replace` | — |

## Appendix — declarative `rest_api` config

Kept for the times you read someone else’s config, or an API is boring enough to deserve one.

> **Source of truth:** `<venv>/lib/python*/site-packages/dlt/sources/rest_api/typing.py`. The TypedDicts there always win over this page. Written against dlt 1.28.2.

``` numberSource
config = {
    "client": {...},              # required
    "resources": [...],           # required
    "resource_defaults": {...},   # merged into every resource — use for shared hints
}
```

**`client`:** `base_url` (req), `headers`, `auth`, `paginator` (default `"auto"`), `session`.

**`resources[]`** — a bare string (`"posts"`, name==path==table) or a dict: `name`, `endpoint`, `include_from_parent`, `max_table_nesting`, `selected`, `parallelized`, `processing_steps`, plus any `dlt.resource` hint (`write_disposition`, `primary_key`, `merge_key`, `columns`, `table_name`, `schema_contract`, `parent`).

**`endpoint`:** `path` (supports `{resources.<name>.<field>}` templating), `method`, `params`, `json`, `data`, `paginator`, `data_selector` (JSONPath), `response_actions`, `incremental`, `auth`, `headers`.

**`auth`** — pick with `type`:

| `type` | Keys |
|----|----|
| `bearer` | `token` |
| `api_key` | `name`, `api_key`, `location` (`header`\|`query`\|`cookie`) |
| `http_basic` | `username`, `password` |
| `oauth2_client_credentials` | `access_token_url`, `client_id`, `client_secret`, `access_token_request_data`, `default_token_expiration` |

**`paginator`** — `auto` (default) · `single_page` · `json_link` (`next_url_path`) · `header_link` (`links_next_key`) · `header_cursor` (`cursor_key`, `cursor_param`) · `cursor` (`cursor_path`, `cursor_param`, `has_more_path`) · `offset` (`limit`, `offset_param`, `limit_param`, `total_path`, `maximum_offset`, `stop_after_empty_page`) · `page_number` (`page_param`, `base_page`, `total_path`, `maximum_page`, `stop_after_empty_page`, `has_more_path`).

**`incremental`:** `cursor_path`, `start_param`, `end_param`, `initial_value`, `convert` (+ all standard `IncrementalArgs`).

**`processing_steps`** — in-flight transforms: `filter` `(row) -> bool`, `map` `(row) -> row`, `yield_map` `(row) -> Iterator[row]`.

**Fan-out, declaratively** — the equivalent of the transformer chain above is a `resolve` param plus a `data_selector` on the parent:

``` numberSource
{
    "name": "character_list",
    "endpoint": {
        "path": CHARACTER_LIST,
        # resolve reads a TOP-LEVEL field of each record the parent yields,
        # so the parent must yield character-level records for `ocid` to be visible.
        "data_selector": "account_list[*].character_list[*]",
    },
},
{
    "name": "character_basic",
    "endpoint": {
        "path": CHARACTER_BASIC,
        "params": {"ocid": {"type": "resolve", "resource": "character_list", "field": "ocid"}},
    },
},
```

The tension the transformer chain avoids: that `data_selector` also changes what `character_list` *stores* — character rows instead of the raw account payload. You cannot keep the raw payload and fan out from the same resource.

## Docs

Task-oriented pages (read via `defuddle parse <url> --md`):

- `dlthub.com/docs/general-usage/http/rest-client`
- `dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api/basic` and `.../advanced`
- `dlthub.com/docs/general-usage/incremental-loading`

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
