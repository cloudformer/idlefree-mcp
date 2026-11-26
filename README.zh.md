# idlefree-mcp

[IdleFree](https://cloudformer.github.io) 家族的 MCP 工具包。一个包，三个门，同一套函数：

| 调用者 | 用法 |
|---|---|
| AI（Claude Code / Desktop / 任何 MCP 客户端） | `claude mcp add pypi -- uvx idlefree-mcp mcp` |
| 人（终端） | `idlefree-mcp pypi check <名字>` · `idlefree-mcp pypi register <名字>` |
| 其他包 | `from idlefree_mcp import pypi` |

## 工具

- **PyPI 名字** —— 查可用性（精确查询，只读）；注册占名（用你自己 `~/.pypirc` 的 token 上传一个空的
  0.0.1 占位包）。owner 和作者走环境变量/参数，不写死任何人。工具会随系列继续增加。

## 配置

```sh
export IDLEFREE_OWNER=<你的 GitHub 用户/组织>      # 占位页会链接 github.com/<owner>/<名字>
export IDLEFREE_AUTHOR="<占位包上的作者名>"          # 可选，默认取 owner
export IDLEFREE_RESERVED_LOG=<路径/reserved.yaml>   # 可选：占名台账
```

上传 token 读 `PYPI_TOKEN` 或 `~/.pypirc` 的 `[pypi]` password——永远不进任何 MCP 配置。

[English](README.md)
