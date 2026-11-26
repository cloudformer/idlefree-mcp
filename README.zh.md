# idlefree-mcp

[IdleFree](https://cloudformer.github.io) 家族的 MCP 工具包。一个包，三个门，同一套函数：

| 调用者 | 用法 |
|---|---|
| AI（Claude Code / Desktop / 任何 MCP 客户端） | `claude mcp add pypi -- uvx idlefree-mcp mcp` |
| 人（终端） | `idlefree-mcp check <名字>` · `idlefree-mcp reserve <名字>` |
| 其他包 | `from idlefree_mcp import pypi` |

## 工具

- **PyPI 名字** —— 查可用性（精确查询，只读）；占名（用你自己 `~/.pypirc` 的 token 上传一个空的
  0.0.1 占位包）。owner 和作者走环境变量/参数，不写死任何人。工具会随系列继续增加。

## 状态

`0.0.1` —— 名字已占，骨架 + CI（tag `vX.Y.Z` → 测试 → PyPI）。pypi 工具在 `0.1.0` 落地。

[English](README.md)
