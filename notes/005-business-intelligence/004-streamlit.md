---
title: Streamlit
icon: devicon:streamlit
---
## Installation

## Setup

## Authentication (RBAC)

## Multi-pages

There are two generations, and they do not coexist quietly.

- **v1 (2022)** — convention based. Files in a `pages/` directory next to the entrypoint become the sidebar automatically. No code, and no way to filter the list.
- **v2 (1.36+)** — `st.Page` + `st.navigation`. You declare the pages, so you can filter them by role. This is the one to use.

### Never name the directory `pages/`

If a directory called `pages` sits next to the entrypoint, Streamlit decides the app is v1 — and it decides **before your entrypoint runs**:

```python
# streamlit/runtime/scriptrunner/script_runner.py
if PagesManager.uses_pages_directory:   # True iff <entrypoint dir>/pages exists
    _mpa_v1(self._main_script_path)     # globs pages/*.py, runs the REQUESTED page
else:
    exec(code, module.__dict__)         # your entrypoint
```

`uses_pages_directory` is a **class attribute computed once per process** (`runtime/pages_manager.py`) and only cleared by `st.navigation` — which your entrypoint never reaches on that first run. So on the first script run of a fresh process, a deep link runs `pages/<name>.py` **instead of** the entrypoint.

Everything the entrypoint does is skipped: auth gates, monkey-patches, the nav itself. If access control lives only in which pages you pass to `st.navigation`, that is an auth bypass on any cold process — and containers give you a cold process on every deploy.

It self-heals once any run reaches `st.navigation`, which makes it maddening to reproduce. Two things hide it:

- A reload is not enough. The flag is per **process** — you must restart the server.
- The URL must be a deep link. Hitting `/` runs the entrypoint (it is the default page) and looks completely normal.

Reproduce it in 20 seconds: drop a `pages/probe.py` that writes a marker, cold-start, open `/probe`. The marker renders with no login.

**Fixes, in order of preference:**

1. **Name the directory something else** — `dashboards/`, `views/`. `_mpa_v1` hardcodes the string `"pages"` in exactly two places, so any other name makes the legacy path unreachable. One rename, done.
2. Move the entrypoint so `<entrypoint dir>/pages` does not exist (entrypoint at repo root, pages under the package).
3. Keep `pages/` but put every page one level down in subdirectories — `_mpa_v1` globs `pages/*.py` non-recursively, so nesting keeps it empty. This is what a real production app I read does.

Whatever you pick, **also gate each page itself**. A nav filter is not an access check — nothing stops a page being reached another way. One guard helper — login, domain, and per-page role check — as the first statement of every page, and a test that asserts every page calls it with its own filename.

`client.showSidebarNavigation = false` does **not** help. Despite what the config docstring says, `commands/navigation.py` applies it to any sidebar position, so it hides your real v2 nav too.

## `st.stop()` is not an early return

Every tab in a multi-tab page is rendered on every script run — the tab widget
only chooses what is *visible*. So a guard that bails out of one tab with
`st.stop()` halts the whole run and leaves every later tab blank.

There is no early return out of a `with tab:` block either, since it is not a
function. The guard has to be an `if`/`else` around the tab body:

```python
with tab:
    ...prepare data...
    if frame.is_empty():
        st.info("...")
    else:
        ...the rest of the tab...
```

Verify with `git diff -w` — if the only real change is the guard, the rest of
the diff is the re-indentation and reads as noise.

## Filters & Components

All filters and components that I use will be native Streamlit components or from the bp-streamlit-tools package.
This package is something that I will build myself as a side project, but that I could use at work too as I develop dashboards solo for now. I might merge my dashboards with the IT team at some point (I'm in the Big Data Team) though.

> [!note]
> This is no right or wrong when it comes to UI/UX and the following components that I use for the filters is a convention for myself, but it would be a good place to start. Without a convention or system to structure your filters, a dashboard can become messy real quick.
#### Swapping Data (Radio)

When swapping data use a radio. By this it means when you have to change the criteria. For example, making a big change in how your data is queried like switching the date column. Imagine that normally you display your data in date_utc, but then you have Korean users and make it date_kst. That's swapping the column that was part of the grain. Also, if this is a filter that you would like to put at the top of the dashboard like a global filter, or in a side by for a vertical stack

#### Choosing from an Enum (Segmented Control)

Use a segmented control when you want to toggle between views like timeframes or metrics. This is a horizontal layout so keep that in mind. Also, this works clean with short texts or emojis.




## Optimizations

@st.cache_data
@st.cache_resource
@st.fragment (parallel=True)
st.form
st.session_state + st.empty()

### Do not copy a cached frame into session_state

A pattern that looks like caching and is actually the opposite:

```python
@st.cache_data
def load(): ...

if "data" not in st.session_state:          # DON'T
    st.session_state.data = load()
df = st.session_state.data.copy()
```

`st.cache_data` is already a cache, and it is **global** (`scope="global"` by default): one copy shared by everyone. `session_state` is **per session**, so this makes a private full copy of the frame for every logged-in person, on top of the shared one. With a 3 GB frame and four people, that is 12 GB of duplicates.

It also breaks refresh. `st.cache_data.clear()` cannot touch anyone else's `session_state`, and `session_state` has no TTL — so other users stay pinned to old data indefinitely, with nothing on screen saying so.

Just call the cached function. `cache_data` returns a fresh copy per call, so mutation safety is unchanged:

```python
df = load()
```

### A refresh button is global, and silent for everyone else

`st.cache_data.clear()` wipes the cache for **all** users, not just the presser. But Streamlit never pushes to a session — other people see new data on their *next interaction*, not immediately. Worth knowing before you promise "refresh updates everyone".

Clear `cache_resource` too if a database connection is cached there; the same button then doubles as auth-token recovery. Do **not** clear `session_state` — that throws away the user's filters.


## Conventions

- When making dynamic titles, add the variables (filters) as badges. (e.g., date/range, metrics, etc.)
- When changing the x-axis labels like dates into string format, check that the lexicographic sort equals chronological order. The formats should be YYYY, YYYY-QQ, YYYY-MM, YYYY-MM-DD (ISO 8601).
-

***

[Last modified: 2026-09-03]{.note-modified}
