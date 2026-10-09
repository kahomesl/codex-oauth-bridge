# 06 · Qoder (IDE/CLI) 接入

在 Qoder **设置 → 模型 → 添加模型**，按本机版本选择自定义模型 / Anthropic Compatible。UI 细节可能随版本变化，实际截图优先。

| 字段 | 值 |
|---|---|
| 供应商 | `Anthropic Compatible` |
| Base URL | `http://127.0.0.1:8787` |
| API Key | `local`（与代理一致） |
| Model ID | [最终 8 个别名](03-model-presets.md)，可一次批量添加 |
| 显示名称 | 逐一填 `GPT-6 Luna · Low` 等易读名称 |
| 默认上下文 | 初始推荐 `200K` |
| 能力 | 视觉按实测开启；Qoder Thinking 先关闭，由网关别名控制推理强度 |

在下一步“配置模型能力”中**不要改 Model ID**，只改显示名。实际可见的 200K/400K/1M 是 Qoder 声明参数，不等同订阅真实上游能力。在验证长会话稳定后可尝试 400K，但网关曾配置的 soft 输入预算为 340K、硬上限 360K、260K 即启动代理侧压缩；勾选 400K 不会自动更改这些限制。1M 不建议未经验证就声明支持。

此前 UI 中保留的 `GPT-6 Luna · None`、`GPT-6 Sol · Low/Medium` 已从**最终方案**淘汰。在 Qoder 模型列表里点对应行 `···` → 删除/移除，若当前版本不支持删除先关闭开关。然后添加新的 `claude-opus-sol61-high`、`claude-opus-astra-low`、`claude-opus-astra-medium`（加上保留的五档总共八个）。

> Qoder 在模型目录里显示成功，也不等于代理可以调用上游。点击“校验并添加模型”后，分别用至少一个 Luna、6.1 Sol 和 Astra 发送短消息做 HTTP 200 端到端确认。

如果本地 HTTP 被 Qoder 标记为不安全：`127.0.0.1` 是同机回环，流量不经过外部网络；**不要因此把 8787 绑定到 `0.0.0.0`**。外部 Codex 上游仍应经 HTTPS。
