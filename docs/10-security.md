# 10 · 安全、权限和风险

- 只在你有权使用相应账号、模型和接口且符合服务条款的情况下运行。ChatGPT/Codex OAuth 通过未官方支持的第三方本地协议网关使用时，上游协议和权限可能改变；不保证持续可用。
- **永远不要上传：** `~/claude-codex-proxy/.auth/codex.json`、`.env`（真实值）、CC Switch SQLite DB、Claude Desktop profile、Qoder 设置、浏览器会话 Cookie、终端的访问令牌、日志里的授权字段。
- 对外只发布 `.env.example`；它只记录键名和示例模型路由，不包含密码。`local` 是当前本机 API Key 的示例值；如你将网关暴露给不可信进程或设备，必须改为随机高强度 Key，并保持网络边界。最安全是始终 `HOST=127.0.0.1`。
- macOS 上 `127.0.0.1:8787` 是回环网络，不需要为了 Qoder 黄色 HTTP 提示改成 `0.0.0.0`。不要通过公网反向代理开放无鉴权的 8787。
- `--probe` 或 curl 的实际请求可能产生订阅额度消耗；先进行少量短请求。
- `gh auth login` 仅在用户 Mac 的 CLI 中执行；不要把个人 GitHub Token 存进该 repo。`publish_github.sh` 默认创建**私有仓库**，发布前须人工确认文件清单。
- 网络代理端口可以不同，不应把换端口或认证失败理解为需要绕过地区限制。遵守服务可用区域及认证政策。
