"""The MCP door: `uvx idlefree-mcp mcp` — a stdio server exposing the tools to any MCP client."""
from mcp.server.fastmcp import FastMCP

from .tools import pypi

server = FastMCP("idlefree")


@server.tool()
def pypi_check(names: list[str]) -> str:
    """Check PyPI availability for each name. Read-only: nothing is published.

    Returns one block per name: Available / taken by someone else / already registered by you
    (the last needs IDLEFREE_OWNER set to your GitHub user/org). PyPI treats -, _ and . as the
    same name, so variants need no separate checks."""
    return pypi.check(names)


@server.tool()
def pypi_register(name: str) -> str:
    """Register ONE name on PyPI by publishing an empty 0.0.1 placeholder (irreversible: PyPI
    names cannot be freed by the owner). Uses PYPI_TOKEN or ~/.pypirc, links the page to
    github.com/$IDLEFREE_OWNER/<name>. Call only after the user confirmed this exact name."""
    return pypi.register([name])


def serve():
    server.run()
