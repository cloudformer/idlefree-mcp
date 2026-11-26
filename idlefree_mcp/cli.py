"""The human door: `idlefree-mcp <tool> <action> <args>` / `idlefree-mcp mcp` (the stdio server)."""
import sys

USAGE = """idlefree-mcp — MCP tools for the IdleFree family

  idlefree-mcp pypi check <name> [name ...]      check PyPI availability (read-only)
  idlefree-mcp pypi register <name> [name ...]   register: publish an empty 0.0.1 placeholder
  idlefree-mcp mcp                               run the stdio MCP server (for claude mcp add)

env: IDLEFREE_OWNER (GitHub user/org, required to register), IDLEFREE_AUTHOR,
     IDLEFREE_RESERVED_LOG (optional ledger path), PYPI_TOKEN or ~/.pypirc"""


def main():
    argv = sys.argv[1:]
    if argv[:1] == ["mcp"]:
        from .server import serve
        serve()
    elif argv[:2] in (["pypi", "check"], ["pypi", "register"]) and argv[2:]:
        from .tools import pypi
        try:
            print(pypi.check(argv[2:]) if argv[1] == "check" else pypi.register(argv[2:]))
        except (ValueError, RuntimeError) as e:
            sys.exit(str(e))
    else:
        sys.exit(USAGE)
