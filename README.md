# MCP Server Template (FastMCP + optional drd toolkit)

Minimal template for building Python MCP servers with the official `mcp` SDK (FastMCP). Use it to spin up new MCP servers quickly (one repo per tool/integration) with optional `drdroid-debug-toolkit` integration.

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

## How to create a new MCP server for each tool

Use this template to create **one repo per integration** (Metabase, SigNoz, Grafana, etc.) for discoverability and per-tool config.

### 1. Create the new repo

- Copy this template into a new directory, e.g. `metabase-mcp-server`, or use “Use this template” on GitHub.
- Optionally create the repo on GitHub first and clone it, then copy template files into it.

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

```
mcp-server-template/
├── .gitignore
├── README.md
├── pyproject.toml
├── src/
│   └── mcp_template/
│       ├── __init__.py
│       ├── config.py
│       ├── drd_extractor.py
│       ├── server.py
│       └── tool_provider.py
└── tests/
    └── test_basic_server.py
```

- **`.gitignore`**: ignores `__pycache__`, `.venv`, `.env`, `config.yaml`, IDE/cache dirs, build artifacts. Keep `.env.example` if you add one.
- **Config**: prefer env vars for deployment; optional `config.yaml` for local overrides (and ignore `config.yaml` in git).

## Example: Metabase MCP server

The **[metabase-mcp-server](https://github.com/your-org/metabase-mcp-server)** repo is an example created from this template. It:

- Uses `MetabaseSourceManager` from `drdroid-debug-toolkit`.
- Builds a connector from `METABASE_URL` and `METABASE_API_KEY`.
- Exposes all Metabase tasks (alerts, pulses, dashboards, questions, databases, collections, search) via `list_tools` and `execute_tool`.

Clone or copy that repo to see a full setup; use the same pattern for other tools (SigNoz, Grafana, etc.).
