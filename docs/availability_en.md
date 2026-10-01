# Mainland China and Hong Kong availability review (2026-10-02)

This review prioritizes official regional documentation from service providers and separates confirmed unavailability from region-sensitive cases with conflicting evidence. Availability can depend on the account, payment profile, IP egress, and specific product; the absence of a product in one cloud region does not by itself mean that users in Hong Kong cannot access it.

This document covers both generated rule sets: the mainland China set, which addresses provider restrictions and clear mainland network blocking, and the Hong Kong set, which selectively proxies services that do not support Hong Kong egress. The two sections are intentionally separate because a service can be unavailable in mainland China while remaining available in Hong Kong, or vice versa.

## Mainland China rules included by default

The mainland China rule set uses the separate source manifest [`config/services_cn.json`](../config/services_cn.json). It targets mainland China egress and covers both provider-side regional restrictions and clear mainland network blocking, so it is intentionally different from the Hong Kong rule set.

### AI services

The official support regions for OpenAI, Anthropic/Claude, and Google AI Studio/Gemini API do not include mainland China. The rules therefore include the related ChatGPT/API, Claude/API, and Gemini domains. Google's AI Studio documentation requires requests to come from supported regions, and a Google AI Developers Forum response explicitly states that the service is currently unavailable in mainland China.

