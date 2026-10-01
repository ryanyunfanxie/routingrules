# Hong Kong selective service routing rules

这套规则面向香港网络环境：默认直连，只把已核实在香港不提供、或对香港出口存在明显区域敏感性的服务送到代理。范围不局限于 AI 和开发者工具，也包含 TikTok 这类平台服务。

当前已确认并纳入规则的服务：

- OpenAI / ChatGPT / OpenAI API
- Anthropic / Claude / Claude API
- Google AI Studio / Gemini API（注意：Gemini 网页版与 Gemini API 的地区名单不同）
- Google Antigravity / Cloud Code 开发者端点（根据用户提供的实际端点清单纳入）
- TikTok / ByteDance delivery services（区域敏感，官方证据存在冲突）

没有节点、密码、订阅 token 或 token 加密逻辑。仓库只发布公开可读的规则文件；任何拿到 URL 的人都能读取规则，但不能从本仓库获得代理节点。

## 生成文件

运行：

```powershell
python scripts/build_rules.py
```

输出到 `public/`：

- `shadowrocket/hk-restricted-services.list`：Shadowrocket 远程 Rule Set，策略名默认是 `PROXY`。
- `v2rayn/custom_routing_rules.json`：v2rayN“自定义路由规则”可导入的 JSON 数组，`outboundTag` 默认是 `proxy`。

请先在客户端把代理节点/出站配置好，再导入规则。规则不包含节点，也不能单独建立代理连接。

## GitHub Pages 订阅 URL

`.github/workflows/deploy-pages.yml` 会在 `main` 分支更新后生成并发布 `public/`。启用一次仓库 Settings → Pages → Source: **GitHub Actions** 后，公开 URL 为：

```text
https://ryanyunfanxie.github.io/routingrules/shadowrocket/hk-restricted-services.list
https://ryanyunfanxie.github.io/routingrules/v2rayn/custom_routing_rules.json
```

Shadowrocket 中把第一条添加为远程规则集，规则策略设为 `PROXY`，其余未匹配流量保持 `DIRECT`。v2rayN 中导入第二条，并确认你的出站 tag 叫 `proxy`；如果实际 tag 不同，请在 `config/services.json` 修改 `v2rayn_outbound_tag` 后重新发布。

格式依据：[v2rayN 自定义路由规则说明](https://github.com/2dust/v2rayn/wiki/Description-of-custom-routing-rules)。

## 研究范围与限制

详见 [`docs/availability.md`](docs/availability.md)。判断标准是服务商的官方支持地区/区域文档；对 TikTok 这类证据相互矛盾的平台则明确标记为 `region_sensitive`，不伪装成确定性封锁。服务商地区政策会变化，规则清单应定期复核。
