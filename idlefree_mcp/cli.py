"""The human door: `idlefree-mcp check <names>` / `reserve <names>` / `mcp` (the stdio server)."""
import sys

USAGE = """idlefree-mcp — MCP tools for the IdleFree family

  idlefree-mcp check <name> [name ...]     check PyPI availability (read-only)
  idlefree-mcp reserve <name> [name ...]   reserve: publish an empty 0.0.1 placeholder
  idlefree-mcp mcp                         run the stdio MCP server (for claude mcp add)

env: IDLEFREE_OWNER (GitHub user/org, required to reserve), IDLEFREE_AUTHOR,
     IDLEFREE_RESERVED_LOG (optional ledger path), PYPI_TOKEN or ~/.pypirc"""


def main():
    argv = sys.argv[1:]
    cmd, args = (argv[0] if argv else ""), argv[1:]
    if cmd == "mcp":
        from .server import serve
        serve()
    elif cmd in ("check", "reserve") and args:
        from .tools import pypi
        try:
            print(pypi.check(args) if cmd == "check" else pypi.reserve(args))
        except (ValueError, RuntimeError) as e:
            sys.exit(str(e))
    else:
        sys.exit(USAGE)
