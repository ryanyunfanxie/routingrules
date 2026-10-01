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
    "cn": "中国大陆选择性服务路由规则",
}
DESCRIPTION_ZH = {
    "hk": "针对从香港出口不可用或受地区限制的服务进行选择性路由",
    "cn": "针对从中国大陆出口受限制或不可用的服务进行选择性路由",
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_v2rayn(manifest: dict, output: Path) -> None:
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
    json_dump(rules, output)


def build_index(manifests: list[dict], output: Path) -> None:
    sections = []
    for manifest in manifests:
        region = manifest["region"]
        service_rows = []
        for service in manifest["services"]:
            links = " ".join(
                f'<a href="{html.escape(source["url"], quote=True)}">source / 来源</a>'
                for source in service["sources"]
            )
            service_name_zh = SERVICE_NAME_ZH.get((region, service["id"]), service["name"])
            reason_zh = REASON_ZH.get((region, service["id"]), service["reason"])
            status_zh = STATUS_ZH.get(service["status"], service["status"])
            service_rows.append(
                "<tr>"
                f"<td><div lang=\"en\">{html.escape(service['name'])}</div><div lang=\"zh\">{html.escape(service_name_zh)}</div></td>"
                f"<td><div lang=\"en\"><code>{html.escape(service['status'])}</code></div><div lang=\"zh\"><code>{html.escape(status_zh)}</code></div></td>"
                f"<td><div lang=\"en\">{html.escape(service['reason'])}</div><div lang=\"zh\">{html.escape(reason_zh)}</div></td>"
                f"<td>{links}</td>"
                "</tr>"
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
<table><thead><tr><th>Service / 服务</th><th>Status / 状态</th><th>Why included / 纳入原因</th><th>Sources / 来源</th></tr></thead><tbody>{''.join(service_rows)}</tbody></table>"""
        )
    body = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>routingrules / 区域选择性服务路由规则</title>
<style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}}p{{margin:.7rem 0}}code{{background:#f1f3f5;padding:.15rem .3rem;border-radius:.25rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;text-align:left;vertical-align:top}}td div+div{{margin-top:.45rem;color:#333}}a{{margin-right:.6rem}}</style>
<h1>routingrules / 区域选择性服务路由规则</h1>
<p>Regional selective routing rules. Public, unauthenticated rule files; no node credentials or subscription tokens are included.</p>
<p>区域选择性服务路由规则。规则文件公开且无需认证，不包含代理节点凭据或订阅 token。</p>
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
