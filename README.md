# idlefree-mcp

<!-- mcp-name: io.github.cloudformer/idlefree-mcp -->

MCP tools for the [IdleFree](https://cloudformer.github.io) family. One package, three doors to
the same functions:

| Caller | How |
|---|---|
| An AI (Claude Code, Desktop, any MCP client) | `claude mcp add pypi -- uvx idlefree-mcp mcp` |
| A human in a terminal | `idlefree-mcp pypi check <name>` · `idlefree-mcp pypi register <name>` |
| Other packages | `from idlefree_mcp import pypi` |

## Tools

- **PyPI names** — check availability (exact lookup, read-only) and register one by publishing an
  empty 0.0.1 placeholder with your own `~/.pypirc` token. The owner and author are yours
  (environment or flags), nothing is hard-coded. More tools join as the series grows.

## Setup

```sh
export IDLEFREE_OWNER=<your GitHub user/org>     # reserve links the page to github.com/<owner>/<name>
export IDLEFREE_AUTHOR="<name on the placeholder>"   # optional, defaults to the owner
export IDLEFREE_RESERVED_LOG=<path/reserved.yaml>    # optional ledger of reserves and refusals
```

The upload token comes from `PYPI_TOKEN` or the `[pypi]` password in `~/.pypirc` — it never
enters any MCP configuration.

[中文说明](README.zh.md)
