# explain-clearly

受 [Andrej Karpathy 关于理解语言模型输出的推文](https://x.com/karpathy/status/2105819303471976479)启发：模型可以用清晰文字、图解和交互网页，帮助人理解和监督它的输出。

和 Agent 对话时，你有没有遇到过：一串术语、一长段解释，读完还是没弄明白，只能继续追问“这个词是什么意思”“能举个例子吗”？

**把不熟悉的专业内容讲清楚，必要时用图解或交互 HTML 看懂过程。**

- **术语讲明白**：用具体例子连接词和步骤，减少反复追问“这是什么意思”。
- **条件留得住**：通俗表达仍保留重要数字、适用条件、风险和不确定性。
- **按需具象化**：文字够用就结束；图或 HTML 确实有帮助时，征得同意后继续生成。

**[在线演示](https://bananasoldier01.github.io/explain-clearly/)** · [下载最新版](https://github.com/BananaSoldier01/explain-clearly/releases/latest) · [完整使用说明](USAGE.md) · [⭐ Star 支持](https://github.com/BananaSoldier01/explain-clearly)

## 安装和使用

把下面这段发给 **Codex、Claude Code、WorkBuddy** 等 Agent，让它按当前版本支持的方式安装：

> 请帮我安装 explain-clearly Skill：
> 仓库：https://github.com/BananaSoldier01/explain-clearly
> Skill 源目录：skills/explain-clearly/
>
> 请按你当前 Agent 支持的安装方式完成安装，保留该目录内的参考、模板和脚本。已有同名技能时先核对来源，不覆盖其他内容；不要修改 AGENTS.md 或 CLAUDE.md。
>
> 完成后验证 explain-clearly 能被发现或调用，告诉我如何使用，以及是否需要重启或新开对话。若某一步必须由我手动操作，请先完成你能做的部分，再说明具体操作。

安装后，按 Agent 给出的调用方法使用，或直接提出：

> 请使用 explain-clearly 解释：RAG 是什么？为什么找到了资料还会答错？

[各 Agent 的安装入口与完整指南](USAGE.md)。

## 看一个文字效果

**问题：** 接口重试里的等待和额度机制分别做什么？

下面是表达方式示意，完整案例中保留了其他机制及适用条件。

**专业式表述：**

> 某 SDK 对可重试的失败采用 exponential backoff 与 jitter，并通过 token bucket 管理 retry quota。

**用 Skill 指导后的易懂表达：**

> 遇到可以重试的失败，先等一等；连续失败时，扩大可选择的等待时间。不同程序随机错开重试。额度像一笔预算，失败会消耗、成功能补回，用完就停止。

[完整表达对照](examples/retry-style.md) · [真实 RAG 文字答复与续问](examples/rag-walkthrough.md)

## 用图和交互 HTML 看清过程

下面用 explain-clearly 自己的工作流程，展示它如何用图和交互 HTML 帮助理解。先看静态总图了解全貌，再打开网页，点击某一步查看说明。

![explain-clearly 工作流程总图：根据语义或用户要求主动触发，讲清内容，并按理解需要继续](examples/screenshots/workflow-overview.png)

**[打开交互演示：点击节点查看做法与示例](https://bananasoldier01.github.io/explain-clearly/examples/workflow.html)**

你直接提出问题或任务即可，不必点名 Skill，也不必特意说“请解释”。Agent 根据语义或用户要求主动应用解释指导；是否自动选用仍取决于所用 Agent 的支持。必要时再建议图解或网页，按对应同意继续。

<details>
<summary>观看流程演示（GIF，约 20 秒）</summary>

下面播放一条示例路径，依次高亮节点并打开说明。上方静态图始终保留完整流程，方便随时查看。

![explain-clearly 流程演示：沿示例路径查看节点与弹窗说明](examples/screenshots/workflow-demo.gif)

</details>

这份流程演示由 Agent 按 explain-clearly 自身的规则与图示、HTML 指导生成。图中的分支和弹窗是预写教学示意，不实时调用模型，也不是模型内部执行轨迹。

## 更多案例与资料

| 想看什么 | 入口 |
| --- | --- |
| 真实文字解释、仍不懂时如何续答 | [RAG 完整对话示例](examples/rag-walkthrough.md) |
| 多个重试术语怎样讲清楚 | [表达方式对照](examples/retry-style.md) · [真实答复](examples/text-retry.md) |
| 图示怎样连接处理步骤 | [缓存流程图](examples/diagram.md) |
| 应用于其他主题的 HTML 示例 | [RAG 教学演示](https://bananasoldier01.github.io/explain-clearly/examples/rag.html) · [自注意力教学演示](https://bananasoldier01.github.io/explain-clearly/examples/attention.html)（主题仅作案例） |
| 带／不带 Skill 有哪些实际差别 | [完整同题对照](examples/text-comparison.md) |
| 工作原理、参考与检查范围 | [Skill 规则](skills/explain-clearly/SKILL.md) · [验证记录](VERIFICATION.md) |

示意与实测分别标注，具体结果见记录；不承诺每次都优于未使用 Skill。明确询问含义、原理，或普通回答涉及影响理解的专业内容时应用；简单直接、纯翻译、润色和只交付代码等按原任务处理。

采用 [MIT 许可证](LICENSE)。中文表达借鉴 [ISO 24495-1](https://www.iso.org/standard/78907.html) 与 [ASD-STE100](https://www.asd-ste100.org/STE_faq.html) 的原则，不宣称标准认证。当前覆盖文字、图解和交互 HTML。
