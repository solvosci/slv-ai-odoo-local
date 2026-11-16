import requests
from langsmith import traceable

from ...application.errors.service_unavailable import ServiceUnavailable
from ...application.errors.tool_rejected import ToolRejected
from ...application.ports.tool_gateway import ToolGateway
from ...domain.entities.tool_spec import ToolSpec


class OdooToolGateway(ToolGateway):
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @traceable(name="odoo.list_tools")
    def list_tools(self, token):
        data = self._request("GET", "/solvy/tools", token)
        specs = []
        for tool in data["tools"]:
            specs.append(ToolSpec(**tool))
        return specs

    @traceable(name="odoo.call_tool", run_type="tool")
    def call_tool(self, token, name, arguments):
        body = {"arguments": arguments}
        return self._request("POST", f"/solvy/tools/{name}", token, body)["result"]

    def _request(self, method, path, token, body=None):
        try:
            response = requests.request(
                method,
                self.base_url + path,
                json=body,
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise ServiceUnavailable(str(e)) from e

        if response.status_code >= 500:
            raise ServiceUnavailable(f"Odoo respondió {response.status_code}")
        if response.status_code >= 400:
            try:
                message = response.json()["error"]
            except (ValueError, KeyError):
                message = f"Error {response.status_code}"
            raise ToolRejected(message)
        return response.json()
