"""
Connector for your drd source (Metabase, Signoz, etc.).

Uncomment and edit the example below for your tool. You need:
- MCP_CONNECTOR_NAME, MCP_CONNECTOR_ID (same as in your manager).
- build_<source>_connector(url, api_key) that returns a ConnectorProto.

Ensure the toolkit path is set (e.g. in server.py) before importing from core.*
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Example: Metabase connector. Uncomment and change for your source (e.g. Signoz).
# ---------------------------------------------------------------------------
# import os
# import sys
#
# def _ensure_toolkit_path() -> None:
#     if "core" in sys.modules:
#         return
#     try:
#         import core.protos.base_pb2  # noqa: F401
#         return
#     except ImportError:
#         pass
#     _this_dir = os.path.dirname(os.path.abspath(__file__))
#     _pkg = os.path.dirname(_this_dir)
#     _projects = os.path.dirname(_pkg)
#     _drd_pkg = os.path.join(_projects, "drdroid-debug-toolkit", "drdroid_debug_toolkit")
#     if os.path.isdir(_drd_pkg) and _drd_pkg not in sys.path:
#         sys.path.insert(0, _drd_pkg)
#
# _ensure_toolkit_path()
#
# from google.protobuf.wrappers_pb2 import StringValue, UInt64Value
# from core.protos.base_pb2 import Source, SourceKeyType
# from core.protos.connectors.connector_pb2 import Connector as ConnectorProto, ConnectorKey
#
#
# MCP_CONNECTOR_NAME = "mcp"
# MCP_CONNECTOR_ID = 0
#
#
# def build_metabase_connector(metabase_url: str, metabase_api_key: str) -> ConnectorProto:
#     """Build a ConnectorProto for Metabase from URL and API key."""
#     return ConnectorProto(
#         type=Source.METABASE,
#         name=StringValue(value=MCP_CONNECTOR_NAME),
#         id=UInt64Value(value=MCP_CONNECTOR_ID),
#         keys=[
#             ConnectorKey(
#                 key_type=SourceKeyType.METABASE_URL,
#                 key=StringValue(value=metabase_url.rstrip("/")),
#             ),
#             ConnectorKey(
#                 key_type=SourceKeyType.METABASE_API_KEY,
#                 key=StringValue(value=metabase_api_key),
#             ),
#         ],
#     )
# ---------------------------------------------------------------------------
# For another source (e.g. Signoz): use that source's SourceKeyType and keys.
# ---------------------------------------------------------------------------
