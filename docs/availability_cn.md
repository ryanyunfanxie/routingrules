# 区域可用性核查（2026-10-02）

这份核查优先使用服务商官方地区页面，并把“确定不支持”和“区域敏感但证据冲突”分开记录。地区支持是账户、付款、IP 出口和具体产品共同决定的；“某个云区域没有该产品”不等价于“香港用户不能访问该产品”。

## 中国大陆版纳入默认代理规则

大陆版使用独立源配置 [`config/services_cn.json`](../config/services_cn.json)，目标是中国大陆网络出口。它不仅处理服务商账户地区限制，也处理大陆网络层面的明确阻断；因此和香港版不是同一份域名清单。

### AI 服务

OpenAI、Anthropic/Claude 和 Google AI Studio/Gemini API 的官方支持地区不包含中国大陆，分别纳入 ChatGPT/API、Claude/API 和 Gemini 相关域名。Google 的 AI Studio 页面明确要求请求来自支持地区，Google AI Developers Forum 也直接回复中国大陆当前不可用。

- [OpenAI ChatGPT 支持地区](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries)
- [OpenAI API 支持地区](https://help.openai.com/en/articles/5347006-openai-api-supported-countries-and-territories)
- [Anthropic Claude 支持地区](https://support.claude.com/en/articles/8461763-where-can-i-access-claude)
- [Google AI Studio / Gemini API 可用地区](https://ai.google.dev/gemini-api/docs/available-regions)
- [Google AI Developers Forum：中国大陆可用性](https://discuss.ai.google.dev/t/a-request-for-help-from-chinese-mainland/178323/2)

### 国际平台

大陆版还纳入 YouTube、TikTok、Facebook、Instagram、Threads、X/Twitter、Telegram、WhatsApp、Discord、Reddit 和 Wikipedia/Wikimedia。GreatFire 的实时测量显示，Google、YouTube、Facebook、Instagram、TikTok、Telegram、WhatsApp、Discord 等域名在大陆存在明确阻断；不同子域和时间点可能表现为 blocked、intermittent 或 unresolvable，因此规则只覆盖这些平台的常用主域、API、媒体和 CDN 域名。

- [GreatFire 当前趋势和大陆测量](https://en.greatfire.org/trends)
- [GreatFire blocked lists](https://en.greatfire.org/blocked)
- [Facebook 测量](https://en.greatfire.org/domain/facebook.com)
- [Instagram 测量](https://en.greatfire.org/domain/instagram.com)
- [TikTok 测量](https://en.greatfire.org/Tiktok.com)
- [YouTube 测量](https://en.greatfire.org/youtube.com%3A443)
- [Telegram 测量](https://en.greatfire.org/domain/t.me)
- [WhatsApp 测量](https://en.greatfire.org/domain/whatsapp.com)
- [Discord 测量](https://en.greatfire.org/domain/discord.com)

TikTok 规则针对国际 TikTok，不是抖音；配置中没有把 `pstatp.com`、`snssdk.com` 等可能与抖音共享的通用 ByteDance 域名加入大陆版，以减少把国内应用流量误送进代理。

## 大陆版暂不纳入的服务

GitHub、GitLab、Cursor、Azure OpenAI、Amazon Bedrock、Google Vertex AI、Hugging Face、OpenRouter、Perplexity 等没有被整体加入大陆版。原因是它们可能只是部分 API、模型、账号、线路或云区域受限，并不能证明所有大陆用户都需要代理整个服务；后续如有具体访问失败域名，可以单独补充。

## 纳入默认代理规则

### OpenAI / ChatGPT / OpenAI API

OpenAI 的 ChatGPT 支持国家/地区列表和 API 支持列表都没有 Hong Kong。OpenAI 同时说明，不在名单内的地区不支持 API，且从不支持地区访问可能导致账号被封锁或暂停。因此默认清单包含 ChatGPT、OpenAI API、平台登录与静态/用户内容域名。

- [ChatGPT Supported Countries](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries)
- [OpenAI API - Supported Countries and Territories](https://help.openai.com/en/articles/5347006-openai-api-supported-countries-and-territories)
- [ChatGPT and API services in unsupported countries and territories](https://help.openai.com/en/articles/9131992-chatgpt-and-api-services-in-unsupported-countries-and-territories)

### Anthropic / Claude / Claude API

Anthropic 在 2026-03-16 更新的 Claude 可用地区列表不包含 Hong Kong。Claude 网页端、控制台及 API 相关域名因此纳入默认代理规则。

- [Where can I access Claude?](https://support.claude.com/en/articles/8461763-where-can-i-access-claude)

### Google AI Studio / Gemini API

Google 的 AI Studio/Gemini API 可用地区页面列出支持的国家和地区，但不包含 Hong Kong。页面还说明地区限制按 Colab 实例所在区域判断，而不是用户所在地；对香港出口的 API 请求，常见结果是 `User location is not supported for the API use`。

不要把 `gemini.google.com` 默认加入这套规则：Google 的 Gemini 网页版有单独的支持名单，官方网页支持页面目前列出 Hong Kong。AI Studio/API 和 Gemini 网页版不能混为一谈。

- [Available regions for Google AI Studio and Gemini API](https://ai.google.dev/gemini-api/docs/available-regions)
- [Where you can use the Gemini web app](https://support.google.com/gemini/answer/13575153)
- [Google AI Developers Forum: API access issue from server in Hong Kong](https://discuss.ai.google.dev/t/api-access-issue-from-server-in-hong-kong/73147)

### Google Antigravity / Cloud Code

你提供的清单还包含 `antigravity.google` 及 `cloudcode-pa.googleapis.com`、`daily-cloudcode-pa.googleapis.com`、`canary-cloudcode-pa.googleapis.com`。Google 官方资料确认 Antigravity 是开发者平台、Cloud Code 是相关开发工具体系，但我没有找到这些端点专门针对香港的官方可用性名单。因此它们按“用户提供的实际开发端点”纳入，后续如果确认香港直连可用，可以从清单中移除以减少代理范围。

- [Google Antigravity](https://antigravity.google/download)
- [Cloud Code overview](https://docs.cloud.google.com/code/docs/vscode/overview)

### TikTok / ByteDance delivery services（区域敏感）

TikTok 不能像 OpenAI、Claude 那样简单标记为“香港确定不可用”：TikTok 在 2020 年公开表示将退出香港并停止当地 App 运营；但后来又有官方公告说明 TikTok 在 App Store 和 Google Play 上可用，TikTok 的商业验证/广告体系也把香港列为部分业务市场。不同产品线、应用商店区域和账号状态可能产生不同结果。

因此默认规则仍然纳入 TikTok 及常见 ByteDance CDN/API 域名，但在清单中标记为 `region_sensitive`。如果你在香港直连 TikTok 已经稳定可用，可以从 `config/services_hk.json` 移除该服务后重新生成，避免不必要的代理流量。

- [TikTok 退出香港的报道及公司声明](https://www.axios.com/2020/07/07/tiktok-to-pull-out-of-hong-kong)
- [TikTok 官方：App Store 和 Google Play 可用](https://newsroom.tiktok.com/tiktok-is-now-available-on-the-app-store-and-play-store?lang=en&pubDate=20250214)
- [TikTok Ads：placements and available locations](https://ads.tiktok.com/resources/help/article/placements-available-locations)

## 已调研但不纳入默认清单

这些服务没有找到足够证据证明“香港用户本身被服务商拒绝”，或者限制属于云资源区域/单一模型的部署差异。把它们放进默认代理会扩大代理面，并不能可靠解决问题。

| 服务 | 结论 |
| --- | --- |
| Google Vertex AI | Google 在 AI Studio 页面把不支持的地区引导到 Gemini Enterprise Agent Platform/Vertex AI。Vertex AI 是另一套区域化云服务，不应按 AI Studio/Gemini API 规则简单替换。[官方说明](https://ai.google.dev/gemini-api/docs/available-regions) |
| Azure OpenAI / Microsoft Foundry | 官方文档按 Azure 资源和模型区域列出可用区域；香港不是某些模型的部署区域，但资源可以部署在其他支持区域。它不是“香港出口必然拒绝”的同类问题。[区域/模型说明](https://learn.microsoft.com/azure/ai-foundry/openai/overview) |
| Amazon Bedrock | AWS 官方区域表列出了 Bedrock 的实际推理区域；香港 `ap-east-1` 不在该表中，但香港用户可以调用其他 AWS 区域的 Bedrock 端点。按云区域选择处理，不加入客户端香港代理规则。[区域表](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints-region-availability.html) |
| Cursor | Cursor 官方说明具体模型供应商可能有区域限制，且直接指向 Anthropic/OpenAI/Google 的地区文档；Cursor 本身不是已确认的香港全面不可用服务。其 Claude/GPT 模型限制由上游供应商决定。[地区说明](https://prod.cursor.com/help/security-and-privacy/regions) |
| xAI / Grok | xAI 官方文档提供全球 API 端点和美国区域端点，没有找到香港不支持的官方地区名单。[区域端点](https://docs.x.ai/developers/advanced-api-usage/regions) |
| GroqCloud | 官方服务协议描述为全球服务，没有找到香港专门限制。[服务协议概览](https://console.groq.com/docs/legal/contractual-framework-overview) |
| Hugging Face | 官方 Hub/API 文档提供全球 API 使用说明，没有找到香港专门限制。[Hub API](https://huggingface.co/docs/hub/api) |
| OpenRouter | OpenRouter 条款明确说某些模型可能按国家/地区限制，并禁止用 VPN/代理规避受限模型；因此不加入默认规则。[服务条款](https://openrouter.ai/terms) |
| TikTok 商业/广告入口 | 香港被列入部分企业验证和商业服务市场，但这不能证明消费者 App 在香港稳定可用；本项目已把 TikTok 整体标成 `region_sensitive`，而不是把广告域名单独当作受限服务。 |
| X / Grok | X 官方说明 Grok 在 X 可用的所有国家/地区提供；X 的商业服务也列出 Hong Kong，因此不加入默认代理规则。[Grok 可用性](https://help.x.com/en/using-x/about-grok) |
| Mistral Vibe / Le Chat | 官方帮助中心提供全球 Web/API 使用入口，但没有找到香港专门不支持的官方名单，因此不加入。[官方帮助中心](https://help.mistral.ai/en/) |
| Sora | OpenAI 已公告 Sora Web/App 于 2026-04-26 停止，API 于 2026-09-24 停止；不应把已停止的产品当作当前香港受限服务。[停止服务说明](https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation) |
| Google Gemini 网页版 | Google 的网页支持名单与 AI Studio/Gemini API 分开，当前名单包含 Hong Kong，因此不加入 `gemini.google.com`。[网页支持地区](https://support.google.com/gemini/answer/13575153) |
| Google NotebookLM | 找到的地区体验反馈不等于官方全球支持清单，且 Workspace/个人账号 rollout 可能不同；暂不把它加入默认规则，后续应以官方地区页为准。 |
| CapCut | 香港 App Store 有 CapCut 主应用条目并显示港币订阅价格；CapCut 的部分模板、AI 功能和试用资格会按地区变化，但没有足够证据证明整个香港服务不可用，因此不加入默认规则。[香港 App Store 条目](https://apps.apple.com/hk/app/capcut-%E7%85%A7%E7%89%87%E8%88%87%E5%BD%B1%E7%89%87%E7%B7%A8%E8%BC%AF%E5%99%A8/id1500855883) · [官方地区功能说明](https://www.capcut.com/help/template-unavailable) |

## 规则设计原则

1. 只匹配明确的服务域名后缀，不使用 `GEOIP`、`FINAL,PROXY` 或“所有海外流量代理”。
2. 未匹配流量由客户端现有配置保持直连。
3. 规则文件是公开的域名清单，不包含节点、账号、密码、token 或认证代理。
4. 如果某服务只在登录阶段失败，可能还需要客户端对其统一身份认证域名单独处理；本项目不把整个 `accounts.google.com` 等公共登录域名加入默认列表，以免把大量无关 Google 流量送进代理。
5. `confirmed_region_restricted` 是跨地区通用的确定性限制标签；`region_sensitive` 表示证据混合或产品线之间存在差异，属于可操作的候选项；`user_provided_operational` 表示根据用户提供的实际端点纳入，不能等同于服务商已公开确认地区限制。

## 与外部清单的差异

你提供的点号前缀（例如 `.openai.com`）等价于本项目生成的 `DOMAIN-SUFFIX,openai.com,PROXY`。本项目在保留这些域名的同时，还保留了开发者 API/控制台域名：`api.openai.com`、`platform.openai.com`、`auth.openai.com`、`api.anthropic.com`、`console.anthropic.com` 和 `makersuite.google.com`。此外，OpenAI 官方网络建议明确列出 `oaistatsig.com`、`cdn.openaimerge.com`，所以本项目按父域后缀加入了 `oaistatsig.com` 和 `openaimerge.com`。

