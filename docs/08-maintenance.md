# 08 · 日常维护、更新与回滚

## 已安装环境的“稳定优先”原则

若 `/health`、真实 `/v1/messages`、Claude Desktop 和 Qoder 都正常，**不必重复运行任何 `--apply`**。仓库是操作手册，不代表未来每次都应重新部署。

常用检查：

```bash
bash scripts/doctor.sh
cd "$HOME/claude-codex-proxy" && npm test
```

更新上游源码时先 `git status`，备份 `.env`、`.auth`（仅本机安全备份，绝不 Git 提交）和本地已修改的 `src/config.js`、`src/anthropic.js`、`src/server.js`。本仓库的补丁使用源码锚点；上游改版后可能需要手工移植。不要强制 `git pull --reset` 丢失本地补丁。更新前检查当前是否有长任务。

## 修复 macOS 网络代理端口更换

新安装的 `run_proxy_macos.sh` 每次服务启动时读取系统当前启用的 HTTP(S) 代理。更换端口期间，已运行进程仍可能保持旧值；任务结束后重启服务。旧版 LaunchAgent 则必须编辑其 plist 并 `bootout`/`bootstrap` 重载，不是仅 `kickstart`。

## 配置 / 回滚备份位置

- `~/.claude-codex-proxy-preset-backups/`：第一轮源码补丁的备份。
- `~/.codex-bridge-backups/`：最终模型 `.env` / test 备份。
- `~/.claude-model-label-backups/`：CC Switch model labels/Claude profile 备份。
- `~/.claude-model-set-backups/`：历史完整迁移脚本备份（若使用过）。

所有备份中可能含 API Key、OAuth 配置或本地数据库，**绝不能复制到本仓库**。

## 切换 Plus / Pro 与推理强度

Plus 建议优先使用 Luna Medium，再按任务难度选择 Sol 6.1 Low/Medium，Astra 单独确认可用性。`xhigh` 默认不作为常用模型。更改 `MODEL_MAP` / `MODEL_EFFORT_MAP` 后请通过 `node` 本地 `resolveModelProfile()` 检查，之后才在没有进行中请求时重启代理。

## 公布更新

如果把这个仓库发布在 GitHub（可选私有），未来更新文档时通过 clone → 编辑 → `git diff` → commit → push。不要自动上传整个 `~/claude-codex-proxy` 文件夹到 GitHub；里面有 OAuth 凭据和本地修改文件。
