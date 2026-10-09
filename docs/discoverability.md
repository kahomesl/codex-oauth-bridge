# Discoverability: GitHub Search, Google, Bing and AI-assisted search

[Home](../README.md) · [中文首页](../README.zh-CN.md) · [Public release checklist](public-release-checklist.md)

## What can help people find this project?

1. **Publish a reviewed, public repository.** A private repository is not publicly searchable. Do not copy private Git history when preparing the public version.
2. **Choose clear names and metadata.** Suggested repository name: `codex-oauth-bridge`; repository title: *Codex OAuth Bridge for Claude Desktop & Qoder*. Use the Description and Topics from the [release checklist](public-release-checklist.md). GitHub Topics classify repositories by purpose, community, and subject matter.
3. **Answer specific user questions in readable text.** This repository has distinct answers for “Qoder Anthropic Compatible localhost”, “Claude Desktop ChatGPT Codex OAuth”, “Codex proxy HTTP 401/500”, and “200K vs 400K context”, each with internal links to a detailed guide.
4. **Maintain bilingual entry points.** The [English README](../README.md) and [Chinese README](../README.zh-CN.md) reference relevant original guidance. Keep them synchronized with actual supported versions and tested behavior.
5. **Link from legitimate relevant places.** Consider your public GitHub profile, project documentation, relevant discussions, and upstream issue threads **when directly relevant**. Avoid unsolicited mass-posting or spammy backlinks.
6. **Measure after publishing.** Search `site:github.com/OWNER/codex-oauth-bridge` on Google/Bing, and GitHub Search for model/interface keywords. New repos may take time to be indexed. No ranking, inclusion in AI answers, or crawl schedule can be guaranteed.

## What does NOT guarantee discovery?

- Publishing a `llms.txt` file or adding invented AI-specific structured data is not a guaranteed inclusion mechanism for major search engines.
- Adding a pile of repetitive keywords does not substitute for useful, accurate documentation.
- UI-visible GPT model IDs are not proof of access, nor are fabricated benchmark/performance claims appropriate SEO content.
- A GitHub repository normally cannot directly control GitHub's site-wide robots.txt, snippets, or Search Console verification for `github.com`.

## Further reading (primary references)

- [GitHub Docs — Classifying repositories with topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
- [Google Search Central — AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [GitHub Docs — Repository visibility and its consequences](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)

## 中文概要

公开仓库后，优先完善 GitHub 的 **Description / Topics / README**，通过真实有用的英文和中文故障指南覆盖自然搜索问题，再从个人主页和相关技术讨论建立合适的引用。不能保证 Google、Bing 或任何 AI 助手立即收录或主动推荐；不要使用关键词堆砌或虚假的性能数据。正式发布前必须检查提交作者身份、敏感文件和 Actions 日志的公开风险。
