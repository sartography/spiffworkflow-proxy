![Tests](https://github.com/sartography/spiffworkflow-proxy/actions/workflows/tests.yml/badge.svg)
# Spiffworkflow Proxy Blueprint
A Flask Blueprint to connect SpiffWorkflow Service Tasks to your organization's APIs. Use this as a library in your connector application.

## Api Endpoints
Adds the following API endpoints:

| Endpoint | Description |
| -------- | ------------|
|/liveness | Returns json {'ok':True} if things are going well. |


The primary endpoints return a list of available commands and their required arguments.

| Endpoint | Description |
| -------- | ------------|
| /v1/commands| Returns a list of commands that can be executed on the system. This feeds directly into the Service Tasks. |
| /v1/do/{plugin}/{command} | Execute the given command. |


In addition to the base commands which can use secrets from a config file or the environment, there is the ability to step BPMN Authors through an Oauth process in order to get authentication tokens.  Here are those endpoints.

| Endpoint | Description |
| -------- | ------------|
| /v1/auths | list all the available authentication schemes |
| /v1/auths/{plugin}/{auth} | Execute the authentication process |
| /v1/auths/{plugin}/{auth}/callback | Redirects back from an Oath call |


