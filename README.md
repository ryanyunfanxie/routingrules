# Regional selective service routing rules

# 区域选择性服务路由规则

This repository provides two selective routing rule sets: one for Hong Kong and one for mainland China. Both use DIRECT by default and proxy only services that are unavailable, network-blocked, or subject to clear regional restrictions in the target region.

本仓库提供两套选择性路由规则：香港版和中国大陆版。两套规则都默认直连，只代理在目标地区不可用、被网络阻断或存在明确地区限制的服务。

## Included service groups

## 纳入的服务组

The Hong Kong rule set includes OpenAI / ChatGPT / OpenAI API, Anthropic / Claude / Claude API, Google AI Studio / Gemini API, Google Antigravity / Cloud Code endpoints, and TikTok / ByteDance delivery services.

香港版包含 OpenAI / ChatGPT / OpenAI API、Anthropic / Claude / Claude API、Google AI Studio / Gemini API、Google Antigravity / Cloud Code 端点，以及 TikTok / ByteDance delivery services。

The TikTok entry is marked as region-sensitive because the available evidence differs between the consumer app, app-store listings, and business services.

TikTok 项目标记为区域敏感项，因为消费者应用、应用商店条目和商业服务之间的可用性证据存在差异。

The mainland China rule set includes OpenAI, Claude, Google AI Studio / Gemini, Google services, YouTube, TikTok, Facebook, Instagram, Threads, X / Twitter, Telegram, WhatsApp, Discord, Reddit, and Wikipedia / Wikimedia.

大陆版包含 OpenAI、Claude、Google AI Studio / Gemini、Google 服务、YouTube、TikTok、Facebook、Instagram、Threads、X / Twitter、Telegram、WhatsApp、Discord、Reddit 和 Wikipedia / Wikimedia。

The rule files contain no proxy nodes, passwords, subscription tokens, or token-encryption logic. Anyone with a URL can read the public rule files, but the repository does not provide proxy credentials or nodes.

规则文件不包含代理节点、密码、订阅 token 或 token 加密逻辑。任何拿到 URL 的人都可以读取公开规则，但本仓库不会提供代理节点或认证信息。

## Generate files

## 生成文件

Run the following command from the repository root:

在仓库根目录运行以下命令：

```powershell
python scripts/build_rules.py
```

The build script reads `config/services_hk.json` and `config/services_cn.json`, then updates four rule files in the existing output directories.

构建脚本读取 `config/services_hk.json` 和 `config/services_cn.json`，然后直接更新现有输出目录中的四个规则文件。

- `shadowrocket/routingrules_hk.list` — Hong Kong Shadowrocket remote rule set.
- `shadowrocket/routingrules_hk.list` — 香港版 Shadowrocket 远程规则集。
- `v2rayn/routingrules_hk.json` — Hong Kong v2rayN custom routing JSON.
- `v2rayn/routingrules_hk.json` — 香港版 v2rayN 自定义路由 JSON。
- `shadowrocket/routingrules_cn.list` — mainland China Shadowrocket remote rule set.
- `shadowrocket/routingrules_cn.list` — 大陆版 Shadowrocket 远程规则集。
- `v2rayn/routingrules_cn.json` — mainland China v2rayN custom routing JSON.
- `v2rayn/routingrules_cn.json` — 大陆版 v2rayN 自定义路由 JSON。

The build process does not create new output directories; both rule sets share `public/shadowrocket` and `public/v2rayn`.

构建过程不会创建新的输出目录；两套规则共用 `public/shadowrocket` 和 `public/v2rayn`。

Configure your proxy node or outbound first, then import the matching rule file. The rules do not create a proxy connection by themselves.

请先在客户端配置代理节点或出站，然后导入对应的规则文件。规则本身不能单独建立代理连接。

## GitHub Pages subscription URLs

## GitHub Pages 订阅 URL

The GitHub Actions workflow rebuilds and publishes `public/` whenever the `main` branch is updated. After enabling Settings → Pages → Source: **GitHub Actions**, use these public URLs:

启用 Settings → Pages → Source: **GitHub Actions** 后，GitHub Actions 会在 `main` 分支更新时重新构建并发布 `public/`，公开 URL 如下：

```text
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_hk.list
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_hk.json
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_cn.list
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_cn.json
```

Use the first two URLs in Hong Kong and the last two in mainland China. In Shadowrocket, add the matching `.list` file as a remote rule set and set its policy to `PROXY`. In v2rayN, import the matching `.json` file and make sure your outbound tag is `proxy`.

在香港网络使用前两条 URL，在大陆网络使用后两条 URL。Shadowrocket 中添加对应的 `.list` 文件为远程规则集，并将策略设为 `PROXY`；v2rayN 中导入对应的 `.json` 文件，并确认出站 tag 为 `proxy`。

If your actual outbound tag is different, update `v2rayn_outbound_tag` in the corresponding regional configuration file and rebuild the rules.

如果实际出站 tag 不同，请修改对应地区配置文件中的 `v2rayn_outbound_tag`，然后重新生成规则。

The v2rayN JSON format follows the [v2rayN custom routing rules documentation](https://github.com/2dust/v2rayn/wiki/Description-of-custom-routing-rules).

v2rayN JSON 格式依据 [v2rayN 自定义路由规则说明](https://github.com/2dust/v2rayn/wiki/Description-of-custom-routing-rules)。

## Research scope and limitations

## 研究范围与限制

See [`docs/availability.md`](docs/availability.md) for the evidence and service-by-service notes. The Hong Kong set primarily uses official service availability documentation; the mainland set also considers GreatFire measurements of mainland network blocking. Regional policies and network conditions can change, so the manifests should be reviewed periodically.

详细证据和逐项说明请见 [`docs/availability.md`](docs/availability.md)。香港版主要依据服务商官方可用地区文档；大陆版同时参考 GreatFire 对大陆网络阻断情况的测量。服务商地区政策和网络状况会变化，因此应定期复核配置文件。
