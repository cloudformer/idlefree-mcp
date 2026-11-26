# idlefree-mcp

<!-- mcp-name: io.github.cloudformer/idlefree-mcp -->

MCP tools for the [IdleFree](https://cloudformer.github.io) family. One package, three doors to
the same functions:

| Caller | How |
|---|---|
| An AI (Claude Code, Desktop, any MCP client) | `claude mcp add pypi -- uvx idlefree-mcp mcp` |
| A human in a terminal | `idlefree-mcp check <name>` · `idlefree-mcp reserve <name>` |
| Other packages | `from idlefree_mcp import pypi` |

## Tools

- **PyPI names** — check availability (exact lookup, read-only) and reserve one by publishing an
  empty 0.0.1 placeholder with your own `~/.pypirc` token. The owner and author are yours
  (environment or flags), nothing is hard-coded. More tools join as the series grows.

## Status

`0.0.1` — name reserved, skeleton with CI (tag `vX.Y.Z` → tests → PyPI). The pypi tool lands in
`0.1.0`.

[中文说明](README.zh.md)
