#!/usr/bin/env python3
"""Build client-specific selective routing rules from both regional manifests."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    ROOT / "config" / "services_hk.json",
    ROOT / "config" / "services_cn.json",
)
DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")

DISPLAY_NAME_ZH = {
    "hk": "香港选择性服务路由规则",
    "cn": "中国大陆白名单路由规则",
}
DESCRIPTION_ZH = {
    "hk": "针对从香港出口不可用或受地区限制的服务进行选择性路由",
    "cn": "中国大陆域名和 IP 直连，其余流量代理",
}
STATUS_ZH = {
    "confirmed_region_restricted": "已确认地区受限",
    "user_provided_operational": "用户提供的实际端点",
    "region_sensitive": "区域敏感",
}
SERVICE_NAME_ZH = {
    ("hk", "openai"): "OpenAI / ChatGPT / API",
    ("hk", "anthropic"): "Anthropic / Claude / Claude API",
    ("hk", "google-ai-studio"): "Google AI Studio / Gemini API",
    ("hk", "google-antigravity"): "Google Antigravity / Cloud Code 端点",
    ("hk", "tiktok"): "TikTok / ByteDance 传输服务",
    ("cn", "openai"): "OpenAI / ChatGPT / API",
    ("cn", "anthropic"): "Anthropic / Claude / Claude API",
    ("cn", "google-ai"): "Google AI Studio / Gemini / Gemini API",
    ("cn", "google-antigravity"): "Google Antigravity / Cloud Code 端点",
    ("cn", "google-services"): "Google 搜索 / Gmail / Google 服务",
    ("cn", "youtube"): "YouTube",
    ("cn", "tiktok"): "TikTok / ByteDance 国际服务",
    ("cn", "meta-social"): "Facebook / Instagram / Threads",
    ("cn", "x-twitter"): "X / Twitter",
    ("cn", "telegram"): "Telegram",
    ("cn", "whatsapp"): "WhatsApp",
    ("cn", "discord"): "Discord",
    ("cn", "reddit"): "Reddit",
    ("cn", "wikipedia"): "Wikipedia / Wikimedia",
    ("cn", "netflix"): "Netflix",
    ("cn", "disney-plus"): "Disney+",
    ("cn", "max"): "Max / HBO Max",
    ("cn", "prime-video"): "Amazon Prime Video",
    ("cn", "twitch"): "Twitch",
    ("cn", "spotify"): "Spotify",
    ("cn", "soundcloud"): "SoundCloud",
    ("cn", "pinterest"): "Pinterest",
    ("cn", "snapchat"): "Snapchat",
    ("cn", "tumblr"): "Tumblr",
    ("cn", "line"): "LINE",
    ("cn", "signal"): "Signal",
    ("cn", "vimeo"): "Vimeo",
    ("cn", "flickr"): "Flickr",
    ("cn", "medium"): "Medium",
    ("cn", "dropbox"): "Dropbox",
    ("cn", "box"): "Box",
    ("cn", "notion"): "Notion",
    ("cn", "steam-community"): "Steam Community",
}
SHADOWROCKET_GEOSITE_DOMAINS = {
    "geosite:google": (
        "google.com",
        "google.com.hk",
        "google.cn",
        "googleapis.com",
        "googleapis.cn",
        "gstatic.com",
        "googleusercontent.com",
        "gmail.com",
        "googlevideo.com",
    ),
}
REASON_ZH = {
    ("hk", "openai"): "OpenAI 官方 ChatGPT 和 API 支持地区列表不包含香港。",
    ("hk", "anthropic"): "Anthropic 官方 Claude 可用地区列表不包含香港。",
    ("hk", "google-ai-studio"): "Google 官方 AI Studio 和 Gemini API 可用地区列表不包含香港；Gemini 网页版有独立的国家/地区名单。",
    ("hk", "google-antigravity"): "该端点来自用户提供的开发者端点清单。Google 官方资料确认 Antigravity 和 Cloud Code 的产品定位，但没有找到这些端点专门针对香港的官方可用性说明。",
    ("hk", "tiktok"): "TikTok 曾宣布退出香港，但当前应用商店和商业服务证据不一致，因此作为香港出口的区域敏感候选项纳入，而不是认定为统一不可用。",
    ("cn", "openai"): "OpenAI 官方 ChatGPT 和 API 支持地区列表不包含中国大陆，且 OpenAI 警告从不支持地区访问可能导致账号暂停。",
    ("cn", "anthropic"): "Anthropic 官方 Claude 可用地区列表不包含中国大陆。",
    ("cn", "google-ai"): "Google 官方 AI Studio 和 Gemini API 可用地区列表不包含中国大陆；Gemini 网页版也不是中国大陆支持的 Google 服务。",
    ("cn", "google-antigravity"): "该端点来自用户提供的开发者端点清单，属于 Google 国际开发者服务；由于相关 Google 服务在中国大陆受限，因此纳入大陆版规则。",
    ("cn", "google-services"): "GreatFire 的当前大陆测量将 Google 列为高度受阻域名。这里只纳入常用 Google 服务域名，并非对所有 Google 主机名一概代理。",
    ("cn", "youtube"): "GreatFire 测量显示 YouTube 及其短链接域名在中国大陆受阻；规则同时覆盖 CDN 和播放器域名以支持应用播放。",
    ("cn", "tiktok"): "GreatFire 的当前测量显示 TikTok 及其 CDN 域名在中国大陆受阻；规则针对国际 TikTok，不针对抖音。",
    ("cn", "meta-social"): "GreatFire 测量显示 Facebook 和 Instagram 在中国大陆受阻；规则同时覆盖 Meta CDN 和 Threads 域名以支持应用加载和媒体传输。",
    ("cn", "x-twitter"): "GreatFire 的阻断数据包含 Twitter 和 X 短链接；规则覆盖 X/Twitter 网页、媒体和跳转域名。",
    ("cn", "telegram"): "GreatFire 测量显示 t.me 在中国大陆受阻；规则覆盖 Telegram 网页、链接、媒体和 CDN 域名。",
    ("cn", "whatsapp"): "GreatFire 测量显示 WhatsApp 及其 CDN 域名在中国大陆大多受阻。",
    ("cn", "discord"): "GreatFire 测量显示 Discord 网站和 API 在中国大陆大多受阻。",
    ("cn", "reddit"): "GreatFire 测量显示 Reddit 短链接域名在中国大陆大多受阻；规则覆盖主站、媒体和静态资源域名。",
    ("cn", "wikipedia"): "GreatFire 测量显示 Wikipedia 和大部分 Wikimedia 域名在中国大陆受阻或受到干扰。",
}


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported schema_version")
    slug = manifest.get("slug")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9_]+(?:-[a-z0-9_]+)*", slug):
        raise ValueError("slug must be a lowercase identifier using letters, digits, underscores, and hyphens")
    region = manifest.get("region")
    if not isinstance(region, str) or not re.fullmatch(r"[a-z0-9-]+", region):
        raise ValueError("region must be a lowercase identifier")
    services = manifest.get("services")
    if not isinstance(services, list) or not services:
        raise ValueError("services must be a non-empty list")

    seen_services: set[str] = set()
    seen_domains: set[str] = set()
    for service in services:
        service_id = service.get("id")
        if not service_id or service_id in seen_services:
            raise ValueError(f"Duplicate or missing service id: {service_id!r}")
        seen_services.add(service_id)
        if service.get("status") not in {
            "confirmed_region_restricted",
            "user_provided_operational",
            "region_sensitive",
        }:
            raise ValueError(f"Unsupported service status: {service_id}")
        domains = service.get("domains")
        if not isinstance(domains, list) or not domains:
            raise ValueError(f"Missing domains for {service_id}")
        for domain in domains:
            if domain != domain.lower() or not DOMAIN_RE.fullmatch(domain):
                raise ValueError(f"Invalid lowercase domain {domain!r} in {service_id}")
            if domain in seen_domains:
                raise ValueError(f"Duplicate domain: {domain}")
            seen_domains.add(domain)
    return manifest


def json_dump(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_shadowrocket(manifest: dict, source: Path, output: Path) -> None:
    if manifest.get("routing_mode") == "mainland_whitelist":
        build_shadowrocket_mainland_whitelist(manifest, source, output)
        return

    policy = manifest["shadowrocket_policy"]
    lines = [
        f"# {manifest.get('display_name', manifest['name'])}",
        "# Selective rules: only matched services use the proxy.",
        f"# Generated from {source.relative_to(ROOT).as_posix()}; checked {manifest['last_checked']}.",
        "# Set the policy name below to the policy/group name in Shadowrocket.",
        "",
    ]
    for service in manifest["services"]:
        lines.append(f"# {service['name']}")
        lines.extend(f"DOMAIN-SUFFIX,{domain},{policy}" for domain in service["domains"])
        lines.append("")
    lines.extend([
        "# Default direct fallback / 默认直连兜底",
        "FINAL,DIRECT",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_shadowrocket_mainland_whitelist(manifest: dict, source: Path, output: Path) -> None:
    whitelist = manifest["mainland_whitelist"]
    direct = manifest.get("shadowrocket_direct_policy", "DIRECT")
    proxy = manifest["shadowrocket_policy"]
    lines = [
        f"# {manifest.get('display_name', manifest['name'])}",
        "# v2rayN-style Mainland China Whitelist: China traffic DIRECT, everything else PROXY.",
        f"# Generated from {source.relative_to(ROOT).as_posix()}; checked {manifest['last_checked']}.",
        "# This is a whitelist profile; it intentionally ends with a proxy fallback.",
        "",
    ]
    if whitelist.get("block_udp443"):
        lines.append("AND,((PROTOCOL,UDP),(DEST-PORT,443)),REJECT")
    for domain_rule in whitelist.get("proxy_domains", []):
        domains = SHADOWROCKET_GEOSITE_DOMAINS.get(domain_rule, (domain_rule,))
        for domain in domains:
            if domain.startswith("geosite:"):
                continue
            lines.append(f"DOMAIN-SUFFIX,{domain},{proxy}")
    lines.extend([
        f"GEOIP,LAN,{direct}",
        f"GEOIP,CN,{direct}",
        f"FINAL,{proxy}",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_v2rayn(manifest: dict, output: Path) -> None:
    if manifest.get("routing_mode") == "mainland_whitelist":
        build_v2rayn_mainland_whitelist(manifest, output)
        return

    outbound = manifest["v2rayn_outbound_tag"]
    rules = []
    for service in manifest["services"]:
        rules.append(
            {
                "port": "",
                "outboundTag": outbound,
                "enabled": True,
                "domain": [f"domain:{domain}" for domain in service["domains"]],
                "remarks": service["name"],
            }
        )
    rules.append(
        {
            "port": "0-65535",
            "outboundTag": manifest.get("v2rayn_direct_outbound_tag", "direct"),
            "enabled": True,
            "remarks": "Default direct / 默认直连",
        }
    )
    json_dump(rules, output)


def build_v2rayn_mainland_whitelist(manifest: dict, output: Path) -> None:
    whitelist = manifest["mainland_whitelist"]
    direct = manifest.get("v2rayn_direct_outbound_tag", "direct")
    proxy = manifest.get("v2rayn_outbound_tag", "proxy")
    block = manifest.get("v2rayn_block_outbound_tag", "block")
    direct_ip = whitelist.get("direct_ip", [])
    direct_domain = whitelist.get("direct_domain", [])
    rules = []

    if whitelist.get("block_udp443"):
        rules.append(
            {
                "remarks": "阻断udp443",
                "outboundTag": block,
                "port": "443",
                "network": "udp",
            }
        )
    proxy_domains = whitelist.get("proxy_domains", [])
    if proxy_domains:
        rules.append(
            {
                "remarks": "代理Google",
                "outboundTag": proxy,
                "domain": proxy_domains,
            }
        )

    private_ip = [item for item in direct_ip if item == "geoip:private"]
    dns_ip = [item for item in direct_ip if item not in {"geoip:private", "geoip:cn"}]
    cn_ip = [item for item in direct_ip if item == "geoip:cn"]
    private_domain = [item for item in direct_domain if item == "geosite:private"]
    dns_domain = [item for item in direct_domain if item not in {"geosite:private", "geosite:cn"}]
    cn_domain = [item for item in direct_domain if item == "geosite:cn"]

    if private_ip:
        rules.append({"remarks": "绕过局域网IP", "outboundTag": direct, "ip": private_ip})
    if private_domain:
        rules.append({"remarks": "绕过局域网域名", "outboundTag": direct, "domain": private_domain})
    if dns_ip:
        rules.append({"remarks": "绕过中国公共DNSIP", "outboundTag": direct, "ip": dns_ip})
    if dns_domain:
        rules.append({"remarks": "绕过中国公共DNS域名", "outboundTag": direct, "domain": dns_domain})
    if cn_ip:
        rules.append({"remarks": "绕过中国IP", "outboundTag": direct, "ip": cn_ip})
    if cn_domain:
        rules.append({"remarks": "绕过中国域名", "outboundTag": direct, "domain": cn_domain})
    if whitelist.get("proxy_fallback", True):
        rules.append(
            {
                "port": "0-65535",
                "outboundTag": proxy,
                "enabled": True,
                "remarks": "Default proxy fallback / 默认代理兜底",
            }
        )
    json_dump(rules, output)


def build_index(manifests: list[dict], output: Path) -> None:
    sections = []
    for manifest in manifests:
        region = manifest["region"]
        service_items = []
        for service in manifest["services"]:
            service_name_zh = SERVICE_NAME_ZH.get((region, service["id"]), service["name"])
            service_items.append(
                f"<li><div lang=\"en\">{html.escape(service['name'])}</div>"
                f"<div lang=\"zh\">{html.escape(service_name_zh)}</div></li>"
            )
        slug = html.escape(manifest["slug"], quote=True)
        display_name = manifest.get("display_name", manifest["name"])
        display_name_zh = DISPLAY_NAME_ZH.get(region, display_name)
        description = manifest.get("description", "")
        description_zh = DESCRIPTION_ZH.get(region, description)
        sections.append(
            f"""<h2>{html.escape(display_name)} / {html.escape(display_name_zh)}</h2>
