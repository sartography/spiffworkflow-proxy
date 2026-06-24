"""Async command used by connector proxy tests."""
from typing import Any

from spiffworkflow_connector_command.command_interface import ConnectorProxyResponseDict


class AsyncBodyStatus:
    """Returns a body-level http_status from execute_async."""

    def __init__(self, upstream_status: int = 500):
        self.upstream_status = upstream_status

    def execute(self, _config: Any, _task_data: Any) -> ConnectorProxyResponseDict:
        return {
            "command_response_version": 2,
            "command_response": {
                "body": {"started": False},
                "mimetype": "application/json",
                "http_status": self.upstream_status,
            },
            "error": {
                "error_code": "AsyncStartRejected",
                "message": "The async command rejected the start request.",
            },
            "spiff__logs": [],
        }

    def execute_async(self, _config: Any, _task_data: Any, callback_url: str) -> ConnectorProxyResponseDict:
        return self.execute(_config, {"callback_url": callback_url})
