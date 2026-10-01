# [routingrules](https://ryanyunfanxie.github.io/routingrules/)

Selective routing rules set for Hong Kong and mainland China network.

香港和中国大陆网络环境选择性路由规则集

## Files / 文件

- `shadowrocket/routingrules_hk.conf` — Hong Kong Shadowrocket config / 香港版 Shadowrocket 配置
- `v2rayn/routingrules_hk.json` — Hong Kong v2rayN rules / 香港版 v2rayN 规则
- `shadowrocket/routingrules_cn.conf` — Mainland China Shadowrocket config / 大陆版 Shadowrocket 配置
- `v2rayn/routingrules_cn.json` — Mainland China v2rayN rules / 大陆版 v2rayN 规则

## URLs

```text
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_hk.conf
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_hk.json
https://ryanyunfanxie.github.io/routingrules/shadowrocket/routingrules_cn.conf
https://ryanyunfanxie.github.io/routingrules/v2rayn/routingrules_cn.json
```

Use the Hong Kong URLs in Hong Kong and the mainland China URLs in mainland China. Import `.conf` as a complete Shadowrocket configuration and `.json` as a v2rayN routing profile.

香港使用前两条 URL，大陆使用后两条 URL。`.conf` 作为完整 Shadowrocket 配置导入，`.json` 作为 v2rayN 路由配置导入。

The Hong Kong profile proxies selected restricted services and uses DIRECT as the fallback. The mainland China profile sends mainland and private traffic DIRECT and all other traffic to `proxy`.

香港版代理指定受限服务，默认直连；大陆版将中国大陆和局域网流量直连，其余流量进入 `proxy`。
