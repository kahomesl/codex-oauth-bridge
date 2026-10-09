# 01 · 开始之前

**平台：** macOS + zsh，Node 版本须满足上游 `package.json` 的要求；终端有 `git`、`npm`、`node`、`python3`。GitHub 发布需要 `gh` 并完成 `gh auth login`。Claude Desktop 需要支持第三方推理（Developer → Configure third-party inference）；Qoder 需要支持 Anthropic Compatible 自定义模型。

```bash
node -v
npm -v
git --version
python3 --version
scutil --proxy | grep -E 'HTTPProxy|HTTPPort|HTTPSProxy|HTTPSPort|HTTPEnable|HTTPSEnable'
```

**开始前检查：** `lsof -nP -iTCP:8787 -sTCP:LISTEN`。若已有 Node 服务，先判断是不是已经安装的 `claude-codex-proxy`；不要启动第二个实例或覆盖既有 LaunchAgent。

本机网络代理 HTTP(S) 监听端口可能因代理软件配置调整而变化，所以**不要假设端口长期固定**。`NODE_USE_ENV_PROXY=1` 让 Node fetch 从 HTTP(S)_PROXY 环境变量读取代理。SOCKS-only 地址不能直接当 HTTP_PROXY 使用。公网接口和客户端特性经常变化，实机响应优先于旧截图。

安全要求：使用本机回环 `127.0.0.1`，不要把 `.auth` 或 `.env` 放进 Git。OAuth 失败不代表应该上传令牌给他人诊断。
