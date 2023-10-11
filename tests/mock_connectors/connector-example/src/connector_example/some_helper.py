class SomeHelper:
    """SomeHelper class, should not be returned as a command or auth."""
    def _execute(self, param_a: str, param_b: str) -> None:
        pass
