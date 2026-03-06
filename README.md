# MCP Server Template (FastMCP + drd toolkit)

Minimal template for building Python MCP servers with the official `mcp` SDK (FastMCP) and [drdroid-debug-toolkit](https://github.com/DrDroidLab/drdroid-debug-toolkit). Use it to spin up a new MCP server per tool (Metabase, Signoz, Grafana, etc.) with minimal edits.

---

## Create a new MCP server from this template

### 1. Create a new repo from the template

- **On GitHub:** Open this repo → click **Use this template** → **Create a new repository**. Name it e.g. `metabase-mcp-server` or `signoz-mcp-server`. Clone your new repo locally.
- **Or** clone this template and re-init as your own repo:

  ```bash
  git clone <this-template-url> my-mcp-server && cd my-mcp-server
  rm -rf .git && git init && git add . && git commit -m "Initial commit from mcp-server-template"
  ```

### 2. Rename the package and entrypoint

- Rename the package folder: `src/mcp_template/` → `src/<name>_mcp_server/` (e.g. `src/metabase_mcp_server/`).
- In **`pyproject.toml`**: set `name = "metabase-mcp-server"` (or your tool name), and set `project.scripts` to your package’s `server:main`, e.g. `metabase-mcp-server = "metabase_mcp_server.server:main"`.
- In **all Python files** under `src/<name>_mcp_server/`: replace `mcp_template` with your package name (e.g. `metabase_mcp_server`).

### 3. Add the drd toolkit and Django

- In **`pyproject.toml`** (or **`requirements.txt`**), add:
  - `drdroid-debug-toolkit` (e.g. `git+https://github.com/DrDroidLab/drdroid-debug-toolkit.git@master`)
  - `django` (required by the toolkit at import time).
- Install: `uv sync` or `pip install -e ".[dev]"`.

### 4. Edit the connector (`connector.py`)

- **File:** `src/<name>_mcp_server/connector.py`
- **What to do:** Uncomment the Metabase example block. For **Metabase** keep it as-is; for **another source** (e.g. Signoz) change `Source`, `SourceKeyType`, and the `keys` in `build_*_connector` to match that source’s proto. Ensure `MCP_CONNECTOR_NAME` and `MCP_CONNECTOR_ID` match what your manager will use.

### 5. Edit the provider and manager (`example_source_provider.py`)

- **File:** `src/<name>_mcp_server/example_source_provider.py`
- **What to do:** Uncomment the full example block.
  - **Manager:** Point to your drd `SourceManager` (e.g. `MetabaseSourceManager` or `SignozSourceManager`) and your `build_*_connector` from `connector.py`.
  - **Provider:** In `super().__init__(...)` set:
    - **`Source.METABASE`** (or `Source.SIGNOZ`, etc.) to your drd source enum.
    - **`prefix="metabase"`** (or `"signoz"`, etc.) to your tool name; this becomes the MCP tool name prefix (e.g. `metabase_list_databases`).
- Rename the class if you like (e.g. `ExampleToolProvider` → `MetabaseToolProvider`) and update imports in `server.py`.

### 6. Wire the provider and config in `server.py`

- **File:** `src/<name>_mcp_server/server.py`
- **What to do:**
  1. At the top (before other local imports), add the **toolkit path** setup so `core` is importable (see [metabase-mcp-server](https://github.com/DrDroidLab/metabase-mcp-server) `server.py` for the block that inserts `drdroid_debug_toolkit` into `sys.path`).
  2. Load backend config (URL, API key) from env or `config.py`.
  3. Create your provider and set it: `_provider = MetabaseToolProvider(url, api_key)` (or `set_tool_provider(...)`), so it runs before `main()`.

### 7. Config and env

- Add backend URL and API key to **`config.py`** (e.g. `SERVICE_URL`, `SERVICE_API_KEY`) or use env vars only.
- Copy **`.env.example`** to **`.env`** and set the variables. The server and tests read from the repo root.

### 8. Start the server

From the repo root (where `pyproject.toml` and `src/` are):

```bash
uv venv .venv && source .venv/bin/activate   # or: python -m venv .venv && source .venv/bin/activate
uv sync   # or: pip install -e ".[dev]"
uv run metabase-mcp-server   # or your script name from pyproject.toml
```

- **Stdio (Cursor / Claude):** run the above; set your MCP client command to `path/to/venv/bin/python -m metabase_mcp_server.server` (or your package name) with `cwd` = repo root.
- **HTTP:** `MCP_TRANSPORT=streamable-http uv run metabase-mcp-server` (default port 8000; override with `MCP_PORT`).

If you see *"No tool provider configured"*, finish steps 4–6 (connector, provider, and wiring in `server.py`).

---

## What this template gives you

- **FastMCP server** (`server.py`): Exits with a clear message until a **ToolProvider** is set. Once set, exposes `ping`, `echo`, `list_tools`, and `execute_tool` (which delegate to your provider).
- **Config** (`config.py`): env-based `ServerConfig` and `BackendConfig`.
- **Tool abstraction** (`tool_provider.py`): `ToolDefinition`, `ToolProvider` protocol, and `InMemoryToolProvider`.
- **Connector example** (`connector.py`): Commented-out Metabase connector example. Uncomment and edit for your source (e.g. Signoz)—change `Source`, `SourceKeyType`, and keys to match your drd source.
- **Example source provider** (`example_source_provider.py`): Commented-out provider and manager (Metabase). Uncomment and change **source enum** (e.g. `Source.METABASE` → `Source.SIGNOZ`) and **prefix** (e.g. `"metabase"` → `"signoz"`) for your tool; then set the provider in `server.py` so the server runs.
- **DRD extractor** (`drd_extractor.py`): `extract_tools_from_source_manager(source_manager, prefix)` to build tool definitions from a drd `SourceManager`.
- **Generic drd provider** (`drd_source_provider.py`): `DrdSourceToolProvider(manager, source_enum, connector_name, connector_id, prefix)`—used by the example provider; no need to duplicate task or execution logic.

## What changes you need to set up tools (MCP-style)

To expose **backend tools** (e.g. from a drd SourceManager) as MCP tools:

1. **Implement a `ToolProvider`** that:
   - `list_tools()` → list of `ToolDefinition` (name, description, `parameters_schema`).
   - `call_tool(name, arguments)` → run the backend operation and return a JSON-serializable result.

2. **Use the generic extractor** (if using drd): call `extract_tools_from_source_manager(manager, prefix="metabase")` to get `ToolDefinition`s from `task_type_callable_map` and `form_fields`. Implement `call_tool` by building the task/connector and calling the source manager’s `execute_task` (or equivalent).

3. **Wire the provider in `server.py`**: before `main()`, call `set_tool_provider(your_provider)`. The template already registers `list_tools` and `execute_tool`; they will then expose your backend’s tools. MCP clients can call `list_tools` to discover names/schemas, then `execute_tool(name, arguments)` to run them.

4. **(Optional)** In a concrete repo (e.g. Metabase), add config (env or YAML) for the backend (URL, API key, etc.) and build the connector/credentials from that so `call_tool` can run without a DB.

See the **metabase-mcp-server** repo (e.g. `../metabase-mcp-server` or your fork) for a full example using `MetabaseSourceManager`.

## Running the template server

**The template does not run until you configure a provider.** Running `uv run mcp-template-server` before that will exit with instructions.

1. Uncomment and edit **`connector.py`** for your source (Metabase, Signoz, etc.).
2. Uncomment and edit **`example_source_provider.py`**: set the source enum and `prefix` for your tool name.
3. In **`server.py`**, set up the toolkit path (if needed), then create your provider and assign it to `_provider` (or call `set_tool_provider(provider)`).
4. Add backend config (e.g. URL, API key) to `config.py` or env, and pass it when creating the provider.

Then:

```bash
cd mcp-server-template
uv venv .venv && source .venv/bin/activate
uv sync
uv run mcp-template-server
```

- **HTTP/streamable** (e.g. MCP Inspector): `MCP_TRANSPORT=streamable-http uv run mcp-template-server`
- Override port with `MCP_PORT`, name with `MCP_SERVER_NAME`.

## Testing

```bash
# Install pytest if needed (e.g. add [project.optional-dependencies] dev = ["pytest"] in pyproject.toml, then uv sync --extra dev)
uv run pytest
```

`tests/conftest.py` adds `src` to the path and loads `.env` from the project root so tests see env-based credentials when present. For backend credential or integration tests (e.g. connection check, calling a real tool), use the pattern from **metabase-mcp-server**: skip when credentials or optional deps are missing, use lazy imports for heavy backends, and run pytest with the project venv so all dependencies are available.

## How to create a new MCP server (summary)

See **[Create a new MCP server from this template](#create-a-new-mcp-server-from-this-template)** at the top for the full step-by-step. In short: use the template → rename package and entrypoint → add toolkit + Django → uncomment and edit `connector.py` and `example_source_provider.py` (source enum + prefix) → wire provider and config in `server.py` → set env → run. One repo per integration (Metabase, Signoz, Grafana, etc.) for discoverability and per-tool config.

### 1. Create the new repo

- Copy this template into a new directory, e.g. `metabase-mcp-server`, or use “Use this template” on GitHub.
- Optionally create the repo on GitHub first and clone it, then copy template files into it.

(Full steps are in the section above; the bullets below are redundant and can be removed.)

### 2. Rename the package

- Rename `src/mcp_template/` to `src/<service>_mcp_server/` (e.g. `metabase_mcp_server`).
- In `pyproject.toml`: set `name = "metabase-mcp-server"`, update `project.scripts` to point to the new package’s `server:main`.
- In all Python files: replace `mcp_template` imports with the new package name.

### 3. Add backend config and provider

- In the new package, add config (env or YAML) for the service (e.g. `METABASE_URL`, `METABASE_API_KEY`).
- **Using the generic provider (easiest):** Add a manager subclass (overrides `get_active_connectors` to return your connector) and a connector module. Then create the provider with `DrdSourceToolProvider(manager, Source.METABASE, connector_name, connector_id, prefix="metabase")`. See **metabase-mcp-server**: `metabase_provider.py` is a thin wrapper that only passes manager, `Source.METABASE`, and prefix; you can do the same for Signoz/Grafana by changing the source enum and prefix.
- **Or** implement a custom `ToolProvider` (e.g. use `extract_tools_from_source_manager` and implement `call_tool` yourself).
- In `server.py`, instantiate the provider and call `set_tool_provider(provider)` (or register tools and set `_provider`) before `main()`.

### 4. Dependencies

- Add `drdroid-debug-toolkit` (or your backend SDK) to `pyproject.toml`. If the toolkit is local or from a private repo, use a path or Git dependency.

### 5. Tests and deployment

- Add tests that call `list_tools` and `execute_tool` (with mocks or a test instance).
- Add a `.gitignore` (see this repo’s root), `.env.example`, and a README with tool list, env vars, and run/deploy instructions.
- Add Dockerfile/docker-compose if you want to run the server in a container.

### 6. README for the new repo

Include:

- What the server does and which tools it exposes.
- **Requirements**: Python version, env vars (with `.env.example`).
- **Install and run**: `uv sync`, `uv run <entrypoint>`, and how to choose stdio vs HTTP.
- **MCP client setup**: example config for Cursor/Claude (command + args for stdio, or URL for HTTP).
- **Creating other MCP servers**: short note that this repo was created from `mcp-server-template` and link back to the template.

## Files and layout

```txt
mcp-server-template/
├── .gitignore
├── README.md
├── pyproject.toml
├── src/
│   └── mcp_template/
│       ├── __init__.py
│       ├── config.py
│       ├── connector.py              # Uncomment and edit for your source
│       ├── drd_extractor.py
│       ├── drd_source_provider.py    # Generic provider (no edits needed)
│       ├── example_source_provider.py  # Uncomment and edit source enum + prefix
│       ├── server.py                 # Add toolkit path + set _provider
│       └── tool_provider.py
└── tests/
    └── test_basic_server.py
```

- **`.gitignore`**: ignores `__pycache__`, `.venv`, `.env`, `config.yaml`, IDE/cache dirs, build artifacts. Keep `.env.example` if you add one.
- **Config**: prefer env vars for deployment; optional `config.yaml` for local overrides (and ignore `config.yaml` in git).

## Example: Metabase MCP server

The **[metabase-mcp-server](https://github.com/DrDroidLab/metabase-mcp-server)** repo is an example created from this template. It:

- Uses `MetabaseSourceManager` from `drdroid-debug-toolkit`.
- Builds a connector from `METABASE_URL` and `METABASE_API_KEY`.
- Exposes all Metabase tasks (alerts, pulses, dashboards, questions, databases, collections, search) via `list_tools` and `execute_tool`.

Clone or copy that repo to see a full setup; use the same pattern for other tools (SigNoz, Grafana, etc.).
