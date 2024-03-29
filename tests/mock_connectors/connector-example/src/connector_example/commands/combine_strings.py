"""Simple Example Command."""
from typing import Any

from spiffworkflow_connector_command.command_interface import CommandResultDictV2
from spiffworkflow_connector_command.command_interface import ConnectorCommand
from spiffworkflow_connector_command.command_interface import ConnectorProxyResponseDict


class CombineStrings(ConnectorCommand):
    """Takes two strings, combines them together, and returns a single string! AMAZIN!."""

    def __init__(
        self, arg1: str, arg2: str
    ):
        """
        :param arg1: The First Argument
        :param arg2: The Second Argument
        :return:  Nothing.  This is just the intialization.  We'll do the hard stuff in execute.
        """
        self.arg1 = arg1
        self.arg2 = arg2

    def execute(self, config: Any, task_data: Any) -> CommandResultDictV2:
        """Execute."""

        return_response: ConnectorProxyResponseDict = {
            "command_response": {"example_response": "whatever you want", "arg1": self.arg1, "arg2": self.arg2},
            "spiff__logs": [],
            "error": None,
        }
        result: CommandResultDictV2 = {
            "response": return_response,
            "status": 200,
            "mimetype": "application/json",
        }

        return result

