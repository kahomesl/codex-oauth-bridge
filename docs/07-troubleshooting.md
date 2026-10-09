# 07 · 故障排查速查

运行 `bash scripts/doctor.sh`，它只检查本地健康状态、监听、系统代理和模型目录，**不读取 Token**。然后通过真实 `/v1/messages` 端到端判断上游连通性。

| 现象 | 可能原因 | 正确处理 |
|---|---|---|
| `curl /health` 失败 | Node/LaunchAgent 没有运行，端口冲突 | `lsof -nP -iTCP:8787 -sTCP:LISTEN`、`launchctl print`、本地日志 |
| `health: ok`，`HTTP 500 fetch failed` | Node 出站链路失败：本机代理监听端口变化、DNS、网络 | 比较 `scutil --proxy` 与 LaunchAgent `HTTP_PROXY`；实测当前 HTTP CONNECT 端口；更新并重新载入服务 |
| OAuth 登录时报 `unsupported_country_region_territory` | 认证端实际拒绝当前请求的地区/服务访问 | 核查官方可用地区和账号状态，不提供绕过限制的方案 |
| OAuth 空 POST 返回 `Missing required parameter grant_type` / HTTP 400 | 测试没有提交参数，但**到达了认证接口** | 只代表基础网络链路可达，不能证明 OAuth 最终登录成功 |
| `/v1/messages` 返回 HTTP 401 / `token expired` | OAuth access token 已过期/刷新失败 | 停止不必要的重试，在 Mac 本地 `npm run auth` 重新授权；绝不要共享 `.auth/codex.json` |
| Qoder/Claude 返回 `model not found` | ID 错误或未启用/未添加别名 | 对照 `/v1/models` 和 `.env` 的 `MODEL_MAP`；检查是否已重启代理 |
| 某个模型 403 / access denied | Codex 订阅未授权该模型或当前上游限制 | 改用已验证模型；模型菜单可见≠订阅有权限 |
| Claude `Compacting session...` 很慢 | 原生客户端压缩、巨大历史或大量 MCP 工具定义 | 减少 MCP、尝试新会话；代理 compact 与 Claude 原生 compact 不相同 |
| `/v1/models` 有新模型，但 Claude 菜单旧 | CC Switch 保存/应用状态、Claude 缓存 | 保存并应用供应商，完全退出并重开 Claude；必要时使用 `sync_friendly_labels.py` |

## 检查代理端口

```bash
lsof -nP -iTCP:8787 -sTCP:LISTEN
scutil --proxy | grep -E 'HTTPProxy|HTTPPort|HTTPSProxy|HTTPSPort|HTTPEnable|HTTPSEnable'
# 按实际端口替换示例端口 10808：
curl --max-time 15 -sS -x http://127.0.0.1:10808 -X POST \
  https://auth.openai.com/oauth/token -w '\nHTTP %{http_code}\n'
```

上述空 POST 返回 HTTP 400 `grant_type` 缺失仅用于**链路检查**，不是正式登录。避免打印真实 OAuth 参数。

## 检查加载的服务

```bash
launchctl print "gui/$(id -u)/com.YOURNAME.claude-codex-proxy" | grep -E 'state =|pid =|last exit code'
# 若使用本仓库新建的 label，用 com.local.codex-subscription-bridge 替换
```

`.env` 修改早于当前 Node 启动时间，通常表示进程已加载修改；但**只有发实际请求才证明上游可用**。重启当前代理会中断进行中的 Claude / Qoder 任务，应先等待请求完成。

## 认证状态与保密

```bash
cd "$HOME/claude-codex-proxy"
# 检查本地是否存在 Token 文件，但不要打印内容
ls -l .auth/codex.json
# OAuth 若需要重新执行，参见 02-setup-macos.md
```

认证/令牌和 ChatGPT 订阅政策可能变化；遇到 HTTP 403/401 时以官方提示为准。
