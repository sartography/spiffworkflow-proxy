"""Simple Example Command."""
import json
from decimal import Decimal


class CombineStrings:
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

    def execute(self, config, task_data):
        """Execute."""
        # Get the service resource.
        return self.arg1 + self.arg2
