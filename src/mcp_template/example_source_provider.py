"""
Example source provider using DrdSourceToolProvider.

Uncomment and edit for your tool: set the source enum (e.g. Source.METABASE,
Source.SIGNOZ) and prefix (e.g. "metabase", "signoz"). Add a manager subclass
that overrides get_active_connectors to return your connector (see manager example below).

Then in server.py: set up toolkit path, load config, create this provider,
and call set_tool_provider(provider) before main().
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Example: Metabase. Uncomment and change source_enum + prefix for your tool.
# ---------------------------------------------------------------------------
# from core.protos.base_pb2 import Source
# from core.integrations.source_managers.metabase_source_manager import MetabaseSourceManager
# from core.protos.connectors.connector_pb2 import Connector as ConnectorProto
#
# from .connector import MCP_CONNECTOR_ID, MCP_CONNECTOR_NAME, build_metabase_connector
# from .drd_source_provider import DrdSourceToolProvider
#
#
# class ExampleManager(MetabaseSourceManager):
#     """Manager that returns our connector from get_active_connectors."""
#
#     def __init__(self, url: str, api_key: str) -> None:
#         super().__init__()
#         self._url = url.rstrip("/")
#         self._api_key = api_key
#
#     def get_active_connectors(
#         self,
#         connector_name: str,
#         connector_id: int,
#         loaded_connections: dict | None = None,
#     ) -> ConnectorProto:
#         if loaded_connections is None and connector_name == MCP_CONNECTOR_NAME and connector_id == MCP_CONNECTOR_ID:
#             return build_metabase_connector(self._url, self._api_key)
#         return super().get_active_connectors(connector_name, connector_id, loaded_connections)
#
#
# class ExampleToolProvider(DrdSourceToolProvider):
#     """Exposes your source's tasks as MCP tools. Change prefix to match your tool (e.g. signoz)."""
#
#     def __init__(self, url: str, api_key: str) -> None:
#         manager = ExampleManager(url, api_key)
#         super().__init__(
#             manager,
#             Source.METABASE,   # <-- change for your source: Source.SIGNOZ, etc.
#             connector_name=MCP_CONNECTOR_NAME,
#             connector_id=MCP_CONNECTOR_ID,
#             prefix="metabase",  # <-- change for your tool: "signoz", "grafana", etc.
#         )
# ---------------------------------------------------------------------------
