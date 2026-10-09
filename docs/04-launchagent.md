# 04 · macOS LaunchAgent（自动启动与代理端口）

## 已有服务：不要重复安装

若 `lsof -nP -iTCP:8787 -sTCP:LISTEN` 已有 Node 监听，且 `launchctl print "gui/$(id -u)/com.YOURNAME.claude-codex-proxy"` 等现有 label 正常，**直接沿用**。这时不应运行新的 `install_launchagent.py`，否则会创建两个争夺同一端口的服务。

已安装服务的重启示例（等 Claude/Qoder 当前任务完成后）：

```bash
launchctl kickstart -k "gui/$(id -u)/com.YOURNAME.claude-codex-proxy"
```

这是曾用过的 label，其他机器请使用各自实际的 label。

## 全新安装（仅 8787 空闲时）

本仓库提供 `run_proxy_macos.sh`：**每次服务启动时**从 macOS 系统设置读取当前启用的 HTTPS/HTTP 代理地址，设置 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NODE_USE_ENV_PROXY=1`，再启动本地 Node 网关。优先使用 HTTPSProxy 字段对应的 HTTP CONNECT 代理；不支持纯 SOCKS 端口。脚本不会记录 OAuth 凭据。

> 它只在**启动时**检测端口。若本机网络代理在 Node 持续运行中更换端口，仍需重启 LaunchAgent；它并不是持续自动切换器。

```bash
# 在此仓库根目录
python3 scripts/install_launchagent.py --check
python3 scripts/install_launchagent.py --apply

# 校验并启动新服务（仅全新安装）
plutil -lint "$HOME/Library/LaunchAgents/com.local.codex-subscription-bridge.plist"
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/com.local.codex-subscription-bridge.plist"
```

之后：

```bash
launchctl print "gui/$(id -u)/com.local.codex-subscription-bridge" | grep -E 'state =|pid =|last exit code'
curl --noproxy '*' -sS http://127.0.0.1:8787/health
```

`install_launchagent.py` **检测到端口已监听会拒绝安装**，不会覆盖已有 plist。需要卸载新服务时：

```bash
launchctl bootout "gui/$(id -u)/com.local.codex-subscription-bridge"
# 确认已经停止，才自行删除相应的 plist
```

## 固定端口为什么会报错

曾出现过 LaunchAgent 写死 `127.0.0.1:7897`，而 macOS 系统代理实际换成 `10808`；此时 `/health` 正常但向上游请求返回 `HTTP 500 fetch failed`。诊断见 [故障排查](07-troubleshooting.md)。如果继续使用旧 LaunchAgent，把对应环境变量的代理地址改成当前 `scutil --proxy` 的值，使用 `launchctl bootout` + `bootstrap` 重新读取 plist。`kickstart -k` 只会重启当前已经载入的配置。

## 使用自定义代理地址

若系统设置无法正确识别，可以在运行时设置 `CODEX_BRIDGE_PROXY_URL=http://127.0.0.1:PORT`，其中 PORT 是已验证支持 HTTP CONNECT 的监听端口。不要填 `socks5://` 给 Node 内置 HTTP_PROXY。