<p>{html.escape(description)}</p>
<p>{html.escape(description_zh)}</p>
<ul>
<li><a href="shadowrocket/{slug}.list">Shadowrocket rule set / Shadowrocket 规则集</a></li>
<li><a href="v2rayn/{slug}.json">v2rayN custom routing JSON / v2rayN 自定义路由 JSON</a></li>
</ul>
<h3>Sites / 站点</h3>
<ul>{''.join(service_items)}</ul>"""
        )
    body = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>routingrules / 区域选择性服务路由规则</title>
<style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}}p{{margin:.7rem 0}}ul{{padding-left:1.5rem}}li{{margin:.35rem 0}}code{{background:#f1f3f5;padding:.15rem .3rem;border-radius:.25rem}}li div+div{{margin-top:.1rem;color:#333}}a{{margin-right:.6rem}}</style>
<h1>routingrules / 区域选择性服务路由规则</h1>
<p>Regional routing profiles. Public, unauthenticated rule files; no node credentials or subscription tokens are included.</p>
<p>区域路由配置。规则文件公开且无需认证，不包含代理节点凭据或订阅 token。</p>
{''.join(sections)}
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "public")
    args = parser.parse_args()

    manifests = [load_manifest(path) for path in MANIFESTS]
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for source, manifest in zip(MANIFESTS, manifests):
        slug = manifest["slug"]
        build_shadowrocket(manifest, source, output / "shadowrocket" / f"{slug}.list")
        build_v2rayn(manifest, output / "v2rayn" / f"{slug}.json")
    build_index(manifests, output / "index.html")
    (output / "availability.json").write_text(
        json.dumps(
            {
                "rulesets": [
                    {
                        "name": manifest["name"],
                        "display_name": manifest.get("display_name", manifest["name"]),
                        "slug": manifest["slug"],
                        "region": manifest.get("region"),
                        "description": manifest.get("description"),
                        "last_checked": manifest["last_checked"],
                        "services": manifest["services"],
                    }
                    for manifest in manifests
                ],
                "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
