# [routingrules](https://github.com/ryanyunfanxie/routingrules)

Selective routing rules for Hong Kong and mainland China, with Shadowrocket, v2rayN, and Clash/Mihomo outputs.

香港和中国大陆网络环境选择性路由规则集，支持 Shadowrocket、v2rayN 和 Clash/Mihomo。

## Files / 文件

- `shadowrocket/routingrules_hk.conf` — Hong Kong Shadowrocket config / 香港版 Shadowrocket 配置
- `v2rayn/routingrules_hk.json` — Hong Kong v2rayN rules / 香港版 v2rayN 规则
- `shadowrocket/routingrules_cn.conf` — Mainland China Shadowrocket config / 大陆版 Shadowrocket 配置
- `v2rayn/routingrules_cn.json` — Mainland China v2rayN rules / 大陆版 v2rayN 规则
- `clash/routingrules_hk.yaml` — Hong Kong Clash/Mihomo rule provider / 香港版 Clash/Mihomo 规则集
- `clash/routingrules_cn.yaml` — Mainland China Clash/Mihomo rule provider / 大陆版 Clash/Mihomo 规则集

## URLs

```text
hk:
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_hk.conf
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_hk.json
https://ryanyunfanxie.github.io/routingrules/clash/routingrules_hk.yaml
cn:
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_cn.conf
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_cn.json
https://ryanyunfanxie.github.io/routingrules/clash/routingrules_cn.yaml
```

Import `.conf` as a complete Shadowrocket configuration, `.json` as a v2rayN routing profile, or `.yaml` as a Clash/Mihomo `classical` rule provider.

`.conf` 作为完整 Shadowrocket 配置导入，`.json` 作为 v2rayN 路由配置导入，`.yaml` 作为 Clash/Mihomo 的 `classical` 规则集导入。

The Hong Kong profile proxies selected restricted services and uses DIRECT as the fallback. The mainland China profile sends mainland and private traffic DIRECT and all other traffic to `proxy`.

香港版代理指定受限服务，默认直连；大陆版将中国大陆和局域网流量直连，其余流量进入 `proxy`。

The mainland Clash/Mihomo rule provider uses `GEOSITE` and `GEOIP`, so use a Clash Meta/Mihomo-compatible core.

大陆版 Clash/Mihomo 规则使用 `GEOSITE` 和 `GEOIP`，请使用兼容 Clash Meta/Mihomo 的内核。

The YAML files are `classical` rule providers. Add the matching provider to `rule-providers`, then use one of these rule sequences:

这些 YAML 文件是 `classical` 规则集。将对应规则集加入 `rule-providers` 后，使用以下对应规则顺序：

```yaml
# Hong Kong
- RULE-SET,routingrules_hk,PROXY
- MATCH,DIRECT

# Mainland China
- AND,((NETWORK,UDP),(DST-PORT,443)),REJECT
- GEOSITE,google,PROXY
- RULE-SET,routingrules_cn,DIRECT
- MATCH,PROXY
```
