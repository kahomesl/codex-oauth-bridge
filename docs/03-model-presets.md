# 03 · 模型预设、推理强度与上下文

## 最终 8 个预设

见 [中文 README](../README.zh-CN.md#八档模型别名) 与 [English table](../README.md#model-alias-presets)。原三类兼容路由可继续工作：`claude-opus-4-8` → 6.1 Sol Low；`claude-sonnet-4-6` → Luna Medium；`claude-haiku-4-5` → Luna Low。兼容 ID 保留并不意味着需要在菜单中展示。

**映射的两步：** `MODEL_MAP=别名=gpt-模型` 选上游模型，`MODEL_EFFORT_MAP=别名=low/medium/high` 选推理等级，`MODEL_DISPLAY_MAP=别名=名称` 影响网关 model discovery。`MODEL_EFFORT_MAP` 和 `MODEL_DISPLAY_MAP` 是本仓库补丁提供的功能，**原版上游未必有**。

`none`：不分配额外的推理阶段，偏直接回答，不等同于“低智力的另一款模型”。这次没有保留 Luna None，因为日常编程选择 Luna Low 更均衡。

## 订阅配额

不同模型和推理强度会影响 Token 数量与订阅额度；同一推理档也可能因历史消息、MCP 工具、缓存、任务复杂度而相差巨大。API 单价不能直接等同 Codex 订阅扣额。日常可从 Luna Medium 开始，较复杂开发尝试 6.1 Sol Low/Medium；Astra 仅在有权限且值得消耗时使用。**请在官方用量页面核实当期限制。**

## 上下文：200K、340K、400K 与 1M 的区别

历史示例代理配置声明 `CODEX_MAX_INPUT_TOKENS=340000`、硬输入上限 `360000`、原始窗口参数 `400000`，压缩触发 `260000`、压缩后目标 `220000`。这些数字是**网关的配置预算示例**，不是所有账号渠道的保证能力，也不是 Claude Desktop 必定显示的数值。

Qoder 可选 200K / 400K / 1M：**选 400K 不会自动把网关输入上限从 340K 提升到 400K**。谨慎从 200K 开始；确认长会话稳定再尝试 400K。1M 未被此工具包保证端到端可用。

Claude Desktop 原生 `Compacting session...` 和网关自己的 `CONTEXT_COMPACT_*` 是不同机制。即使网关压缩模型为 Luna Low，也不能保证 Claude 自己的压缩按同样推理档执行。MCP 工具 schema 可大量占用上下文；只启用当前项目必需的工具。

## 诊断模型映射

```bash
cd "$HOME/claude-codex-proxy"
node --input-type=module <<'NODE'
import {loadConfig} from './src/config.js';
import {resolveModelProfile} from './src/anthropic.js';
const config = loadConfig();
for (const id of config.discoveryModels.filter(x => /luna|astra|sol61/.test(x))) {
  const p = resolveModelProfile(id, config);
  console.log(`${id} -> ${p.model}, effort=${p.reasoningEffort}`);
}
NODE
```

输出反映磁盘配置；若 `.env` 修改晚于进程启动时间，需要在任务空闲后重启服务才能生效。
