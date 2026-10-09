# 常见问题：Claude Desktop / Qoder / CC Switch / Codex OAuth

[中文首页](../README.zh-CN.md) · [英文 FAQ](faq-en.md)

### ChatGPT/Codex 订阅可以本地接入 Claude Desktop 吗？

这是一个**非官方**第三方兼容网关的配置案例，不是 OpenAI 或 Anthropic 官方集成功能。必须由用户自己完成合规授权；不能增加未开放的模型权限。安装请看 [macOS 指南](02-setup-macos.md)。

### Qoder 的 Anthropic Compatible 怎么填？

供应商选 Anthropic Compatible，Base URL 填 `http://127.0.0.1:8787`，Key 填本地网关的密钥，而不是 Codex OAuth Token。模型 ID 使用完整别名，见 [Qoder 说明](06-qoder.md)。

### 选了 GPT-6 Luna Low，为什么返回 Claude Haiku 名字？

`claude-haiku-luna-low` 是客户端兼容别名。代理内部再把它路由到 GPT 模型与推理等级；响应中的别名不能单独证明上游型号。见 [模型路由检查](03-model-presets.md)。

### HTTP 500 `fetch failed` 怎么排查？

确认本地网关 8787 正常，再检查 `scutil --proxy` 的当前 HTTP 代理端口和 LaunchAgent 启动变量。`/health` 返回 200 只证明本地进程在运行，见 [故障排查](07-troubleshooting.md)。

### HTTP 401 Token expired 怎么办？

通过官方 OAuth 交互重新授权，并检查本机认证文件权限。不要把 `codex.json`、Cookie 或一次性登录回调发给任何人。见 [安装与 OAuth](02-setup-macos.md)。

### Qoder 的 400K 和 Claude Desktop 的 1M 真能使用吗？

客户端显示数值、代理软/硬输入预算、上游实际允许的上下文大小，是三个不同概念。单纯勾选 400K 不代表代理接受 400K 输入。见 [上下文说明](03-model-presets.md)。

### 为什么会话自动压缩慢？

Claude Desktop 内建压缩与代理 `CONTEXT_COMPACT_*` 是不同机制；MCP 工具定义可能占用大量 Token。减少不用的 MCP 服务、避免超长任务会有帮助。
