# 02 · macOS 安装 + OAuth 登录

## 1. 获取上游

```bash
cd "$HOME"
git clone https://github.com/brianconnoly/claude-codex-proxy.git
cd claude-codex-proxy
npm install
cp -n .env.example .env
chmod 600 .env
```

如果目录已经存在，**停止执行 clone；转到 [维护手册](08-maintenance.md)**。本仓库保存安装说明与兼容性补丁，不替代上游源码。

## 2. 初始 `.env`

确认 `.env` 中 `HOST=127.0.0.1`、`PORT=8787`、`UPSTREAM=codex`、`DEFAULT_MODEL=gpt-6-luna`，并配置 `CLAUDE_OPUS_MODEL=gpt-6.1-sol` 等回退项（见 [模型预设](03-model-presets.md)）。原样保留上游其他所需变量。**不要把本机 `.env` 提交到 GitHub。**

## 3. OAuth

先在 macOS `scutil --proxy` 查看当前启用的 HTTP/HTTPS 代理。以下 `10808` 是**示例端口**，不是永久地址；依实际输出调整。

```bash
cd "$HOME/claude-codex-proxy"
HTTP_PROXY=http://127.0.0.1:10808 \
HTTPS_PROXY=http://127.0.0.1:10808 \
NO_PROXY=127.0.0.1,localhost \
NODE_USE_ENV_PROXY=1 \
npm run auth
```

完成浏览器中的官方账号授权。Token 应只写入上游项目本地 `.auth/codex.json`，不要截图、提交或传递文件。网络无需 HTTP 代理时，按正常网络设置直接执行 `npm run auth`。

## 4. 单次前台运行验证

```bash
cd "$HOME/claude-codex-proxy"
HTTP_PROXY=http://127.0.0.1:10808 HTTPS_PROXY=http://127.0.0.1:10808 \
NO_PROXY=127.0.0.1,localhost NODE_USE_ENV_PROXY=1 npm start
```

在另一个终端运行 `curl --noproxy '*' -sS http://127.0.0.1:8787/health`。看到 `{"ok":true,"upstream":"codex"}` 只说明本地服务运行；还需要发 `/v1/messages` 验证上游。之后停止前台服务，再考虑 LaunchAgent。

## 5. 应用每模型独立推理能力

必须按此顺序（在本仓库根目录，路径适当修改）：

```bash
python3 scripts/install_legacy_8.py --check
python3 scripts/install_legacy_8.py --apply
python3 scripts/set_final_models.py --check
python3 scripts/set_final_models.py --apply
```

第一脚本在上游增加 `MODEL_EFFORT_MAP` / `MODEL_DISPLAY_MAP` 代码，第二脚本把临时旧 8 档转换成**最终** Luna/6.1 Sol/Astra 的 8 档。两者均校验源码锚点、备份文件并运行测试；遇到不匹配时**不要强制替换**，可能是上游更新。修改后重启代理进程才能生效。`--apply` 不负责重启服务。

## 6. 独立测试 Astra 权限

`/v1/models` 有 Astra 名称不等于可以实际调用 `gpt-6-astra`。使用下面真实请求测试（会消耗少量订阅额度）：

```bash
curl --noproxy '*' -sS --max-time 120 \
  http://127.0.0.1:8787/v1/messages \
  -H 'content-type: application/json' -H 'x-api-key: local' \
  -d '{"model":"claude-opus-astra-low","max_tokens":64,"messages":[{"role":"user","content":"Reply with OK."}]}'
```

如果 HTTP 401：先看 OAuth；HTTP 403/模型不支持：按实际上游权限处理，不要尝试绕过限制。其他模型也是如此。
