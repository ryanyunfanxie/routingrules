# routingrules

This repository provides two routing rule sets: a selective service set for Hong Kong and a v2rayN-style mainland China Whitelist. Hong Kong uses DIRECT by default; mainland China sends private and mainland-China traffic DIRECT and proxies everything else.

本仓库提供两套路由规则：香港选择性服务规则，以及复刻 v2rayN“绕过大陆（Whitelist）”逻辑的中国大陆版。香港版默认直连；大陆版将局域网和中国大陆流量直连，其余流量代理。

## Included service groups / 纳入的服务组

The Hong Kong rule set includes OpenAI / ChatGPT / OpenAI API, Anthropic / Claude / Claude API, Google AI Studio / Gemini API, Google Antigravity / Cloud Code endpoints, and TikTok / ByteDance delivery services.

香港版包含 OpenAI / ChatGPT / OpenAI API、Anthropic / Claude / Claude API、Google AI Studio / Gemini API、Google Antigravity / Cloud Code 端点，以及 TikTok / ByteDance delivery services。

The mainland China profile follows the v2rayN Whitelist rule set: private IPs and domains, mainland-China public DNS endpoints, `geoip:cn`, and `geosite:cn` go DIRECT; Google goes PROXY before the mainland rules; all remaining traffic goes to the `proxy` outbound.

大陆版复刻 v2rayN 白名单规则：局域网 IP 和域名、中国大陆公共 DNS、中国大陆 IP（`geoip:cn`）和中国大陆域名（`geosite:cn`）直连；Google 规则优先走代理；其余流量全部进入 `proxy` 出站。

The rule files contain no proxy nodes, passwords, subscription tokens, or token-encryption logic. Anyone with a URL can read the public rule files, but the repository does not provide proxy credentials or nodes.

规则文件不包含代理节点、密码、订阅 token 或 token 加密逻辑。任何拿到 URL 的人都可以读取公开规则，但本仓库不会提供代理节点或认证信息。

## Generate custom rules / 生成自定义规则

After configuring your rules in config/services_xx.json, run the following command from the repository root:

在config/services_xx.json自定义规则后，在仓库根目录运行以下命令：

```powershell
python scripts/build_rules.py
```

The build script reads `config/services_hk.json` and `config/services_cn.json`, then updates four rule files in the existing output directories.

构建脚本读取 `config/services_hk.json` 和 `config/services_cn.json`，然后直接更新现有输出目录中的四个规则文件。

- `shadowrocket/routingrules_hk.list` — Hong Kong Shadowrocket remote rule set / 香港版 Shadowrocket 远程规则集
- `v2rayn/routingrules_hk.json` — Hong Kong v2rayN custom routing JSON / 香港版 v2rayN 自定义路由 JSON
- `shadowrocket/routingrules_cn.list` — mainland China Shadowrocket remote rule set / 大陆版 Shadowrocket 远程规则集
- `v2rayn/routingrules_cn.json` — mainland China v2rayN custom routing JSON / 大陆版 v2rayN 自定义路由 JSON

Configure your proxy node or outbound first, then import the matching rule file. The rules do not create a proxy connection by themselves.

请先在客户端配置代理节点或出站，然后导入对应的规则文件。规则本身不能单独建立代理连接。

## GitHub Pages subscription URLs / GitHub Pages 订阅 URL

```text
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_hk.list
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_hk.json
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_cn.list
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_cn.json
```

Use the first two URLs in Hong Kong and the last two in mainland China. In Shadowrocket, add the matching `.list` file as a remote rule set. In v2rayN, import the matching `.json` file and make sure your `proxy`, `direct`, and `block` outbound tags use those names.

在香港网络使用前两条 URL，在大陆网络使用后两条 URL。Shadowrocket 中添加对应的 `.list` 文件为远程规则集；v2rayN 中导入对应的 `.json` 文件，并确认 `proxy`、`direct`、`block` 出站 tag 与文件一致。

If your actual proxy, direct, or block outbound tag is different, update `v2rayn_outbound_tag`, `v2rayn_direct_outbound_tag`, or `v2rayn_block_outbound_tag` in the corresponding regional configuration file and rebuild the rules.

如果实际的代理、直连或阻断出站 tag 不同，请修改对应地区配置文件中的 `v2rayn_outbound_tag`、`v2rayn_direct_outbound_tag` 或 `v2rayn_block_outbound_tag`，然后重新生成规则。

The v2rayN JSON format follows the [v2rayN custom routing rules documentation](https://github.com/2dust/v2rayn/wiki/Description-of-custom-routing-rules). Each regional JSON is an independent routing profile at the same level as Global, Whitelist, and Blacklist; select only one active routing profile. The Hong Kong profile ends with a full-port `direct` fallback. The mainland profile instead ends with a full-port `proxy` fallback, which is required for Whitelist behavior.

v2rayN JSON 格式依据 [v2rayN 自定义路由规则说明](https://github.com/2dust/v2rayn/wiki/Description-of-custom-routing-rules)。每个地区的 JSON 都是与 Global、Whitelist、Blacklist 同级的独立路由配置，只选择一个启用。香港版最后是全端口 `direct` 兜底；大陆版最后改为全端口 `proxy` 兜底，这是白名单模式所必需的行为。

## Research scope and limitations / 研究范围与限制

See [`docs/availability_en.md`](docs/availability_en.md) for the English evidence and service-by-service notes for both mainland China and Hong Kong. The Hong Kong set primarily uses official service availability documentation; the mainland set also considers GreatFire measurements of mainland network blocking. Regional policies and network conditions can change, so the manifests should be reviewed periodically.

大陆和香港的详细证据及逐项说明请见 [`docs/availability_cn.md`](docs/availability_cn.md)。香港版主要依据服务商官方可用地区文档；大陆版同时参考 GreatFire 对大陆网络阻断情况的测量。服务商地区政策和网络状况会变化，因此应定期复核配置文件。
