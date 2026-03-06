# MCP Server Template (FastMCP + optional drd toolkit)

Minimal template for building Python MCP servers with the official `mcp` SDK (FastMCP). Use it to spin up new MCP servers quickly (one repo per tool/integration) with optional `drdroid-debug-toolkit` integration.

## What this template gives you

- **FastMCP server** (`src/mcp_template/server.py`): `ping`, `echo`, plus `list_tools` and `execute_tool` that delegate to an optional **ToolProvider**.
- **Config** (`config.py`): env-based `ServerConfig` and `BackendConfig`.
- **Tool abstraction** (`tool_provider.py`): `ToolDefinition`, `ToolProvider` protocol, and `InMemoryToolProvider`.
- **DRD extractor** (`drd_extractor.py`): `extract_tools_from_source_manager(source_manager, prefix)` to turn a drd `SourceManager` into a list of `ToolDefinition`s (name, description, parameters from form fields).

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

```bash
cd mcp-server-template
uv venv .venv && source .venv/bin/activate
uv sync
```

- **Stdio** (default, for Claude/Cursor):

  ```bash
  uv run mcp-template-server
  ```

- **HTTP/streamable** (e.g. MCP Inspector, port 8000):

  ```bash
  MCP_TRANSPORT=streamable-http uv run mcp-template-server
  ```

Override port with `MCP_PORT`, name with `MCP_SERVER_NAME`. See `config.py` for all env vars.

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
- Implement a `ToolProvider` that:
  - Uses `extract_tools_from_source_manager(SourceManager(), prefix="...")` for `list_tools()` if using drd.
  - Implements `call_tool(name, arguments)` (e.g. build connector from config, build task, call `execute_task` or the API).
- In `server.py`, instantiate the provider and call `set_tool_provider(provider)` before `main()`.

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
