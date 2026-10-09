# FAQ: Claude Desktop, Qoder, CC Switch and local Codex OAuth

[Home](../README.md) · [Quick start](quickstart-en.md) · [中文常见问题](faq-zh-CN.md)

### Can Claude Desktop use a ChatGPT/Codex subscription through a local gateway?

This repository documents one **unofficial** third-party interoperability setup using an authorized local Codex session and a separate Anthropic Messages-compatible gateway. It is not an OpenAI or Anthropic feature, and it cannot grant access to unsupported models or change service terms. See [quick start](quickstart-en.md).

### How do I configure Qoder with an Anthropic-compatible local endpoint?

Choose **Anthropic Compatible** and set the root Base URL to `http://127.0.0.1:8787`, with the gateway's **local** API key (not the OAuth token). Add the exact aliases from the [model table](../README.md#model-alias-presets). See the [Qoder guide](06-qoder.md).

### What is the difference between the client model name and upstream GPT model?

A name such as `claude-haiku-luna-medium` is a local routing alias. The gateway converts it to a configured upstream model and a reasoning effort. Changing the display label alone does not change model routing. See [model presets](03-model-presets.md).

### Why does the gateway return HTTP 500 with `fetch failed`?

The local service may be running while its **outbound** network path fails. Check the system HTTP(S) proxy (`scutil --proxy`), the actual proxy listener, and the LaunchAgent environment. Do not mistake `/health` success for a successful upstream call. See [troubleshooting](07-troubleshooting.md).

### Why does it return HTTP 401 or "authentication token has expired"?

Check the local OAuth refresh state and repeat the official OAuth authorization flow if necessary. Do not paste your auth file into diagnostics. See [OAuth setup](02-setup-macos.md).

### Can I set Qoder to 400K or Claude Desktop to 1M context?

The UI's advertised size, the gateway's soft/hard input budgets, and the upstream service's actual context limit are different. A larger client selection alone does not raise the gateway limits. Benchmark safely before increasing. See [context notes](03-model-presets.md).

### Why is Claude Desktop compaction slow?

Claude Desktop's built-in `Compacting session...` process can differ from gateway-side summarization. Large MCP tool catalogs and tool results consume significant input tokens. Reduce enabled tools and distinguish the two compaction paths. See [model presets](03-model-presets.md).

### Does this repository include credentials, or is it an official API endpoint?

No real credentials are intended to be included. It documents use of a third-party local bridge, not an official OpenAI API Key integration. Inspect [security](../SECURITY.md) and [release checks](public-release-checklist.md); never expose a demo-key localhost server to the network.
