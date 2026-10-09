# 05 · Claude Desktop + CC Switch

## 网关连接

进入 Claude Desktop 第三方推理设置，或在 CC Switch 的 **Claude Desktop** 供应商页新增 / 编辑 *直连* 供应商：

| 字段 | 值 |
|---|---|
| 模式 | `Gateway` / `Anthropic Compatible` / CC Switch **直连** |
| Base URL | `http://127.0.0.1:8787`（不附加 `/v1`） |
| API Key | `local`（若你在 `.env` 配置了其他 `PROXY_API_KEY`，用该值） |
| 认证 | Anthropic `x-api-key` 或 Bearer，由客户端处理 |
| 1M | **暂不勾选**，尚未端到端验证 |

此处绝不填写 Codex OAuth access/refresh token。**CC Switch 直连模式**意味着由 `8787` 代理负责 Anthropic → Codex 协议转换；不要再打开 CC Switch 的模型映射路由，避免把模型 ID 二次转换。

## 模型列表与显示名称

在 CC Switch 编辑供应商页面，先点击**获取模型列表**，选择 [8 个最终预设](03-model-presets.md)。如果发现的列表太长，可以只保留当前 8 个别名。历史旧会话使用的 `claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5` 可以保留，保留本身不会消费额度。

CC Switch「直连」模型列表的 GUI 只填写 Model ID / 1M；自定义显示名称 `labelOverride` 可在保存后使用本仓库辅助脚本写入到**已保存的 CC Switch 供应商元数据**和 Claude Desktop 3P profile。脚本会备份 CC Switch SQLite 数据库，**一定先完全退出 CC Switch 和 Claude Desktop（Command+Q）**。

```bash
python3 scripts/sync_friendly_labels.py --check
python3 scripts/sync_friendly_labels.py --apply
```

注意：脚本要求已经在 CC Switch 与 Claude profile 中存在全部 8 个当前 ID，且只找到一个指向 `127.0.0.1:8787` 的直连供应商。未满足就会拒绝修改。重新打开 Claude 后应看到如 `GPT-6 Luna · Medium`、`GPT-6.1 Sol · Low` 等易读名称。

## 解释菜单里的灰色描述

Claude Desktop 的“速度最快”“能力最强”可能仍按其内建的 Haiku/Opus/Sonnet 分类显示；**不代表实际 Luna / Sol / Astra 的性能排名**。菜单显示成功只证明客户端收到了模型列表；真实上游权限还要通过模型请求验证。

## Claude 自带的压缩可能很慢

Claude Desktop 自己的 `Compacting session...` 与本地代理的 `CONTEXT_COMPACT_MODEL` 是不同机制。网关设置 Luna Low 压缩不保证 Claude 自带的压缩自动走 Luna Low。MCP schema 占用可能非常高；建议按任务精简已启用 MCP 工具。200K 菜单显示也不必然意味着代理仅支持 200K。