- [OpenAI ChatGPT supported countries](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries)
- [OpenAI API supported countries](https://help.openai.com/en/articles/5347006-openai-api-supported-countries-and-territories)
- [Anthropic Claude supported regions](https://support.claude.com/en/articles/8461763-where-can-i-access-claude)
- [Google AI Studio / Gemini API available regions](https://ai.google.dev/gemini-api/docs/available-regions)
- [Google AI Developers Forum: mainland China availability](https://discuss.ai.google.dev/t/a-request-for-help-from-chinese-mainland/178323/2)

### International platforms

The mainland rule set also includes YouTube, TikTok, Facebook, Instagram, Threads, X/Twitter, Telegram, WhatsApp, Discord, Reddit, and Wikipedia/Wikimedia. GreatFire's live measurements show clear interference with domains such as Google, YouTube, Facebook, Instagram, TikTok, Telegram, WhatsApp, and Discord. Because individual subdomains and test times can produce `blocked`, `intermittent`, or `unresolvable` results, the rules cover the common primary, API, media, and CDN domains for these platforms.

- [GreatFire current trends and mainland measurements](https://en.greatfire.org/trends)
- [GreatFire blocked lists](https://en.greatfire.org/blocked)
- [Facebook measurement](https://en.greatfire.org/domain/facebook.com)
- [Instagram measurement](https://en.greatfire.org/domain/instagram.com)
- [TikTok measurement](https://en.greatfire.org/Tiktok.com)
- [YouTube measurement](https://en.greatfire.org/youtube.com%3A443)
- [Telegram measurement](https://en.greatfire.org/domain/t.me)
- [WhatsApp measurement](https://en.greatfire.org/domain/whatsapp.com)
- [Discord measurement](https://en.greatfire.org/domain/discord.com)

The TikTok rules target international TikTok, not Douyin. The mainland manifest intentionally excludes generic ByteDance domains such as `pstatp.com` and `snssdk.com` that may be shared with Douyin, reducing the chance of sending domestic-app traffic through the proxy.

## Mainland services not included by default

GitHub, GitLab, Cursor, Azure OpenAI, Amazon Bedrock, Google Vertex AI, Hugging Face, OpenRouter, and Perplexity are not included as whole-service rules. Some may have restrictions affecting only particular APIs, models, accounts, routes, or cloud regions; that is not enough to conclude that every mainland user needs the entire service proxied. Specific failed domains can be added later when there is concrete evidence.

## Services included in the Hong Kong default rules

### OpenAI / ChatGPT / OpenAI API

OpenAI's ChatGPT and API supported-country lists do not include Hong Kong. OpenAI also states that API access is unsupported outside the listed regions and that access from unsupported locations may result in account suspension. The default set therefore includes ChatGPT, OpenAI API, platform login, static, and user-content domains.

- [ChatGPT Supported Countries](https://help.openai.com/en/articles/7947663-chatgpt-supported-countries)
- [OpenAI API - Supported Countries and Territories](https://help.openai.com/en/articles/5347006-openai-api-supported-countries-and-territories)
- [ChatGPT and API services in unsupported countries and territories](https://help.openai.com/en/articles/9131992-chatgpt-and-api-services-in-unsupported-countries-and-territories)

### Anthropic / Claude / Claude API

Anthropic's Claude availability list, updated on 2026-03-16, does not include Hong Kong. The default rules therefore include Claude web, console, and API-related domains.

- [Where can I access Claude?](https://support.claude.com/en/articles/8461763-where-can-i-access-claude)

### Google AI Studio / Gemini API

Google's AI Studio and Gemini API available-regions page lists supported countries and territories but does not include Hong Kong. It also explains that regional restrictions for Colab users are based on the region of the Colab instance rather than the user's physical location; requests from Hong Kong egress commonly receive `User location is not supported for the API use`.

`gemini.google.com` is not included in the Hong Kong default set: the Gemini web app has a separate supported-country list that currently includes Hong Kong. The AI Studio/API and Gemini web products must not be treated as the same service.

- [Available regions for Google AI Studio and Gemini API](https://ai.google.dev/gemini-api/docs/available-regions)
- [Where you can use the Gemini web app](https://support.google.com/gemini/answer/13575153)
- [Google AI Developers Forum: API access issue from a server in Hong Kong](https://discuss.ai.google.dev/t/api-access-issue-from-server-in-hong-kong/73147)

### Google Antigravity / Cloud Code

The supplied list also contains `antigravity.google`, `cloudcode-pa.googleapis.com`, `daily-cloudcode-pa.googleapis.com`, and `canary-cloudcode-pa.googleapis.com`. Google documentation confirms Antigravity as a developer platform and Cloud Code as part of its developer tooling, but no official Hong Kong availability list was found for these endpoints. They are therefore included as user-provided operational developer endpoints and can be removed if direct Hong Kong access is confirmed.

- [Google Antigravity](https://antigravity.google/download)
- [Cloud Code overview](https://docs.cloud.google.com/code/docs/vscode/overview)

### TikTok / ByteDance delivery services (region-sensitive)

TikTok cannot be classified as definitively unavailable in Hong Kong in the same way as OpenAI or Claude. TikTok publicly said in 2020 that it would leave Hong Kong and stop operating the local app, but later official material stated that TikTok was available on the App Store and Google Play, while TikTok's business verification and advertising systems list Hong Kong for some services. Availability can therefore differ by product line, app-store region, and account state.

The default rules still include TikTok and common ByteDance CDN/API domains, but mark the service as `region_sensitive`. If TikTok works reliably over direct Hong Kong egress, remove it from `config/services_hk.json` and rebuild the rules to reduce unnecessary proxy traffic.

- [TikTok reporting and company statement on leaving Hong Kong](https://www.axios.com/2020/07/07/tiktok-to-pull-out-of-hong-kong)
- [TikTok official: available on the App Store and Google Play](https://newsroom.tiktok.com/tiktok-is-now-available-on-the-app-store-and-play-store?lang=en&pubDate=20250214)
- [TikTok Ads: placements and available locations](https://ads.tiktok.com/resources/help/article/placements-available-locations)

## Researched but not included in the Hong Kong default set

These services did not have enough evidence that Hong Kong users themselves are rejected by the provider, or their limitation concerns a cloud-resource region or an individual model rather than the whole service. Adding them by default would expand the proxy scope without reliably solving the original problem.

| Service | Conclusion |
| --- | --- |
| Google Vertex AI | Google's AI Studio page directs unsupported regions toward Gemini Enterprise Agent Platform / Vertex AI. Vertex AI is a separate regional cloud service and should not automatically inherit the AI Studio/Gemini API rule. [Official explanation](https://ai.google.dev/gemini-api/docs/available-regions) |
| Azure OpenAI / Microsoft Foundry | Official documentation lists availability by Azure resource and model region. Hong Kong is not a deployment region for some models, but resources can be deployed in other supported regions; this is not necessarily a Hong Kong-egress rejection. [Region/model documentation](https://learn.microsoft.com/azure/ai-foundry/openai/overview) |
| Amazon Bedrock | AWS documents the actual Bedrock inference regions. Hong Kong `ap-east-1` is not in that list, but users in Hong Kong can call Bedrock endpoints in other AWS regions. This should be handled by cloud-region selection rather than a client-wide Hong Kong proxy rule. [Regional availability](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints-region-availability.html) |
| Cursor | Cursor explains that individual model providers may have regional limitations and points to Anthropic, OpenAI, and Google documentation. Cursor itself is not confirmed to be wholly unavailable in Hong Kong. [Regional notes](https://prod.cursor.com/help/security-and-privacy/regions) |
| xAI / Grok | xAI documents global and US API endpoints, but no official Hong Kong-specific unsupported-region list was found. [Regional endpoints](https://docs.x.ai/developers/advanced-api-usage/regions) |
| GroqCloud | The official service agreement describes a global service and no Hong Kong-specific restriction was found. [Service agreement](https://console.groq.com/docs/legal/contractual-framework-overview) |
| Hugging Face | Official Hub/API documentation describes global API usage and no Hong Kong-specific restriction was found. [Hub API](https://huggingface.co/docs/hub/api) |
| OpenRouter | OpenRouter's terms state that some models may be restricted by country or region and prohibit using VPNs/proxies to bypass model restrictions; it is therefore not included. [Terms](https://openrouter.ai/terms) |
| TikTok business/advertising entry points | Hong Kong appears in some business verification and commercial-service markets, but that does not prove stable consumer-app availability. TikTok is handled as one `region_sensitive` service rather than treating ad domains alone as restricted. |
| X / Grok | X states that Grok is available wherever X is available, and X commercial services list Hong Kong; it is therefore not included by default. [Grok availability](https://help.x.com/en/using-x/about-grok) |
| Mistral Vibe / Le Chat | The official help center provides global web/API entry points, but no Hong Kong-specific unsupported-region list was found. [Official help center](https://help.mistral.ai/en/) |
| Sora | OpenAI announced that the Sora web/app experience ended on 2026-04-26 and the API ended on 2026-09-24; a discontinued product should not be treated as a current Hong Kong-restricted service. [Discontinuation notice](https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation) |
| Google Gemini web app | Google's web-app supported-country list is separate from the AI Studio/Gemini API list and currently includes Hong Kong, so `gemini.google.com` is not included. [Web-app availability](https://support.google.com/gemini/answer/13575153) |
| Google NotebookLM | Available regional feedback is not an official global support list, and rollout may differ between Workspace and personal accounts; it is not included until an official regional page provides stronger evidence. |
| CapCut | The Hong Kong App Store lists the main CapCut app and Hong Kong-dollar subscriptions. Some templates, AI functions, and trial eligibility are region-dependent, but there is not enough evidence that the entire Hong Kong service is unavailable. [Hong Kong App Store listing](https://apps.apple.com/hk/app/capcut-%E7%85%A7%E7%89%87%E8%88%87%E5%BD%B1%E7%89%87%E7%B7%A8%E8%BC%AF%E5%99%A8/id1500855883) · [Official regional feature notes](https://www.capcut.com/help/template-unavailable) |

## Rule design principles

1. Match explicit service domain suffixes only; do not use `GEOIP`, `FINAL,PROXY`, or a rule that proxies all overseas traffic.
2. Unmatched traffic remains DIRECT according to the client's existing configuration.
3. The rule files are public domain lists and contain no nodes, accounts, passwords, tokens, or authentication proxy details.
4. If a service fails only during login, the client may also need selected identity-provider domains. This project does not add broad domains such as `accounts.google.com` to a default list unless a regional manifest explicitly requires them.
5. `confirmed_region_restricted` is the generic label for a confirmed regional restriction. `region_sensitive` means that evidence or product-line behavior differs, while `user_provided_operational` means that endpoints were included from the supplied operational list and are not necessarily provider-confirmed regional restrictions.

## Difference from the supplied list

The supplied dot-prefixed entries, such as `.openai.com`, are equivalent to generated rules such as `DOMAIN-SUFFIX,openai.com,PROXY`. The Hong Kong manifest keeps those domains and also includes developer API/console domains such as `api.openai.com`, `platform.openai.com`, `auth.openai.com`, `api.anthropic.com`, `console.anthropic.com`, and `makersuite.google.com`. OpenAI's network recommendations also explicitly list `oaistatsig.com` and `cdn.openaimerge.com`, so the project includes the parent suffixes `oaistatsig.com` and `openaimerge.com`.
