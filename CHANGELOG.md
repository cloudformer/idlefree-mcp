# Changelog

## 0.1.0 — 2026-11-26

- The pypi tool lands: `tools/pypi.py` — check names (read-only) and register one (an empty 0.0.1
  placeholder uploaded with your own token), ported from the series' reserve script with nothing
  hard-coded: `IDLEFREE_OWNER` / `IDLEFREE_AUTHOR` / `IDLEFREE_RESERVED_LOG` / `PYPI_TOKEN`.
- Three doors to the same functions: `uvx idlefree-mcp mcp` (stdio MCP server: `pypi_check`,
  `pypi_register`), `idlefree-mcp pypi check|register` (CLI, hierarchical: tool then action), `from idlefree_mcp.tools import pypi`
  (library). Offline test suite (fake PyPI, nothing leaves the process).

## 0.0.1 — 2026-11-26

- The name `idlefree-mcp` reserved on PyPI; flat package skeleton (the idlefree-auth shape) with
  CI wired: tag `vX.Y.Z` → tests → PyPI. The plan: one package, three doors — MCP server
  (`uvx idlefree-mcp mcp`), CLI (`idlefree-mcp check/reserve`), library (`from idlefree_mcp
  import pypi`); the PyPI name check/reserve tool lands in 0.1.0.
