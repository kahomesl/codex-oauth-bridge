# Codex OAuth Bridge：连接 Claude Desktop、Qoder 与 CC Switch

**简体中文 | [English](README.md)**

一套面向 macOS 的**非官方、可复现**的配置手册和本地脚本：通过本机 Anthropic Messages 兼容网关，把已获授权的 ChatGPT/Codex OAuth 会话接入 **Claude Desktop、CC Switch、Qoder**。包含模型路由、不同推理强度、自动启动、上下文预算、OAuth 故障排查和隐私检查。

> **非官方项目。** 本仓库基于 [brianconnoly/claude-codex-proxy](https://github.com/brianconnoly/claude-codex-proxy) 的安装流程，不包含该上游的源码。服务协议、权限和支持的模型可能改变；请在服务条款和所在地区允许的范围内使用。ChatGPT 订阅不等于无限制 API 权限。

## 功能与适用范围

| 客户端 | 配置方式 |
|---|---|
| Claude Desktop | 第三方推理 Gateway，接入本机 `127.0.0.1:8787` |
| CC Switch | Claude Desktop 供应商使用**直连**，避免重复路由 |
| Qoder | 添加 **Anthropic Compatible** 自定义供应商 |
| Codex OAuth | 在本机完成授权，令牌由上游代理保管，不共享给客户端 |

本地 API 提供 `/health`、`/v1/models`、`/v1/messages`。`local` 只是本机示例网关口令，不是 ChatGPT Token；**不可把演示口令的 8787 服务暴露到公网**。

## 从零安装

1. 阅读 [环境准备](docs/01-preflight.md) 与 [macOS OAuth 安装](docs/02-setup-macos.md)，单独克隆上游代理。
2. 在本仓库目录中依次执行模型补丁的 `--check`、`--apply`：`scripts/install_legacy_8.py` → `scripts/set_final_models.py`。两步分别实现独立推理等级与最终八档预设；只对兼容且已备份的上游代码应用。
3. 验证 `http://127.0.0.1:8787/health`、`/v1/models`，再发真实 `/v1/messages` 请求。仅健康检查正常不足以证明 OAuth 有效。
4. 按 [Claude Desktop + CC Switch](docs/05-claude-desktop.md)、[Qoder](docs/06-qoder.md) 指南分别配置。
5. 新机器可按 [LaunchAgent](docs/04-launchagent.md) 配置后台自启。**已有正常运行服务的机器不要重复安装。**

完整的模型配置见 [模型预设与上下文](docs/03-model-presets.md)。

## 八档模型（别名）

| Qoder / Claude 模型别名 | 上游模型 | 推理等级 |
|---|---|---|
| `claude-haiku-luna-low` | `gpt-6-luna` | Low |
| `claude-haiku-luna-medium` | `gpt-6-luna` | Medium |
| `claude-haiku-luna-high` | `gpt-6-luna` | High |
| `claude-opus-sol61-low` | `gpt-6.1-sol` | Low |
| `claude-opus-sol61-medium` | `gpt-6.1-sol` | Medium |
| `claude-opus-sol61-high` | `gpt-6.1-sol` | High |
| `claude-opus-astra-low` | `gpt-6-astra` | Low |
| `claude-opus-astra-medium` | `gpt-6-astra` | Medium |

这些是**自定义路由 ID**，不是 Anthropic 官方型号。建议优先使用 Luna Medium 完成日常任务，复杂问题才尝试更高推理强度；Astra 必须先验证订阅渠道支持。不保证不同客户端都开放全部上游模型。

## 关键问题

- **为什么显示 `200K` 上下文？** 客户端显示限制、网关输入预算和上游模型窗口是不同层级。选择 Qoder 的 `400K` 不会自动扩大本地代理的 soft/hard 输入预算。
- **为什么压缩很慢？** Claude Desktop 的原生 `Compacting session...` 与代理侧 `CONTEXT_COMPACT_*` 不同；大量 MCP 工具定义也会占满上下文。
- **`HTTP 500 fetch failed` 怎么办？** 首先检查当前系统 HTTP 代理端口和 LaunchAgent 的实际环境变量。
- **`HTTP 401 token expired` 怎么办？** 通过官方 OAuth 交互重新授权；不要上传 Token。

继续阅读：[中文常见问题](docs/faq-zh-CN.md) · [排障](docs/07-troubleshooting.md) · [维护](docs/08-maintenance.md) · [AI 交接](docs/09-ai-handoff.md)。

## 安全声明

只在 `127.0.0.1` 提供本地服务；不要上传真实 `.env`、`.auth/codex.json`、CC Switch 数据库、Qoder/Claude 完整设置或带凭据的日志。发布前运行 `python3 scripts/public_release_audit.py --strict`，**且必须人工审阅**。详见 [SECURITY.md](SECURITY.md)、[如何提升 GitHub 与 AI 搜索发现率](docs/discoverability.md) 和 [公开发布检查清单](docs/public-release-checklist.md)。

**许可证：** MIT（仅适用于本仓库的原创内容，不能覆盖上游许可或平台服务条款）。
