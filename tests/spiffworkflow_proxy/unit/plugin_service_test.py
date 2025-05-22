

from spiffworkflow_proxy.plugin_service import PluginService

"""Connector_example is a Dev dependency and should be picked
up by these tests. """

def test_find_dependencies() -> None:
    assert(list(PluginService.available_plugins().keys()) == ['connector_example'])


def test_display_name() -> None:
    assert(PluginService.plugin_display_name('connector_example') == "example")


def test_plugin_for_display_name() -> None:
    assert(PluginService.plugin_name_from_display_name('example') == "connector_example")


def test_available_commands_by_plugin() -> None:
    commands = PluginService.available_commands_by_plugin()
    assert(list(commands['connector_example'].keys()) == ['CombineStrings'])

def test_describe_target() -> None:
    commands = PluginService.available_commands_by_plugin()
    combine_strings = commands["connector_example"]["CombineStrings"]
    description = PluginService.describe_target(
        "connector_example", "CombineStrings", combine_strings
    )
    assert description == {
        "id": "example/CombineStrings",
        "parameters": [
            {
                "id": "arg1",
                "required": True,
                "type": "str",
            },
            {
                "id": "arg2",
                "required": True,
                "type": "str",
            }
        ]
    }