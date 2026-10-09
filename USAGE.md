# 安装和使用 explain-clearly

## 把安装交给 Agent

在你使用的 Codex、Claude Code、WorkBuddy 等 Agent 中发送：

> 请帮我安装 explain-clearly Skill：
> 仓库：https://github.com/BananaSoldier01/explain-clearly
> Skill 源目录：skills/explain-clearly/
>
> 请按你当前 Agent 支持的安装方式完成安装，保留该目录内的参考、模板和脚本。已有同名技能时先核对来源，不覆盖其他内容；不要修改 AGENTS.md 或 CLAUDE.md。
>
> 完成后验证 explain-clearly 能被发现或调用，告诉我如何使用，以及是否需要重启或新开对话。若某一步必须由我手动操作，请先完成你能做的部分，再说明具体操作。

安装的是仓库中的 `skills/explain-clearly/` 整个目录。README、演示和项目测试不用加入每次读取的 Skill 上下文。

## 安装完成后怎么用

按 Agent 给出的调用方法选择 explain-clearly，然后提出普通问题。例如：

> 请使用 explain-clearly 解释：RAG 是什么？为什么找到了资料还会答错？

> 请使用 explain-clearly 解释这段方案。这些术语分别做什么，整套流程怎样配合？

必要术语应随文解释；多步骤问题可以沿用具体情境。重要数字、条件、风险和未验证状态保留。仍不懂时，直接指出哪个词或哪一步；需要图或网页时，按对应同意继续。

## 不同 Agent 的安装方式

安装位置和调用入口由当前 Agent 及其版本决定，不要求所有产品使用相同目录。

- **Codex**：官方文档说明本地 Skills 发现目录包括项目 `.agents/skills/` 和用户 `~/.agents/skills/`，也支持让内置 Skill Installer 从其他仓库安装。CLI／IDE 可通过技能选择器或 `$` 显式调用。[OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。
- **Claude Code**：官方文档提供用户级 `~/.claude/skills/` 和项目级 `.claude/skills/`，可用 `/explain-clearly` 调用；云端与其他运行方式的发现范围以文档为准。[Claude Code 官方说明](https://code.claude.com/docs/en/skills)。
- **WorkBuddy**：腾讯云的 WorkBuddy Enterprise 文档提供技能导入、启用和对话召唤入口；需要导入技能包时，让 Agent 先准备适配的包并完成可自动执行的部分。其他版本以当前产品支持的方式为准。[腾讯云官方说明](https://cloud.tencent.com/document/product/1831/134432)。

上面的提示词把安装操作交给 Agent，不代表每个版本都能全自动完成。若产品要求你确认、导入或重启，按安装结果完成那一步。当前没有对这三个产品的完整安装、自动匹配或跨轮持续做统一实测。

## 确认是否装好、是否调用

让 Agent 确认安装位置、完整目录和技能发现／选择器结果，再按对应方法调用。调用时，实际读取记录可以确认 Skill 文件载入；一句“已使用”或一份易懂回答本身不够。

显式调用确认这次使用；自动匹配是 Agent 的行为，不保证每个解释请求都触发。切换对话或工作目录后是否继续可用，取决于安装范围及产品机制。

## 备用：已持有文件时按路径试用

不安装也可让能读取本地文件的 Agent 按路径使用：

> 请先用文件读取工具打开 `skills/explain-clearly/SKILL.md`，成功读取后按它的说明回答我的问题：RAG 是什么？为什么找到了资料还会答错？如果无法读取，请先告诉我。

路径不在工作目录中时，提供这份文件的完整路径。此方法只确认这次文件加载，不代表已经安装或加入自动发现目录。

本地 Codex CLI 检查曾观察到读取 `SKILL.md` 后作答，也出现过未读取而直接作答的请求；因此要通过实际记录确认。[验证范围](VERIFICATION.md)。
