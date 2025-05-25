import importlib
import inspect
import pkgutil
import types
import typing
from collections.abc import Generator
from inspect import Parameter
from typing import Any

from spiffworkflow_connector_command.command_interface import ConnectorCommand


class PluginService:
    """
    This service introspects on the available libraries that are included when this Service is invoked.  It specifically
    seeks out libraries that start with "connector_" and assumes these are the services the connector should provide.
    """

    PLUGIN_PREFIX: str = "connector_"

    @staticmethod
    def plugin_display_name(plugin_name: str) -> str:
        return plugin_name.removeprefix(PluginService.PLUGIN_PREFIX)

    @staticmethod
    def plugin_name_from_display_name(plugin_display_name: str) -> str:
        return PluginService.PLUGIN_PREFIX + plugin_display_name

    @staticmethod
    def available_plugins() -> dict[str, types.ModuleType]:
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules()
            if name.startswith(PluginService.PLUGIN_PREFIX)
        }

    @staticmethod
    def available_auths_by_plugin() -> dict[str, dict[str, type[ConnectorCommand]]]:
        return {
            plugin_name: dict(PluginService.auths_for_plugin(
                    plugin_name, plugin
                ))
            for plugin_name, plugin in PluginService.available_plugins().items()
        }

    @staticmethod
    def available_commands_by_plugin() -> dict[str, dict[str, type[ConnectorCommand]]]:
        return {
            plugin_name: dict(PluginService.commands_for_plugin(
                    plugin_name, plugin
                ))
            for plugin_name, plugin in PluginService.available_plugins().items()
        }

    @staticmethod
    def target_id(plugin_name: str, target_name: str) -> str:
        plugin_display_name = PluginService.plugin_display_name(plugin_name)
        return f"{plugin_display_name}/{target_name}"

    @staticmethod
    def auth_named(plugin_display_name: str, auth_name: str) -> type[ConnectorCommand] | None:
        plugin_name = PluginService.plugin_name_from_display_name(plugin_display_name)
        available_auths_by_plugin = PluginService.available_auths_by_plugin()

        try:
            return available_auths_by_plugin[plugin_name][auth_name]
        except Exception:
            return None

    @staticmethod
    def command_named(plugin_display_name: str, command_name: str) -> type[ConnectorCommand] | None:
        plugin_name = PluginService.plugin_name_from_display_name(plugin_display_name)
        available_commands_by_plugin = PluginService.available_commands_by_plugin()

        try:
            return available_commands_by_plugin[plugin_name][command_name]
        except Exception:
            return None

    @staticmethod
    def modules_for_plugin_in_package(
        plugin: types.ModuleType, package_name: str | None
    ) -> Generator[tuple[str, types.ModuleType], None, None]:
        for finder, name, ispkg in pkgutil.iter_modules(plugin.__path__):
            if ispkg and name == package_name:
                sub_pkg = importlib.import_module(f"{plugin.__name__}.{name}")
                yield from PluginService.modules_for_plugin_in_package(sub_pkg, None)
            elif not package_name:
                spec = finder.find_spec(name)  # type: ignore
                if spec is not None and spec.loader is not None:
                    module = types.ModuleType(spec.name)
                    spec.loader.exec_module(module)
                    yield name, module

    @staticmethod
    def targets_for_plugin(
        plugin_name: str, plugin: types.ModuleType, target_package_name: str
    ) -> Generator[tuple[str, type[ConnectorCommand]], None, None]:
        for module_name, module in PluginService.modules_for_plugin_in_package(
                plugin, target_package_name
        ):
            # for member_name, member in inspect.getmembers(module, inspect.isclass):
            for member_name, member in inspect.getmembers(module, PluginService.is_connector_command):
                if member.__module__ == module_name:
                    yield member_name, member

    @staticmethod
    def auths_for_plugin(plugin_name: str, plugin: types.ModuleType) -> Generator[tuple[str, type[ConnectorCommand]], None, None]:
        yield from PluginService.targets_for_plugin(plugin_name, plugin, "auths")

    @staticmethod
    def commands_for_plugin(
        plugin_name: str, plugin: types.ModuleType
    ) -> Generator[tuple[str, type[ConnectorCommand]], None, None]:
        yield from PluginService.targets_for_plugin(plugin_name, plugin, "commands")

    @staticmethod
    def param_annotation_desc(param: Parameter) -> dict:
        """Parses a callable parameter's type annotation, if any, to form a ParameterDescription."""
        param_id = param.name
        param_type_desc = "any"

        none_type = type(None)
        supported_types = {str, int, bool, none_type}
        unsupported_type_marker = object

        annotation = param.annotation

        if annotation in supported_types:
            annotation_types = {annotation}
        else:
            # an annotation can have more than one type in the case of a union
            # get_args normalizes Union[str, dict] to (str, dict)
            # get_args normalizes Optional[str] to (str, none)
            # all unsupported types are marked so (str, dict) -> (str, unsupported)
            # the absense of a type annotation results in an empty set
            annotation_types = {t if t in supported_types else unsupported_type_marker for t in typing.get_args(annotation)}

        # a parameter is required if it has no default value and none is not in its type set
        param_req = param.default is param.empty and none_type not in annotation_types

        # the none type from a union is used for requiredness, but needs to be discarded
        # to single out the optional type
        annotation_types.discard(none_type)

        # if we have a single supported type use that, else any is the default
        if len(annotation_types) == 1:
            annotation_type = annotation_types.pop()
            if annotation_type in supported_types:
                param_type_desc = annotation_type.__name__

        return {"id": param_id, "type": param_type_desc, "required": param_req}

    @staticmethod
    def param_schema(param: Parameter) -> dict:
        """Parses a callable parameter's type annotation, if any, to form a ParameterSchema."""
        schema = {
            "title": param.name,
        }

        none_type = type(None)
        supported_types_map = {
            str: "string",
            int: "integer",
            float: "number",
            dict: "object",
            list: "array",
            bool: "boolean",
            none_type: "null",
        } # https://json-schema.org/understanding-json-schema/reference/type

        annotation = param.annotation

        if annotation in supported_types_map.keys():
            supported_annotation_types = {annotation}
        else:
            supported_annotation_types = {t for t in typing.get_args(annotation) if t in supported_types_map.keys()}

        # only add the type keyword if at least one type is supported
        if(len(supported_annotation_types)):
            schema["type"] = [supported_types_map[annotation_type] for annotation_type in supported_annotation_types]

        param_req = param.default is param.empty and none_type not in supported_annotation_types

        if param.default is not param.empty:
            schema["default"] = param.default

        return {"schema": schema, "required": param_req}

    @staticmethod
    def callable_params_desc(kallable: Any) -> list[dict]:
        sig = inspect.signature(kallable)
        params_to_skip = ["self", "kwargs"]
        sig_params = filter(
            lambda param: param.name not in params_to_skip, sig.parameters.values()
        )
        params = [PluginService.param_annotation_desc(param) for param in sig_params]

        return params

    @staticmethod
    def callable_params_schema(kallable: Any) -> list[dict]:
        sig = inspect.signature(kallable)
        params_to_skip = ["self", "kwargs"]
        sig_params = filter(lambda param: param.name not in params_to_skip, sig.parameters.values())
        params = [PluginService.param_schema(param) for param in sig_params]
        schema = {
            "title": "Parameters",
            "type": "object",
            "required": [p["schema"]["title"] for p in params if p["required"]],
            "properties": {p["schema"]["title"]: p["schema"] for p in params}
        }

        return schema

    @staticmethod
    def describe_target(plugin_name: str, target_name: str, target: type) -> dict:
        parameters = PluginService.callable_params_desc(target.__init__)  # type: ignore
        target_id = PluginService.target_id(plugin_name, target_name)
        schema = PluginService.callable_params_schema(target.__init__)
        return {"id": target_id, "parameters": parameters, "schema": schema}

    @staticmethod
    def is_connector_command(module: Any) -> bool:
        # TODO: once all known connectors are updated to use spiffworkflow-connector-command
        # we should use this line to determine if something is a value command or not
        # return inspect.isclass(module) and issubclass(module, ConnectorCommand)
        return inspect.isclass(module)
