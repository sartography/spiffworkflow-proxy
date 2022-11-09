import pkgutil
import sys

from flask import Flask

from spiffworkflow_proxy.plugin_service import PluginService

"""Connector_example is a Dev dependency and should be picked
up by these tests. """

def test_find_dependencies():
    assert(list(PluginService.available_plugins().keys()) == ['connector_example'])


def test_display_name():
    assert(PluginService.plugin_display_name('connector_example') == "example")


def test_plugin_for_display_name():
    assert(PluginService.plugin_name_from_display_name('example') == "connector_example")


def test_available_commands_by_plugin():
    commands = PluginService.available_commands_by_plugin()
    assert(list(commands['connector_example'].keys()) == ['CombineStrings'])
    print(commands)

